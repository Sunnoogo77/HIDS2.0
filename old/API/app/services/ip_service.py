# import subprocess
# from app.utils.json_utils import read_json, write_json
# import os
# import ipaddress

# class IpService:
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
    
#     def add_ip_to_monitoring(self, ip_address):
#         """
#         Add an IP address to the list of monitored IP addresses.
#         """
#         try:
#             ipaddress.ip_address(ip_address)
#         except ValueError:
#             raise ValueError("Invalid IP address.")
#         output = self.run_powershell_script("configs.ps1", ["-Action", "ADD", "-Type", "IP", "-Value", ip_address])
#         if "IP added:" not in output:
#             raise ValueError("Failed to add IP address: " + output)
    
#     def remove_ip_from_monitoring(self, ip_address):
#         """
#         Remove an IP address from the list of monitored IP addresses.
#         """
#         output = self.run_powershell_script("configs.ps1", ["-Action", "REMOVE", "-Type", "IP", "-Value", ip_address])
#         if "IP removed:" not in output:
#             raise ValueError("Failed to remove IP address: " + output)
    
#     def list_monitored_ips(self):
#         """
#         List all IP addresses being monitored.
#         """
#         config = read_json(self.config_file)
#         return config.get("ips", [])

#------------------------------------------------------------------
import json
import os
import ipaddress
from configs.settings import Config  

class IpService:
    def __init__(self):
        self.config_file = os.path.join(Config.BASE_DIR, "Core", "data", "config.json")
        self.status_file = os.path.join(Config.BASE_DIR, "Core", "data", "status.json")

    def _read_config(self):
        """Lit le fichier de configuration"""
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"ips": []}

    def _write_config(self, config):
        """Écrit les données dans le fichier de configuration"""
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=4)

    def _read_status(self):
        """Lit le fichier de statut"""
        if not os.path.exists(self.status_file):
            return {}

        try:
            with open(self.status_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def add_ip_to_monitoring(self, ip_address):
        """Ajoute une IP à la configuration pour surveillance"""
        try:
            ipaddress.ip_address(ip_address)  # Vérifier si c'est une IP valide
        except ValueError:
            raise ValueError("Invalid IP address.")

        config = self._read_config()

        if ip_address in config["ips"]:
            raise ValueError("IP is already being monitored.")

        config["ips"].append(ip_address)
        self._write_config(config)

    def remove_ip_from_monitoring(self, ip_address):
        """Supprime une IP de la surveillance si possible"""
        config = self._read_config()

        if ip_address not in config["ips"]:
            raise ValueError("IP is not currently monitored.")

        config["ips"].remove(ip_address)
        self._write_config(config)

    def list_configured_ips(self):
        """Retourne la liste des IPs configurées dans `config.json`"""
        config = self._read_config()
        return config.get("ips", [])

    def get_active_monitored_ips(self):
        """Retourne la liste des IPs réellement surveillées (dans `status.json`)"""
        status_data = self._read_status()
        return status_data.get("monitor_ips", {}).get("MonitoredIPs", [])

    def is_ip_monitored(self, ip_address):
        """Vérifie si une IP est en cours de surveillance (dans `status.json`)"""
        monitored_ips = self.get_active_monitored_ips()
        return ip_address in monitored_ips
