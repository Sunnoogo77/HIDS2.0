# import subprocess
# from app.utils.json_utils import read_json, write_json
# import os

# class StatusService:
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
    
#     def get_general_status(self):
#         """
#         Get the general status of the system.
#         """
#         config = read_json(self.config_file)
#         return config.get('status', {}).get('general', {})
    
#     def get_files_status(self):
#         """
#         Get the status of all monitored files.
#         """
#         config = read_json(self.config_file)
#         return config.get('status', {}).get('files', {})

#     def get_folders_status(self):
#         """
#         Get the status of all monitored folders.
#         """
#         config = read_json(self.config_file)
#         return config.get('status', {}).get('folders', {})
    
#     def get_ips_status(self):
#         """
#         Get the status of all monitored IP addresses.
#         """
#         config = read_json(self.config_file)
#         return config.get('status', {}).get('ips', {})
    
#     def get_emails_status(self):
#         """
#         Get the status of all monitored email addresses.
#         """
#         config = read_json(self.config_file)
#         return config.get('status', {}).get('emails', {})

# API/app/services/status_service.py

import json
import os
# from app.configs.settings import Config  # Importez votre classe de configuration
from configs.settings import Config
class StatusService:
    def __init__(self):
        self.status_file = os.path.join(Config.BASE_DIR, "Core", "data", "status.json")

    def _read_status(self):
        try:
            with open(self.status_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def get_script_status(self, script_name):
        status = self._read_status()
        script_status = status.get(script_name, {})
        if not script_status:
            return {"message": f"Status for {script_name} not found"}, 404
        return script_status, 200
    
    def get_all_scripts_status(self):
        status = self._read_status()
        return status, 200