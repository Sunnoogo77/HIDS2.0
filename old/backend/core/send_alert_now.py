# core/send_alert_now.py
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from utils.json_handler import read_json, write_json
from utils.logger import log_event

CONFIG_FILE = os.path.join("data", "config.json")
ALERTS_FILE = os.path.join("data", "alerts.json")


def send_alerts_now(clear_after_send: bool = False):
    config = read_json(CONFIG_FILE)
    alerts = read_json(ALERTS_FILE) or {"files": [], "folders": [], "ips": []}
    if not config or not config.get("email") or not any(alerts.values()):
        log_event("Alerts", "No alerts or email config missing.")
        return

    email_conf = config["email"]
    recipients = email_conf.get("recipients", [])
    sender = email_conf.get("sender")
    password = email_conf.get("password", "")

    def build_table(title, entries):
        rows = ''.join(f"<tr><td>{a['Timestamp']}</td><td>{a['Message']}</td></tr>" for a in entries)
        return f"""
        <h3>{title}:</h3>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Alert Message</th>
            </tr>
            {rows}
        </table>
        """

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h2>HIDS Manual Alert</h2>
        <p>The following security events were detected:</p>
        {build_table('Files', alerts.get('files', []))}
        {build_table('Folders', alerts.get('folders', []))}
        {build_table('IPs', alerts.get('ips', []))}
        <p><i>This is a manually triggered alert notification.</i></p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = f"HIDS Manual Alerts - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    msg.attach(MIMEText(html, 'html'))

    try:
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipients, msg.as_string())
            log_event("Alerts", "Manual email alert sent.")
    except Exception as e:
        log_event("Alerts", f"Manual email send failed: {e}")

    if clear_after_send:
        write_json(ALERTS_FILE, {"files": [], "folders": [], "ips": []})
        log_event("Alerts", "Alerts cleared after manual send.")
