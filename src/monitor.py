from datetime import datetime, timedelta, timezone
import requests
from src.config import DAYS_THRESHOLD, TENANT_ID, CLIENT_ID, CLIENT_SECRET


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

def get_expiring_secrets():
    token = get_access_token()
    url = "https://graph.microsoft.com/v1.0/applications"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    expiring_secrets = []
    current_date = datetime.now(timezone.utc)  # Ensure timezone-aware
    alert_date = current_date + timedelta(days=DAYS_THRESHOLD)

    for app in response.json().get("value", []):
        app_name = app.get("displayName")
        app_id = app.get("appId")
        secrets = app.get("passwordCredentials", [])

        for cred in secrets:
            expiry_date = datetime.fromisoformat(cred["endDateTime"].replace("Z", "+00:00"))
            days_remaining = (expiry_date - current_date).days

            if current_date < expiry_date < alert_date:
                expiring_secrets.append({
                    "App Registration": app_name,
                    "App ID": app_id,
                    "Secret Expiry Date": expiry_date.strftime("%d-%b-%Y"),
                    "Days Remaining": days_remaining
                })

    return expiring_secrets
