from app.engine.templates import get_template as get_template_dict

class DraftComposer:
    @staticmethod
    def compose_email(campaign, user, template_id='ms_signin', **extra):
        template = get_template_dict(template_id)
        if not template:
            return "<p>Template not found</p>"

        html = template['email_body_html']
        replacements = {
            '{{first_name}}': getattr(user, 'username', 'there'),
            '{{sender_name}}': getattr(campaign, 'sender_name', 'System'),
            '{{date}}': campaign.created_at.strftime('%Y-%m-%d') if campaign.created_at else 'today',
            '{{company}}': getattr(campaign, 'company', 'your company'),
            '{{link}}': extra.get('link', '#'),
            '{{user_code}}': extra.get('user_code', ''),
        }
        replacements.update(extra)
        for key, value in replacements.items():
            html = html.replace(key, str(value))
        return html

    @staticmethod
    def compose_lure(campaign, template_id='ms_signin', **extra):
        template = get_template_dict(template_id)
        if not template:
            return "<p>Lure template not found</p>"

        html = template['lure_body_html']
        replacements = {
            '{{first_name}}': getattr(campaign, 'sender_name', 'there'),
            '{{sender_name}}': getattr(campaign, 'sender_name', 'System'),
            '{{date}}': campaign.created_at.strftime('%Y-%m-%d') if campaign.created_at else 'today',
            '{{company}}': getattr(campaign, 'company', 'your company'),
            '{{continue_url}}': extra.get('continue_url', '#'),
            '{{user_code}}': extra.get('user_code', '000000'),
        }
        replacements.update(extra)
        for key, value in replacements.items():
            html = html.replace(key, str(value))
        return html