import requests
from flask import current_app

class P2P:
    def __init__(self):
        self.peers = {}  # { "node2:7001": [] }

    def add_node(self, addr):
        self.peers[addr] = []
    def remove_node(self, addr):
        self.peers.pop(addr, None)
    def get_network_info(self):
        return self.peers

    def send_task(self, node_addr, payload):
        url = f"http://{node_addr}/task"
        try:
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            current_app.logger.error(f"P2P.send_task → {url} failed: {e}")
            return []