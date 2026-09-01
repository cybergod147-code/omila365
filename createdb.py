# createdb.py
from app import create_app
from app.extensions import db
import os

app = create_app()
with app.app_context():
    os.makedirs(app.instance_path, exist_ok=True)
    db.create_all()
    print("✅ Database tables created at:", app.config['SQLALCHEMY_DATABASE_URI'])