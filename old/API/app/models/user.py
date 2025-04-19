# API/app/models/user.py

class User:
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

    def to_dict(self):
        return {
            "username": self.username,
            "password_hash": self.password_hash
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["username"], data["password_hash"])