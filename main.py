"""
Codeplex AI - Main Application Entry Point
"""
import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configuration
    app.config.update(
        DEBUG=os.getenv('DEBUG', 'False').lower() == 'true',
        JSON_SORT_KEYS=False,
        MAX_CONTENT_LENGTH=int(os.getenv('MAX_REQUEST_SIZE', 10485760)),
    )
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": os.getenv('CORS_ORIGINS', '*').split(','),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })
    
    # Register blueprints
    from app.routes import api_bp, health_bp
    from app.web import web_bp
    app.register_blueprint(api_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(web_bp)
    
    logger.info(f"Flask app created successfully in {os.getenv('ENVIRONMENT', 'production')} mode")
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host=os.getenv('API_HOST', '0.0.0.0'),
        port=int(os.getenv('API_PORT', 8000)),
        debug=os.getenv('DEBUG', 'False').lower() == 'true'
    )

