import time
import os
from flask import current_app
import requests

class TaskManager:
    def __init__(self):
        self.tasks = {}
        self.results = {}
        self.start_times = {}

    def set_elapsed_seconds(self, task_id, elapsed):
        print(f"[DEBUG][set_elapsed_seconds] Setting elapsed_seconds={elapsed} for task_id={task_id}")
        if task_id not in self.results:
            self.results[task_id] = {}
        self.results[task_id]["elapsed_seconds"] = elapsed

    def add_task(self, task_id, task):
        self.tasks[task_id] = task
        self.start_times[task_id] = time.time()

    def add_result(self, task_id, result):
        print(f"[DEBUG][add_result] task_id={task_id} | result keys={list(result.keys())}")
        if 'executed_by' in result:
            print(f"[DEBUG][add_result] executed_by={result['executed_by']}")
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
        elapsed = result.get("elapsed_seconds")
        if elapsed is None and start_time:
            elapsed = round(time.time() - start_time, 2)

        # Print debug sobre per_module e executed_by
        for mod, v in per_module.items():
            executed_by = v.get("executed_by", None)
            print(f"[DEBUG][get_evaluation_status] module={mod} executed_by={executed_by} passed={v.get('passed', 0)} failed={v.get('failed', 0)}")

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

    def get_all_evaluation_ids(self):
        return list(self.results.keys())
    
    def add_multiple_results(self, task_id, results):
        print(f"[DEBUG][add_multiple_results] task_id={task_id} | num_results={len(results)}")
        for idx, r in enumerate(results):
            print(f"[DEBUG][add_multiple_results] result[{idx}] executed_by={r.get('executed_by', None)} project_id={r.get('project_id', None)} module_path={r.get('module_path', None)} passed={r.get('passed', 0)} failed={r.get('failed', 0)}")
        total = sum(r.get("total", 0) for r in results)
        passed = sum(r.get("passed", 0) for r in results)
        failed = sum(r.get("failed", 0) for r in results)
        nota_final = sum(r.get("nota_final", 0) for r in results) // len(results) if results else 0

        # Agregação por projeto e por módulo
        per_project = {}
        per_module = {}
        for r in results:
            proj = r.get("project_id") or r.get("project_path")
            mod = r.get("module_path")
            if proj:
                if proj not in per_project:
                    per_project[proj] = {"total": 0, "passed": 0, "failed": 0}
                per_project[proj]["total"] += r.get("total", 0)
                per_project[proj]["passed"] += r.get("passed", 0)
                per_project[proj]["failed"] += r.get("failed", 0)
            if proj and mod:
                mod_key = f"{proj}/{os.path.basename(mod)}"
                per_module[mod_key] = {
                    "total": r.get("total", 0),
                    "passed": r.get("passed", 0),
                    "failed": r.get("failed", 0),
                    "executed_by": r.get("executed_by", None),
                    "project_id": proj
                }

        prev = self.results.get(task_id, {})
        elapsed = prev.get("elapsed_seconds")
        print(f"[DEBUG][add_multiple_results] task_id={task_id} | prev_elapsed={elapsed}")

        self.results[task_id] = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "nota_final": nota_final,
            "per_project": per_project,
            "per_module": per_module,
        }
        if elapsed is not None:
            print(f"[DEBUG][add_multiple_results] Preserving elapsed_seconds={elapsed} for task_id={task_id}")
            self.results[task_id]["elapsed_seconds"] = elapsed
        else:
            print(f"[DEBUG][add_multiple_results] No elapsed_seconds to preserve for task_id={task_id}")

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
        """Returns statistics from all nodes in the network"""
        try:
            p2p = current_app.p2p
        except RuntimeError:
            # Handle case when outside application context
            print("[WARNING] Accessing p2p outside application context")
            return []
            
        nodes_info = []
        for node in p2p.connected_nodes:
            try:
                if node == p2p.node_address:
                    # Get local node stats
                    stats = p2p.node_stats
                else:
                    # Get remote node stats
                    resp = requests.get(f"http://{node}/stats/node", timeout=1)
                    if resp.status_code == 200:
                        stats = resp.json()
                    else:
                        continue
                nodes_info.append({
                    "address": node,
                    "failed": stats.get("failed", 0),
                    "passed": stats.get("passed", 0),
                    "projects": stats.get("projects", 0),
                    "modules": stats.get("modules", 0),
                    "evaluations": stats.get("evaluations", [])
                })
            except Exception as e:
                print(f"Failed to get stats from node {node}: {e}")
                continue
        
        return nodes_info