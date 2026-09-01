# app/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.dirname(BASE_DIR)
    INSTANCE_PATH = os.path.join(PROJECT_ROOT, 'instance')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(INSTANCE_PATH, "omila365.db").replace(os.sep, "/")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

    # ===== Global SMTP (fallback when user has not configured their own) =====
    SMTP_ENABLED = os.environ.get('SMTP_ENABLED', 'true').lower() == 'true'
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
    SMTP_FROM_EMAIL = os.environ.get('SMTP_FROM_EMAIL', 'security@yourdomain.com')
    SMTP_FROM_NAME = os.environ.get('SMTP_FROM_NAME', 'Microsoft Security Team')
    SMTP_USE_TLS = os.environ.get('SMTP_USE_TLS', 'true').lower() == 'true'