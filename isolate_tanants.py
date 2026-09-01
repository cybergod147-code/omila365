from app import create_app
from app.models import User, Tenant
from app.extensions import db

app = create_app()
with app.app_context():
    # Get all non-admin users
    users = User.query.filter(User.role != 'admin').all()
    if not users:
        print("No operators found.")
    else:
        for user in users:
            # Check if user already has a tenant that is not the default (optional)
            if user.tenant_id:
                # If they already have a tenant, we could skip or create a new one
                print(f"User {user.username} already has tenant {user.tenant_id}. Skipping.")
                continue
            # Create a new tenant for this user
            tenant = Tenant(
                name=f"{user.username}'s Tenant",
                is_active=True,
                plan='Trial'
            )
            db.session.add(tenant)
            db.session.commit()
            # Assign user to this tenant
            user.tenant_id = tenant.id
            db.session.commit()
            print(f"✅ Created tenant '{tenant.name}' and assigned {user.username}.")