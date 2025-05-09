from flask import Blueprint, jsonify
import json

network_bp = Blueprint('network', __name__)

# Simulated data structure to hold the network information
network_data = {}

@network_bp.route('/network', methods=['GET'])
def get_network():
    return jsonify(network_data)