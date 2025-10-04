from flask import Blueprint, request, jsonify, current_app
import os
import uuid
from werkzeug.utils import secure_filename
from services.invoice_parser import parse_invoice_file
from services.po_validator import validate_invoice
from models.db_setup import execute_query, update_leaderboard_score
import json

invoice_bp = Blueprint('invoices', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@invoice_bp.route('/upload', methods=['POST'])
def upload_invoice():
    """
    Upload and process an invoice file
    Accepts PDF or image files and returns validation results
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        team_id = request.form.get('team_id')  # Optional team ID for scoring
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Please upload PDF or image files.'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Ensure upload folder exists
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        try:
            # Parse the invoice
            invoice_data = parse_invoice_file(file_path)
            
            if 'error' in invoice_data:
                return jsonify({
                    'error': 'Failed to parse invoice',
                    'details': invoice_data['error']
                }), 400
            
            # Validate against purchase orders
            validation_result = validate_invoice(invoice_data)
            
            # Save invoice to database if parsing was successful
            if invoice_data.get('invoice_number'):
                invoice_id = invoice_data['invoice_number']
                
                # Save main invoice record (using first line item or defaults)
                line_items = invoice_data.get('line_items', [])
                if line_items:
                    first_item = line_items[0]
                    item_name = first_item.get('item', 'Unknown Item')
                    qty = first_item.get('qty', 1)
                    unit_price = first_item.get('unit_price', 0)
                    total = first_item.get('total', 0)
                else:
                    item_name = 'Unknown Item'
                    qty = 1
                    unit_price = float(invoice_data.get('total', 0))
                    total = unit_price
                
                # Determine PO ID from validation results
                po_id = None
                if validation_result.get('matches'):
                    po_id = validation_result['matches'][0]['po_id']
                elif validation_result.get('best_match'):
                    po_id = validation_result['best_match']['po_id']
                
                # Determine status from validation
                summary = validation_result.get('summary', {})
                status = summary.get('status', 'pending')
                
                try:
                    execute_query("""
                        INSERT OR REPLACE INTO invoices 
                        (invoice_id, vendor, item, qty, unit_price, total, date, po_id, status, validation_result)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        invoice_id,
                        invoice_data.get('vendor', 'Unknown Vendor'),
                        item_name,
                        qty,
                        unit_price,
                        total,
                        invoice_data.get('date', ''),
                        po_id,
                        status,
                        json.dumps(validation_result)
                    ))
                    current_app.logger.info(f"Successfully saved invoice {invoice_id} to database")

                    # Insert extracted line items into purchase_orders if not already present
                    for item in line_items:
                        # Check if PO for this vendor/item/date already exists
                        existing_po = execute_query(
                            "SELECT po_id FROM purchase_orders WHERE vendor = ? AND item = ? AND date = ?",
                            (invoice_data.get('vendor', 'Unknown Vendor'), item.get('item', ''), invoice_data.get('date', ''))
                        )
                        if not existing_po:
                            # Generate a new PO ID
                            new_po_id = f"PO-{invoice_id}-{item.get('item', '').replace(' ', '').upper()}"
                            execute_query("""
                                INSERT INTO purchase_orders (po_id, vendor, item, qty, unit_price, total, date)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (
                                new_po_id,
                                invoice_data.get('vendor', 'Unknown Vendor'),
                                item.get('item', ''),
                                item.get('qty', 1),
                                item.get('unit_price', 0.0),
                                item.get('total', 0.0),
                                invoice_data.get('date', '')
                            ))
                            current_app.logger.info(f"Inserted new PO {new_po_id} for item {item.get('item', '')}")

                    # Update leaderboard if team_id provided
                    if team_id:
                        score_increment = 20 if status == 'approved' else 10
                        update_leaderboard_score(team_id, validation_increment=1, score_increment=score_increment)
                
                except Exception as db_error:
                    current_app.logger.error(f"Failed to save invoice to database: {str(db_error)}")
                    current_app.logger.error(f"Invoice data: {invoice_data}")
                    current_app.logger.error(f"Validation result: {validation_result}")
                    # Still continue with response despite DB error
            
            # Return combined results
            return jsonify({
                'success': True,
                'invoice_data': invoice_data,
                'validation_result': validation_result,
                'filename': filename
            })
            
        finally:
            # Keep uploaded file in uploads folder for record keeping
            # Only clean up on error or if explicitly requested
            pass
        
    except Exception as e:
        current_app.logger.error(f"Error processing invoice upload: {str(e)}")
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

@invoice_bp.route('/list', methods=['GET'])
def list_invoices():
    """
    Get a list of all processed invoices
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        invoices = execute_query("""
            SELECT invoice_id, vendor, item, qty, unit_price, total, date, 
                   po_id, status, created_at 
            FROM invoices 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        # Get total count
        total_count = execute_query("SELECT COUNT(*) as count FROM invoices")[0]['count']
        
        return jsonify({
            'success': True,
            'invoices': invoices,
            'total_count': total_count,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        current_app.logger.error(f"Error listing invoices: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@invoice_bp.route('/<invoice_id>', methods=['GET'])
def get_invoice_details(invoice_id):
    """
    Get detailed information about a specific invoice
    """
    try:
        invoice = execute_query("""
            SELECT * FROM invoices WHERE invoice_id = ?
        """, (invoice_id,))
        
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        invoice_data = invoice[0]
        
        # Parse validation result if available
        if invoice_data['validation_result']:
            try:
                invoice_data['validation_result'] = json.loads(invoice_data['validation_result'])
            except:
                pass
        
        return jsonify({
            'success': True,
            'invoice': invoice_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting invoice details: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@invoice_bp.route('/validate', methods=['POST'])
def validate_invoice_data():
    """
    Validate invoice data directly (without file upload)
    Useful for testing or API integration
    """
    try:
        invoice_data = request.get_json()
        
        if not invoice_data:
            return jsonify({'error': 'No invoice data provided'}), 400
        
        # Validate the invoice data
        validation_result = validate_invoice(invoice_data)
        
        return jsonify({
            'success': True,
            'validation_result': validation_result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error validating invoice data: {str(e)}")
        return jsonify({'error': f'Validation error: {str(e)}'}), 500

@invoice_bp.route('/stats', methods=['GET'])
def get_invoice_stats():
    """
    Get invoice processing statistics
    """
    try:
        stats = {}
        
        # Total invoices
        total_result = execute_query("SELECT COUNT(*) as count FROM invoices")
        stats['total_invoices'] = total_result[0]['count'] if total_result else 0
        
        # Status breakdown
        status_results = execute_query("""
            SELECT status, COUNT(*) as count 
            FROM invoices 
            GROUP BY status
        """)
        stats['status_breakdown'] = {row['status']: row['count'] for row in status_results}
        
        # Recent activity (last 7 days)
        recent_results = execute_query("""
            SELECT COUNT(*) as count 
            FROM invoices 
            WHERE created_at >= date('now', '-7 days')
        """)
        stats['recent_activity'] = recent_results[0]['count'] if recent_results else 0
        
        # Top vendors
        vendor_results = execute_query("""
            SELECT vendor, COUNT(*) as invoice_count, SUM(total) as total_amount
            FROM invoices 
            GROUP BY vendor 
            ORDER BY invoice_count DESC 
            LIMIT 5
        """)
        stats['top_vendors'] = vendor_results
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting invoice stats: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
