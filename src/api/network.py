from flask import Blueprint, jsonify # type: ignore
import json

network_bp = Blueprint('network', __name__)

# Simulated data structure to hold the network information
network_data = {}

@network_bp.route('', methods=['GET'])
def get_network():
    return jsonify(network_data)