# Distributed P2P Pytest Runner

A lightweight, distributed test runner for Python projects. It exposes an HTTP API to submit projects (from GitHub or as a ZIP), distributes test execution (pytest) across a peer-to-peer network of nodes, aggregates results, and serves evaluation status, stats, and network info.

## Features

- P2P task distribution with simple gossip-based peer discovery.
- Workers create a per-project virtual environment and run pytest per test module.
- Aggregated metrics: totals, per-project and per-module breakdowns, elapsed time, and a simple nota_final.
- Network and stats endpoints for observability.

## Usage

1) Please change the `.env` according to your machine's IP and add the IPs of the other machines in which you want to run the system.

Use `$ hostname -I` to find your own machine's IP address.

```sh
# .env
HOST_IP=192.168.0.2
```

Now, add the Seed nodes, you should always give your own machine's IP and port first, and then, if you want to add more machines, you need to add the IP and port of the new machine.

```sh
SEED_NODES=192.168.0.2:7000
```

If you want the system to have more than one machine, you need to add the IP and port of the new machine(s).

```sh
SEED_NODES=192.168.0.2:7000,192.168.0.7:7000
```

For each future change in the `.env` file, you need to restart the terminal or run `source .env` to apply the changes.

2) Build and start the system with docker (main way).

```sh
# build for the first time
docker-compose build --no-cache
# start the system
docker-compose --env-file .env up --build -d
# stop
docker-compose down --rmi all --volumes --remove-orphans
```

3) Verify the network from any node.

```sh
curl -s http://192.168.0.2:7000/network
```

4) Submit an evaluation.

You can submit an evaluation by sending a POST request to the `/evaluation` endpoint with a JSON payload containing, either,  the list ofGitHub project's URLs and the authentication token, or by uploading a ZIP file containing the projects.

```sh
# GitHub URLs
curl -X POST http://192.168.0.2:7000/evaluation \
  -H 'Content-Type: application/json' \
  -d '{
    "auth_token":"YOUR_GITHUB_TOKEN",
    "projects":[
      "https://github.com/org/repo1",
      "https://github.com/org/repo2"
    ]
  }'
```

```sh
# ZIP mode
curl -X POST http://192.168.0.2:7000/evaluation \
  -H 'Content-Type: multipart/form-data' \
  -F "file=@/path/to/projects.zip"
```

5) Check status and stats.

```sh
# List evaluations with results:
curl http://192.168.0.2:7000/evaluation
# Evaluation details:
curl http://192.168.0.2:7000/evaluation/<id>
# Global and per-node stats:
curl http://192.168.0.2:7000/stats
```

If you need to view all of the API endpoints, please look at the `docs/protocols/protocol.md`.

## How does this project work?

- Nodes start with NODE_ADDRESS and SEED_NODES (set by `.env`).
- Simple gossip spreads peer info via POST /network/gossip.
- Evaluations:
  - Projects are cloned (GitHub) or unpacked (ZIP).
  - Test modules (tests/test_*.py) are split and shipped to nodes with POST /task.
  - Nodes create a venv inside each project folder, run pytest per module, and expose results via GET /task/results/<evaluation_id>.
  - The initiator aggregates results and syncs them to peers with POST /evaluation/sync_result/<id>.
- Stats:
  - Global stats are aggregated locally.
  - Per-node stats are computed from module-level execution provenance and fetched from peers.

## Project Structure

The project is organized as follows:

```
distributed-testing-system
├── docs
│   ├── reports           # Contains this project's report and the assignment given to students
│   ├── protocols         # Contains the API protocols used in the project
├── src
│   ├── api               # Contains the API endpoints for evaluation, stats, and network and new ones
│   ├── core              # Core functionality including node management and task distribution
│   ├── utils             # Utility functions for handling ZIP files and GitHub interactions
│   └── main.py           # Entry point for running the server and CLI commands
├── .env                   # Environment variables for Docker and manual runs
├── Dockerfile             # Dockerfile for building the application image
├── docker-compose.yml     # Configuration for running the application in Docker
├── entrypoint.sh          # Script to set up environment and launch the Flask server in Docker (for running manually)
├── requirements.txt       # Project dependencies
└── README.md              # Overview and setup instructions for the project
```
