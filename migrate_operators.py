from app import create_app
from app.models import User, Tenant
from app.extensions import db

app = create_app()
with app.app_context():
    # Find the default tenant (the one everyone is sharing)
    default_tenant = Tenant.query.filter_by(name='Default Tenant').first()
    if not default_tenant:
        default_tenant = Tenant.query.first()
    if not default_tenant:
        print("❌ No tenant found. Please create a tenant first.")
        exit()

    # Get all non-admin users
    operators = User.query.filter(User.role != 'admin').all()
    if not operators:
        print("No operators found.")
    else:
        for op in operators:
            # If the operator is still in the default tenant or has no tenant
            if op.tenant_id == default_tenant.id or op.tenant_id is None:
                # Create a new tenant for this operator
                new_tenant = Tenant(
                    name=f"{op.username}'s Tenant",
                    is_active=True,
                    plan='Trial'
                )
                db.session.add(new_tenant)
                db.session.commit()
                op.tenant_id = new_tenant.id
                db.session.commit()
                print(f"✅ Moved {op.username} to new tenant '{new_tenant.name}'")
            else:
                print(f"✅ {op.username} already has tenant {op.tenant_id}")