class Node:
    def __init__(self, address):
        self.address = address
        self.connected_nodes = []
        self.tasks = []
        self.results = {}

    def connect(self, node_address):
        if node_address not in self.connected_nodes:
            self.connected_nodes.append(node_address)

    def disconnect(self, node_address):
        if node_address in self.connected_nodes:
            self.connected_nodes.remove(node_address)

    def send_task(self, task, node_address):
        # Logic to send a task to another node
        pass

    def receive_task(self, task):
        self.tasks.append(task)
        # Logic to process the received task
        pass

    def aggregate_results(self, result):
        # Logic to aggregate results from test executions
        pass

    def get_status(self):
        return {
            "address": self.address,
            "connected_nodes": self.connected_nodes,
            "tasks": len(self.tasks),
            "results": self.results
        }