import sys
sys.path.append('.')

from services.invoice_parser import parse_invoice_file

# Test with the sample text we saw in the logs
sample_text = """Invoice
Invoice Number INV-3337
From:
DEMO - Sliced Invoices Order Number 12345
Suite 5A-1204 Invoice Date January 25, 2016
123 Somewhere Street
Due Date January 31, 2016
Your City AZ 12345
Total Due $93.50
admin@slicedinvoices.com
To:
Test Business
123 Somewhere St
Melbourne, VIC 3000
test@test.com
Hrs/Qty Service Rate/Price Adjust Sub Total
Web Design
1.00 $85.00 0.00% $85.00
This is a sample description...
Sub Total $85.00
Tax $8.50
Total $93.50"""

# Test the regex patterns
import re
from services.invoice_parser import InvoiceParser

parser = InvoiceParser()

print("Testing improved regex patterns:")
print("=" * 50)

# Test vendor extraction
vendor_patterns = parser.patterns['vendor']
for i, pattern in enumerate(vendor_patterns):
    matches = re.finditer(pattern, sample_text.lower(), re.IGNORECASE | re.MULTILINE)
    for match in matches:
        print(f"Vendor pattern {i+1}: '{match.group(1).strip()}'")

print("\n" + "=" * 50)

# Test date extraction
date_patterns = parser.patterns['date']
for i, pattern in enumerate(date_patterns):
    matches = re.finditer(pattern, sample_text.lower(), re.IGNORECASE | re.MULTILINE)
    for match in matches:
        print(f"Date pattern {i+1}: '{match.group(1).strip()}'")

print("\n" + "=" * 50)

# Test total extraction
total_patterns = parser.patterns['total']
for i, pattern in enumerate(total_patterns):
    matches = re.finditer(pattern, sample_text.lower(), re.IGNORECASE | re.MULTILINE)
    for match in matches:
        print(f"Total pattern {i+1}: '{match.group(1).strip()}'")
