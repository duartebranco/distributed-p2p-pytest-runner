import os
import tempfile
import subprocess
import requests
import zipfile
import io

def handle_github_projects(projects, auth_token):
    """
    Clones the given list of GitHub repositories using the provided auth token.
    Returns a list of paths to the cloned repositories.
    """
    cloned_paths = []
    temp_dir = tempfile.mkdtemp()
    for url in projects:
        # Insert token into URL if not already present
        if "@" not in url and auth_token:
            url_parts = url.split("://")
            url = f"{url_parts[0]}://{auth_token}@{url_parts[1]}"
        repo_name = url.rstrip('/').split('/')[-1]
        dest_path = os.path.join(temp_dir, repo_name)
        subprocess.run(["git", "clone", url, dest_path], check=True)
        cloned_paths.append(dest_path)
    return cloned_paths

def fetch_github_repo(auth_token, repo_url):
    headers = {
        'Authorization': f'token {auth_token}',
        'Accept': 'application/vnd.github.v3.raw'
    }

    response = requests.get(repo_url, headers=headers)

    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to fetch repository: {response.status_code} - {response.text}")

def extract_project_files(zip_content):
    with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
        z.extractall("extracted_projects")
        return z.namelist()

def get_project_files_from_github(auth_token, repo_urls):
    project_files = []
    for url in repo_urls:
        try:
            content = fetch_github_repo(auth_token, url)
            project_files.append(content)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    return project_files