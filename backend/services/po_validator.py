from rapidfuzz import fuzz, process
from models.db_setup import execute_query
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class POValidator:
    def __init__(self):
        self.vendor_similarity_threshold = 80
        self.item_similarity_threshold = 75
        self.price_tolerance_percentage = 5  # 5% tolerance for price differences
    
    def validate_invoice_against_pos(self, invoice_data):
        """
        Validate an invoice against all purchase orders in the database
        Returns a comprehensive validation report
        """
        try:
            # Get all purchase orders from database
            pos = execute_query("SELECT * FROM purchase_orders ORDER BY date DESC")
            
            if not pos:
                return {
                    'status': 'error',
                    'message': 'No purchase orders found in database',
                    'matches': [],
                    'mismatches': []
                }
            
            # Find potential matches
            matches = self._find_potential_matches(invoice_data, pos)
            
            # Perform detailed validation
            validation_result = self._perform_detailed_validation(invoice_data, matches, pos)
            
            # Generate summary
            validation_result['summary'] = self._generate_validation_summary(validation_result)
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating invoice: {str(e)}")
            return {
                'status': 'error',
                'message': f'Validation error: {str(e)}',
                'matches': [],
                'mismatches': []
            }
    
    def _find_potential_matches(self, invoice_data, pos):
        """Find potential PO matches based on vendor and item similarity"""
        potential_matches = []
        
        invoice_vendor = (invoice_data.get('vendor') or '').strip()
        invoice_items = invoice_data.get('line_items', [])
        
        for po in pos:
            match_score = 0
            match_details = {
                'po_id': po['po_id'],
                'po_vendor': po['vendor'],
                'po_item': po['item'],
                'vendor_similarity': 0,
                'item_similarity': 0,
                'overall_score': 0,
                'po_data': dict(po)
            }
            
            # Check vendor similarity
            if invoice_vendor:
                vendor_similarity = fuzz.ratio(invoice_vendor.lower(), po['vendor'].lower())
                match_details['vendor_similarity'] = vendor_similarity
                
                if vendor_similarity >= self.vendor_similarity_threshold:
                    match_score += vendor_similarity * 0.6  # Vendor match is 60% of score
            
            # Check item similarity
            best_item_similarity = 0
            for invoice_item in invoice_items:
                item_name = (invoice_item.get('item') or '').strip()
                if item_name:
                    item_similarity = fuzz.ratio(item_name.lower(), po['item'].lower())
                    best_item_similarity = max(best_item_similarity, item_similarity)
            
            match_details['item_similarity'] = best_item_similarity
            if best_item_similarity >= self.item_similarity_threshold:
                match_score += best_item_similarity * 0.4  # Item match is 40% of score
            
            match_details['overall_score'] = match_score
            
            # Only include matches above a certain threshold
            if match_score >= 50:  # Minimum 50% overall match
                potential_matches.append(match_details)
        
        # Sort by overall score descending
        potential_matches.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return potential_matches
    
    def _perform_detailed_validation(self, invoice_data, matches, all_pos):
        """Perform detailed validation against the best matches"""
        validation_result = {
            'status': 'processed',
            'invoice_data': invoice_data,
            'matches': [],
            'mismatches': [],
            'warnings': [],
            'validation_timestamp': datetime.now().isoformat()
        }
        
        if not matches:
            validation_result['mismatches'].append({
                'type': 'no_matching_po',
                'severity': 'high',
                'message': 'No matching purchase order found for this invoice',
                'details': {
                    'invoice_vendor': invoice_data.get('vendor'),
                    'invoice_items': [item.get('item') for item in invoice_data.get('line_items', [])]
                }
            })
            return validation_result
        
        # Validate against the best matches
        for i, match in enumerate(matches[:3]):  # Check top 3 matches
            po_data = match['po_data']
            match_validation = self._validate_against_single_po(invoice_data, po_data, match)
            
            if match_validation['is_valid']:
                validation_result['matches'].append(match_validation)
            else:
                validation_result['mismatches'].extend(match_validation['issues'])
            
            # Only process the best match in detail
            if i == 0:
                validation_result['best_match'] = match_validation
        
        return validation_result
    
    def _validate_against_single_po(self, invoice_data, po_data, match_info):
        """Validate invoice against a single purchase order"""
        validation = {
            'po_id': po_data['po_id'],
            'match_score': match_info['overall_score'],
            'is_valid': True,
            'issues': [],
            'details': {}
        }
        
        # Vendor validation
        invoice_vendor = (invoice_data.get('vendor') or '').strip()
        if invoice_vendor and match_info['vendor_similarity'] < self.vendor_similarity_threshold:
            validation['is_valid'] = False
            validation['issues'].append({
                'type': 'vendor_mismatch',
                'severity': 'high',
                'message': f'Vendor mismatch: Invoice shows "{invoice_vendor}", PO shows "{po_data["vendor"]}"',
                'details': {
                    'invoice_vendor': invoice_vendor,
                    'po_vendor': po_data['vendor'],
                    'similarity_score': match_info['vendor_similarity']
                }
            })
        
        # Item and quantity validation
        invoice_items = invoice_data.get('line_items', [])
        po_item = po_data['item']
        po_qty = po_data['qty']
        po_unit_price = po_data['unit_price']
        po_total = po_data['total']
        
        item_found = False
        for invoice_item in invoice_items:
            item_similarity = fuzz.ratio(invoice_item.get('item', '').lower(), po_item.lower())
            
            if item_similarity >= self.item_similarity_threshold:
                item_found = True
                
                # Quantity validation
                invoice_qty = invoice_item.get('qty', 0)
                if invoice_qty != po_qty:
                    validation['issues'].append({
                        'type': 'quantity_mismatch',
                        'severity': 'medium',
                        'message': f'Quantity mismatch for {po_item}: Invoice shows {invoice_qty}, PO shows {po_qty}',
                        'details': {
                            'item': po_item,
                            'invoice_qty': invoice_qty,
                            'po_qty': po_qty,
                            'difference': invoice_qty - po_qty
                        }
                    })
                
                # Price validation
                invoice_unit_price = invoice_item.get('unit_price', 0)
                price_difference_pct = abs(invoice_unit_price - po_unit_price) / po_unit_price * 100 if po_unit_price > 0 else 100
                
                if price_difference_pct > self.price_tolerance_percentage:
                    validation['issues'].append({
                        'type': 'price_mismatch',
                        'severity': 'medium',
                        'message': f'Price mismatch for {po_item}: Invoice shows ${invoice_unit_price}, PO shows ${po_unit_price}',
                        'details': {
                            'item': po_item,
                            'invoice_unit_price': invoice_unit_price,
                            'po_unit_price': po_unit_price,
                            'difference_percentage': round(price_difference_pct, 2)
                        }
                    })
                
                # Total validation
                invoice_total = invoice_item.get('total', 0)
                expected_total = invoice_qty * po_unit_price
                total_difference_pct = abs(invoice_total - expected_total) / expected_total * 100 if expected_total > 0 else 100
                
                if total_difference_pct > self.price_tolerance_percentage:
                    validation['issues'].append({
                        'type': 'total_mismatch',
                        'severity': 'medium',
                        'message': f'Total mismatch for {po_item}: Invoice shows ${invoice_total}, expected ${expected_total}',
                        'details': {
                            'item': po_item,
                            'invoice_total': invoice_total,
                            'expected_total': expected_total,
                            'difference_percentage': round(total_difference_pct, 2)
                        }
                    })
                
                break
        
        if not item_found:
            validation['is_valid'] = False
            validation['issues'].append({
                'type': 'item_not_found',
                'severity': 'high',
                'message': f'Item "{po_item}" from PO not found in invoice',
                'details': {
                    'po_item': po_item,
                    'invoice_items': [item.get('item') for item in invoice_items]
                }
            })
        
        # Date validation (optional warning)
        invoice_date = invoice_data.get('date')
        po_date = po_data['date']
        if invoice_date and po_date:
            try:
                invoice_dt = datetime.strptime(invoice_date, '%Y-%m-%d')
                po_dt = datetime.strptime(po_date, '%Y-%m-%d')
                if invoice_dt < po_dt:
                    validation['issues'].append({
                        'type': 'date_warning',
                        'severity': 'low',
                        'message': f'Invoice date ({invoice_date}) is before PO date ({po_date})',
                        'details': {
                            'invoice_date': invoice_date,
                            'po_date': po_date
                        }
                    })
            except ValueError:
                pass  # Skip date validation if format is invalid
        
        # Set overall validity based on high severity issues
        high_severity_issues = [issue for issue in validation['issues'] if issue['severity'] == 'high']
        if high_severity_issues:
            validation['is_valid'] = False
        
        return validation
    
    def _generate_validation_summary(self, validation_result):
        """Generate a summary of the validation results"""
        total_issues = len(validation_result['mismatches'])
        high_severity = len([issue for issue in validation_result['mismatches'] if issue.get('severity') == 'high'])
        medium_severity = len([issue for issue in validation_result['mismatches'] if issue.get('severity') == 'medium'])
        low_severity = len([issue for issue in validation_result['mismatches'] if issue.get('severity') == 'low'])
        
        has_matches = len(validation_result['matches']) > 0
        
        if has_matches and total_issues == 0:
            status = 'approved'
            message = 'Invoice successfully validated against purchase order'
        elif has_matches and high_severity == 0:
            status = 'approved_with_warnings'
            message = f'Invoice approved with {total_issues} minor issues'
        elif has_matches:
            status = 'rejected'
            message = f'Invoice rejected due to {high_severity} critical issues'
        else:
            status = 'no_po_match'
            message = 'No matching purchase order found'
        
        return {
            'status': status,
            'message': message,
            'total_issues': total_issues,
            'severity_breakdown': {
                'high': high_severity,
                'medium': medium_severity,
                'low': low_severity
            },
            'has_matches': has_matches
        }

# Convenience function for external use
def validate_invoice(invoice_data):
    """Validate an invoice against purchase orders"""
    validator = POValidator()
    return validator.validate_invoice_against_pos(invoice_data)
