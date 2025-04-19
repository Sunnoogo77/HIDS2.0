import json
import os
from configs.settings import Config

class ConfigService:
    def __init__(self):
        self.config_file = os.path.join(Config.BASE_DIR, "Core", "data", "config.json")

    def _read_config(self):
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _write_config(self, config):
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=4)

    def get_config(self):
        """Retourne toute la configuration"""
        return self._read_config()

    def update_intervals(self, scan_interval=None, email_interval=None):
        """Met à jour les intervalles des scans et des emails séparément"""
        config = self._read_config()

        # Vérifier et modifier l'intervalle des scans
        if scan_interval is not None:
            if not isinstance(scan_interval, int) or scan_interval <= 0:
                raise ValueError("Invalid scan interval. Must be a positive integer.")
            config["interval"] = scan_interval  # ✅ Mise à jour intervalle scan

        # Vérifier et modifier l'intervalle des emails
        if email_interval is not None:
            if not isinstance(email_interval, int) or email_interval <= 0:
                raise ValueError("Invalid email interval. Must be a positive integer.")
            if "email" not in config:
                config["email"] = {}
            config["email"]["interval"] = email_interval  # ✅ Mise à jour intervalle email

        self._write_config(config)
