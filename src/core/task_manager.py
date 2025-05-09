import time

class TaskManager:
    def __init__(self):
        self.tasks = {}
        self.results = {}
        self.start_times = {}

    def add_task(self, task_id, task):
        print(f"[DEBUG] Adding task: {task_id} with task: {task}")
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