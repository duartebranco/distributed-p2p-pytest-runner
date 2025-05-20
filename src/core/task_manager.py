import time

class TaskManager:
    def __init__(self):
        self.tasks = {}
        self.results = {}
        self.start_times = {}

    def add_task(self, task_id, task):
        self.tasks[task_id] = task
        self.start_times[task_id] = time.time()

    def add_result(self, task_id, result):
        self.results[task_id] = result

    def get_evaluation_status(self, evaluation_id):
        result = self.results.get(evaluation_id)
        start_time = self.start_times.get(evaluation_id)
        if not result:
            return {
                "status": "running",
                "executed": 0,
                "in_progress": 1,
                "pending": 0
            }
        total = result.get("total", 0)
        passed = result.get("passed", 0)
        failed = result.get("failed", 0)
        per_project = result.get("per_project", {})
        per_module = result.get("per_module", {})
        nota_final = result.get("nota_final", 0)
        elapsed = round(time.time() - start_time, 2) if start_time else None

        return {
            "percent_passed": (passed / total * 100) if total else 0,
            "percent_failed": (failed / total * 100) if total else 0,
            "percent_passed_per_project": {proj: (v["passed"] / v["total"] * 100) if v["total"] else 0 for proj, v in per_project.items()},
            "percent_failed_per_project": {proj: (v["failed"] / v["total"] * 100) if v["total"] else 0 for proj, v in per_project.items()},
            "percent_passed_per_module": {mod: (v["passed"] / v["total"] * 100) if v["total"] else 0 for mod, v in per_module.items()},
            "percent_failed_per_module": {mod: (v["failed"] / v["total"] * 100) if v["total"] else 0 for mod, v in per_module.items()},
            "executed": passed + failed,
            "in_progress": 0,
            "pending": total - (passed + failed),
            "nota_final": nota_final,
            "elapsed_seconds": elapsed
        }
    
    def get_all_evaluation(self):
        evaluations = []
        for result in self.results.keys():
            evaluations.append(self.get_evaluation_status(result))
        
        return evaluations

    
    def add_multiple_results(self, task_id, results):
        total = sum(r.get("total", 0) for r in results)
        passed = sum(r.get("passed", 0) for r in results)
        failed = sum(r.get("failed", 0) for r in results)
        nota_final = sum(r.get("nota_final", 0) for r in results) // len(results) if results else 0
        self.results[task_id] = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "nota_final": nota_final,
        }
    
    def get_all_stats(self):
        """
        Returns global stats across all evaluations:
          failed, passed, number of projects, number of evaluations.
        """
        passed = sum(r.get("passed", 0) for r in self.results.values())
        failed = sum(r.get("failed", 0) for r in self.results.values())
        evaluations = len(self.results)
        # count 1 project for a single-path task, or len(list) for multiple
        projects = sum(
            len(self.tasks[eid]) if isinstance(self.tasks[eid], list) else 1
            for eid in self.results
        )
        return {
            "failed": failed,
            "passed": passed,
            "projects": projects,
            "evaluations": evaluations
        }

    def get_nodes_stats(self):
        """
        TODO: hook into your P2P layer to build per-node stats.
        For now, returns an empty list.
        """
        return []