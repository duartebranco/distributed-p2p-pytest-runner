import unittest
from src.core.node import Node
from src.core.task_manager import TaskManager

class TestCoreFunctionality(unittest.TestCase):

    def setUp(self):
        self.node = Node("192.168.1.100:7000")
        self.task_manager = TaskManager()

    def test_node_initialization(self):
        self.assertEqual(self.node.address, "192.168.1.100:7000")
        self.assertEqual(len(self.node.connected_nodes), 0)

    def test_add_connected_node(self):
        self.node.add_connected_node("192.168.1.100:7001")
        self.assertIn("192.168.1.100:7001", self.node.connected_nodes)

    def test_remove_connected_node(self):
        self.node.add_connected_node("192.168.1.100:7001")
        self.node.remove_connected_node("192.168.1.100:7001")
        self.assertNotIn("192.168.1.100:7001", self.node.connected_nodes)

    def test_task_distribution(self):
        self.task_manager.add_task("test_project_1")
        self.task_manager.add_task("test_project_2")
        tasks = self.task_manager.distribute_tasks([self.node])
        self.assertEqual(len(tasks), 2)

    def test_task_aggregation(self):
        self.task_manager.add_result("test_project_1", {"passed": 5, "failed": 1})
        self.task_manager.add_result("test_project_2", {"passed": 3, "failed": 2})
        aggregated_results = self.task_manager.aggregate_results()
        self.assertEqual(aggregated_results["total"]["passed"], 8)
        self.assertEqual(aggregated_results["total"]["failed"], 3)

if __name__ == '__main__':
    unittest.main()