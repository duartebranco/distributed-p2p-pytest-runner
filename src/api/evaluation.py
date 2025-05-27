from flask import Blueprint, request, jsonify, current_app
import uuid
from utils.zip_handler    import handle_zip_upload
from utils.github_handler import handle_github_projects
from core.task_manager    import TaskManager
from utils.pytest_runner  import run_pytest_on_project
import math
import requests
import os
import time
from utils.zip_handler import zip_project_folder
from utils.pytest_runner  import find_test_modules

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

    # GitHub list
    elif request.is_json:
        data          = request.get_json()
        auth_token    = data.get("auth_token")
        projects      = data.get("projects", [])
        evaluation_id = str(uuid.uuid4())
        task_manager.start_times[evaluation_id] = time.time()

        nodes = list(current_app.p2p.get_network_info().keys())
        if nodes:
            # 1. Clona os projetos localmente para identificar módulos
            cloned_paths = handle_github_projects(projects, auth_token)
            all_modules = []
            for proj_path in cloned_paths:
                project_id = os.path.basename(proj_path)  # Nome da pasta do projeto
                modules = find_test_modules(proj_path)
                all_modules.extend([
                    (proj_path, os.path.relpath(m, proj_path), project_id) for m in modules
                ])

            # 2. Divide os módulos pelos nós
            num_nodes = len(nodes)
            chunk_size = math.ceil(len(all_modules) / num_nodes)
            module_chunks = [all_modules[i:i+chunk_size] for i in range(0, len(all_modules), chunk_size)]

            all_results = []
            for idx, node in enumerate(nodes):
                chunk = module_chunks[idx] if idx < len(module_chunks) else []
                print(f"[DEBUG][EVAL] Vou tentar enviar chunk {idx} para {node} ({len(chunk)} módulos)")
                modules_payload = []
                for p, m, project_id in chunk:
                    zipped = zip_project_folder(p)
                    modules_payload.append({
                        "project_path": p,
                        "module_path": m,
                        "project_zip": zipped,
                        "project_id": project_id
                    })
                payload = {
                    "auth_token": auth_token,
                    "modules": modules_payload
                }
                res = current_app.p2p.send_task(node, payload)
                print(f"[DEBUG][EVAL] Resultado de {node}: {res}")
                if res:
                    all_results.extend(res)

            task_manager.add_multiple_results(evaluation_id, all_results)
            task_manager.add_task(evaluation_id, [m[1] for m in all_modules])

            elapsed = round(time.time() - task_manager.start_times[evaluation_id], 2)
            print(f"[DEBUG][EVAL] Syncing elapsed_seconds={elapsed} to other nodes")
            for node in nodes:
                if node != current_app.p2p.node_address:
                    try:
                        requests.post(
                            f"http://{node}/evaluation/sync_result/{evaluation_id}",
                            json={"results": all_results, "elapsed_seconds": elapsed},
                            timeout=5
                        )
                    except Exception as e:
                        print(f"[WARN] Falha ao sincronizar resultado com {node}: {e}")
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
    return jsonify({"evaluations": task_manager.get_all_evaluation_ids()}), 200

@evaluation_bp.route('<id>', methods=['GET'])
def get_evaluation_status(id):
    status = task_manager.get_evaluation_status(id)
    return (jsonify(status), 200) if status else (jsonify({"error": "not found"}), 404)

# used internally by nodes, not meant to be used by the client
@evaluation_bp.route('/sync_result/<id>', methods=['POST'])
def sync_result(id):
    data = request.get_json()
    task_manager.add_multiple_results(id, data.get("results", []))
    if "elapsed_seconds" in data:
        task_manager.set_elapsed_seconds(id, data["elapsed_seconds"])
    return jsonify({"status": "ok"}), 200