from flask import Blueprint, request, jsonify
from app.services.config_service import ConfigService
from app.utils.auth_decorators import token_required

config_bp = Blueprint('config', __name__, url_prefix='/config')
config_service = ConfigService()

@config_bp.route('/get', methods=['GET'])
@token_required
def get_config():
    """Récupère toute la configuration"""
    config = config_service.get_config()
    return jsonify(config), 200

@config_bp.route('/update', methods=['PUT'])
@token_required
def update_config():
    """
    Met à jour les intervalles (scan et emails)
    - Peut modifier uniquement le scan, uniquement l'email, ou les deux
    """
    data = request.get_json()
    scan_interval = data.get("scan_interval")
    email_interval = data.get("email_interval")

    if scan_interval is None and email_interval is None:
        return jsonify({'error': 'At least one interval (scan_interval or email_interval) is required'}), 400

    try:
        config_service.update_intervals(scan_interval, email_interval)
        return jsonify({'message': 'Configuration updated successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
