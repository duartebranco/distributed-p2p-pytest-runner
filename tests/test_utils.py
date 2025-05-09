import pytest
from src.utils.zip_handler import extract_zip
from src.utils.github_handler import fetch_github_repo

def test_extract_zip_valid():
    # Test extracting a valid ZIP file
    zip_path = 'tests/test_files/valid_project.zip'
    output_dir = 'tests/test_files/extracted'
    result = extract_zip(zip_path, output_dir)
    assert result is True
    # Additional assertions to check extracted files can be added here

def test_extract_zip_invalid():
    # Test extracting an invalid ZIP file
    zip_path = 'tests/test_files/invalid_project.zip'
    output_dir = 'tests/test_files/extracted'
    result = extract_zip(zip_path, output_dir)
    assert result is False

def test_fetch_github_repo_valid():
    # Test fetching a valid GitHub repository
    repo_url = 'https://github.com/user/repo'
    token = 'valid_token'
    result = fetch_github_repo(repo_url, token)
    assert result is not None
    # Additional assertions to check the fetched content can be added here

def test_fetch_github_repo_invalid():
    # Test fetching an invalid GitHub repository
    repo_url = 'https://github.com/user/invalid_repo'
    token = 'valid_token'
    result = fetch_github_repo(repo_url, token)
    assert result is None