from app import create_app
from app.models import User, Tenant
from app.extensions import db

app = create_app()
with app.app_context():
    tenant = Tenant.query.first()
    if not tenant:
        tenant = Tenant(name='Admin Tenant', is_active=True, plan='Premium')
        db.session.add(tenant)
        db.session.commit()

    admin = User.query.filter_by(username='admin').first()
    if admin:
        print("Admin already exists.")
    else:
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin',
            is_active=True,
            tenant_id=tenant.id
        )
        admin.set_password('Admin123!')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin created: username='admin', password='Admin123!'")