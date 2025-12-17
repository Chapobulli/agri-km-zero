import os
import logging
import requests

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
MAIL_FROM = os.environ.get('MAIL_FROM', 'no-reply@agrikmzero.it')

SENDGRID_URL = 'https://api.sendgrid.com/v3/mail/send'


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Send an email using SendGrid if configured.
    Falls back to logging the email content if API key is missing.
    Returns True if the operation was dispatched successfully (or logged in fallback).
    """
    if not SENDGRID_API_KEY:
        logging.info("[Email Fallback] To: %s | Subject: %s\n%s", to_email, subject, html_content)
        return True

    headers = {
        'Authorization': f'Bearer {SENDGRID_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'personalizations': [
            {
                'to': [{'email': to_email}],
                'subject': subject
            }
        ],
        'from': {'email': MAIL_FROM, 'name': 'Agri KM Zero'},
        'content': [
            { 'type': 'text/html', 'value': html_content }
        ]
    }
    try:
        resp = requests.post(SENDGRID_URL, headers=headers, json=data, timeout=10)
        if 200 <= resp.status_code < 300:
            return True
        logging.error("SendGrid error %s: %s", resp.status_code, resp.text)
        return False
    except Exception as e:
        logging.exception("SendGrid request failed: %s", e)
        return False
