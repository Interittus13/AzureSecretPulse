from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from src.config import SMTP_SERVER, SMTP_PORT, SMTP_PASS, EMAIL_FROM, EMAIL_TO
from src.html_renderer import render_html_report


def send_email(html_content):
    """Send an email alert for expiring secrets."""
    recipients = [email.strip() for email in EMAIL_TO.split(",") if email.strip()]
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = "Expiring App Registration Secrets Alert"

    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_FROM, SMTP_PASS)
            server.sendmail(EMAIL_FROM, recipients, msg.as_string())
            print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
