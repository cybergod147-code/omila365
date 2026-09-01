from app import create_app
from app.models import User

app = create_app()
with app.app_context():
    users = User.query.all()
    if users:
        for u in users:
            print(f"ID: {u.id} | Username: {u.username} | Role: {u.role} | Active: {u.is_active}")
    else:
        print("No users found.")