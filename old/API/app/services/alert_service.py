# from app.utils.json_utils import read_json, write_json
# import os

# class AlertService:
#     def __init__(self):
#         self.alerts_file = "../Core/data/alerts.json"
#         self.logs_file = "../Core/logs/hids.json"
        
#     def list_recent_alerts(self):
#         """
#         List the most recent alerts.
#         """
#         alerts = read_json(self.alerts_file)
#         return alerts.get("alerts", [])
    
#     def list_system_logs(self):
#         """
#         List the system logs.
#         """
#         logs = read_json(self.logs_file)
#         return logs.get("logs", [])

#-----------------------------------------------------------------------

import json
import os
from configs.settings import Config

class AlertService:
    def __init__(self):
        self.alerts_file = os.path.join(Config.BASE_DIR, "Core", "data", "alerts.json")

    def _read_alerts(self):
        """Charge les alertes depuis le fichier JSON"""
        try:
            with open(self.alerts_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"files": [], "folders": [], "ips": []}

    def _write_alerts(self, alerts):
        """Écrit les alertes dans le fichier JSON"""
        with open(self.alerts_file, "w") as f:
            json.dump(alerts, f, indent=4)

    def get_all_alerts(self):
        """Récupère toutes les alertes"""
        return self._read_alerts()

    def get_alerts_by_category(self, category):
        """Récupère les alertes d’une catégorie spécifique"""
        alerts = self._read_alerts()
        return alerts.get(category, None)

    def get_alerts_by_multiple_categories(self, categories):
        """Récupère les alertes de plusieurs catégories"""
        alerts = self._read_alerts()
        filtered_alerts = {cat: alerts[cat] for cat in categories if cat in alerts}
        return filtered_alerts

    def clear_all_alerts(self):
        """Efface toutes les alertes"""
        self._write_alerts({"files": [], "folders": [], "ips": []})

    def clear_alerts_by_category(self, category):
        """Efface les alertes d’une catégorie"""
        alerts = self._read_alerts()
        if category not in alerts:
            return False
        alerts[category] = []
        self._write_alerts(alerts)
        return True

    def remove_alerts_group(self, category, messages):
        """Supprime un groupe d’alertes spécifique"""
        alerts = self._read_alerts()
        if category not in alerts:
            return False
        alerts[category] = [alert for alert in alerts[category] if alert['message'] not in messages]
        self._write_alerts(alerts)
        return True
