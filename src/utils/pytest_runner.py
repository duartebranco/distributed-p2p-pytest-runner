import pytest
import os
import subprocess
import sys

def run_pytest_on_project(project_path):
    result = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "per_project": {},
        "per_module": {},
        "nota_final": 0,
    }

    venv_dir_name = "project_venv" # Name of the virtual environment directory
    venv_path = os.path.join(project_path, venv_dir_name)

    # Determine platform-specific paths for python executable in venv
    if sys.platform == "win32":
        python_exe_in_venv = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        python_exe_in_venv = os.path.join(venv_path, "bin", "python")

    # 1. Create virtual environment
    print(f"Creating virtual environment in: {venv_path}")
    try:
        subprocess.check_call([sys.executable, '-m', 'venv', venv_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Error creating virtual environment for {project_path}: {e}")
        result["failed"] = 1
        result["total"] = 1 # Placeholder
        result["nota_final"] = 0
        return result
    except FileNotFoundError: # sys.executable not found, highly unlikely
        print(f"Error: Current Python executable '{sys.executable}' not found. Cannot create venv.")
        result["failed"] = 1
        result["total"] = 1
        result["nota_final"] = 0
        return result

    # 2. Install dependencies from requirements.txt if it exists, using pip from the venv
    requirements_file = os.path.join(project_path, 'requirements.txt')
    if os.path.exists(requirements_file):
        print(f"Installing dependencies from {requirements_file} into {venv_path}")
        try:
            # Use the python from the venv to run pip, ensuring correct environment
            subprocess.check_call([python_exe_in_venv, '-m', 'pip', 'install', '-r', requirements_file], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies for {project_path}: {e}")
            print(f"Pip Stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
            result["failed"] = 1
            result["total"] = 1 # Placeholder
            result["nota_final"] = 0
            # Optionally, clean up venv before returning on failure
            # shutil.rmtree(venv_path, ignore_errors=True)
            return result
        except FileNotFoundError:
            # This means python_exe_in_venv was not found, venv creation likely failed or path is wrong
            print(f"Error: Python executable not found at {python_exe_in_venv}. Venv might not be set up correctly.")
            result["failed"] = 1
            result["total"] = 1
            result["nota_final"] = 0
            return result


    # 3. Run pytest using the python from the venv
    print(f"Running pytest for project: {project_path} using venv: {venv_path}")
    retcode = -1 # Default to an error code if subprocess fails to start
    try:
        pytest_command = [
            python_exe_in_venv, '-m', 'pytest',
            project_path, # Pytest will discover tests in this path
            "--maxfail=100",
            "--disable-warnings",
            "-q"
        ]
        
        # Run pytest from the project's directory to help with test discovery and relative paths.
        process = subprocess.run(
            pytest_command,
            cwd=project_path, # Set current working directory for pytest
            capture_output=True,
            text=True,
            check=False # We will check the returncode manually
        )
        retcode = process.returncode

        # Log detailed output if pytest itself had an issue (not just test failures)
        # These are standard pytest exit codes.
        # pytest.ExitCode.OK (0), pytest.ExitCode.TESTS_FAILED (1), pytest.ExitCode.NO_TESTS_COLLECTED (5)
        # are common 'expected' outcomes. Others might indicate setup or internal pytest errors.
        if retcode not in [
            pytest.ExitCode.OK,
            pytest.ExitCode.TESTS_FAILED,
            pytest.ExitCode.NO_TESTS_COLLECTED,
        ] and retcode != -1 : # Also check our default error code
            print(f"Pytest for {project_path} encountered an issue or exited with an unexpected code: {retcode}")
            if process.stdout:
                print(f"Pytest Stdout:\n{process.stdout}")
            if process.stderr:
                print(f"Pytest Stderr:\n{process.stderr}")

    except FileNotFoundError:
        print(f"Error: Could not find Python executable ({python_exe_in_venv}) or pytest module within the venv for {project_path}.")
        # retcode remains -1
    except Exception as e:
        print(f"An unexpected error occurred while preparing to run pytest for {project_path}: {e}")
        # retcode remains -1

    # 4. Interpret pytest exit codes
    # Note: The "total", "passed", "failed" counts are placeholders.
    # A robust solution would parse pytest's output (e.g., JSON report) for actual counts.
    if retcode == pytest.ExitCode.OK:
        result["total"] = 1 # Placeholder
        result["passed"] = 1 # Placeholder
        result["nota_final"] = 20
    elif retcode == pytest.ExitCode.NO_TESTS_COLLECTED:
        result["total"] = 0
        result["passed"] = 0
        result["nota_final"] = 0 # Or an appropriate value indicating no tests
        print(f"No tests collected in {project_path}")
    else: # Covers TESTS_FAILED (1) and other error codes like INTERRUPTED(2), INTERNAL_ERROR(3), USAGE_ERROR(4), or our -1
        result["total"] = 1 # Placeholder
        result["failed"] = 1 # Placeholder
        result["nota_final"] = 0
        if retcode == -1: # Our custom indicator for subprocess execution failure
             print(f"Pytest execution failed for {project_path} due to an issue before or during subprocess run.")
        # Stderr for other critical pytest errors would have been printed above.

    return result