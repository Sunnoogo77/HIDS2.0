# from flask import Blueprint, request, jsonify
# from app.services.email_service import EmailService

# emails_bp = Blueprint('emails', __name__, url_prefix='/emails')
# email_service = EmailService()

# @emails_bp.route('/add', methods=['POST'])
# def add_email():
#     data = request.get_json()
#     email = data.get('email')
#     if not email:
#         return jsonify({'error': 'Email is required'}), 400
#     try:
#         email_service.add_email_recipient(email)
#         return jsonify({'message': 'Recipient added successfully'}), 201
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400

# @emails_bp.route('/remove', methods=['DELETE'])
# def remove_email():
#     data = request.get_json()
#     email = data.get('email')
#     if not email:
#         return jsonify({'error': 'Email is required'}), 400
#     try:
#         email_service.remove_email_recipient(email)
#         return jsonify({'message': 'Recipient removed successfully'}), 200
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400

# @emails_bp.route('/list', methods=['GET'])
# def list_emails():
#     emails = email_service.list_email_recipients()
#     return jsonify({'emails': emails}), 200

# @emails_bp.route('/send', methods=['POST'])
# def send_email():
#     try:
#         email_service.send_test_email()
#         return jsonify({'message': 'Email sent successfully'}), 200
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400

# @emails_bp.route('/set-frequency', methods=['POST'])
# def set_frequency():
#     data = request.get_json()
#     frequency = data.get('frequency')
#     if not frequency:
#         return jsonify({'error': 'Frequency is required'}), 400
#     try:
#         email_service.set_email_frequency(frequency)
#         return jsonify({'message': 'Email frequency updated successfully'}), 200
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400



#----------------------------------------------------------------

from flask import Blueprint, request, jsonify
from app.services.email_service import EmailService
from app.utils.auth_decorators import token_required

emails_bp = Blueprint('emails', __name__, url_prefix='/emails')
email_service = EmailService()

@emails_bp.route('/add', methods=['POST'])
@token_required
def add_email():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email address is required'}), 400
    try:
        email_service.add_email(email)
        return jsonify({'message': 'Email added successfully'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@emails_bp.route('/remove', methods=['DELETE'])
@token_required
def remove_email():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email address is required'}), 400

    # 🚨 Empêcher la suppression si l'email est actif
    if email_service.is_email_active(email):
        return jsonify({'error': 'Cannot remove an active email'}), 403

    try:
        email_service.remove_email(email)
        return jsonify({'message': 'Email removed successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@emails_bp.route('/list', methods=['GET'])
@token_required
def list_emails():
    emails = email_service.list_emails()
    return jsonify(emails), 200

@emails_bp.route('/check', methods=['POST'])
@token_required
def check_email():
    """Vérifie si un email est configuré ou actif"""
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email address is required'}), 400

    is_configured = email_service.is_email_configured(email)
    is_active = email_service.is_email_active(email)

    return jsonify({
        'email': email,
        'is_configured': is_configured,
        'is_active': is_active
    }), 200
