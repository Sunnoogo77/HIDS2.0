# import subprocess
# from app.utils.json_utils import read_json, write_json
# import os

# class FileService:
#     def __init__(self):
#         self.config_file = "../Core/data/config.json"
#         self.scripts_dir = "../Core/scripts"
        
#     def run_powershell_script(self, script_name, args=None):
#         """
#         Run a PowerShell script. and return the output.
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
    
#     def add_file_to_monitoring(self, file_path):
#         """
#         Add a file to the list of monitored files.
#         """
#         if not os.path.isfile(file_path):
#             raise ValueError("File does not exist.")
#         output = self.run_powershell_script("configs.ps1", ["-Action", "ADD", "-Type", "File", "-Value", file_path])
#         if "File added:" not in output:
#             raise ValueError("Failed to add file: " + output)
    
#     def remove_file_from_monitoring(self, file_path):
#         """
#         Remove a file from the list of monitored files.
#         """
#         output = self.run_powershell_script("configs.ps1", ["-Action", "REMOVE", "-Type", "File", "-Value", file_path])
#         if "File removed:" not in output:
#             raise ValueError("Failed to remove file: " + output)
    
#     def list_monitored_files(self):
#         """
#         List all files being monitored.
#         """
#         config = read_json(self.config_file)
#         return config.get("files", [])

# #---------------------------------------------------------------------------
# # API/app/services/file_service.py

# import subprocess
# import json
# import os
# from configs.settings import Config  # Importez votre classe de configuration

# class FileService:
#     def __init__(self):
#         self.config_file = os.path.join(Config.BASE_DIR, "Core", "data", "config.json")
#         self.scripts_dir = os.path.join(Config.BASE_DIR, "Core", "scripts")

#     def _read_config(self):
#         try:
#             with open(self.config_file, "r") as f:
#                 return json.load(f)
#         except FileNotFoundError:
#             return {"files": []}
#         except json.JSONDecodeError:
#             return {"files": []}

#     def _write_config(self, config):
#         with open(self.config_file, "w") as f:
#             json.dump(config, f, indent=4)

#     def add_file_to_monitoring(self, file_path):
#         if not os.path.isfile(file_path):
#             raise ValueError("File does not exist.")
#         config = self._read_config()
#         if file_path not in config["files"]:
#             config["files"].append(file_path)
#             self._write_config(config)
#         else:
#             raise ValueError("File already monitored.")

#     def remove_file_from_monitoring(self, file_path):
#         config = self._read_config()
#         if file_path in config["files"]:
#             config["files"].remove(file_path)
#             self._write_config(config)
#         else:
#             raise ValueError("File not found in monitored list.")

#     def list_monitored_files(self):
#         config = self._read_config()
#         return config.get("files", [])

#------------------------------------------
# #avant dernier -******************
# import json
# import os
# from configs.settings import Config  # Importation de la configuration

# class FileService:
#     def __init__(self):
#         self.config_file = os.path.join(Config.BASE_DIR, "Core", "data", "config.json")

#     def _read_config(self):
#         try:
#             with open(self.config_file, "r") as f:
#                 return json.load(f)
#         except (FileNotFoundError, json.JSONDecodeError):
#             return {"files": []}

#     def _write_config(self, config):
#         with open(self.config_file, "w") as f:
#             json.dump(config, f, indent=4)

#     def is_file_monitored(self, file_path):
#         """Vérifie si un fichier est surveillé."""
#         file_path = self._normalize_path(file_path)  # 🔹 Normalisation ici aussi
#         config = self._read_config()
#         return file_path in config.get("files", [])


#     def _normalize_path(self, file_path):
#         """Normalise les chemins pour éviter les doublons."""
#         return os.path.normpath(file_path)
    
#     def add_file_to_monitoring(self, file_path):
#         """Ajoute un fichier à la liste de surveillance"""
#         normalized_file_path = self._normalize_path(file_path)
#         config = self._read_config()
#         if normalized_file_path not in config["files"]:
#             config["files"].append(normalized_file_path)
#             self._write_config(config)
#         else:
#             raise ValueError("File already monitored.")
        
#         # config["files"].append(normalized_file_path)
#         self._write_config(config)

#     def remove_file_from_monitoring(self, file_path):
#         """Supprime un fichier de la liste de surveillance"""
#         config = self._read_config()
#         if file_path not in config["files"]:
#             raise ValueError("File is not currently monitored.")

#         config["files"].remove(file_path)
#         self._write_config(config)

#     def list_monitored_files(self):
#         config = self._read_config()
#         return [self._normalize_path(f) for f in config.get("files", [])]



# #------------------------------------------

import json
import os
from configs.settings import Config  

class FileService:
    def __init__(self):
        self.config_file = os.path.join(Config.BASE_DIR, "Core", "data", "config.json")
        self.status_file = os.path.join(Config.BASE_DIR, "Core", "data", "status.json")

    def _read_config(self):
        """Lit le fichier de configuration"""
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"files": []}

    def _write_config(self, config):
        """Écrit les données dans le fichier de configuration"""
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=4)

    def _read_status(self):
        """Lit le fichier de statut"""
        if not os.path.exists(self.status_file):
            print("Status file does not exist")
            return {}

        try:
            with open(self.status_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def add_file_to_monitoring(self, file_path):
        """Ajoute un fichier à la configuration pour surveillance"""
        config = self._read_config()

        if file_path in config["files"]:
            raise ValueError("File is already being monitored.")

        config["files"].append(file_path)
        self._write_config(config)

    def remove_file_from_monitoring(self, file_path):
        """Supprime un fichier de la surveillance si possible"""
        config = self._read_config()

        if file_path not in config["files"]:
            raise ValueError("File is not currently monitored.")

        config["files"].remove(file_path)
        self._write_config(config)

    def list_configured_files(self):
        """Retourne la liste des fichiers configurés dans `config.json`"""
        config = self._read_config()
        return config.get("files", [])

    def get_active_monitored_files(self):
        """Retourne la liste des fichiers réellement surveillés (ceux qui sont dans `status.json`)"""
        status_data = self._read_status()
        return status_data.get("monitor_files", {}).get("monitoredFiles", [])

    def is_file_monitored(self, file_path):
        """Vérifie si un fichier est en cours de surveillance (dans `status.json`)"""
        monitored_files = self.get_active_monitored_files()
        return file_path in monitored_files
