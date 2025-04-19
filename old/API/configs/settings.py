import os

class Config:
    DEBUG = True
    SECRET_KEY = "My058Sc@Ckey"
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    USERS_FILE = os.path.join(BASE_DIR, "Core", "data", "users.json")
    
class DevelopmentConfig(Config):
    ENV = "development"
    
config = {
    "development": DevelopmentConfig
}
