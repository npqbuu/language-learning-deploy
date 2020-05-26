import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from flask_login import LoginManager
from flask_admin import Admin
from flask_bootstrap import Bootstrap

# Globally accessible libraries
basedir = os.path.abspath(os.path.dirname(__file__))
staticdir = os.path.join(basedir, 'static')
db = SQLAlchemy()
login_manager = LoginManager()
admin = Admin()
bootstrap = Bootstrap()


def create_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    # Initialize Plugins
    db.init_app(app)
    Session(app)
    login_manager.init_app(app)
    admin.init_app(app)
    bootstrap.init_app(app)
    

    with app.app_context():
        from . import views, auth

        # Create Database Models
        db.create_all()

        return app