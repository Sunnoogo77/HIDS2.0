from flask import Flask, request
from configs.settings import config
from flask_cors import CORS
from app.services.auth_service import AuthService
from app.utils.history_utils import log_request


def create_app(config_name="development"):
    app = Flask(__name__)
    CORS(app)
    
    # Configuration de l'application
    app.config.from_object(config[config_name])

    # Initialisation du service d'authentification
    global auth_service
    auth_service = AuthService(app.config["USERS_FILE"], app.config["SECRET_KEY"])

    
    #Importer les routes API
    from app.routes.files import files_bp
    from app.routes.folders import folders_bp
    from app.routes.ips import ips_bp
    from app.routes.alerts import alerts_bp
    from app.routes.emails import emails_bp
    from app.routes.monitor import monitor_bp
    from app.routes.status import status_bp
    from app.routes.config import config_bp
    from app.routes.auth import auth_bp
    
    
    #Save blueprints
    app.register_blueprint(files_bp, url_prefix="/api/files")
    app.register_blueprint(folders_bp, url_prefix="/api/folders")
    app.register_blueprint(ips_bp, url_prefix="/api/ips")
    app.register_blueprint(alerts_bp, url_prefix="/api/alerts")
    app.register_blueprint(emails_bp, url_prefix="/api/emails")
    app.register_blueprint(monitor_bp, url_prefix="/api/monitor")
    app.register_blueprint(status_bp, url_prefix="/api/status") 
    app.register_blueprint(config_bp, url_prefix="/api/config")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    
    @app.after_request
    def after_request(response):
        return log_request(response)

    return app