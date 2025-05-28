from flask import Blueprint, request, jsonify
import base64, os, tempfile, threading, time
from utils.zip_handler import extract_zip
from utils.pytest_runner import run_pytest_on_project

worker_bp = Blueprint('worker', __name__)

# in-memory buffers
worker_tasks = {}    # evaluation_id -> list of mods ready to run
worker_results = {}  # evaluation_id -> list of pytest results

def _process_stored_modules(evaluation_id):
    # pull out the modules we stored on receive
    mods = worker_tasks.pop(evaluation_id, [])
    results = []
    for mod in mods:
        project_path = mod["project_path"]
        module_abs = os.path.join(project_path, mod["module_path"])
        r = run_pytest_on_project(project_path, module_abs)
        r["project_id"] = mod["project_id"]
        results.append(r)
    worker_results[evaluation_id] = results

@worker_bp.route('/task', methods=['POST'])
def receive_task():
    data   = request.json
    eval_id= data.get("evaluation_id")
    mods   = data.get("modules", [])
    if not eval_id:
        return jsonify({"error": "missing evaluation_id"}), 400

    # 1) decode & store each ZIP (or leave project_path as is)
    stored = []
    for mod in mods:
        if mod.get("project_zip"):
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "project.zip")
            with open(zip_path, "wb") as f:
                f.write(base64.b64decode(mod["project_zip"]))
            extract_zip(zip_path, temp_dir)
            mod["project_path"] = temp_dir
            del mod["project_zip"]
        stored.append(mod)

    # 2) only now ACK – the node has "everything it needs"
    worker_tasks[eval_id] = stored
    ack = jsonify({"status": "ack"}), 200

    # 3) kick off pytest in background (non-blocking for the HTTP request)
    threading.Thread(
        target=_process_stored_modules,
        args=(eval_id,),
        daemon=True
    ).start()

    return ack

@worker_bp.route('/task/results/<evaluation_id>', methods=['GET'])
def fetch_results(evaluation_id):
    # block here only when client asks for results
    while evaluation_id not in worker_results:
        time.sleep(0.5)
    return jsonify(worker_results.pop(evaluation_id)), 200