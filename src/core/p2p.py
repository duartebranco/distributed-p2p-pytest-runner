from flask import jsonify, request
import requests

class P2P:
    def __init__(self):
        self.nodes = {}

    def add_node(self, address):
        if address not in self.nodes:
            self.nodes[address] = []

    def remove_node(self, address):
        if address in self.nodes:
            del self.nodes[address]

    def send_task(self, node_address, task):
        try:
            response = requests.post(f'http://{node_address}/task', json=task)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending task to {node_address}: {e}")
            return None

    def receive_results(self, node_address, results):
        if node_address in self.nodes:
            self.nodes[node_address].append(results)

    def get_network_info(self):
        return self.nodes

    def broadcast(self, task):
        for node in self.nodes:
            self.send_task(node, task)