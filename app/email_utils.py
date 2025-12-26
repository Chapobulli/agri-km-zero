import os
import logging
import smtplib
from email.message import EmailMessage

# Optional: requests is only needed for SendGrid API
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
MAIL_FROM = os.environ.get('MAIL_FROM', 'no-reply@agrikmzero.it')

# Optional generic SMTP envs
EMAIL_PROVIDER = os.environ.get('EMAIL_PROVIDER')  # 'sendgrid' | 'smtp'
SMTP_HOST = os.environ.get('SMTP_HOST')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASS = os.environ.get('SMTP_PASS')
SMTP_STARTTLS = os.environ.get('SMTP_STARTTLS', 'true').lower() in ('1', 'true', 'yes')

SENDGRID_URL = 'https://api.sendgrid.com/v3/mail/send'


def _send_via_sendgrid(to_email: str, subject: str, html_content: str) -> bool:
    if not HAS_REQUESTS:
        logging.warning("SendGrid requires 'requests' library (not installed)")
        return False
    headers = {
        'Authorization': f'Bearer {SENDGRID_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'personalizations': [
            {'to': [{'email': to_email}], 'subject': subject}
        ],
        'from': {'email': MAIL_FROM, 'name': 'Agri KM Zero'},
        'content': [{'type': 'text/html', 'value': html_content}]
    }
    resp = requests.post(SENDGRID_URL, headers=headers, json=data, timeout=8)
    if 200 <= resp.status_code < 300:
        return True
    logging.error("SendGrid error %s: %s", resp.status_code, resp.text)
    return False


def _send_via_smtp(to_email: str, subject: str, html_content: str) -> bool:
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
        logging.warning("SMTP not configured (missing SMTP_HOST/SMTP_USER/SMTP_PASS)")
        return False
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = MAIL_FROM
    msg['To'] = to_email
    msg.set_content("This email requires an HTML-compatible client.")
    msg.add_alternative(html_content, subtype='html')
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=5) as server:
            if SMTP_STARTTLS:
                server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        logging.exception("SMTP send failed: %s", e)
        return False


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Send an email using the configured provider.
    Order of preference:
    1) If EMAIL_PROVIDER == 'smtp' use SMTP.
    2) Else if SENDGRID_API_KEY set, use SendGrid.
    3) Else if SMTP envs present, try SMTP.
    4) Fallback: log email content and return True (never block user flow).
    """
    try:
        if EMAIL_PROVIDER == 'smtp':
            try:
                ok = _send_via_smtp(to_email, subject, html_content)
                if ok:
                    return True
            except Exception as e:
                logging.warning("SMTP send failed, falling back: %s", e)
        
        if SENDGRID_API_KEY and (EMAIL_PROVIDER in (None, '', 'sendgrid')):
            try:
                ok = _send_via_sendgrid(to_email, subject, html_content)
                if ok:
                    return True
            except Exception as e:
                logging.warning("SendGrid send failed, falling back: %s", e)
        
        # Attempt SMTP if creds exist and not already tried
        if SMTP_HOST and SMTP_USER and SMTP_PASS and EMAIL_PROVIDER != 'smtp':
            try:
                ok = _send_via_smtp(to_email, subject, html_content)
                if ok:
                    return True
            except Exception as e:
                logging.warning("SMTP fallback failed: %s", e)
        
        # Ultimate fallback: log and succeed (don't block user actions)
        logging.info("[Email Fallback - Dev Mode] To: %s | Subject: %s\n%s", to_email, subject, html_content)
        return True
    except Exception as e:
        logging.exception("send_email completely failed, but returning True to not block user flow: %s", e)
        return True  # Never block registration/reset on email failure
