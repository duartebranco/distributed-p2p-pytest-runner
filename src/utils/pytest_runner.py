import pytest
import os

def run_pytest_on_project(project_path):
    result = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "per_project": {},
        "per_module": {},
        "nota_final": 0,
    }

    # Run pytest and capture results
    retcode = pytest.main([project_path, "--maxfail=100", "--disable-warnings", "-q"])
    # NOTE: For a real implementation, use pytest's hooks or a plugin to get detailed stats.
    # Here, we just set pass/fail based on retcode for demo purposes.
    if retcode == 0:
        # All tests passed
        result["total"] = 1
        result["passed"] = 1
        result["nota_final"] = 20
    else:
        result["total"] = 1
        result["failed"] = 1
        result["nota_final"] = 0

    return result