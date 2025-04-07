import os
from flask import Flask
from flask_migrate import Migrate
from models import db
from api.routes import api_bp
from dashapp import create_dash_app
from config import Config

def create_app():
    """Application factory to create Flask app and attach extensions."""
    app = Flask(__name__)

    app.config.from_object(Config)

    # Initialize DB
    db.init_app(app)
    Migrate(app, db)

    # Register blueprints
    # The Blueprint in aggregator/api/routes.py handles / and /api routes
    app.register_blueprint(api_bp)

    # Create and attach Dash app
    create_dash_app(app)

    return app
