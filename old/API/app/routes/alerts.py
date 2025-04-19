# from flask import Blueprint, request, jsonify
# import json

# alerts_bp = Blueprint('alerts', __name__)

# ALERT_FILE = "Core/data/alerts.json"

# #Read alerts 
# def load_alerts():
#     if not(ALERT_FILE and isinstance(ALERT_FILE, str)):
#         return {"file":[], "folders":[], "ips":[]}
#     try:
#         with open(ALERT_FILE, "r") as file:
#             return json.load(file)
#     except(FileNotFoundError, json.JSONDecodeError):
#         return {"file":[], "folders":[], "ips":[]}

# #Save alerts
# def save_alerts(data):
#     with open(ALERT_FILE, "w") as file:
#         json.dump(data, file, indent=4)

# #Retreive all alerts
# @alerts_bp.route("/", methods=["GET"])
# def get_alerts():
#     alerts = load_alerts()
#     return jsonify(alerts)

# #Clear all alerts
# @alerts_bp.route("/clear", methods=["POST"])
# def clear_alerts():
#     save_alerts({"file":[], "folders":[], "ips":[]})
#     return jsonify({"message": "Alerts cleared."}), 200

#--------------------------------------------------------

# from flask import Blueprint, jsonify
# from app.services.alert_service import AlertService

# alerts_bp = Blueprint('alerts', __name__, url_prefix='/alerts')
# alert_service = AlertService()

# @alerts_bp.route('/list', methods=['GET'])
# def list_alerts():
#     alerts = alert_service.list_recent_alerts()
#     return jsonify({'alerts': alerts}), 200

# @alerts_bp.route('/logs/list', methods=['GET'])
# def list_logs():
#     logs = alert_service.list_system_logs()
#     return jsonify({'logs': logs}), 200


#--------------------------------------------------

from flask import Blueprint, request, jsonify
from app.services.alert_service import AlertService
from app.utils.auth_decorators import token_required

alerts_bp = Blueprint('alerts', __name__, url_prefix='/alerts')
alert_service = AlertService()

@alerts_bp.route('/', methods=['GET'])
@token_required
def get_all_alerts():
    """Récupère toutes les alertes"""
    alerts = alert_service.get_all_alerts()
    return jsonify(alerts), 200

@alerts_bp.route('/<category>', methods=['GET'])
@token_required
def get_alerts_by_category(category):
    """Récupère les alertes d’une catégorie spécifique"""
    alerts = alert_service.get_alerts_by_category(category)
    if alerts is None:
        return jsonify({'error': 'Category not found'}), 404
    return jsonify(alerts), 200

@alerts_bp.route('/multiple', methods=['GET'])
@token_required
def get_alerts_by_multiple_categories():
    """Récupère les alertes de plusieurs catégories"""
    categories = request.args.get('categories')
    if not categories:
        return jsonify({'error': 'Categories parameter is required'}), 400
    categories = categories.split(',')
    alerts = alert_service.get_alerts_by_multiple_categories(categories)
    return jsonify(alerts), 200

@alerts_bp.route('/clear', methods=['DELETE'])
@token_required
def clear_all_alerts():
    """Supprime toutes les alertes"""
    alert_service.clear_all_alerts()
    return jsonify({'message': 'All alerts cleared'}), 200

@alerts_bp.route('/clear/<category>', methods=['DELETE'])
@token_required
def clear_alerts_by_category(category):
    """Supprime toutes les alertes d’une catégorie spécifique"""
    success = alert_service.clear_alerts_by_category(category)
    if not success:
        return jsonify({'error': 'Category not found'}), 404
    return jsonify({'message': f'Alerts for {category} cleared'}), 200

@alerts_bp.route('/remove_group', methods=['DELETE'])
@token_required
def remove_alerts_group():
    """Supprime un groupe d’alertes en fonction de critères"""
    data = request.get_json()
    if not data or 'category' not in data or 'messages' not in data:
        return jsonify({'error': 'Category and messages are required'}), 400
    
    success = alert_service.remove_alerts_group(data['category'], data['messages'])
    if not success:
        return jsonify({'error': 'Category not found or messages not found'}), 404
    return jsonify({'message': 'Selected alerts removed successfully'}), 200
