from flask import Blueprint, request, jsonify, current_app
import uuid
from utils.zip_handler    import handle_zip_upload
from utils.github_handler import handle_github_projects
from core.task_manager    import TaskManager
from utils.pytest_runner  import run_pytest_on_project, find_projects
import math
import requests
import os
import time
from random import shuffle
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

        projects = find_projects(extracted)
        
        all_results = [run_pytest_on_project(p) for p in projects]

        task_manager.add_multiple_results(evaluation_id, all_results)

        return jsonify({"id": evaluation_id}), 201

    # GitHub list
    elif request.is_json:
        data          = request.get_json()
        auth_token    = data.get("auth_token")
        projects      = data.get("projects", [])
        evaluation_id = str(uuid.uuid4())

        nodes = list(current_app.p2p.get_network_info().keys())
        if nodes:
            cloned = handle_github_projects(projects, auth_token)
            all_mods = []
            for p in cloned:
                pid = os.path.basename(p)
                for m in find_test_modules(p):
                    all_mods.append((p, os.path.relpath(m, p), pid))

            # split into per-node chunks
            size   = math.ceil(len(all_mods) / len(nodes))
            chunks = [all_mods[i:i+size] for i in range(0, len(all_mods), size)]

            # record dispatch start time just before first POST /task
            t0 = time.time()

            # PHASE 1: fire‐and‐forget send + ACK
            for idx, node in enumerate(nodes):
                chunk = chunks[idx] if idx < len(chunks) else []
                payload = {
                    "evaluation_id": evaluation_id,
                    "auth_token":    auth_token,
                    "modules": [
                        {
                            "project_path": p,
                            "module_path":  m,
                            "project_zip":  zip_project_folder(p),
                            "project_id":   pid
                        }
                        for p, m, pid in chunk
                    ]
                }
                ack = current_app.p2p.send_task(node, payload)
                print(f"[DEBUG][EVAL] ACK from {node}: {ack}")

            # PHASE 2: iterative collect (blocks only here)
            shuffle(nodes)
            all_results = []
            for node in nodes:
                print(f"[DEBUG][EVAL] fetching results from {node}")
                res = current_app.p2p.get_results(node, evaluation_id)
                if res:
                    all_results.extend(res)

            # aggregate
            task_manager.add_multiple_results(evaluation_id, all_results)

            # compute real elapsed
            elapsed = round(time.time() - t0, 2)
            task_manager.set_elapsed_seconds(evaluation_id, elapsed)

            # sync elapsed+results to peers
            for node in nodes:
                if node != current_app.p2p.node_address:
                    try:
                        requests.post(
                            f"http://{node}/evaluation/sync_result/{evaluation_id}",
                            json={"results": all_results, "elapsed_seconds": elapsed},
                            timeout=5
                        )
                    except:
                        pass

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