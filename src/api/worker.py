from flask import Blueprint, request, jsonify
import base64, os, tempfile, threading, time
from utils.zip_handler import extract_zip
from utils.pytest_runner import run_pytest_on_project

worker_bp = Blueprint('worker', __name__)

# in-memory buffers
worker_tasks = {}    # evaluation_id -> list of mods ready to run
worker_results = {}  # evaluation_id -> list of pytest results

def _process_stored_modules(evaluation_id):
    mods = worker_tasks.pop(evaluation_id, [])
    print(f"[DEBUG][WORKER] Processing {len(mods)} modules for evaluation_id={evaluation_id}")
    for idx, m in enumerate(mods):
        print(f"[DEBUG][WORKER]   Module {idx}: project_id={m.get('project_id')} module_path={m.get('module_path')}")
    results = []
    for mod in mods:
        project_path = mod["project_path"]
        module_abs = os.path.join(project_path, mod["module_path"])
        print(f"[DEBUG][WORKER]   Running pytest for project_id={mod.get('project_id')} module_path={mod.get('module_path')}")
        r = run_pytest_on_project(project_path, module_abs)
        r["project_id"] = mod["project_id"]
        r["module_path"] = mod["module_path"]  # garantir que devolve o relativo
        # Print do resultado detalhado
        print(f"[RESULT][WORKER] project_id={r.get('project_id')} module_path={r.get('module_path')} passed={r.get('passed')} failed={r.get('failed')} errors={r.get('errors', 0)}")
        results.append(r)
    print(f"[DEBUG][WORKER] Finished processing. Results to return:")
    for idx, r in enumerate(results):
        print(f"  [RESULT] {idx}: project_id={r.get('project_id')} module_path={r.get('module_path')}")
    worker_results[evaluation_id] = results

@worker_bp.route('', methods=['POST'])
def receive_task():
    data   = request.json
    eval_id= data.get("evaluation_id")
    mods   = data.get("modules", [])
    if not eval_id:
        return jsonify({"error": "missing evaluation_id"}), 400

    print(f"[DEBUG][WORKER] Received task: evaluation_id={eval_id} | {len(mods)} modules")
    for idx, mod in enumerate(mods):
        print(f"  [RECV MOD] {idx}: project_id={mod.get('project_id')} module_path={mod.get('module_path')}")

    # 1) decode & store each ZIP (or leave project_path as is)
    stored = []
    for idx, mod in enumerate(mods):
        if mod.get("project_zip"):
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "project.zip")
            with open(zip_path, "wb") as f:
                f.write(base64.b64decode(mod["project_zip"]))
            extract_zip(zip_path, temp_dir)
            mod["project_path"] = temp_dir
            del mod["project_zip"]
            print(f"  [EXTRACT] {idx}: project_id={mod.get('project_id')} extracted to {temp_dir}")
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

@worker_bp.route('/results/<evaluation_id>', methods=['GET'])
def fetch_results(evaluation_id):
    print(f"[DEBUG][WORKER] Results requested for evaluation_id={evaluation_id}")
    # block here only when client asks for results
    while evaluation_id not in worker_results:
        time.sleep(0.5)
    results = worker_results.pop(evaluation_id)
    print(f"[DEBUG][WORKER] Returning {len(results)} results for evaluation_id={evaluation_id}")
    for idx, r in enumerate(results):
        print(f"  [SEND RESULT] {idx}: project_id={r.get('project_id')} module_path={r.get('module_path')}")
    return jsonify(results), 200