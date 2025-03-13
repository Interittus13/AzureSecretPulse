import datetime
import requests
import smtplib
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load environment variables from .env file
load_dotenv(override=True)

# Azure Creds
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")

# SMTP Configuration
SMTP_SERVER = "smtp.your-email.com"
SMTP_PORT = 587
SMTP_USER = "your-email@yourcompany.com"
SMTP_PASSWORD = "your-email-password"
TO_EMAILS = ["admin@yourcompany.com"]

# Authentication: Get Azure Token
def get_access_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json().get("access_token")

# Fetch App Registrations
def get_app_registrations():
    token = get_access_token()
    url = "https://graph.microsoft.com/v1.0/applications"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("value", [])

# Check Expiring Secrets
def check_expiring_secrets(apps, days_threshold=30):
    expiring_secrets = []
    current_date = datetime.datetime.now(datetime.UTC)  # Ensure timezone-aware

    for app in apps:
        app_name = app.get("displayName")
        app_id = app.get("appId")
        secrets = app.get("passwordCredentials", [])

        for secret in secrets:
            expiry_date_str = secret.get("endDateTime")
            if expiry_date_str:
                expiry_date = datetime.datetime.fromisoformat(expiry_date_str[:-1]).replace(tzinfo=datetime.UTC)
                days_remaining = (expiry_date - current_date).days

                if 0 < days_remaining < days_threshold:
                    expiring_secrets.append({
                        "App Registration": app_name,
                        "App ID": app_id,
                        "Secret Expiry Date": expiry_date.strftime("%d-%b-%Y"),
                        "Days Remaining": days_remaining
                    })

    return expiring_secrets

# Generate HTML Email
def generate_html(expiring_secrets, days_threshold):
    html_table_rows = "".join(
        f"<tr><td>{sec['App Registration']}</td><td>{sec['App ID']}</td><td>{sec['Secret Expiry Date']}</td><td>{sec['Days Remaining']}</td></tr>"
        for sec in expiring_secrets
    )

    html_content = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Expiring App Registration Secrets Alert</title>
        <style>
            :root {{
                --primary-color: #f44336;
                --success-color: #4caf50;
                --border-color: #e0e0e0;
                --background-color: #f9f9f9;
                --text-color: #333333;
                --text-secondary: #666666;
                --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                --border-radius: 8px;
                --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                }}
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                }}
            body {{
                font-family: var(--font-family);
                line-height: 1.6;
                color: var(--text-color);
                background-color: var(--background-color);
                padding: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                }}
            .alert-card {{
                width: 100%;
                max-width: 800px;
                background-color: white;
                border-radius: var(--border-radius);
                overflow: hidden;
                box-shadow: var(--card-shadow);
                }}
            .alert-header {{
                background-color: var(--primary-color);
                color: white;
                padding: 16px 24px;
                display: flex;
                align-items: center;
                gap: 12px;
                }}
            .alert-header h2 {{
                font-size: 1.25rem;
                font-weight: 600;
                }}
            .alert-icon {{
                display: inline-flex;
                width: 24px;
                height: 24px;
                }}
            .alert-body {{
                padding: 24px;
                }}
            .alert-message {{
                margin-bottom: 24px;
                }}
            .alert-message p {{
                margin-bottom: 12px;
                }}
            .alert-message strong {{
                font-weight: 600;
                }}
            .table-container {{
                overflow-x: auto;
                margin-bottom: 24px;
                border: 1px solid var(--border-color);
                border-radius: var(--border-radius);
                }}
            table {{
                width: 100%;
                border-collapse: collapse;
                }}
            th {{
                background-color: #f5f5f5;
                text-align: left;
                padding: 12px 16px;
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-weight: 600;
                color: var(--text-secondary);
                border-bottom: 1px solid var(--border-color);
                }}
            td {{
                padding: 12px 16px;
                border-bottom: 1px solid var(--border-color);
                font-size: 0.875rem;
                }}
            tr:last-child td {{
                border-bottom: none;
                }}
            .actions {{
                display: flex;
                flex-wrap: wrap;
                gap: 16px;
                align-items: center;
                margin-bottom: 16px;
                }}
            .btn {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                background-color: var(--primary-color);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 0.875rem;
                font-weight: 500;
                text-decoration: none;
                border-radius: 4px;
                transition: background-color 0.2s, transform 0.1s;
                }}
            .btn:hover {{
                background-color: #e53935;
                }}
            .support-text {{
                font-size: 0.875rem;
                color: var(--text-secondary)
                }}
            .alert-footer {{
                background-color: #f5f5f5;
                padding: 16px 24px;
                border-top: 1px solid var(--border-color);
                display: flex;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 12px;
                font-size: 0.875rem;
                color: var(--text-secondary)
                }}
            @media (max-width: 640px) {{
                .alert-footer {{
                    flex-direction: column;
                    align-items: center;
                    text-align: center;
                    }}
                .actions {{
                    flex-direction: column;
                    align-items: flex-start;
                    }}
                .btn {{
                    width: 100%;
                    }}
                }}
        </style>
    </head>
    <body>
        <div class="alert-card">
            <div class="alert-header">
                <div class="alert-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line>
                        <line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>
                </div>
                <h2>Expiring App Registration Secrets Alert</h2>
            </div>

            <div class="alert-body">
                <div class="alert-message">
                    <p>Dear Admin,</p>
                    <p>The following App Registration secrets will expire in the next <strong>{days_threshold} days</strong>. Please take action to renew them.</p>
                </div>

                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>App Registration</th>
                                <th>App ID</th>
                                <th>Expiry Date</th>
                                <th>Days Remaining</th>
                            </tr>
                        </thead>
                        <tbody>
                        {html_table_rows}
                        </tbody>
                    </table>
                </div>

                <div class="actions">
                    <a href="https://portal.azure.com" class="btn">Renew Now</a>
                    <p class="support-text">If you need assistance, please contact IT support.</p>
                </div>
            </div>

            <div class="alert-footer">
                <div>Best regards,</div>
                <div>IT Team | Your Company</div>
            </div>
        </div>
    </body>
    </html>"""
    
    return html_content

# Send Email
def send_email(html_content):
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = ", ".join(TO_EMAILS)
        msg["Subject"] = "Expiring App Registration Secrets Alert"
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, TO_EMAILS, msg.as_string())

        print("✅ Email sent successfully.")
    except Exception as e:
        print(f"❌ SMTP failed: {e}")
        save_html_preview(html_content)

# Save HTML Preview if SMTP Fails
def save_html_preview(html_content):
    html_file = "App_Secret_Expiry_Alert.html"
    with open(html_file, "w", encoding="utf-8") as file:
        file.write(html_content)
    print(f"📄 Email preview saved as: {html_file}")

# Main Execution
if __name__ == "__main__":
    apps = get_app_registrations()
    expiring_secrets = check_expiring_secrets(apps)

    if expiring_secrets:
        html_content = generate_html(expiring_secrets, 30)
        save_html_preview(html_content)
        # send_email(html_content)
    else:
        print("✅ No expiring app registration secrets found.")
