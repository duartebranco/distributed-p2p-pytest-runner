import pytest
import os
import subprocess
import sys
import os

def find_test_modules(project_path):
    """
    Devolve uma lista de caminhos absolutos para todos os ficheiros test_*.py no projeto.
    """
    test_dir = os.path.join(project_path, "tests")
    if not os.path.isdir(test_dir):
        return []
    return [
        os.path.join(test_dir, f)
        for f in os.listdir(test_dir)
        if f.endswith(".py")
    ]

def run_pytest_on_project(project_path, module_path=None):
    result = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "per_project": {},
        "per_module": {},
        "nota_final": 0,
    }

    venv_dir_name = "project_venv"
    venv_path = os.path.join(project_path, venv_dir_name)

    if sys.platform == "win32":
        python_exe_in_venv = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        python_exe_in_venv = os.path.join(venv_path, "bin", "python")

    print(f"Creating virtual environment in: {venv_path}")
    try:
        subprocess.check_call([sys.executable, '-m', 'venv', venv_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Error creating virtual environment for {project_path}: {e}")
        result["failed"] = 1
        result["total"] = 1
        result["nota_final"] = 0
        return result
    except FileNotFoundError:
        print(f"Error: Current Python executable '{sys.executable}' not found. Cannot create venv.")
        result["failed"] = 1
        result["total"] = 1
        result["nota_final"] = 0
        return result

    requirements_file = os.path.join(project_path, 'requirements.txt')
    if os.path.exists(requirements_file):
        print(f"Installing dependencies from {requirements_file} into {venv_path}")
        try:
            subprocess.check_call([python_exe_in_venv, '-m', 'pip', 'install', '-r', requirements_file], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies for {project_path}: {e}")
            print(f"Pip Stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
            result["failed"] = 1
            result["total"] = 1
            result["nota_final"] = 0
            return result
        except FileNotFoundError:
            print(f"Error: Python executable not found at {python_exe_in_venv}. Venv might not be set up correctly.")
            result["failed"] = 1
            result["total"] = 1
            result["nota_final"] = 0
            return result

    print(f"Running pytest for project: {project_path} using venv: {venv_path}")
    retcode = -1
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

        if retcode not in [
            pytest.ExitCode.OK,
            pytest.ExitCode.TESTS_FAILED,
            pytest.ExitCode.NO_TESTS_COLLECTED,
        ] and retcode != -1:
            print(f"Pytest for {project_path} encountered an issue or exited with an unexpected code: {retcode}")
            if process.stdout:
                print(f"Pytest Stdout:\n{process.stdout}")
            if process.stderr:
                print(f"Pytest Stderr:\n{process.stderr}")

    except FileNotFoundError:
        print(f"Error: Could not find Python executable ({python_exe_in_venv}) or pytest module within the venv for {project_path}.")
    except Exception as e:
        print(f"An unexpected error occurred while preparing to run pytest for {project_path}: {e}")

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