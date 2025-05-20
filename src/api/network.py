from flask import Blueprint, request, jsonify, current_app
import requests

network_bp = Blueprint('network', __name__)

@network_bp.route('', methods=['GET'])
def get_network():
    return jsonify(current_app.p2p.get_network_info()), 200

@network_bp.route('', methods=['POST'])
def add_node():
    data      = request.get_json()
    addr      = data.get("address")
    broadcast = data.get("broadcast", True)

    # 1) add the new peer locally
    current_app.p2p.add_node(addr)

    # 2) if this is the initial call, notify the peer to add us back
    if broadcast:
        self_addr = current_app.config['NODE_ADDRESS']
        try:
            requests.post(
                f"http://{addr}/network",
                json={"address": self_addr, "broadcast": False},
                timeout=5
            )
            # also record the reverse link locally
            current_app.p2p.peers[addr].append(self_addr)
        except Exception:
            current_app.logger.warning(f"Could not connect back to peer {addr}")

    return jsonify({"message": "node added"}), 201

@network_bp.route('', methods=['DELETE'])
def remove_node():
    addr = request.json.get("address")
    current_app.p2p.remove_node(addr)
    return jsonify({"message": "node removed"}), 200