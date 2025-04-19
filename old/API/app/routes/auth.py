# # API/app/routes/auth.py

# from flask import Blueprint, request, jsonify
# from app.services.auth_service import AuthService
# from app import auth_service # Importation de l'instance du service d'authentification

# auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# @auth_bp.route("/register", methods=["POST"])
# def register():
#     data = request.get_json()
#     username = data.get("username")
#     password = data.get("password")
#     if not username or not password:
#         return jsonify({"message": "Username and password are required"}), 400
#     success, message = auth_service.create_user(username, password)
#     if success:
#         return jsonify({"message": "User created successfully"}), 201
#     else:
#         return jsonify({"message": message}), 400

# @auth_bp.route("/login", methods=["POST"])
# def login():
#     data = request.get_json()
#     username = data.get("username")
#     password = data.get("password")
#     if not username or not password:
#         return jsonify({"message": "Username and password are required"}), 400
#     if auth_service.verify_password(username, password):
#         token = auth_service.generate_token(username)
#         return jsonify({"token": token}), 200
#     else:
#         return jsonify({"message": "Invalid username or password"}), 401
# API/app/routes/auth.py

from flask import Blueprint, request, jsonify
from app.utils.auth_decorators import token_required
from app.services.auth_service import AuthService
from app import auth_service  # Importation de l'instance du service d'authentification

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400
    success, message = auth_service.create_user(username, password)
    try:
        if success:
            return jsonify({"message": "User created successfully"}), 201
        else:
            return jsonify({"message": message}), 400
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400
    try:
        if auth_service.verify_password(username, password):
            token = auth_service.generate_token(username)
            return jsonify({"token": token}), 200
        else:
            return jsonify({"message": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout():
    try:
        # Implémenter la révocation du jeton ici (par exemple, ajouter le jeton à une liste noire)
        return jsonify({"message": "Logout successful"}), 200
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@auth_bp.route("/change-password", methods=["POST"])
@token_required
def change_password():
    data = request.get_json()
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not old_password or not new_password:
        return jsonify({"message": "Old and new password are required"}), 400

    success, message = auth_service.change_password(request.username, old_password, new_password)

    if success:
        return jsonify({"message": "Password changed successfully. Please log in again."}), 200
    else:
        return jsonify({"message": message}), 400
