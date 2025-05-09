import zipfile
import tempfile
import os

def handle_zip_upload(zip_file):
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    return temp_dir

def extract_zip(zip_file_path, extract_to):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def prepare_projects(zip_file_path, extract_to):
    extract_zip(zip_file_path, extract_to)
    projects = []
    
    for root, dirs, files in os.walk(extract_to):
        for dir_name in dirs:
            projects.append(os.path.join(root, dir_name))
    
    return projects

def validate_zip_file(zip_file_path):
    if not zipfile.is_zipfile(zip_file_path):
        raise ValueError("The provided file is not a valid ZIP file.")