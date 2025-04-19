# # API/app/services/auth_service.py

# import json
# import os
# import bcrypt
# import jwt
# from datetime import datetime, timedelta
# from app.models.user import User

# class AuthService:
#     def __init__(self, users_file, secret_key):
#         self.users_file = users_file
#         self.secret_key = secret_key
#         self.load_users()

#     def load_users(self):
#         if not os.path.exists(self.users_file):
#             self.users = {}
#             self.save_users()
#         else:
#             with open(self.users_file, "r") as f:
#                 data = json.load(f)
#                 self.users = {username: User.from_dict(user_data) for username, user_data in data.items()}

#     def save_users(self):
#         with open(self.users_file, "w") as f:
#             data = {username: user.to_dict() for username, user in self.users.items()}
#             json.dump(data, f, indent=4)

#     def create_user(self, username, password):
#         if username in self.users:
#             return False, "Username already exists"
#         password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
#         self.users[username] = User(username, password_hash.decode("utf-8"))
#         self.save_users()
#         return True, None

#     def verify_password(self, username, password):
#         if username not in self.users:
#             return False
#         user = self.users[username]
#         return bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8"))

#     def generate_token(self, username):
#         payload = {
#             "exp": datetime.utcnow() + timedelta(hours=1),
#             "iat": datetime.utcnow(),
#             "sub": username
#         }
#         return jwt.encode(payload, self.secret_key, algorithm="HS256")

#     def decode_token(self, token):
#         try:
#             payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
#             return payload["sub"]
#         except jwt.ExpiredSignatureError:
#             return None
#         except jwt.InvalidTokenError:
#             return None


# API/app/services/auth_service.py

import json
import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from app.models.user import User
from app.utils.auth_utils import validate_password_complexity

class AuthService:
    def __init__(self, users_file, secret_key):
        self.users_file = users_file
        self.secret_key = secret_key
        self.load_users()

    def load_users(self):
        if not os.path.exists(self.users_file):
            self.users = {}
            self.save_users()
        else:
            with open(self.users_file, "r") as f:
                data = json.load(f)
                self.users = {username: User.from_dict(user_data) for username, user_data in data.items()}

    def save_users(self):
        with open(self.users_file, "w") as f:
            data = {username: user.to_dict() for username, user in self.users.items()}
            json.dump(data, f, indent=4)

    def create_user(self, username, password):
        if username in self.users:
            return False, "Username already exists"
        
        if not validate_password_complexity(password):
            return False, "Password does not meet security requirements (8+ chars, uppercase, lowercase, number, special character)"
    
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        self.users[username] = User(username, password_hash)
        self.save_users()
        return True, None

    def verify_password(self, username, password):
        if username not in self.users:
            return False
        user = self.users[username]
        return bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8"))

    def change_password(self, username, old_password, new_password):
        # Vérifier si l'utilisateur existe
        if username not in self.users:
            return False, "User not found"

        user = self.users[username]

        # Vérifier l'ancien mot de passe
        if not bcrypt.checkpw(old_password.encode("utf-8"), user.password_hash.encode("utf-8")):
            return False, "Incorrect old password"

        # Vérifier la complexité du nouveau mot de passe
        if not validate_password_complexity(new_password):
            return False, "New password does not meet security requirements"

        # Hasher et enregistrer le nouveau mot de passe
        new_hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        self.users[username].password_hash = new_hashed_password
        self.save_users()

        return True, "Password changed successfully"


    def generate_token(self, username):
        payload = {
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
            "sub": username
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            return None