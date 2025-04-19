# import subprocess
# from app.utils.json_utils import read_json, write_json
# import os

# class EmailService:
#     def __init__(self):
#         self.config_file = "../Core/data/config.json"
#         self.scripts_dir = "../Core/scripts"
    
    
#     def run_powershell_script(self, script_name, args=None):
#         """
#         Run a PowerShell script and return the output.
#         """
#         script_path = os.path.join(self.scripts_dir, script_name)
#         command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path]
#         if args:
#             command.extend(args)
#         try:
#             result = subprocess.run(command, capture_output=True, text=True, check=True)
#             return result.stdout
#         except subprocess.CalledProcessError as e:
#             return e.stderr
    
#     def add_email_to_recipient(self, email_address):
#         """
#         Add an email address to the list of monitored email addresses.
#         """
#         output = self.run_powershell_script("configs.ps1", ["-Action", "ADD", "-Type", "Email", "-Value", email_address])
#         if "Recipient added:" not in output:
#             raise ValueError("Failed to add Recipient: " + output)
    
#     def remove_email_recipient(self, email_address):
#         """
#         Remove an email address from the list of monitored email addresses.
#         """
#         output = self.run_powershell_script("configs.ps1", ["-Action", "REMOVE", "-Type", "Email", "-Value", email_address])
#         if "Recipient removed:" not in output:
#             raise ValueError("Failed to remove Recipient: " + output)
    
#     def list_email_recipients(self):
#         """
#         List all email addresses being monitored.
#         """
#         config = read_json(self.config_file)
#         return config.get('email', {}).get('recipients', [])
    
#     # def send_test_email(self):
#     #     """Force l'envoi immédiat d'un email d'alerte."""
#     #     output = self.run_powershell_script("alerts.ps1", ["-ForceSend"]) # Assumant que -ForceSend force l'envoi
#     #     if "Email sent successfully" not in output:
#     #         raise ValueError("Failed to send test email: " + output)
        
#     def set_email_frequency(self, frequency):
#         """
#         Set the email notification frequency.
#         """
#         output = self.run_powershell_script("configs.ps1", ["-Action", "SET-EMAIL-INTERVAL", "-Value", str(frequency)])
#         if "Email frequency set:" not in output:
#             raise ValueError("Failed to set email frequency: " + output)


#--------------------------------------------------------------------------------------------------------------------------------------

import json
import os
import re
from configs.settings import Config

class EmailService:
    def __init__(self):
        self.config_file = os.path.join(Config.BASE_DIR, "Core", "data", "config.json")
        self.status_file = os.path.join(Config.BASE_DIR, "Core", "data", "status.json")

    def _read_config(self):
        """Charge les emails configurés"""
        try:
            with open(self.config_file, "r") as f:
                data = json.load(f)
            return data.get("email", {}).get("recipients", [])  # ✅ Correction ici
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write_config(self, recipients):
        """Écrit la liste des emails configurés"""
        try:
            with open(self.config_file, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        if "email" not in data:
            data["email"] = {}

        data["email"]["recipients"] = recipients  # ✅ Correction ici

        with open(self.config_file, "w") as f:
            json.dump(data, f, indent=4)

    def _read_status(self):
        """Charge les emails actifs (pendant l'exécution du script)"""
        try:
            with open(self.status_file, "r") as f:
                return json.load(f).get("alerts", {}).get("Emails", [])  # ✅ Correction ici
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def is_email_configured(self, email):
        """Vérifie si un email est configuré dans config.json"""
        return email in self._read_config()

    def is_email_active(self, email):
        """Vérifie si un email est actif dans status.json"""
        return email in self._read_status()

    def add_email(self, email):
        """Ajoute un email à la liste des destinataires d'alertes"""
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email format.")

        recipients = self._read_config()
        if email in recipients:
            raise ValueError("Email is already in the list.")

        recipients.append(email)
        self._write_config(recipients)

    def remove_email(self, email):
        """Supprime un email de la liste des destinataires"""
        recipients = self._read_config()
        if email not in recipients:
            raise ValueError("Email not found in the list.")

        recipients.remove(email)
        self._write_config(recipients)

    def list_emails(self):
        """Retourne tous les emails enregistrés"""
        return {
            "configured_emails": self._read_config(),
            "active_emails": self._read_status()
        }
