# lead_generator.py - Generate B2B leads from verified emails
from app.models import B2BLead
from app import db
from app.engine.sorter import EmailSorter

class LeadGenerator:
    @staticmethod
    def generate_leads(campaign_id, verified_emails, provider_groups):
        """
        Creates B2BLead records for each verified email.
        - verified_emails: list of dicts with keys ['email', 'score', 'status']
        - provider_groups: dict from EmailSorter.sort_batch() (grouped by provider)
        Returns number of leads created.
        """
        leads_created = 0
        for email_obj in verified_emails:
            email = email_obj['email']
            # Determine provider using sorter
            provider = EmailSorter.classify(email)
            # Avoid duplicates
            existing = B2BLead.query.filter_by(
                campaign_id=campaign_id,
                target_email=email
            ).first()
            if not existing:
                lead = B2BLead(
                    campaign_id=campaign_id,
                    target_email=email,
                    provider=provider,
                    verification_score=email_obj.get('score', 0),
                    is_contacted=False
                )
                db.session.add(lead)
                leads_created += 1
        db.session.commit()
        return leads_created

    @staticmethod
    def get_leads_by_campaign(campaign_id):
        """Return all leads for a campaign as a list of dicts"""
        leads = B2BLead.query.filter_by(campaign_id=campaign_id).all()
        return [{
            'id': l.id,
            'email': l.target_email,
            'provider': l.provider,
            'score': l.verification_score,
            'contacted': l.is_contacted
        } for l in leads] 
