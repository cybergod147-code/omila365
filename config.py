# app/config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Build absolute path to the instance folder
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))          # /app
    PROJECT_ROOT = os.path.dirname(BASE_DIR)                      # /omila365
    INSTANCE_PATH = os.path.join(PROJECT_ROOT, 'instance')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(INSTANCE_PATH, "omila365.db").replace(os.sep, "/")}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True   # Set to False in production