# from flask import Blueprint, request, jsonify
# import json

# folders_bp = Blueprint('folders', __name__)

# CONFIG_FILE = "Core/data/config.json"

# #Read config file
# def load_config():
#     with open(CONFIG_FILE, "r") as file:
#         return json.load(file)

# #Save config file
# def save_config(data):
#     with open(CONFIG_FILE, "w") as file:
#         json.dump(data, file, indent=4)

# #Retreive all monitored folders
# @folders_bp.route("/", methods=["GET"])
# def get_folders():
#     config = load_config()
#     return jsonify(config.get("folders", []))

# #Add a folder to monitor
# @folders_bp.route("/add", methods=["POST"])
# def add_folder():
#     data = request.json
#     folder_path = data.get("folder")

#     if not folder_path:
#         return jsonify({"error": "Missing folder parameter"}), 400

#     config = load_config()
#     if folder_path not in config["folders"]:
#         config["folders"].append(folder_path)
#         save_config(config)
#         return jsonify({"message": f"Folder {folder_path} added to monitoring."}), 201
#     else:
#         return jsonify({"error": f"Folder {folder_path} already monitored."}), 200

# #Remove a folder from monitoring
# @folders_bp.route("/remove", methods=["POST"])
# def remove_folder():
#     data = request.json
#     folder_path = data.get("folder")

#     if not folder_path:
#         return jsonify({"error": "Missing folder parameter"}), 400

#     config = load_config()
#     if folder_path in config["folders"]:
#         config["folders"].remove(folder_path)
#         save_config(config)
#         return jsonify({"message": f"Folder {folder_path} removed from monitoring."}), 200
#     else:
#         return jsonify({"error": f"Folder {folder_path} not monitored."}), 404

#*--*-*-********************************************

# from flask import Blueprint, request, jsonify
# from app.services.folder_service import FolderService
# from app.utils.auth_decorators import token_required
# import os

# folders_bp = Blueprint('folders', __name__, url_prefix='/folders')
# folder_service = FolderService()

# @folders_bp.route('/add', methods=['POST'])
# @token_required
# def add_folder():
#     data = request.get_json()
#     folder_path = data.get('folder_path')
#     if not folder_path:
#         return jsonify({'error': 'Folder path is required'}), 400
#     try:
#         folder_service.add_folder_to_monitoring(folder_path)
#         return jsonify({'message': 'Folder added successfully'}), 201
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400

# @folders_bp.route('/remove', methods=['DELETE'])
# @token_required
# def remove_folder():
#     data = request.get_json()
#     folder_path = data.get('folder_path')
#     if not folder_path:
#         return jsonify({'error': 'Folder path is required'}), 400
#     try:
#         folder_service.remove_folder_from_monitoring(folder_path)
#         return jsonify({'message': 'Folder removed successfully'}), 200
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400

# @folders_bp.route('/list', methods=['GET'])
# @token_required
# def list_folders():
#     folders = folder_service.list_monitored_folders()
#     return jsonify({'folders': folders}), 200



from flask import Blueprint, request, jsonify
from app.services.folder_service import FolderService
from app.utils.auth_decorators import token_required
import os

folders_bp = Blueprint('folders', __name__, url_prefix='/folders')
folder_service = FolderService()

@folders_bp.route('/add', methods=['POST'])
@token_required
def add_folder():
    """Ajoute un dossier à la surveillance"""
    data = request.get_json()
    folder_path = data.get('folder_path')

    if not folder_path:
        return jsonify({'error': 'Folder path is required'}), 400

    folder_path = os.path.normpath(folder_path)  # Normaliser le chemin

    if not os.path.exists(folder_path):
        return jsonify({'error': 'Folder path does not exist'}), 400

    if folder_service.is_folder_monitored(folder_path):
        return jsonify({'error': 'Folder is already being monitored'}), 400

    try:
        folder_service.add_folder_to_monitoring(folder_path)
        return jsonify({'message': 'Folder added successfully'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@folders_bp.route('/remove', methods=['DELETE'])
@token_required
def remove_folder():
    """Supprime un dossier de la surveillance uniquement s'il n'est pas en cours de monitoring"""
    data = request.get_json()
    folder_path = data.get('folder_path')

    if not folder_path:
        return jsonify({'error': 'Folder path is required'}), 400

    folder_path = os.path.normpath(folder_path)  # Normaliser le chemin

    monitored_folders = folder_service.get_active_monitored_folders()

    if folder_path in monitored_folders:
        return jsonify({'error': 'Cannot remove folder: It is currently being monitored'}), 403

    try:
        folder_service.remove_folder_from_monitoring(folder_path)
        return jsonify({'message': 'Folder removed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@folders_bp.route('/list', methods=['GET'])
@token_required
def list_folders():
    """Retourne la liste des dossiers présents dans la configuration (pas forcément surveillés)"""
    try:
        folders = folder_service.list_configured_folders()
        return jsonify({'folders': folders}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@folders_bp.route('/monitored', methods=['GET'])
@token_required
def list_monitored_folders():
    """Retourne uniquement la liste des dossiers réellement surveillés"""
    try:
        monitored_folders = folder_service.get_active_monitored_folders()
        return jsonify({'monitored_folders': monitored_folders}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@folders_bp.route('/check', methods=['POST'])
@token_required
def check_folder_status():
    """Vérifie si un dossier est actuellement surveillé"""
    data = request.get_json()
    folder_path = data.get('folder_path')

    if not folder_path:
        return jsonify({'error': 'Folder path is required'}), 400

    folder_path = os.path.normpath(folder_path)  # Normaliser le chemin

    is_monitored = folder_service.is_folder_monitored(folder_path)
    return jsonify({'is_monitored': is_monitored}), 200

