from openai import OpenAI
import re
import json
import logging
import os
from datetime import datetime
from models.db_setup import execute_query, get_db_connection
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryEngine:
    def __init__(self, openai_api_key=None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.openai_client = None
        
        if self.openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        
        # Database schema information for GPT context
        self.schema_info = {
            "purchase_orders": {
                "columns": ["po_id", "vendor", "item", "qty", "unit_price", "total", "date", "created_at"],
                "description": "Contains purchase order records with vendor, item details, quantities, prices and dates"
            },
            "invoices": {
                "columns": ["invoice_id", "vendor", "item", "qty", "unit_price", "total", "date", "po_id", "status", "validation_result", "created_at"],
                "description": "Contains invoice records with vendor, item details, and validation status"
            },
            "leaderboard": {
                "columns": ["team_id", "team_name", "score", "validations_completed", "queries_executed", "last_updated"],
                "description": "Contains team performance metrics and scores"
            },
            "query_history": {
                "columns": ["id", "natural_language_query", "sql_query", "execution_time", "result_count", "team_id", "created_at"],
                "description": "Contains history of natural language queries and their SQL translations"
            }
        }
        
        # Common query patterns for fallback
        self.fallback_patterns = {
            r'total.*spend.*vendor.*quarter': 'SELECT vendor, SUM(total) as total_spend FROM purchase_orders WHERE date >= date("now", "-3 months") GROUP BY vendor ORDER BY total_spend DESC',
            r'top.*vendor.*spend': 'SELECT vendor, SUM(total) as total_spend FROM purchase_orders GROUP BY vendor ORDER BY total_spend DESC LIMIT 10',
            r'leaderboard|top.*team': 'SELECT team_name, score, validations_completed, queries_executed FROM leaderboard ORDER BY score DESC',
            r'recent.*invoice': 'SELECT invoice_id, vendor, total, date FROM invoices ORDER BY created_at DESC LIMIT 10',
            r'total.*purchase.*order': 'SELECT COUNT(*) as total_pos, SUM(total) as total_value FROM purchase_orders',
            r'average.*order.*value': 'SELECT AVG(total) as average_order_value FROM purchase_orders',
            r'vendor.*count': 'SELECT vendor, COUNT(*) as order_count FROM purchase_orders GROUP BY vendor ORDER BY order_count DESC'
        }
    
    def translate_to_sql(self, natural_query, team_id=None):
        """
        Translate natural language query to SQL using GPT-4 or fallback patterns
        """
        try:
            # First try GPT-4 if client is available
            if self.openai_client:
                sql_query = self._translate_with_gpt4(natural_query)
                if sql_query:
                    return {
                        'success': True,
                        'sql_query': sql_query,
                        'method': 'gpt4',
                        'natural_query': natural_query
                    }
            
            # Fallback to pattern matching
            sql_query = self._translate_with_patterns(natural_query)
            if sql_query:
                return {
                    'success': True,
                    'sql_query': sql_query,
                    'method': 'pattern_matching',
                    'natural_query': natural_query
                }
            
            # If no translation found, return a helpful error
            return {
                'success': False,
                'error': 'Could not translate query. Try asking about vendors, purchase orders, invoices, or leaderboard.',
                'suggestions': [
                    'Show me total spend per vendor',
                    'What are the recent invoices?',
                    'Show me the leaderboard',
                    'What is the average order value?'
                ]
            }
            
        except Exception as e:
            logger.error(f"Error translating query: {str(e)}")
            return {
                'success': False,
                'error': f'Translation error: {str(e)}'
            }
    
    def _translate_with_gpt4(self, natural_query):
        """Translate using GPT-4 API"""
        try:
            if not self.openai_client:
                return None
                
            schema_description = self._get_schema_description()
            
            prompt = f"""
You are a SQL expert. Convert the following natural language query to SQL.

Database Schema:
{schema_description}

Rules:
1. Only use SELECT statements
2. Use proper SQLite syntax
3. Return only the SQL query, no explanations
4. Use appropriate JOINs when needed
5. Include proper GROUP BY and ORDER BY clauses
6. Use date functions like date('now', '-3 months') for relative dates

Natural Language Query: {natural_query}

SQL Query:"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a SQL expert that converts natural language to SQL queries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up the response
            sql_query = re.sub(r'^```sql\s*', '', sql_query)
            sql_query = re.sub(r'\s*```$', '', sql_query)
            sql_query = sql_query.strip()
            
            # Basic validation
            if self._validate_sql_query(sql_query):
                return sql_query
            else:
                logger.warning(f"Generated SQL failed validation: {sql_query}")
                return None
                
        except Exception as e:
            logger.error(f"GPT-4 translation error: {str(e)}")
            return None
    
    def _translate_with_patterns(self, natural_query):
        """Translate using predefined patterns"""
        query_lower = natural_query.lower()
        
        for pattern, sql in self.fallback_patterns.items():
            if re.search(pattern, query_lower):
                return sql
        
        return None
    
    def _validate_sql_query(self, sql_query):
        """Basic validation of SQL query"""
        if not sql_query:
            return False
        
        # Must be a SELECT statement
        if not sql_query.strip().upper().startswith('SELECT'):
            return False
        
        # Check for potentially dangerous operations
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        query_upper = sql_query.upper()
        
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False
        
        return True
    
    def execute_natural_language_query(self, natural_query, team_id=None):
        """
        Execute a natural language query end-to-end
        """
        start_time = datetime.now()
        
        try:
            # Translate to SQL
            translation_result = self.translate_to_sql(natural_query, team_id)
            
            if not translation_result['success']:
                return translation_result
            
            sql_query = translation_result['sql_query']
            
            # Execute SQL query
            results = execute_query(sql_query)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Save to query history
            self._save_query_history(natural_query, sql_query, execution_time, len(results) if results else 0, team_id)
            
            # Update leaderboard if team_id provided
            if team_id:
                from models.db_setup import update_leaderboard_score
                update_leaderboard_score(team_id, query_increment=1, score_increment=10)
            
            return {
                'success': True,
                'natural_query': natural_query,
                'sql_query': sql_query,
                'results': results,
                'result_count': len(results) if results else 0,
                'execution_time': execution_time,
                'method': translation_result['method']
            }
            
        except Exception as e:
            logger.error(f"Error executing natural language query: {str(e)}")
            return {
                'success': False,
                'error': f'Execution error: {str(e)}',
                'natural_query': natural_query
            }
    
    def _save_query_history(self, natural_query, sql_query, execution_time, result_count, team_id):
        """Save query to history table"""
        try:
            execute_query(
                """INSERT INTO query_history 
                   (natural_language_query, sql_query, execution_time, result_count, team_id) 
                   VALUES (?, ?, ?, ?, ?)""",
                (natural_query, sql_query, execution_time, result_count, team_id)
            )
        except Exception as e:
            logger.error(f"Error saving query history: {str(e)}")
    
    def _get_schema_description(self):
        """Get formatted schema description for GPT prompt"""
        schema_text = "Database Tables:\n\n"
        
        for table_name, info in self.schema_info.items():
            schema_text += f"Table: {table_name}\n"
            schema_text += f"Description: {info['description']}\n"
            schema_text += f"Columns: {', '.join(info['columns'])}\n\n"
        
        return schema_text
    
    def get_query_suggestions(self):
        """Get suggested queries for the UI"""
        return [
            "Show me total spend per vendor this quarter",
            "What are the top 10 vendors by spending?",
            "Show me the current leaderboard",
            "What are the recent invoices?",
            "What is the average purchase order value?",
            "How many orders does each vendor have?",
            "Show me invoices from last month",
            "What items do we buy most frequently?",
            "Which team has completed the most validations?",
            "Show me all purchase orders over $5000"
        ]
    
    def get_sample_queries_with_sql(self):
        """Get sample queries with their SQL for demonstration"""
        return [
            {
                "natural": "Show me total spend per vendor",
                "sql": "SELECT vendor, SUM(total) as total_spend FROM purchase_orders GROUP BY vendor ORDER BY total_spend DESC"
            },
            {
                "natural": "What are the recent invoices?",
                "sql": "SELECT invoice_id, vendor, total, date FROM invoices ORDER BY created_at DESC LIMIT 10"
            },
            {
                "natural": "Show me the leaderboard",
                "sql": "SELECT team_name, score, validations_completed, queries_executed FROM leaderboard ORDER BY score DESC"
            }
        ]

# Convenience function for external use
def execute_nl_query(natural_query, team_id=None, openai_api_key=None):
    """Execute a natural language query"""
    engine = QueryEngine(openai_api_key)
    return engine.execute_natural_language_query(natural_query, team_id)
