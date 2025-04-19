# from flask import Blueprint, request, jsonify
# from app.services.file_service import FileService
# import json

# files_bp = Blueprint('files', __name__)

# CONFIG_FILE = "Core/data/config.json"

# #Read config file
# def load_config():
#     with open(CONFIG_FILE, "r") as file:
#         return json.load(file)
    
# #Save config file
# def save_config(data):
#     with open(CONFIG_FILE, "w") as file:
#         json.dump(data, file, indent=4)

# #Retreive all monitored files
# @files_bp.route("/", methods=["GET"])
# def get_files():
#     config = load_config()
#     return jsonify(config["files"])

# #Add a file to monitor
# @files_bp.route("/add", methods=["POST"])
# def add_file():
#     data = request.json()
#     file_path = data.get("file")
    
#     if not file_path:
#         return jsonify({"error": "Missing file parameter"}), 400
    
#     config = load_config()
#     if file_path not in config["files"]:
#         config["files"].append(file_path)
#         save_config(config)
#         return jsonify({"message": f"File {file_path} added to monitoring."}), 201
#     else:
#         return jsonify({"error": f"File {file_path} already monitored."}), 200

# #Remove a file from monitoring
# @files_bp.route("/remove", methods=["POST"])
# def remove_file():
#     data = request.json()
#     file_path = data.get("file")
    
#     if not file_path:
#         return jsonify({"error": "Missing file parameter"}), 400
    
#     config = load_config()
#     if file_path in config["files"]:
#         config["files"].remove(file_path)
#         save_config(config)
#         return jsonify({"message": f"File {file_path} removed from monitoring."}), 200
#     else:
#         return jsonify({"error": f"File {file_path} not monitored."}), 404


# #---------------------------------------------------------

# from flask import Blueprint, request, jsonify
# from app.services.file_service import FileService
# from app.utils.auth_decorators import token_required
# import os

# files_bp = Blueprint('files', __name__, url_prefix='/files')
# file_service = FileService()

# @files_bp.route('/add', methods=['POST'])
# @token_required
# def add_file():
#     data = request.get_json()
#     file_path = data.get('file_path')
#     if not file_path:
#         return jsonify({'error': 'File path is required'}), 400
#     try:
#         file_service.add_file_to_monitoring(file_path)
#         return jsonify({'message': 'File added successfully'}), 201
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400

# @files_bp.route('/remove', methods=['DELETE'])
# @token_required
# def remove_file():
#     data = request.get_json()
#     file_path = data.get('file_path')
#     if not file_path:
#         return jsonify({'error': 'File path is required'}), 400
#     try:
#         file_service.remove_file_from_monitoring(file_path)
#         return jsonify({'message': 'File removed successfully'}), 200
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400

# @files_bp.route('/list', methods=['GET'])
# @token_required
# def list_files():
#     files = file_service.list_monitored_files()
#     return jsonify({'files': files}), 200



# #---------------------------------------------------------

# API/app/routes/files.py

# from flask import Blueprint, request, jsonify
# from app.services.file_service import FileService
# from app.utils.auth_decorators import token_required
# import os

# files_bp = Blueprint('files', __name__, url_prefix='/files')
# file_service = FileService()

# @files_bp.route('/add', methods=['POST'])
# @token_required
# def add_file():
#     data = request.get_json()
#     file_path = data.get('file_path')
#     if not file_path:
#         return jsonify({'error': 'File path is required'}), 400
#     if not os.path.exists(file_path):
#         return jsonify({'error': 'File path does not exist'}), 400
#     try:
#         file_service.add_file_to_monitoring(file_path)
#         return jsonify({'message': 'File added successfully'}), 201
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @files_bp.route('/remove', methods=['DELETE'])
# @token_required
# def remove_file():
#     data = request.get_json()
#     file_path = data.get('file_path')
#     if not file_path:
#         return jsonify({'error': 'File path is required'}), 400
#     try:
#         file_service.remove_file_from_monitoring(file_path)
#         return jsonify({'message': 'File removed successfully'}), 200
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @files_bp.route('/list', methods=['GET'])
# @token_required
# def list_files():
#     try:
#         files = file_service.list_monitored_files()
#         return jsonify({'files': files}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
    
    # #---------------------------------------------------------


# #---------------------- Avant dernier *****
# from flask import Blueprint, request, jsonify
# from app.services.file_service import FileService
# from app.utils.auth_decorators import token_required
# import os

# files_bp = Blueprint('files', __name__, url_prefix='/files')
# file_service = FileService()

# @files_bp.route('/add', methods=['POST'])
# @token_required
# def add_file():
#     """Ajoute un fichier à la surveillance"""
#     data = request.get_json()
#     file_path = data.get('file_path')

