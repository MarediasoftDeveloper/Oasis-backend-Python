import requests
from django.conf import settings

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"

def send_mail_via_sendgrid(to_email, subject, html_content):
    headers = {
        "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "personalizations": [
            {
                "to": [{"email": to_email}],
                "cc": [
                    {"email": "info@myoasis.co.nz"}  # add more if needed
                ]
            }
        ],
        "from": {"email": settings.DEFAULT_FROM_EMAIL},
        "subject": subject,
        "content": [
            {
                "type": "text/html",
                "value": html_content
            }
        ]
    }

    try:
        response = requests.post(SENDGRID_API_URL, json=data, headers=headers, verify=False)  # SSL bypass
        if response.status_code in [200, 202]:
            return True
        else:
            print("SendGrid Error:", response.text)
            return False

    except Exception as e:
        print("Exception while sending email:", e)
        return False
