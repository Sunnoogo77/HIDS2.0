import json
import os
from datetime import datetime
from flask import request

HISTORY_FILE = "../Core/data/history.json"

def ensure_history_file():
    """Créer le fichier history.json s'il n'existe pas"""
    if not os.path.exists(HISTORY_FILE):
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)  # Créer les dossiers manquants
        with open(HISTORY_FILE, "w") as file:
            json.dump([], file)  # Créer un fichier vide

def load_history():
    """Charge l'historique depuis history.json"""
    ensure_history_file()  # Vérifier et créer le fichier si nécessaire
    try:
        with open(HISTORY_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []

def save_history(history):
    """Sauvegarde l'historique des requêtes dans history.json"""
    ensure_history_file()  # Vérifier et créer le fichier si nécessaire
    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)

def log_request(response):
    """Enregistre une requête API dans l'historique"""
    history = load_history()
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user": getattr(request, "username", "Unknown"),  # Récupérer l'utilisateur s'il est connecté
        "method": request.method,
        "route": request.path,
        "data": request.get_json() if request.method in ["POST", "PUT"] else None,
        "response_code": response.status_code
    }

    history.append(log_entry)
    save_history(history)  # Sauvegarde avec la vérification

    return response
