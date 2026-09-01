# app/models.py
from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Tenant(db.Model):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    plan = db.Column(db.String(50), default='Trial')
    telegram_bot_token = db.Column(db.String(255))
    telegram_chat_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # AI & Alert settings
    alert_mode = db.Column(db.String(20), default='ai')  # 'keyword', 'ai', 'both'
    ai_provider = db.Column(db.String(50), default='deepseek')
    ai_api_key = db.Column(db.String(255))
    ai_model = db.Column(db.String(50), default='deepseek-chat')
    ai_risk_threshold = db.Column(db.Integer, default=70)

    users = db.relationship('User', backref='tenant', lazy=True)
    campaigns = db.relationship('Campaign', backref='tenant', lazy=True)
    keywords = db.relationship('KeywordRule', backref='tenant', lazy=True)

    def __repr__(self):
        return f'<Tenant {self.name}>'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    expiry_date = db.Column(db.DateTime)
    balance = db.Column(db.Float, default=0.0)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'))

    # SMTP fields
    smtp_enabled = db.Column(db.Boolean, default=False)
    smtp_server = db.Column(db.String(120))
    smtp_port = db.Column(db.Integer, default=587)
    smtp_username = db.Column(db.String(120))
    smtp_password = db.Column(db.String(255))
    smtp_from_email = db.Column(db.String(120))
    smtp_from_name = db.Column(db.String(120))
    smtp_use_tls = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'))
    status = db.Column(db.String(20), default='active')
    template_id = db.Column(db.String(50), default='ms_alert')
    sender_name = db.Column(db.String(80))
    document_title = db.Column(db.String(120))
    document_type = db.Column(db.String(20), default='.PDF')
    exit_url = db.Column(db.String(255))
    language = db.Column(db.String(20), default='English')
    token_type = db.Column(db.String(30), default='B2B (Office)')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    victims = db.relationship('Victim', backref='campaign', lazy=True)
    leads = db.relationship('B2BLead', backref='campaign', lazy=True)
    drafts = db.relationship('DraftEmail', backref='campaign', lazy=True)

    def __repr__(self):
        return f'<Campaign {self.name}>'


class Victim(db.Model):
    __tablename__ = 'victims'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'))
    user_code = db.Column(db.String(20))
    device_code = db.Column(db.String(120))
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    harvested_emails = db.relationship('HarvestedEmail', backref='victim', lazy=True)

    def __repr__(self):
        return f'<Victim {self.id} ({self.email})>'


class HarvestedEmail(db.Model):
    __tablename__ = 'harvested_emails'
    id = db.Column(db.Integer, primary_key=True)
    victim_id = db.Column(db.Integer, db.ForeignKey('victims.id'))
    sender = db.Column(db.String(120))
    recipient = db.Column(db.String(120))
    subject = db.Column(db.String(255))
    body_preview = db.Column(db.Text)
    received_date = db.Column(db.DateTime)
    provider = db.Column(db.String(50))
    verification_score = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<HarvestedEmail {self.sender} → {self.recipient}>'


class B2BLead(db.Model):
    __tablename__ = 'b2b_leads'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'))
    target_email = db.Column(db.String(120))
    provider = db.Column(db.String(50))
    verification_score = db.Column(db.Integer, default=0)
    is_contacted = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<B2BLead {self.target_email}>'


class DraftEmail(db.Model):
    __tablename__ = 'draft_emails'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'))
    from_victim_id = db.Column(db.Integer, db.ForeignKey('victims.id'))
    to_email = db.Column(db.String(120))
    subject = db.Column(db.String(255))
    body = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')
    ai_generated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<DraftEmail {self.id}>'


# ===== NEW: KeywordRule =====
class KeywordRule(db.Model):
    __tablename__ = 'keyword_rules'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'))
    keyword = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), default='general')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<KeywordRule {self.keyword}>'