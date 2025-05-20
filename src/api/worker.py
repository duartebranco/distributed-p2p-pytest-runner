from flask import Blueprint, request, jsonify, current_app
from utils.zip_handler import handle_zip_upload
from utils.github_handler import handle_github_projects
from utils.pytest_runner import run_pytest_on_project

worker_bp = Blueprint('worker', __name__)

@worker_bp.route('/task', methods=['POST'])
def receive_task():
    current_app.logger.info(f"WORKER got /task payload: {request.json}")
    paths   = handle_github_projects(request.json["projects"], request.json.get("auth_token"))
    results = [run_pytest_on_project(p) for p in paths]
    return jsonify(results), 200