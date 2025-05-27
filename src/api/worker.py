from flask import Blueprint, request, jsonify, current_app
from utils.zip_handler import handle_zip_upload
import base64
import os
import tempfile
from utils.zip_handler import extract_zip
from utils.pytest_runner import run_pytest_on_project

worker_bp = Blueprint('worker', __name__)

@worker_bp.route('/task', methods=['POST'])
def receive_task():
    if "modules" in request.json:
        print("Vou correr os módulos:")
        for mod in request.json["modules"]:
            print(f"  - module_path: {mod.get('module_path')}, project_path: {mod.get('project_path')}")
        results = []
        for mod in request.json["modules"]:
            project_zip = mod.get("project_zip")
            project_id = mod.get("project_id")
            if project_zip:
                temp_dir = tempfile.mkdtemp()
                zip_path = os.path.join(temp_dir, "project.zip")
                with open(zip_path, "wb") as f:
                    f.write(base64.b64decode(project_zip))
                extract_zip(zip_path, temp_dir)
                project_path = temp_dir
            else:
                project_path = mod["project_path"]
            # Reconstrói o caminho absoluto do módulo
            module_rel_path = mod["module_path"]
            module_abs_path = os.path.join(project_path, module_rel_path)
            res = run_pytest_on_project(project_path, module_abs_path)
            res["project_id"] = project_id
            results.append(res)
        return jsonify(results), 200