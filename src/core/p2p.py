import threading
import time
import requests
import os
import random

class P2P:
    def __init__(self):
        self.running = True
        self.node_address = os.getenv('NODE_ADDRESS', '')
        self.known_seeds = os.getenv('SEED_NODES', '').split(',') if os.getenv('SEED_NODES') else []
        self.connected_nodes = set(self.known_seeds)
        self.connected_nodes.add(self.node_address)
        self.auto_join()
        threading.Thread(target=self.gossip_loop, daemon=True).start()

    def auto_join(self):
        for seed in self.known_seeds:
            if seed and seed != self.node_address:
                self.connected_nodes.add(seed)

    def gossip_loop(self):
        while self.running:
            time.sleep(2)
            peers = list(self.connected_nodes - {self.node_address})
            if not peers:
                continue
            peer = random.choice(peers)
            try:
                requests.post(f"http://{peer}/network/gossip", json={
                    "peers": list(self.connected_nodes)
                }, timeout=1)
            except Exception:
                continue

    def receive_gossip(self, peers):
        self.connected_nodes.update(peers)

    def get_network_info(self):
        # Só devolve os peers conhecidos por cada node
        network = {}
        for addr in self.connected_nodes:
            try:
                if addr == self.node_address:
                    peers = list(self.connected_nodes - {self.node_address})
                else:
                    resp = requests.get(f"http://{addr}/network/peers", timeout=1)
                    peers = resp.json().get("peers", [])
                network[addr] = peers
            except Exception:
                network[addr] = []
        return network