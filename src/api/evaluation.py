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
from random import randint
from random import shuffle
from utils.zip_handler import zip_project_folder
from utils.pytest_runner  import find_test_modules

evaluation_bp = Blueprint('evaluation', __name__)
task_manager   = TaskManager()

def is_node_alive(node):
    try:
        # Tenta um pedido rápido (timeout curto)
        requests.get(f"http://{node}/network/peers", timeout=1)
        return True
    except Exception:
        return False

def distribute_and_collect(evaluation_id, auth_token, nodes, modules):
    if not modules or not nodes:
        print(f"[DEBUG][DIST] distribute_and_collect called with modules={modules} nodes={nodes}")
        return []

    print(f"[DEBUG][DIST] Distributing {len(modules)} modules to {len(nodes)} nodes: {[n for n in nodes]}")
    for idx, m in enumerate(modules):
        print(f"[DEBUG][DIST]   Module {idx}: project_id={m.get('project_id')} module_path={m.get('module_path')}")

    size = math.ceil(len(modules) / len(nodes))
    chunks = [modules[i:i+size] for i in range(0, len(modules), size)]

    for idx, node in enumerate(nodes):
        chunk = chunks[idx] if idx < len(chunks) else []
        print(f"[DEBUG][DIST] Sending chunk to {node}: {[m.get('module_path') for m in chunk]}")
        payload = {
            "evaluation_id": evaluation_id,
            "auth_token":    auth_token,
            "modules": chunk
        }
        ack = current_app.p2p.send_task(node, payload)
        print(f"[DEBUG][DIST] Sent chunk to {node} | ACK: {ack} | Chunk size: {len(chunk)}")

    all_results = []
    for idx, node in enumerate(nodes):
        try:
            print(f"[DEBUG][DIST] Fetching results from {node}")
            res = current_app.p2p.get_results(node, evaluation_id)
        except Exception as e:
            print(f"[ERROR][DIST] Node {node} unreachable: {e}")
            res = None
        if res:
            print(f"[DEBUG][DIST] Received {len(res)} results from {node}")
            for r in res:
                print(f"[DEBUG][DIST]   Result: project_id={r.get('project_id')} module_path={r.get('module_path')}")
            all_results.extend(res)
        else:
            print(f"[WARN][DIST] No results from {node}")
    return all_results

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

        all_nodes = list(current_app.p2p.get_network_info().keys())
        if all_nodes:
            cloned = handle_github_projects(projects, auth_token)
            all_mods = []
            for p in cloned:
                pid = os.path.basename(p)
                zipped = zip_project_folder(p)
                for m in find_test_modules(p):
                    all_mods.append({
                        "project_path": p,
                        "module_path": os.path.relpath(m, p),
                        "project_zip": zipped,
                        "project_id": pid
                    })

            tested_modules = set()
            all_results = []
            t0 = time.time()

            ronda = 0
            while True:
                ronda += 1
                missing_mods = [
                    m for m in all_mods
                    if (m["project_id"], m["module_path"], m["project_zip"]) not in tested_modules
                ]
                print(f"\n[DEBUG][EVAL][RONDA {ronda}] Módulos em falta ({len(missing_mods)}):")
                for m in missing_mods:
                    print(f"  [MISSING] project_id={m['project_id']} module_path={m['module_path']}")

                if not missing_mods:
                    print(f"[DEBUG][EVAL][RONDA {ronda}] Todos os módulos testados!")
                    break

                alive_nodes = [n for n in all_nodes if is_node_alive(n)]
                print(f"[DEBUG][EVAL][RONDA {ronda}] Alive nodes: {alive_nodes}")
                if not alive_nodes:
                    print("[ERROR][EVAL] No alive nodes available for distribution!")
                    break

                print(f"[DEBUG][EVAL][RONDA {ronda}] A distribuir para os nodes:")
                for n in alive_nodes:
                    print(f"  [NODE] {n}")

                print(f"[DEBUG][EVAL][RONDA {ronda}] A ENVIAR para os nodes:")
                for m in missing_mods:
                    print(f"  [SEND] project_id={m['project_id']} module_path={m['module_path']}")

                results = distribute_and_collect(evaluation_id, auth_token, alive_nodes, missing_mods)
                print(f"[DEBUG][EVAL][RONDA {ronda}] RECEBIDO dos nodes ({len(results)} resultados):")
                for r in results:
                    pid = r.get("project_id") or r.get("project_path")
                    mod = r.get("module_path")
                    print(f"  [RECV] project_id={pid} module_path={mod}")

                all_results.extend(results)
                for r in results:
                    pid = r.get("project_id") or r.get("project_path")
                    mod = r.get("module_path")
                    # Procurar o ziphash correto em all_mods
                    ziphash = None
                    for m in all_mods:
                        if m["project_id"] == pid and m["module_path"] == mod:
                            ziphash = m["project_zip"]
                            break
                    if pid and mod and ziphash:
                        tested_modules.add((pid, mod, ziphash))
                        print(f"  [MARK TESTED] project_id={pid} module_path={mod}")

            print(f"[DEBUG][EVAL][FINAL] Aggregating results. Total results: {len(all_results)}")
            task_manager.add_multiple_results(evaluation_id, all_results)
            elapsed = round(time.time() - t0, 2)
            print(f"[DEBUG][EVAL][FINAL] Elapsed seconds: {elapsed}")
            task_manager.set_elapsed_seconds(evaluation_id, elapsed)

            # sync elapsed+results to peers
            for node in all_nodes:
                if node != current_app.p2p.node_address:
                    try:
                        print(f"[DEBUG][EVAL][SYNC] Syncing results to {node}")
                        requests.post(
                            f"http://{node}/evaluation/sync_result/{evaluation_id}",
                            json={"results": all_results, "elapsed_seconds": elapsed},
                            timeout=5
                        )
                    except Exception as e:
                        print(f"[WARN][EVAL][SYNC] Failed to sync to {node}: {e}")

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