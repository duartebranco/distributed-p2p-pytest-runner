import pytest
import os
import subprocess
import sys
import time

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

def wait_for_pytest_to_finish(timeout=60):
    """
    Espera até não haver nenhum processo pytest ativo (máx: timeout segundos).
    """
    start = time.time()
    while time.time() - start < timeout:
        # Procura processos pytest (exclui o próprio comando grep)
        result = subprocess.run(
            "ps aux | grep '[p]ytest' | grep -v grep",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if not result.stdout:
            # Não há pytest a correr
            return True
        time.sleep(1)
    print("[DEBUG][PYTEST] Timeout à espera que pytest termine!")
    return False

## Used for development purposes and debugging
def print_dir_tree(start_path):
    for root, dirs, files in os.walk(start_path):
        level = root.replace(start_path, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")

def find_projects(base_path):
    # Ao correr zip tentar encontrar os projetos através to /tests
    projs = []
    for root, dirs, _ in os.walk(base_path):
        if 'tests' in dirs:
            projs.append(root)
    return projs

def run_pytest_on_project(project_path, module_path=None):
    wait_for_pytest_to_finish(timeout=60)
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
            "-vvv",
            "--tb=long",
            "-s"
        ]
        print(f"[PYTEST][CMD] {' '.join(pytest_command)}", flush=True)
        # Use subprocess.run com timeout
        completed = subprocess.run(
            pytest_command,
            cwd=project_path,
            timeout=70  # Timeout de 70 segundos
        )
        retcode = completed.returncode
        result["pytest_stdout"] = "[ver logs do container]"
        result["pytest_stderr"] = "[ver logs do container]"
    except subprocess.TimeoutExpired:
        retcode = -2
        result["pytest_stdout"] = ""
        result["pytest_stderr"] = "Timeout: pytest demorou mais de 60 segundos"
    except Exception as e:
        retcode = -1
        result["pytest_stdout"] = ""
        result["pytest_stderr"] = str(e)

    if retcode == pytest.ExitCode.OK:
        result["total"] = 1
        result["passed"] = 1
        result["nota_final"] = 20
    elif retcode == pytest.ExitCode.NO_TESTS_COLLECTED:
        result["total"] = 0
        result["passed"] = 0
        result["nota_final"] = 0
        print(f"No tests collected in {project_path}")
    elif retcode == -2:
        result["total"] = 1
        result["failed"] = 1
        result["nota_final"] = 0
        print(f"[ERROR] Timeout: pytest demorou mais de 60 segundos em {module_path}")
    else:
        result["total"] = 1
        result["failed"] = 1
        result["nota_final"] = 0
    return result
