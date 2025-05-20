from flask import Blueprint, jsonify, request
from core.p2p import P2P

p2p = P2P()
network_bp = Blueprint('network', __name__)

@network_bp.route('', methods=['GET'])
def get_network():
    """
    GET /network
    Returns the full P2P adjacency map.
    """
    return jsonify(p2p.get_network_info()), 200

@network_bp.route('', methods=['POST'])
def add_node():
    """
    POST /network  {"address": "ip:port"}
    Adds a new peer to the mesh.
    """
    data = request.get_json() or {}
    address = data.get('address')
    if not address:
        return jsonify({"error": "Missing 'address'"}), 400

    p2p.add_node(address)
    return jsonify({"status": "node added", "address": address}), 201

@network_bp.route('', methods=['DELETE'])
def remove_node():
    """
    DELETE /network  {"address": "ip:port"}
    Removes a peer from the mesh.
    """
    data = request.get_json() or {}
    address = data.get('address')
    if not address:
        return jsonify({"error": "Missing 'address'"}), 400

    p2p.remove_node(address)
    return jsonify({"status": "node removed", "address": address}), 200