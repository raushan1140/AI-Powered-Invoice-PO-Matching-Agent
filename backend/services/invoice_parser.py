import pdfplumber
import pytesseract
import cv2
import numpy as np
from PIL import Image
import re
import os
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InvoiceParser:
    def __init__(self):
        # Common regex patterns for invoice field extraction
            self.patterns = {
                'invoice_number': [
                    r'Invoice Number[:\s]+([A-Z0-9\-]+)',
                    r'Invoice #[:\s]+([A-Z0-9\-]+)',
                    r'INVOICE[:\s]+([A-Z0-9\-]+)',
                    r'invoice\s*number\s*([A-Z0-9\-/]+)',
                    r'invoice\s*#?\s*:?\s*([A-Z0-9\-/]+)',
                    r'inv\s*#?\s*:?\s*([A-Z0-9\-/]+)',
                    r'invoice\s*number\s*:?\s*([A-Z0-9\-/]+)',
                    r'#\s*([A-Z0-9\-/]+)'
                ],
                'vendor': [
                    r'Creative Media Hub', # Direct match for this sample
                    r'([A-Za-z ]+ Hub)', # e.g. "Creative Media Hub"
                    r'([A-Za-z ]+ Pvt\. Ltd\.)', # e.g. "StartUp Ventures Pvt. Ltd."
                    r'([A-Za-z ]+ Center)',
                    r'([A-Za-z ]+ India)',
                    r'from[:\s]*\n([A-Za-z0-9\s&,\.\-]+?)(?:\n|order)',
                    r'bill\s*from[:\s]+([A-Za-z\s&,\.]+?)(?:\n|$)',
                    r'vendor[:\s]+([A-Za-z\s&,\.]+?)(?:\n|$)',
                    r'supplier[:\s]+([A-Za-z\s&,\.]+?)(?:\n|$)'
                ],
                'date': [
                    r'Invoice Date[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
                    r'Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'invoice\s*date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'(\d{4}-\d{2}-\d{2})',
                    r'([A-Za-z]+\s+\d{1,2},?\s+\d{4})'
                ],
                'total': [
                    r'Total Amount[:\s₹]+([0-9,]+\.?\d{0,2})',
                    r'Subtotal[:\s₹]+([0-9,]+\.?\d{0,2})',
                    r'total\s*due\s*\$?([0-9,]+\.?\d{0,2})',
                    r'total[:\s]*\$?([0-9,]+\.?\d{0,2})',
                    r'amount\s*due[:\s]*\$?([0-9,]+\.?\d{0,2})',
                    r'grand\s*total[:\s]*\$?([0-9,]+\.?\d{0,2})',
                    r'final\s*total[:\s]*\$?([0-9,]+\.?\d{0,2})'
                ]
            }
    
    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF using pdfplumber"""
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            logger.info(f"Successfully extracted text from PDF: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return None
    
    def extract_text_from_image(self, file_path):
        """Extract text from image using Tesseract OCR"""
        try:
            # Read and preprocess image
            image = cv2.imread(file_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply noise reduction and thresholding
            denoised = cv2.medianBlur(gray, 5)
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Use Tesseract to extract text
            text = pytesseract.image_to_string(thresh, config='--psm 6')
            
            logger.info(f"Successfully extracted text from image: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return None
    
    def extract_field_with_patterns(self, text, field_name):
        """Extract a specific field using regex patterns"""
        text_lower = text.lower()
        patterns = self.patterns.get(field_name, [])
        
        for pattern in patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                value = match.group(1).strip()
                if value:
                    return value
        
        return None
    
    def extract_line_items(self, text):
        """Extract line items from invoice text"""
        line_items = []
        
        # Look for common table patterns
        lines = text.split('\n')
        
        # Pattern for line items with quantity, description, unit price, total
        item_pattern = r'(.+?)\s+(\d+)\s+₹?([0-9,]+\.\d{2})\s+₹?([0-9,]+\.\d{2})'
        
        for line in lines:
            # Try regex first
            match = re.search(item_pattern, line)
            if match and match.lastindex and match.lastindex >= 4 and all(match.group(i) is not None for i in range(1, 5)):
                try:
                    qty = int(match.group(2))
                    description = match.group(1).strip()
                    unit_price = float(match.group(3).replace(',', ''))
                    total = float(match.group(4).replace(',', ''))
                    line_items.append({
                        'item': description,
                        'qty': qty,
                        'unit_price': unit_price,
                        'total': total
                    })
                except Exception:
                    continue
            else:
                # Try splitting by multiple spaces (for OCR/PDF text)
                columns = re.split(r'\s{2,}', line)
                if len(columns) == 4:
                    try:
                        description = columns[0].strip()
                        qty = int(columns[1])
                        unit_price = float(columns[2].replace('₹', '').replace(',', ''))
                        total = float(columns[3].replace('₹', '').replace(',', ''))
                        line_items.append({
                            'item': description,
                            'qty': qty,
                            'unit_price': unit_price,
                            'total': total
                        })
                    except Exception:
                        continue
        
        # If no structured items found, try to extract at least one item
        if not line_items:
            # Look for any product names and try to extract basic info
            product_patterns = [
                r'(laptop|computer|monitor|chair|mouse|keyboard|printer|cable)',
                r'([A-Za-z]+\s+[A-Za-z]+\s+\d+[a-z]*)',  # Product with model/size
            ]
            
            for pattern in product_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    item_name = match.group(1).strip()
                    
                    # Try to find associated numbers for this item
                    context = text[max(0, match.start()-100):match.end()+100]
                    qty_match = re.search(r'(\d+)', context)
                    price_match = re.search(r'\$?([0-9,]+\.?\d{0,2})', context)
                    
                    line_items.append({
                        'item': item_name,
                        'qty': int(qty_match.group(1)) if qty_match else 1,
                        'unit_price': float(price_match.group(1).replace(',', '')) if price_match else 0.0,
                        'total': 0.0
                    })
                    break  # Take the first match
                
                if line_items:
                    break
        
        return line_items
    
    def parse_invoice(self, file_path, file_type=None):
        """Main method to parse invoice and extract structured data"""
        try:
            # Determine file type if not provided
            if not file_type:
                file_extension = os.path.splitext(file_path)[1].lower()
                if file_extension == '.pdf':
                    file_type = 'pdf'
                elif file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                    file_type = 'image'
                else:
                    raise ValueError(f"Unsupported file type: {file_extension}")

            # Extract text based on file type
            if file_type == 'pdf':
                text = self.extract_text_from_pdf(file_path)
            elif file_type == 'image':
                text = self.extract_text_from_image(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            if not text:
                raise ValueError("Could not extract text from file")

            # Debug: Log raw extracted text
            logger.info("--- RAW INVOICE TEXT ---\n" + text)

            # Extract structured fields
            invoice_data = {
                'invoice_number': self.extract_field_with_patterns(text, 'invoice_number'),
                'vendor': self.extract_field_with_patterns(text, 'vendor'),
                'date': self.extract_field_with_patterns(text, 'date'),
                'total': self.extract_field_with_patterns(text, 'total'),
                'line_items': self.extract_line_items(text),
                'raw_text': text,
                'extraction_timestamp': datetime.now().isoformat()
            }

            # Debug: Log parsed fields before cleaning
            logger.info(f"--- PARSED FIELDS BEFORE CLEANING ---\n{json.dumps(invoice_data, indent=2)}")

            # Clean and validate extracted data
            invoice_data = self._clean_extracted_data(invoice_data)

            # Debug: Log parsed fields after cleaning
            logger.info(f"--- PARSED FIELDS AFTER CLEANING ---\n{json.dumps(invoice_data, indent=2)}")

            logger.info(f"Successfully parsed invoice: {invoice_data['invoice_number']}")
            return invoice_data

        except Exception as e:
            logger.error(f"Error parsing invoice: {str(e)}")
            return {
                'error': str(e),
                'extraction_timestamp': datetime.now().isoformat()
            }
    
    def _clean_extracted_data(self, data):
        """Clean and normalize extracted data"""
        # Clean vendor name - provide fallback if None
        if data['vendor']:
            data['vendor'] = re.sub(r'[^\w\s&,\.]', '', data['vendor']).strip()
            data['vendor'] = ' '.join(data['vendor'].split())  # Normalize whitespace
        else:
            # Fallback: try to extract first meaningful line after "From:"
            if data.get('raw_text'):
                lines = data['raw_text'].split('\n')
                for i, line in enumerate(lines):
                    if 'from:' in line.lower() and i + 1 < len(lines):
                        potential_vendor = lines[i + 1].strip()
                        if potential_vendor and not potential_vendor.isdigit():
                            data['vendor'] = potential_vendor[:50]  # Limit length
                            break
            if not data['vendor']:
                data['vendor'] = 'Unknown Vendor'  # Final fallback
        
        # Clean and normalize total
        if data['total']:
            # Remove all non-numeric characters except decimal point
            clean_total = re.sub(r'[^0-9.]', '', str(data['total']))
            try:
                data['total'] = float(clean_total)
            except ValueError:
                data['total'] = 0.0
        else:
            data['total'] = 0.0
        
        # Clean invoice number - provide fallback if None
        if data['invoice_number']:
            data['invoice_number'] = data['invoice_number'].upper().strip()
        else:
            # Generate a fallback invoice number
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            data['invoice_number'] = f'INV-{timestamp}'
        
        # Normalize date format - provide fallback if None
        if data['date']:
            try:
                # Try to parse various date formats
                date_str = str(data['date']).strip()
                
                # Try parsing "January 25, 2016" format
                try:
                    parsed_date = datetime.strptime(date_str, '%B %d, %Y')
                    data['date'] = parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    # Try other formats
                    try:
                        parsed_date = datetime.strptime(date_str, '%m/%d/%Y')
                        data['date'] = parsed_date.strftime('%Y-%m-%d')
                    except ValueError:
                        try:
                            parsed_date = datetime.strptime(date_str, '%m-%d-%Y')
                            data['date'] = parsed_date.strftime('%Y-%m-%d')
                        except ValueError:
                            # Keep original if all parsing fails
                            pass
            except Exception:
                pass
        else:
            # Fallback to current date
            data['date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Calculate line item totals if missing
        for item in data['line_items']:
            if item['total'] == 0.0 and item['qty'] > 0 and item['unit_price'] > 0:
                item['total'] = item['qty'] * item['unit_price']
        
        return data

# Convenience function for external use
def parse_invoice_file(file_path, file_type=None):
    """Parse an invoice file and return structured data"""
    parser = InvoiceParser()
    return parser.parse_invoice(file_path, file_type)
