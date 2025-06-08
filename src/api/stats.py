from flask import Blueprint, jsonify, current_app
import requests
import socket

stats_bp = Blueprint('stats', __name__)

def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "127.0.0.1"

def get_node_address():
    # Preferencialmente usa o que está em p2p, senão tenta calcular
    if hasattr(current_app, "p2p") and getattr(current_app.p2p, "node_address", None):
        return current_app.p2p.node_address
    return f"{get_local_ip()}:{current_app.config.get('PORT', 7000)}"

@stats_bp.route('', methods=['GET'])
def get_stats():
    from api.evaluation import task_manager

    # 1. Agrega todos os projetos únicos
    all_projects = set()
    for result in task_manager.results.values():
        for proj in result.get("per_project", {}):
            all_projects.add(proj)

    # 2. Stats globais
    global_stats = {
        "failed": sum(r.get("failed", 0) for r in task_manager.results.values()),
        "passed": sum(r.get("passed", 0) for r in task_manager.results.values()),
        "projects": len(all_projects),
        "evaluations": len(task_manager.results)
    }

    # 3. Stats do node local
    node_address = get_node_address()
    node_stats = {
        "address": node_address,
        "failed": 0,
        "passed": 0,
        "projects": 0,
        "modules": 0,
        "evaluations": []
    }

    for eval_id, result in task_manager.results.items():
        # result pode ser agregação de vários módulos, tens de ir buscar os módulos individuais
        per_module = result.get("per_module", {})
        eval_has_local = False
        for mod_key, mod_stats in per_module.items():
            # Se guardaste executed_by por módulo:
            executed_by = mod_stats.get("executed_by")
            if executed_by == node_address:
                node_stats["modules"] += 1
                node_stats["failed"] += mod_stats.get("failed", 0)
                node_stats["passed"] += mod_stats.get("passed", 0)
                eval_has_local = True
        if eval_has_local:
            node_stats["evaluations"].append(eval_id)
        # Para projects, podes fazer set dos projetos dos módulos executados localmente
        local_projects = set()
        for mod_key, mod_stats in per_module.items():
            if mod_stats.get("executed_by") == node_address:
                proj = mod_stats.get("project_id")
                if proj:
                    local_projects.add(proj)
        node_stats["projects"] += len(local_projects)

    nodes_stats = [node_stats]

    # 4. Pede aos outros nodes os seus stats
    known_nodes = list(current_app.p2p.get_network_info().keys()) if hasattr(current_app, 'p2p') else []
    for peer in known_nodes:
        if peer == node_address:
            continue
        try:
            resp = requests.get(f"http://{peer}/stats/node_stats", timeout=3)
            if resp.status_code == 200:
                peer_stats = resp.json()
                nodes_stats.append(peer_stats)
        except Exception:
            continue

    return jsonify({
        "all": global_stats,
        "nodes": nodes_stats
    })

@stats_bp.route('/node_stats', methods=['GET'])
def get_node_stats():
    from api.evaluation import task_manager
    node_address = get_node_address()
    node_stats = {
        "address": node_address,
        "failed": 0,
        "passed": 0,
        "projects": 0,
        "modules": 0,
        "evaluations": []
    }
    local_projects = set()
    for eval_id, result in task_manager.results.items():
        per_module = result.get("per_module", {})
        eval_has_local = False
        for mod_stats in per_module.values():
            if mod_stats.get("executed_by") == node_address:
                node_stats["modules"] += 1
                node_stats["failed"] += mod_stats.get("failed", 0)
                node_stats["passed"] += mod_stats.get("passed", 0)
                eval_has_local = True
                if mod_stats.get("project_id"):
                    local_projects.add(mod_stats["project_id"])
        if eval_has_local:
            node_stats["evaluations"].append(eval_id)
    node_stats["projects"] = len(local_projects)
    return jsonify(node_stats)