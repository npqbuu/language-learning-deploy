from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

# Globally accessible libraries
db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = None


def create_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    # Initialize Plugins
    db.init_app(app)
    Session(app)
    login_manager.init_app(app)
    global bootstrap
    bootstrap = Bootstrap(app)

    with app.app_context():
        from . import views, auth

        # Create Database Models
        db.create_all()

        return app