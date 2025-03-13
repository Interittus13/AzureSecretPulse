from src.email_service import send_email
from src.html_renderer import render_html_report
from src.monitor import get_expiring_secrets


if __name__ == "__main__":
    secrets = get_expiring_secrets()
    if secrets:
        html = render_html_report(secrets)
        send_email(html)
    else:
        print("No expiring secrets found.")