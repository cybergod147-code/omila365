# app/utils/notify.py
import requests
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import paramiko
import socket
from flask import current_app

def send_telegram(bot_token, chat_id, message):
    """Send a Telegram message. Returns True if successful."""
    if not bot_token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(url, json=payload, timeout=5)
        return resp.status_code == 200
    except Exception as e:
        logging.error(f"Telegram error: {e}")
        return False

def test_vps_connection(ip, port, username, auth_method, password=None, ssh_key=None):
    """Test SSH connection to VPS. Returns (success, message)."""
    if not ip or not port or not username:
        return False, "Missing required fields"
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if auth_method == 'password' and password:
            client.connect(ip, port=port, username=username, password=password, timeout=5)
        elif auth_method == 'key' and ssh_key:
            from io import StringIO
            key = paramiko.RSAKey.from_private_key(StringIO(ssh_key))
            client.connect(ip, port=port, username=username, pkey=key, timeout=5)
        else:
            return False, "Invalid auth method or missing credentials"
        client.close()
        return True, "SSH connection successful"
    except paramiko.AuthenticationException:
        return False, "Authentication failed"
    except socket.timeout:
        return False, "Connection timeout"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def send_email_via_vps(vps_config, to_emails, subject, body_html):
    """Send emails using the VPS's SMTP server."""
    if not vps_config.get('smtp_host'):
        return 0, "No SMTP host configured"
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = vps_config.get('smtp_from', 'noreply@yourdomain.com')
        part = MIMEText(body_html, 'html')
        msg.attach(part)
        server = smtplib.SMTP(vps_config['smtp_host'], vps_config.get('smtp_port', 587))
        if vps_config.get('smtp_tls', True):
            server.starttls()
        if vps_config.get('smtp_user') and vps_config.get('smtp_password'):
            server.login(vps_config['smtp_user'], vps_config['smtp_password'])
        sent_count = 0
        for email in to_emails:
            msg['To'] = email
            server.sendmail(msg['From'], [email], msg.as_string())
            sent_count += 1
        server.quit()
        return sent_count, None
    except Exception as e:
        return 0, str(e)

# ============================================================
# NEW: SMTP SENDER WITH PER-USER SUPPORT
# ============================================================
def send_email_smtp(recipients, subject, html_body,
                    from_email=None, from_name=None,
                    server=None, port=None, username=None, password=None, use_tls=None):
    """
    Send an email via SMTP.
    If user SMTP parameters are provided, use them; otherwise fallback to global config.
    Returns: (success, message, sent_count, failed_list)
    """
    try:
        config = current_app.config

        # Use user-provided values if given, else fallback to config
        server = server or config.get('SMTP_SERVER')
        port = port or config.get('SMTP_PORT', 587)
        username = username or config.get('SMTP_USERNAME')
        password = password or config.get('SMTP_PASSWORD')
        from_email = from_email or config.get('SMTP_FROM_EMAIL')
        from_name = from_name or config.get('SMTP_FROM_NAME', 'Microsoft Security')
        use_tls = use_tls if use_tls is not None else config.get('SMTP_USE_TLS', True)

        # Check if SMTP is enabled globally
        if not config.get('SMTP_ENABLED', False):
            return False, "SMTP is disabled in global configuration", 0, recipients

        # Validate required fields
        if not all([server, username, password, from_email]):
            return False, "SMTP configuration incomplete (server, username, password, or from_email missing)", 0, recipients

        # Ensure recipients is a list
        if isinstance(recipients, str):
            recipients = [r.strip() for r in recipients.split('\n') if r.strip()]
        if not recipients:
            return False, "No recipients provided", 0, []

        # Build email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = ', '.join(recipients)

        part = MIMEText(html_body, 'html')
        msg.attach(part)

        # Connect and send
        if use_tls:
            smtp = smtplib.SMTP(server, port)
            smtp.starttls()
        else:
            smtp = smtplib.SMTP_SSL(server, port)

        smtp.login(username, password)
        smtp.send_message(msg)
        smtp.quit()

        return True, "Email sent successfully", len(recipients), []

    except Exception as e:
        logging.error(f"SMTP send failed: {e}")
        return False, str(e), 0, recipients