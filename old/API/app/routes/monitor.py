# # from flask import Blueprint, request, jsonify
# # from app.services.monitor_service import MonitorService

# # monitor_bp = Blueprint('monitor', __name__, url_prefix='/monitor')
# # monitor_service = MonitorService()

# # @monitor_bp.route('/start', methods=['POST'])
# # def start_monitor():
# #     """Lance les types de monitoring spécifiés."""
# #     data = request.get_json()
# #     monitor_types = data.get('monitor_types')
# #     if not monitor_types or not isinstance(monitor_types, list):
# #         return jsonify({'error': 'Monitor types list is required'}), 400
# #     results = monitor_service.start_monitoring(monitor_types)
# #     return jsonify(results), 200

# # @monitor_bp.route('/stop', methods=['POST'])
# # def stop_monitor():
# #     """Arrête un type de monitoring."""
# #     data = request.get_json()
# #     monitor_type = data.get('monitor_type')
# #     if not monitor_type:
# #         return jsonify({'error': 'Monitor type is required'}), 400
# #     try:
# #         output = monitor_service.stop_monitoring(monitor_type)
# #         return jsonify({'message': 'Monitoring stopped successfully', 'output': output}), 200
# #     except ValueError as e:
# #         return jsonify({'error': str(e)}), 400

# #monitor.py
# from flask import Blueprint, request, jsonify
# from app.services.monitor_service import MonitorService
# from app.utils.auth_decorators import token_required
# # from quart import Blueprint, request, jsonify
# # from app.services.monitor_service import MonitorService

# monitor_bp = Blueprint('monitor', __name__, url_prefix='/monitor')
# monitor_service = MonitorService()

# @monitor_bp.route('/start', methods=['POST'])
# @token_required
# async def start_monitor():
#     """Starts the specified types of monitoring asynchronously."""
    
#     data = await request.get_json()
#     monitor_types = data.get('monitor_types')
#     if not monitor_types or not isinstance(monitor_types, list):
#         return jsonify({'error': 'Monitor types list is required'}), 400
#     results = await monitor_service.start_monitoring(monitor_types)
#     return jsonify({"results": results}), 200

# @monitor_bp.route('/stop', methods=['POST'])
# @token_required
# async def stop_monitor():
#     """Stops a type of monitoring."""
    
#     data = await request.get_json()
#     monitor_type = data.get('monitor_type')
#     if not monitor_type:
#         return jsonify({'error': 'Monitor type is required'}), 400
#     try:
#         output = await monitor_service.stop_monitoring(monitor_type)
#         return jsonify({'message': 'Monitoring stopped successfully', 'output': output}), 200
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400

#-----------------------------------------

# from flask import Blueprint, request, jsonify
# from app.services.monitor_service import MonitorService
# from app.utils.auth_decorators import token_required

# monitor_bp = Blueprint('monitor', __name__, url_prefix='/monitor')
# monitor_service = MonitorService()

# @monitor_bp.route('/start', methods=['POST'])
# @token_required
# async def start_monitor():
#     """Starts the specified types of monitoring asynchronously."""
#     data = await request.get_json()
#     monitor_types = data.get('monitor_types')
#     if not monitor_types or not isinstance(monitor_types, list):
#         return jsonify({'error': 'Monitor types list is required'}), 400
#     try:
#         results = await monitor_service.start_monitoring(monitor_types)
#         return jsonify({"results": results}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @monitor_bp.route('/stop', methods=['POST'])
# @token_required
# async def stop_monitor():
#     """Stops a type of monitoring."""
#     data = await request.get_json()
#     monitor_type = data.get('monitor_type')
#     if not monitor_type:
#         return jsonify({'error': 'Monitor type is required'}), 400
#     try:
#         output = await monitor_service.stop_monitoring(monitor_type)
#         return jsonify({'message': 'Monitoring stopped successfully', 'output': output}), 200
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


#--------------------------------------
import os
import subprocess
import signal
import json
from flask import Blueprint, jsonify, request
from app.utils.auth_decorators import token_required
from configs.settings import Config

monitor_bp = Blueprint('monitor', __name__, url_prefix='/monitor')

STATUS_FILE = os.path.join(Config.BASE_DIR, "Core", "data", "status.json")
SCRIPTS_DIR = os.path.join(Config.BASE_DIR, "Core", "scripts")

# Liste des scripts disponibles
SCRIPTS = {
    "monitor_files": "monitor_files.ps1",
    "monitor_folders": "monitor_folders.ps1",
    "monitor_ips": "monitor_ips.ps1",
    "alerts": "alerts.ps1",
    "send_alert_now": "send_alert_now.ps1"
}

def read_status():
    """Lit le fichier status.json et retourne son contenu"""
    try:
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def is_running(script_key):
    """Vérifie si un script est en cours d'exécution en consultant status.json"""
    status = read_status()
    return status.get(script_key, {}).get("Status") == "Running"

def get_pid(script_key):
    """Récupère le PID d’un script s’il est en cours d’exécution"""
    status = read_status()
    return status.get(script_key, {}).get("PID")

# @monitor_bp.route('/start/<script_key>', methods=['POST'])
# @token_required
# def start_script(script_key):
#     """Démarrer un script PowerShell"""
#     if script_key not in SCRIPTS:
#         return jsonify({'error': 'Invalid script name'}), 400

#     if is_running(script_key):
#         return jsonify({'error': f'{script_key} is already running'}), 400

#     script_path = os.path.join(SCRIPTS_DIR, SCRIPTS[script_key])

#     try:
#         process = subprocess.Popen(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path],
#                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         return jsonify({'message': f'{script_key} started successfully', 'PID': process.pid}), 200

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

@monitor_bp.route('/start/<script_key>', methods=['POST'])
@token_required
def start_script(script_key):
    if script_key not in SCRIPTS:
        return jsonify({'error': 'Invalid script name'}), 400

    if is_running(script_key):
        return jsonify({'error': f'{script_key} is already running'}), 400

    script_path = os.path.join(SCRIPTS_DIR, SCRIPTS[script_key])
    
    # Définir le répertoire de travail comme le dossier des scripts PowerShell
    working_dir = os.path.join(Config.BASE_DIR, "Core", "scripts")

    try:
        process = subprocess.Popen(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path],
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            cwd=working_dir  # <-- Clé : exécuter depuis le bon dossier
        )
        return jsonify({'message': f'{script_key} started', 'PID': process.pid}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@monitor_bp.route('/stop/<script_key>', methods=['POST'])
@token_required
def stop_script(script_key):
    """Arrêter un script en fonction de son PID"""
    if not is_running(script_key):
        return jsonify({'error': f'{script_key} is not running'}), 400

    pid = get_pid(script_key)
    if not pid:
        return jsonify({'error': 'Could not retrieve process ID'}), 500

    try:
        os.kill(pid, signal.SIGTERM)  # Tuer le process
        return jsonify({'message': f'{script_key} stopped successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
