from flask import Blueprint, request, jsonify
import uuid
import os
from utils.zip_handler import handle_zip_upload
from utils.github_handler import handle_github_projects
from core.task_manager import TaskManager

evaluation_bp = Blueprint('evaluation', __name__)
task_manager = TaskManager()

@evaluation_bp.route('/evaluation', methods=['POST'])
def evaluation():
    if 'file' in request.files:
        zip_file = request.files['file']
        evaluation_id = str(uuid.uuid4())
        extracted_path = handle_zip_upload(zip_file)
        task_manager.add_task(evaluation_id, extracted_path)
        return jsonify({"id": evaluation_id}), 201

    elif request.is_json:
        data = request.get_json()
        auth_token = data.get("auth_token")
        projects = data.get("projects")
        evaluation_id = str(uuid.uuid4())
        handle_github_projects(projects, auth_token, evaluation_id)
        task_manager.add_task(evaluation_id)
        return jsonify({"id": evaluation_id}), 201

    return jsonify({"error": "Invalid request"}), 400

@evaluation_bp.route('/evaluation', methods=['GET'])
def list_evaluations():
    evaluations = task_manager.get_all_evaluations()
    return jsonify({"evaluations": evaluations}), 200

@evaluation_bp.route('/evaluation/<id>', methods=['GET'])
def get_evaluation_status(id):
    status = task_manager.get_evaluation_status(id)
    if status:
        return jsonify(status), 200
    return jsonify({"error": "Evaluation not found"}), 404