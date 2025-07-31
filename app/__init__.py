from flask import Flask
from app.routes import main  # Importing the routes Blueprint
from app.cache import cache

def create_app():
    """Application Factory Pattern: Creates and configures a Flask app instance"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object("config.Config")

    # Optionally set defaults (won’t override Config)
    app.config.setdefault('CACHE_TYPE', 'simple')
    app.config.setdefault('CACHE_DEFAULT_TIMEOUT', 300)

    cache.init_app(app)

    # Register Blueprints (Routes)
    app.register_blueprint(main)

    return app  # Returns a Flask app instance
