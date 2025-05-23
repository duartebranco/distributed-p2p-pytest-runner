from flask import Blueprint, request, jsonify, current_app
from utils.zip_handler import handle_zip_upload
from utils.github_handler import handle_github_projects
from utils.pytest_runner import run_pytest_on_project

worker_bp = Blueprint('worker', __name__)

@worker_bp.route('/task', methods=['POST'])
def receive_task():
    current_app.logger.info(f"WORKER got /task payload: {request.json}")
    if "modules" in request.json:
        print(f"Vou correr os módulos: {request.json['modules']}")
        results = []
        for mod in request.json["modules"]:
            res = run_pytest_on_project(mod["project_path"], mod["module_path"])
            results.append(res)
        return jsonify(results), 200
