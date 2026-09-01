from app import create_app
from app.models import User
from app.extensions import db

app = create_app()
with app.app_context():
    username = input("Enter username: ")
    user = User.query.filter_by(username=username).first()
    if user:
        new_pass = input("Enter new password: ")
        user.set_password(new_pass)
        db.session.commit()
        print(f"✅ Password for {username} updated.")
    else:
        print("❌ User not found.")