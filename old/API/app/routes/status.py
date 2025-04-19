# from flask import Blueprint, jsonify
# import psutil

# status_bp = Blueprint('status', __name__)

# #Verify if the script is running
# def is_script_running(script_name):
#     for process in psutil.process_iter():
#         try:
#             if script_name in " ".join(process.info["cmdline"]):
#                 return True
#         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#             continue
#     return False

# #Check the general status of the monitoring
# @status_bp.route("/", methods=["GET"])
# def get_status():
#     status = {
#         "files_monitoring": is_script_running("monitor_files.ps1"),
#         "folders_monitoring": is_script_running("monitor_folders.ps1"),
#         "ips_monitoring": is_script_running("monitor_ips.ps1"),
#         "email_sending": is_script_running("send_email.ps1")
#     }
#     return jsonify(status)

# API/app/routes/status.py

from flask import Blueprint, jsonify
from app.services.status_service import StatusService
from app.utils.auth_decorators import token_required

status_bp = Blueprint('status', __name__)
status_service = StatusService()


@status_bp.route("/", methods=["GET"])
@token_required
def get_all_status():
    status, code = status_service.get_all_scripts_status()
    return jsonify(status), code
    
@status_bp.route("/<script_name>", methods=["GET"])
@token_required
def get_status(script_name):
    status, code = status_service.get_script_status(script_name)
    return jsonify(status), code