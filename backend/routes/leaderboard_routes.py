from flask import Blueprint, request, jsonify, current_app
from models.db_setup import execute_query, update_leaderboard_score
import json

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/', methods=['GET'])
def get_leaderboard():
    """
    Get the current leaderboard rankings
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        
        leaderboard = execute_query("""
            SELECT team_id, team_name, score, validations_completed, 
                   queries_executed, last_updated
            FROM leaderboard 
            ORDER BY score DESC, validations_completed DESC 
            LIMIT ?
        """, (limit,))
        
        # Add ranking
        for i, team in enumerate(leaderboard):
            team['rank'] = i + 1
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard,
            'total_teams': len(leaderboard)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting leaderboard: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@leaderboard_bp.route('/team/<team_id>', methods=['GET'])
def get_team_stats(team_id):
    """
    Get detailed statistics for a specific team
    """
    try:
        # Get team info
        team_result = execute_query("""
            SELECT * FROM leaderboard WHERE team_id = ?
        """, (team_id,))
        
        if not team_result:
            return jsonify({'error': 'Team not found'}), 404
        
        team_data = team_result[0]
        
        # Get team's query history
        query_history = execute_query("""
            SELECT natural_language_query, sql_query, execution_time, 
                   result_count, created_at
            FROM query_history 
            WHERE team_id = ? 
            ORDER BY created_at DESC 
            LIMIT 10
        """, (team_id,))
        
        # Get team's invoice validations (if any invoices were processed with team_id)
        # Note: This would require modification to invoice processing to track team_id
        
        # Calculate additional stats
        total_execution_time = sum(float(q['execution_time'] or 0) for q in query_history)
        avg_execution_time = total_execution_time / len(query_history) if query_history else 0
        
        return jsonify({
            'success': True,
            'team_data': team_data,
            'query_history': query_history,
            'stats': {
                'total_execution_time': round(total_execution_time, 3),
                'average_execution_time': round(avg_execution_time, 3),
                'recent_queries': len(query_history)
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting team stats: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@leaderboard_bp.route('/update', methods=['POST'])
def update_team_score():
    """
    Manually update team scores (for admin use)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        team_id = data.get('team_id')
        validation_increment = data.get('validation_increment', 0)
        query_increment = data.get('query_increment', 0)
        score_increment = data.get('score_increment', 0)
        
        if not team_id:
            return jsonify({'error': 'Team ID is required'}), 400
        
        # Update the leaderboard
        success = update_leaderboard_score(
            team_id, 
            validation_increment, 
            query_increment, 
            score_increment
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Team score updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Team not found or update failed'
            }), 404
        
    except Exception as e:
        current_app.logger.error(f"Error updating team score: {str(e)}")
        return jsonify({'error': f'Update error: {str(e)}'}), 500