#     if not file_path:
#         return jsonify({'error': 'File path is required'}), 400
#     if not os.path.exists(file_path):
#         return jsonify({'error': 'File path does not exist'}), 400
#     if file_service.is_file_monitored(file_path):
#         return jsonify({'error': 'File is already being monitored'}), 409

#     try:
#         file_service.add_file_to_monitoring(file_path)
#         return jsonify({'message': 'File added successfully'}), 201
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @files_bp.route('/remove', methods=['DELETE'])
# @token_required
# def remove_file():
#     """Supprime un fichier de la surveillance"""
#     data = request.get_json()
#     file_path = data.get('file_path')

#     if not file_path:
#         return jsonify({'error': 'File path is required'}), 400

#     file_path = file_service._normalize_path(file_path)  # 🔹 Normalisation du chemin

#     if not file_service.is_file_monitored(file_path):  # 🔹 Vérification
#         return jsonify({'error': 'File is not currently monitored'}), 404

#     try:
#         file_service.remove_file_from_monitoring(file_path)
#         return jsonify({'message': 'File removed successfully'}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# @files_bp.route('/list', methods=['GET'])
# @token_required
# def list_files():
#     """Retourne la liste des fichiers surveillés"""
#     try:
#         files = file_service.list_monitored_files()
#         return jsonify({'files': files}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @files_bp.route('/check', methods=['POST'])
# @token_required
# def check_file():
#     """Vérifie si un fichier est déjà surveillé"""
#     data = request.get_json()
#     file_path = data.get('file_path')

#     if not file_path:
#         return jsonify({'error': 'File path is required'}), 400

#     is_monitored = file_service.is_file_monitored(file_path)
#     return jsonify({'is_monitored': is_monitored}), 200

# @files_bp.route('/monitored', methods=['GET'])
# @token_required
# def list_monitored_files():
#     """Retourne la liste des fichiers réellement surveillés"""
#     monitored_files = file_service.get_active_monitored_files()
#     return jsonify({'monitored_files': monitored_files}), 200



#---------------------------------------------------

from flask import Blueprint, request, jsonify
from app.services.file_service import FileService
from app.utils.auth_decorators import token_required
import os

files_bp = Blueprint('files', __name__, url_prefix='/files')
file_service = FileService()

@files_bp.route('/add', methods=['POST'])
@token_required
def add_file():
    """Ajoute un fichier à la surveillance"""
    data = request.get_json()
    file_path = data.get('file_path')

    if not file_path:
        return jsonify({'error': 'File path is required'}), 400

    file_path = os.path.normpath(file_path)  # Normaliser le chemin pour éviter les doublons avec des formats différents

    if not os.path.exists(file_path):
        return jsonify({'error': 'File path does not exist'}), 400

    if file_service.is_file_monitored(file_path):
        return jsonify({'error': 'File is already being monitored'}), 400

    try:
        file_service.add_file_to_monitoring(file_path)
        return jsonify({'message': 'File added successfully'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/remove', methods=['DELETE'])
@token_required
def remove_file():
    """Supprime un fichier de la surveillance uniquement s'il n'est pas en cours de monitoring"""
    data = request.get_json()
    file_path = data.get('file_path')

    if not file_path:
        return jsonify({'error': 'File path is required'}), 400

    file_path = os.path.normpath(file_path)  # Normaliser le chemin

    monitored_files = file_service.get_active_monitored_files()

    if file_path in monitored_files:
        return jsonify({'error': 'Cannot remove file: It is currently being monitored'}), 403

    try:
        file_service.remove_file_from_monitoring(file_path)
        return jsonify({'message': 'File removed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/list', methods=['GET'])
@token_required
def list_files():
    """Retourne la liste des fichiers présents dans la configuration (pas forcément surveillés)"""
    try:
        files = file_service.list_configured_files()
        return jsonify({'files': files}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/monitored', methods=['GET'])
@token_required
def list_monitored_files():
    """Retourne uniquement la liste des fichiers réellement surveillés"""
    try:
        monitored_files = file_service.get_active_monitored_files()
        return jsonify({'monitored_files': monitored_files}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/check', methods=['POST'])
@token_required
def check_file_status():
    """Vérifie si un fichier est actuellement surveillé"""
    data = request.get_json()
    file_path = data.get('file_path')

    if not file_path:
        return jsonify({'error': 'File path is required'}), 400

    file_path = os.path.normpath(file_path)  # Normaliser le chemin

    is_monitored = file_service.is_file_monitored(file_path)
    return jsonify({'is_monitored': is_monitored}), 200
