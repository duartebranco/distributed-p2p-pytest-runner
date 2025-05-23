from flask import Blueprint, request, jsonify, current_app

network_bp = Blueprint('network', __name__)

@network_bp.route('', methods=['GET'])
def get_network():
    return jsonify(current_app.p2p.get_network_info()), 200

# used by nodes, not meant to be used by the client
@network_bp.route('/peers', methods=['GET'])
def get_peers():
    peers = list(current_app.p2p.connected_nodes - {current_app.p2p.node_address})
    return jsonify({"peers": peers}), 200

@network_bp.route('/gossip', methods=['POST'])
def gossip():
    data = request.get_json()
    peers = data.get("peers", [])
    current_app.p2p.receive_gossip(peers)
    return jsonify({"status": "ok"}), 200