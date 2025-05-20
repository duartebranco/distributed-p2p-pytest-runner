from flask import Blueprint, request, jsonify, current_app
import uuid
from utils.zip_handler    import handle_zip_upload
from utils.github_handler import handle_github_projects
from core.task_manager    import TaskManager
from utils.pytest_runner  import run_pytest_on_project

evaluation_bp = Blueprint('evaluation', __name__)
task_manager   = TaskManager()

@evaluation_bp.route('', methods=['POST'])
def evaluation():
    # ZIP‐file path (local only)
    if 'file' in request.files:
        zip_file      = request.files['file']
        evaluation_id = str(uuid.uuid4())
        extracted     = handle_zip_upload(zip_file)
        task_manager.add_task(evaluation_id, extracted)
        result = run_pytest_on_project(extracted)
        task_manager.add_result(evaluation_id, result)
        return jsonify({"id": evaluation_id}), 201

    # GitHub list (P2P or local)
    elif request.is_json:
        data          = request.get_json()
        auth_token    = data.get("auth_token")
        projects      = data.get("projects", [])
        evaluation_id = str(uuid.uuid4())

        # if peers exist, broadcast and aggregate
        nodes = list(current_app.p2p.get_network_info().keys())
        if nodes:
            task_manager.add_task(evaluation_id, projects)
            payload = {"auth_token": auth_token, "projects": projects}
            all_results = []
            for node in nodes:
                res = current_app.p2p.send_task(node, payload)
                if res:
                    all_results.extend(res)
            task_manager.add_multiple_results(evaluation_id, all_results)
            return jsonify({"id": evaluation_id}), 201

        # fallback: local run
        cloned_paths = handle_github_projects(projects, auth_token)
        task_manager.add_task(evaluation_id, cloned_paths)
        all_results = [run_pytest_on_project(p) for p in cloned_paths]
        task_manager.add_multiple_results(evaluation_id, all_results)
        return jsonify({"id": evaluation_id}), 201

    return jsonify({"error": "Invalid request"}), 400

@evaluation_bp.route('', methods=['GET'])
def list_evaluations():
    return jsonify({"evaluations": task_manager.get_all_evaluation()}), 200

@evaluation_bp.route('<id>', methods=['GET'])
def get_evaluation_status(id):
    status = task_manager.get_evaluation_status(id)
    return (jsonify(status), 200) if status else (jsonify({"error": "not found"}), 404)