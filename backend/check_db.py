import sqlite3

# Check invoice_po_matching.db
try:
    conn = sqlite3.connect('invoice_po_matching.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables in invoice_po_matching.db:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check if invoices table exists and count records
    cursor.execute("SELECT COUNT(*) FROM invoices")
    count = cursor.fetchone()[0]
    print(f"Invoice records: {count}")
    
    conn.close()
    print("✓ Database check completed successfully")
except Exception as e:
    print(f"Error checking database: {e}")
