from flask import Blueprint, jsonify
from core.task_manager import TaskManager

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('', methods=['GET'])
def get_stats():
    all_stats = TaskManager.get_all_stats()
    nodes_stats = TaskManager.get_nodes_stats()
    
    response = {
        "all": all_stats,
        "nodes": nodes_stats
    }
    
    return jsonify(response)