@leaderboard_bp.route('/create-team', methods=['POST'])
def create_team():
    """
    Create a new team
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        team_id = data.get('team_id')
        team_name = data.get('team_name')
        
        if not team_id or not team_name:
            return jsonify({'error': 'Team ID and team name are required'}), 400
        
        # Check if team already exists
        existing_team = execute_query("""
            SELECT team_id FROM leaderboard WHERE team_id = ?
        """, (team_id,))
        
        if existing_team:
            return jsonify({'error': 'Team already exists'}), 409
        
        # Create new team
        execute_query("""
            INSERT INTO leaderboard (team_id, team_name, score, validations_completed, queries_executed)
            VALUES (?, ?, 0, 0, 0)
        """, (team_id, team_name))
        
        return jsonify({
            'success': True,
            'message': 'Team created successfully',
            'team_id': team_id,
            'team_name': team_name
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating team: {str(e)}")
        return jsonify({'error': f'Creation error: {str(e)}'}), 500

@leaderboard_bp.route('/stats', methods=['GET'])
def get_leaderboard_stats():
    """
    Get overall leaderboard statistics
    """
    try:
        stats = {}
        
        # Total teams
        total_teams_result = execute_query("SELECT COUNT(*) as count FROM leaderboard")
        stats['total_teams'] = total_teams_result[0]['count'] if total_teams_result else 0
        
        # Total score across all teams
        total_score_result = execute_query("SELECT SUM(score) as total_score FROM leaderboard")
        stats['total_score'] = total_score_result[0]['total_score'] or 0
        
        # Total validations and queries
        totals_result = execute_query("""
            SELECT SUM(validations_completed) as total_validations,
                   SUM(queries_executed) as total_queries
            FROM leaderboard
        """)
        if totals_result:
            stats['total_validations'] = totals_result[0]['total_validations'] or 0
            stats['total_queries'] = totals_result[0]['total_queries'] or 0
        else:
            stats['total_validations'] = 0
            stats['total_queries'] = 0
        
        # Average score
        if stats['total_teams'] > 0:
            stats['average_score'] = round(stats['total_score'] / stats['total_teams'], 2)
        else:
            stats['average_score'] = 0
        
        # Top performer
        top_team_result = execute_query("""
            SELECT team_name, score FROM leaderboard 
            ORDER BY score DESC 
            LIMIT 1
        """)
        if top_team_result:
            stats['top_team'] = top_team_result[0]
        else:
            stats['top_team'] = None
        
        # Most active team (most validations + queries + recent activity weight)
        most_active_result = execute_query("""
            SELECT 
                l.team_name, 
                l.team_id,
                (l.validations_completed + l.queries_executed) as activity,
                l.validations_completed,
                l.queries_executed,
                l.last_updated,
                (
                    SELECT COUNT(*) 
                    FROM query_history q 
                    WHERE q.team_id = l.team_id 
                    AND q.created_at >= datetime('now', '-24 hours')
                ) as recent_queries
            FROM leaderboard l
            ORDER BY 
                (l.validations_completed + l.queries_executed + 
                 (CASE WHEN l.last_updated >= datetime('now', '-24 hours') THEN 10 ELSE 0 END)) DESC,
                l.last_updated DESC
            LIMIT 1
        """)
        if most_active_result:
            team = most_active_result[0]
            stats['most_active_team'] = {
                'team_name': team['team_name'],
                'team_id': team['team_id'],
                'activity': team['activity'],
                'validations_completed': team['validations_completed'],
                'queries_executed': team['queries_executed'],
                'recent_queries': team['recent_queries'],
                'last_updated': team['last_updated']
            }
        else:
            stats['most_active_team'] = None
        
        # Recent activity (teams updated in last 24 hours)
        recent_activity_result = execute_query("""
            SELECT COUNT(*) as count 
            FROM leaderboard 
            WHERE last_updated >= datetime('now', '-24 hours')
        """)
        stats['recent_activity'] = recent_activity_result[0]['count'] if recent_activity_result else 0
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting leaderboard stats: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@leaderboard_bp.route('/activity', methods=['GET'])
def get_real_time_activity():
    """
    Get real-time activity data including recent queries and validations
    """
    try:
        # Get teams with recent activity (last 24 hours)
        recent_activity = execute_query("""
            SELECT 
                l.team_id,
                l.team_name,
                l.score,
                l.validations_completed,
                l.queries_executed,
                l.last_updated,
                (
                    SELECT COUNT(*) 
                    FROM query_history q 
                    WHERE q.team_id = l.team_id 
                    AND q.created_at >= datetime('now', '-24 hours')
                ) as queries_last_24h,
                (
                    SELECT COUNT(*) 
                    FROM query_history q 
                    WHERE q.team_id = l.team_id 
                    AND q.created_at >= datetime('now', '-1 hour')
                ) as queries_last_1h
            FROM leaderboard l
            WHERE l.last_updated >= datetime('now', '-24 hours')
            ORDER BY l.last_updated DESC
            LIMIT 10
        """)
        
        # Get most active team with enhanced calculation
        most_active = execute_query("""
            SELECT 
                l.team_id,
                l.team_name,
                l.validations_completed,
                l.queries_executed,
                (l.validations_completed + l.queries_executed) as total_activity,
                l.last_updated,
                (
                    SELECT COUNT(*) 
                    FROM query_history q 
                    WHERE q.team_id = l.team_id 
                    AND q.created_at >= datetime('now', '-24 hours')
                ) as recent_queries,
                (
                    CASE 
                        WHEN l.last_updated >= datetime('now', '-1 hour') THEN 'Very Active'
                        WHEN l.last_updated >= datetime('now', '-6 hours') THEN 'Active'
                        WHEN l.last_updated >= datetime('now', '-24 hours') THEN 'Recently Active'
                        ELSE 'Inactive'
                    END
                ) as activity_status
            FROM leaderboard l
            ORDER BY 
                (l.validations_completed + l.queries_executed + 
                 (CASE WHEN l.last_updated >= datetime('now', '-1 hour') THEN 20 
                       WHEN l.last_updated >= datetime('now', '-6 hours') THEN 10
                       WHEN l.last_updated >= datetime('now', '-24 hours') THEN 5
                       ELSE 0 END)) DESC
            LIMIT 1
        """)
        
        return jsonify({
            'success': True,
            'recent_activity': recent_activity,
            'most_active_team': most_active[0] if most_active else None,
            'activity_timestamp': execute_query("SELECT datetime('now') as current_time")[0]['current_time']
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting real-time activity: {str(e)}")
        return jsonify({'error': f'Activity fetch error: {str(e)}'}), 500

@leaderboard_bp.route('/team/<team_id>', methods=['DELETE'])
def delete_team(team_id):
    """
    Delete a team from the leaderboard
    """
    try:
        # Check if team exists
        existing_team = execute_query("""
            SELECT team_id FROM leaderboard WHERE team_id = ?
        """, (team_id,))
        
        if not existing_team:
            return jsonify({'error': 'Team not found'}), 404
        
        # Delete the team
        execute_query("""
            DELETE FROM leaderboard WHERE team_id = ?
        """, (team_id,))
        
        # Also delete related query history
        execute_query("""
            DELETE FROM query_history WHERE team_id = ?
        """, (team_id,))
        
        return jsonify({
            'success': True,
            'message': 'Team deleted successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error deleting team: {str(e)}")
        return jsonify({'error': f'Deletion error: {str(e)}'}), 500

@leaderboard_bp.route('/rankings', methods=['GET'])
def get_rankings_by_category():
    """
    Get rankings by different categories
    """
    try:
        rankings = {}
        
        # By total score
        rankings['by_score'] = execute_query("""
            SELECT team_name, score, ROW_NUMBER() OVER (ORDER BY score DESC) as rank
            FROM leaderboard 
            ORDER BY score DESC 
            LIMIT 10
        """)
        
        # By validations completed
        rankings['by_validations'] = execute_query("""
            SELECT team_name, validations_completed, 
                   ROW_NUMBER() OVER (ORDER BY validations_completed DESC) as rank
            FROM leaderboard 
            ORDER BY validations_completed DESC 
            LIMIT 10
        """)
        
        # By queries executed
        rankings['by_queries'] = execute_query("""
            SELECT team_name, queries_executed,
                   ROW_NUMBER() OVER (ORDER BY queries_executed DESC) as rank
            FROM leaderboard 
            ORDER BY queries_executed DESC 
            LIMIT 10
        """)
        
        # By recent activity (last updated) - include all team data for frontend compatibility
        rankings['most_recent'] = execute_query("""
            SELECT team_id, team_name, score, validations_completed, queries_executed, last_updated,
                   ROW_NUMBER() OVER (ORDER BY last_updated DESC) as rank
            FROM leaderboard 
            ORDER BY last_updated DESC 
            LIMIT 10
        """)
        
        return jsonify({
            'success': True,
            'rankings': rankings
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting rankings: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
