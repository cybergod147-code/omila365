# app/__init__.py
from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, migrate
from apscheduler.schedulers.background import BackgroundScheduler
from app.engine.scanner import scan_tenant_emails
from app.models import Tenant
import logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # Register blueprints
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.operator import operator_bp
    app.register_blueprint(operator_bp, url_prefix='/operator')

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.routes.public import public_bp
    app.register_blueprint(public_bp)

    from app.routes.panel import panel_bp
    app.register_blueprint(panel_bp, url_prefix='/panel')

    @app.errorhandler(404)
    def not_found(e):
        return "Page not found", 404

    @app.errorhandler(500)
    def internal_error(e):
        return "Internal server error", 500

    # ---- Background Scheduler ----
    scheduler = BackgroundScheduler()
    def scheduled_scan():
        with app.app_context():
            tenants = Tenant.query.all()
            for tenant in tenants:
                # Only scan if Telegram configured and at least one alert mode
                if tenant.telegram_bot_token and tenant.telegram_chat_id:
                    scan_tenant_emails(tenant)

    scheduler.add_job(func=scheduled_scan, trigger="interval", minutes=5)
    scheduler.start()

    return app