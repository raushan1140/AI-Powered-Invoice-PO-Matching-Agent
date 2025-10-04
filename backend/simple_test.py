import re

sample = """From:
DEMO - Sliced Invoices Order Number 12345
Suite 5A-1204 Invoice Date January 25, 2016"""

# Test vendor pattern
vendor_pattern = r'from[:\s]*\n([A-Za-z0-9\s&,\.\-]+?)(?:\n|order)'
match = re.search(vendor_pattern, sample, re.IGNORECASE)
print(f"Vendor match: '{match.group(1).strip()}'" if match else "No vendor match")

# Test date pattern
date_pattern = r'invoice\s*date\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})'
match = re.search(date_pattern, sample, re.IGNORECASE)
print(f"Date match: '{match.group(1).strip()}'" if match else "No date match")

print("Test completed!")
