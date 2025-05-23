import pytest
import os
import subprocess
import sys

def find_test_modules(project_path):
    """
    Devolve uma lista de caminhos absolutos para todos os ficheiros test_*.py no projeto.
    """
    test_dir = os.path.join(project_path, "tests")
    if not os.path.isdir(test_dir):
        return []
    files = os.listdir(test_dir)
    return [
        os.path.join(test_dir, f)
        for f in files
        if f.startswith("test_") and f.endswith(".py")
    ]

## Used for development purposes and debugging
def print_dir_tree(start_path):
    for root, dirs, files in os.walk(start_path):
        level = root.replace(start_path, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")

def run_pytest_on_project(project_path, module_path=None):
    result = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "per_project": {},
        "per_module": {},
        "nota_final": 0,
        "project_path": project_path,
        "module_path": module_path,
    }

    venv_dir_name = "project_venv"
    venv_path = os.path.join(project_path, venv_dir_name)

    if sys.platform == "win32":
        python_exe_in_venv = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        python_exe_in_venv = os.path.join(venv_path, "bin", "python")

    if not os.path.exists(venv_path):
        try:
            subprocess.check_call([sys.executable, '-m', 'venv', venv_path])
        except Exception as e:
            print(f"[ERROR] Failure to create virtual environment: {e}")
            result["failed"] = 1
            result["total"] = 1
            result["nota_final"] = 0
            return result

    requirements_file = os.path.join(project_path, 'requirements.txt')
    if os.path.exists(requirements_file):
        try:
            subprocess.check_call([python_exe_in_venv, '-m', 'pip', 'install', '-r', requirements_file])
        except Exception as e:
            result["failed"] = 1
            result["total"] = 1
            result["nota_final"] = 0
            return result

    try:
        pytest_command = [
            python_exe_in_venv, '-m', 'pytest',
            module_path if module_path else project_path,
            "--maxfail=100",
            "--disable-warnings",
            "-q"
        ]
        process = subprocess.run(
            pytest_command,
            cwd=project_path,
            capture_output=True,
            text=True,
            check=False
        )
        retcode = process.returncode
    except Exception as e:
        retcode = -1

    if retcode == pytest.ExitCode.OK:
        result["total"] = 1
        result["passed"] = 1
        result["nota_final"] = 20
    elif retcode == pytest.ExitCode.NO_TESTS_COLLECTED:
        result["total"] = 0
        result["passed"] = 0
        result["nota_final"] = 0
        print(f"No tests collected in {project_path}")
    else:
        result["total"] = 1
        result["failed"] = 1
        result["nota_final"] = 0
        if retcode == -1:
            print(f"Pytest execution failed for {project_path} due to an issue before or during subprocess run.")

    return result