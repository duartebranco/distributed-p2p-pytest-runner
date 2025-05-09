import json
import pytest
from flask import Flask, jsonify, request
from src.api.evaluation import evaluate_zip, evaluate_github
from src.api.stats import get_stats
from src.api.network import get_network

app = Flask(__name__)

@app.route('/evaluation', methods=['POST'])
def evaluation():
    if 'file' in request.files:
        zip_file = request.files['file']
        evaluation_id = evaluate_zip(zip_file)
        return jsonify({"id": evaluation_id}), 201
    elif request.is_json:
        data = request.get_json()
        auth_token = data.get('auth_token')
        projects = data.get('projects')
        evaluation_id = evaluate_github(auth_token, projects)
        return jsonify({"id": evaluation_id}), 201
    return jsonify({"error": "Invalid request"}), 400

@app.route('/stats', methods=['GET'])
def stats():
    statistics = get_stats()
    return jsonify(statistics), 200

@app.route('/network', methods=['GET'])
def network():
    network_info = get_network()
    return jsonify(network_info), 200

def test_evaluation_zip(client):
    response = client.post('/evaluation', data={'file': (open('test.zip', 'rb'))})
    assert response.status_code == 201
    assert 'id' in response.json

def test_evaluation_github(client):
    response = client.post('/evaluation', json={
        "auth_token": "123e4567-e89b-12d3-a456-426614174000",
        "projects": ["http://github.com/example/repo1", "http://github.com/example/repo2"]
    })
    assert response.status_code == 201
    assert 'id' in response.json

def test_stats(client):
    response = client.get('/stats')
    assert response.status_code == 200
    assert 'all' in response.json

def test_network(client):
    response = client.get('/network')
    assert response.status_code == 200
    assert isinstance(response.json, dict)