from flask import Blueprint, jsonify # type: ignore
from api.evaluation import task_manager

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('', methods=['GET'])
def get_stats():
    all_stats = task_manager.get_all_stats()
    nodes_stats = task_manager.get_nodes_stats()
    
    response = {
        "all": all_stats,
        "nodes": nodes_stats
    }
    
    return jsonify(response)