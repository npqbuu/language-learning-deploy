import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Set Flask configuration from environment variables."""

    FLASK_APP = 'wsgi.py'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'pib1secretkey'
    DEBUG = True
    
    # Static Assets
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SEND_FILE_MAX_AGE_DEFAULT = 300

    # Flask-SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/mylocaldb'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Admin
    FLASK_ADMIN_SWATCH = 'cerulean'

    # Session
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"