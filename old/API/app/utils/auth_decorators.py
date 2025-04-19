# # API/app/utils/auth_decorators.py

# from flask import request, jsonify
# from functools import wraps
# from app import auth_service # Importation de l'instance du service d'authentification

# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = request.headers.get("Authorization")
#         if not token:
#             return jsonify({"message": "Token is missing"}), 401
#         try:
#             username = auth_service.decode_token(token)
#             if not username:
#                 return jsonify({"message": "Invalid token"}), 401
            
#             # Stocker le nom d'utilisateur authentifié dans l'objet request
#             request.username = username
#         except Exception as e:
#             return jsonify({"message": "Invalid token"}), 401
#         return f(*args, **kwargs)
#     return decorated

# API/app/utils/auth_decorators.py

from flask import request, jsonify
from functools import wraps
from app import auth_service  # Importation de l'instance du service d'authentification

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            username = auth_service.decode_token(token)
            if not username:
                return jsonify({"message": "Invalid token"}), 401
            request.username = username
        except Exception as e:
            return jsonify({"message": f"An error occurred: {str(e)}"}), 401
        return f(*args, **kwargs)
    return decorated