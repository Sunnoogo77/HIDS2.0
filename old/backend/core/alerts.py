# core/alerts.py
import os
import time
import smtplib
from threading import Thread
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from utils.json_handler import read_json, write_json
from utils.logger import log_event

CONFIG_FILE = os.path.join("data", "config.json")
ALERTS_FILE = os.path.join("data", "alerts.json")
STATUS_FILE = os.path.join("data", "status.json")

class PeriodicAlertSender(Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = False
        self.interval = 300
        self.email_recipients = []
        self.smtp_server = "smtp.office365.com"
        self.smtp_port = 587
        self.sender_email = ""
        self.sender_password = ""  # WARNING: For production use, load securely!
        self.pid = os.getpid()
        self.start_time = datetime.now().isoformat()

    def load_config(self):
        config = read_json(CONFIG_FILE)
        if not config or not config.get("email"):
            return False
        email_conf = config["email"]
        self.interval = email_conf.get("interval", 300)
        self.email_recipients = email_conf.get("recipients", [])
        self.sender_email = email_conf.get("sender")
        self.sender_password = email_conf.get("password", "")
        return True

    def update_status(self, counter):
        status = read_json(STATUS_FILE) or {}
        status["alerts"] = {
            "PID": self.pid,
            "StartTime": self.start_time,
            "Status": "Running" if self.running else "Stopped",
            "Interval": self.interval,
            "EmailCounter": counter,
            "Emails": self.email_recipients,
            "LastUpdate": datetime.now().isoformat()
        }
        write_json(STATUS_FILE, status)

    def format_alerts_html(self, alerts):
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

        return f"""
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
            <h2>HIDS Alert Report</h2>
            <p>The following security events were detected:</p>
            {build_table('Files', alerts.get('files', []))}
            {build_table('Folders', alerts.get('folders', []))}
            {build_table('IPs', alerts.get('ips', []))}
            <p><i>This is an automated notification. Please review the details above.</i></p>
        </body>
        </html>
        """

    def send_email(self, html_content):
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = ", ".join(self.email_recipients)
        msg['Subject'] = f"HIDS Alerts - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        msg.attach(MIMEText(html_content, 'html'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.email_recipients, msg.as_string())
                log_event("Alerts", "Email alert sent successfully.")
        except Exception as e:
            log_event("Alerts", f"Email send failed: {e}")

    def run(self):
        self.running = True
        if not self.load_config():
            log_event("Alerts", "Invalid email configuration.")
            return

        email_count = 0
        while self.running:
            alerts = read_json(ALERTS_FILE) or {"files": [], "folders": [], "ips": []}
            if any(alerts.values()):
                html = self.format_alerts_html(alerts)
                self.send_email(html)
                write_json(ALERTS_FILE, {"files": [], "folders": [], "ips": []})
                email_count += 1
            self.update_status(email_count)
            time.sleep(self.interval)
        self.update_status(email_count)

    def stop(self):
        self.running = False