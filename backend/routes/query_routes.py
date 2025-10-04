from flask import Blueprint, request, jsonify, current_app
from services.query_engine import QueryEngine, execute_nl_query
from models.db_setup import execute_query
import os

query_bp = Blueprint('queries', __name__)

@query_bp.route('/execute', methods=['POST'])
def execute_natural_language_query():
    """
    Execute a natural language query and return results
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'No query provided'}), 400
        
        natural_query = data['query'].strip()
        team_id = data.get('team_id')  # Optional team ID for scoring
        
        if not natural_query:
            return jsonify({'error': 'Empty query provided'}), 400
        
        # Get OpenAI API key from environment or request
        openai_api_key = os.environ.get('OPENAI_API_KEY') or data.get('openai_api_key')
        
        # Execute the query
        result = execute_nl_query(natural_query, team_id, openai_api_key)
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error executing natural language query: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Query execution error: {str(e)}'
        }), 500

@query_bp.route('/suggestions', methods=['GET'])
def get_query_suggestions():
    """
    Get suggested queries for the UI
    """
    try:
        engine = QueryEngine()
        suggestions = engine.get_query_suggestions()
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting query suggestions: {str(e)}")
        return jsonify({'error': f'Error: {str(e)}'}), 500

@query_bp.route('/samples', methods=['GET'])
def get_sample_queries():
    """
    Get sample queries with their SQL translations for demonstration
    """
    try:
        engine = QueryEngine()
        samples = engine.get_sample_queries_with_sql()
        
        return jsonify({
            'success': True,
            'samples': samples
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting sample queries: {str(e)}")
        return jsonify({'error': f'Error: {str(e)}'}), 500

@query_bp.route('/history', methods=['GET'])
def get_query_history():
    """
    Get query execution history
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        team_id = request.args.get('team_id')
        
        # Build query with optional team filter
        base_query = """
            SELECT id, natural_language_query, sql_query, execution_time, 
                   result_count, team_id, created_at 
            FROM query_history 
        """
        
        params = []
        if team_id:
            base_query += " WHERE team_id = ? "
            params.append(team_id)
        
        base_query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        history = execute_query(base_query, params)
        
        # Get total count
        count_query = "SELECT COUNT(*) as count FROM query_history"
        count_params = []
        if team_id:
            count_query += " WHERE team_id = ?"
            count_params.append(team_id)
        
        total_count = execute_query(count_query, count_params)[0]['count']
        
        return jsonify({
            'success': True,
            'history': history,
            'total_count': total_count,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting query history: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@query_bp.route('/translate', methods=['POST'])
def translate_query():
    """
    Translate natural language to SQL without executing
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'No query provided'}), 400
        
        natural_query = data['query'].strip()
        
        if not natural_query:
            return jsonify({'error': 'Empty query provided'}), 400
        
        # Get OpenAI API key from environment or request
        openai_api_key = os.environ.get('OPENAI_API_KEY') or data.get('openai_api_key')
        
        # Create query engine and translate
        engine = QueryEngine(openai_api_key)
        result = engine.translate_to_sql(natural_query)
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error translating query: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Translation error: {str(e)}'
        }), 500

@query_bp.route('/execute-sql', methods=['POST'])
def execute_sql_directly():
    """
    Execute SQL query directly (for advanced users)
    """
    try:
        data = request.get_json()
        
        if not data or 'sql' not in data:
            return jsonify({'error': 'No SQL query provided'}), 400
        
        sql_query = data['sql'].strip()
        team_id = data.get('team_id')
        
        if not sql_query:
            return jsonify({'error': 'Empty SQL query provided'}), 400
        
        # Basic security check - only allow SELECT statements
        if not sql_query.upper().strip().startswith('SELECT'):
            return jsonify({'error': 'Only SELECT statements are allowed'}), 400
        
        # Check for dangerous keywords
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        sql_upper = sql_query.upper()
        
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return jsonify({'error': f'Keyword "{keyword}" is not allowed'}), 400
        
        # Execute the query
        results = execute_query(sql_query)
        
        # Update leaderboard if team_id provided
        if team_id:
            from models.db_setup import update_leaderboard_score
            update_leaderboard_score(team_id, query_increment=1, score_increment=5)
        
        return jsonify({
            'success': True,
            'sql_query': sql_query,
            'results': results,
            'result_count': len(results) if results else 0
        })
        
    except Exception as e:
        current_app.logger.error(f"Error executing SQL query: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'SQL execution error: {str(e)}'
        }), 500

@query_bp.route('/stats', methods=['GET'])
def get_query_stats():
    """
    Get query execution statistics
    """
    try:
        stats = {}
        
        # Total queries executed
        total_result = execute_query("SELECT COUNT(*) as count FROM query_history")
        stats['total_queries'] = total_result[0]['count'] if total_result else 0
        
        # Average execution time
        avg_time_result = execute_query("SELECT AVG(execution_time) as avg_time FROM query_history")
        stats['average_execution_time'] = round(avg_time_result[0]['avg_time'] or 0, 3)
        
        # Recent activity (last 24 hours)
        recent_result = execute_query("""
            SELECT COUNT(*) as count 
            FROM query_history 
            WHERE created_at >= datetime('now', '-24 hours')
        """)
        stats['recent_queries'] = recent_result[0]['count'] if recent_result else 0
        
        # Most active teams
        team_activity = execute_query("""
            SELECT team_id, COUNT(*) as query_count 
            FROM query_history 
            WHERE team_id IS NOT NULL 
            GROUP BY team_id 
            ORDER BY query_count DESC 
            LIMIT 5
        """)
        stats['top_teams'] = team_activity
        
        # Common query patterns
        common_patterns = execute_query("""
            SELECT natural_language_query, COUNT(*) as frequency
            FROM query_history 
            GROUP BY LOWER(natural_language_query)
            HAVING frequency > 1
            ORDER BY frequency DESC 
            LIMIT 5
        """)
        stats['common_queries'] = common_patterns
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting query stats: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
