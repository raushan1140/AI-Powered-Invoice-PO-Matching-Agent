from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from models.db_setup import init_db

# Load environment variables from .env file
load_dotenv()

# Import route blueprints
from routes.invoice_routes import invoice_bp
from routes.query_routes import query_bp
from routes.leaderboard_routes import leaderboard_bp

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-for-development')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    # Enable CORS for all routes
    CORS(app, origins=['http://localhost:5173'])  # Vite default port
    
    # Initialize database
    init_db()
    
    # Register blueprints
    app.register_blueprint(invoice_bp, url_prefix='/api/invoices')
    app.register_blueprint(query_bp, url_prefix='/api/queries')
    app.register_blueprint(leaderboard_bp, url_prefix='/api/leaderboard')
    
    # Create upload directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Root endpoint: show all available routes
    @app.route('/')
    def list_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            if "static" not in rule.endpoint:
                routes.append({
                    'endpoint': rule.endpoint,
                    'methods': list(rule.methods),
                    'url': str(rule)
                })
        return {'available_routes': routes}
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Invoice-PO Matching Agent API is running'}
    
    # Error handlers
    @app.errorhandler(413)
    def too_large(e):
        return {'error': 'File too large. Maximum size is 16MB.'}, 413
    
    @app.errorhandler(404)
    def not_found(e):
        return {'error': 'Endpoint not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return {'error': 'Internal server error'}, 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
