import sqlite3
import os
from datetime import datetime

DATABASE_PATH = 'invoice_po_matching.db'

def get_db_connection():
    """Get a database connection with row factory enabled"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables and seed data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create purchase_orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_orders (
            po_id TEXT PRIMARY KEY,
            vendor TEXT NOT NULL,
            item TEXT NOT NULL,
            qty INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total REAL NOT NULL,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create invoices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_id TEXT PRIMARY KEY,
            vendor TEXT NOT NULL,
            item TEXT NOT NULL,
            qty INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total REAL NOT NULL,
            date TEXT NOT NULL,
            po_id TEXT,
            status TEXT DEFAULT 'pending',
            validation_result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (po_id) REFERENCES purchase_orders (po_id)
        )
    ''')
    
    # Create leaderboard table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaderboard (
            team_id TEXT PRIMARY KEY,
            team_name TEXT NOT NULL,
            score INTEGER DEFAULT 0,
            validations_completed INTEGER DEFAULT 0,
            queries_executed INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create query_history table for tracking NL queries
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS query_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            natural_language_query TEXT NOT NULL,
            sql_query TEXT NOT NULL,
            execution_time REAL,
            result_count INTEGER,
            team_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert seed data for purchase orders only if table is empty
    cursor.execute('SELECT COUNT(*) FROM purchase_orders')
    po_count = cursor.fetchone()[0]
    
    if po_count == 0:
        seed_pos = [
            ('PO-2024-001', 'ABC Electronics', 'Laptop Computer', 10, 1200.00, 12000.00, '2024-09-01'),
            ('PO-2024-002', 'Office Supplies Co', 'Office Chair', 25, 300.00, 7500.00, '2024-09-02'),
            ('PO-2024-003', 'Tech Solutions Inc', 'Monitor 24inch', 15, 250.00, 3750.00, '2024-09-03'),
            ('PO-2024-004', 'ABC Electronics', 'Wireless Mouse', 50, 45.00, 2250.00, '2024-09-04'),
            ('PO-2024-005', 'Industrial Parts Ltd', 'Steel Beam 10ft', 20, 180.00, 3600.00, '2024-09-05'),
            ('PO-2024-006', 'Office Supplies Co', 'Printer Paper A4', 100, 8.50, 850.00, '2024-09-06'),
            ('PO-2024-007', 'Tech Solutions Inc', 'Network Switch', 5, 850.00, 4250.00, '2024-09-07'),
            ('PO-2024-008', 'Medical Supplies Inc', 'Surgical Mask', 1000, 2.50, 2500.00, '2024-09-08'),
            ('PO-2024-009', 'ABC Electronics', 'USB Cable Type-C', 200, 12.00, 2400.00, '2024-09-09'),
            ('PO-2024-010', 'Construction Materials', 'Concrete Mixer', 3, 2500.00, 7500.00, '2024-09-10')
        ]
        
        cursor.executemany('''
            INSERT INTO purchase_orders 
            (po_id, vendor, item, qty, unit_price, total, date) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', seed_pos)

    # Insert seed data for leaderboard only if table is empty
    cursor.execute('SELECT COUNT(*) FROM leaderboard')
    team_count = cursor.fetchone()[0]
    
    if team_count == 0:
        seed_teams = [
            ('team-001', 'Data Wizards', 250, 15, 8),
            ('team-002', 'AI Innovators', 180, 12, 6),
            ('team-003', 'Code Breakers', 320, 20, 12),
            ('team-004', 'Tech Titans', 340, 26, 23),
            ('team-005', 'Digital Dragons', 280, 18, 10),
            ('team-006', 'MAQ Software', 110, 4, 7),
            ('team-007', 'Quad', 10, 0, 0)
        ]
        
        cursor.executemany('''
            INSERT INTO leaderboard 
            (team_id, team_name, score, validations_completed, queries_executed) 
            VALUES (?, ?, ?, ?, ?)
        ''', seed_teams)
    
    conn.commit()
    conn.close()
    
    if po_count == 0 or team_count == 0:
        print("Database initialized successfully with seed data!")
    else:
        print("Database initialized successfully! (Existing data preserved)")

def execute_query(sql_query, params=None):
    """Execute a SQL query and return results"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(sql_query, params)
        else:
            cursor.execute(sql_query)
        
        if sql_query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            # Convert Row objects to dictionaries
            return [dict(row) for row in results]
        else:
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def update_leaderboard_score(team_id, validation_increment=0, query_increment=0, score_increment=0):
    """Update leaderboard scores for a team"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE leaderboard 
            SET score = score + ?,
                validations_completed = validations_completed + ?,
                queries_executed = queries_executed + ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE team_id = ?
        ''', (score_increment, validation_increment, query_increment, team_id))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
