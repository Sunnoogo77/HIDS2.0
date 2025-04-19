# import subprocess
# from app.utils.json_utils import read_json, write_json
# import os

# class FolderService:
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
    
#     def add_folder_to_monitoring(self, folder_path):
#         """
#         Add a folder to the list of monitored folders.
#         """
#         if not os.path.isdir(folder_path):
#             raise ValueError("Folder does not exist.")
#         output = self.run_powershell_script("configs.ps1", ["-Action", "ADD", "-Type", "Folder", "-Value", folder_path])
#         if "Folder added:" not in output:
#             raise ValueError("Failed to add folder: " + output)
    
#     def remove_folder_from_monitoring(self, folder_path):
#         """
#         Remove a folder from the list of monitored folders.
#         """
#         output = self.run_powershell_script("configs.ps1", ["-Action", "REMOVE", "-Type", "Folder", "-Value", folder_path])
#         if "Folder removed:" not in output:
#             raise ValueError("Failed to remove folder: " + output)
    
#     def list_monitored_folders(self):
#         """
#         List all folders being monitored.
#         """
#         config = read_json(self.config_file)
#         return config.get("folders", [])




import json
import os
from configs.settings import Config  

class FolderService:
    def __init__(self):
        self.config_file = os.path.join(Config.BASE_DIR, "Core", "data", "config.json")
        self.status_file = os.path.join(Config.BASE_DIR, "Core", "data", "status.json")

    def _read_config(self):
        """Lit le fichier de configuration"""
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"folders": []}

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

    def add_folder_to_monitoring(self, folder_path):
        """Ajoute un dossier à la configuration pour surveillance"""
        config = self._read_config()

        if folder_path in config["folders"]:
            raise ValueError("Folder is already being monitored.")

        config["folders"].append(folder_path)
        self._write_config(config)

    def remove_folder_from_monitoring(self, folder_path):
        """Supprime un dossier de la surveillance si possible"""
        config = self._read_config()

        if folder_path not in config["folders"]:
            raise ValueError("Folder is not currently monitored.")

        config["folders"].remove(folder_path)
        self._write_config(config)

    def list_configured_folders(self):
        """Retourne la liste des dossiers configurés dans `config.json`"""
        config = self._read_config()
        return config.get("folders", [])

    def get_active_monitored_folders(self):
        """Retourne la liste des dossiers réellement surveillés (ceux qui sont dans `status.json`)"""
        status_data = self._read_status()
        return status_data.get("monitor_folders", {}).get("MonitoredFolders", [])

    def is_folder_monitored(self, folder_path):
        """Vérifie si un dossier est en cours de surveillance (dans `status.json`)"""
        monitored_folders = self.get_active_monitored_folders()
        return folder_path in monitored_folders
