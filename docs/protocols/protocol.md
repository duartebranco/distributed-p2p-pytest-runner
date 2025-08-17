# Protocol used in this project

## 
- [evaluation](#evaluation)
  - [POST /evaluation](#post-evaluation)
  - [GET /evaluation](#get-evaluation)
  - [GET /evaluation/<id>](#get-evaluationid)
  - [POST /evaluation/sync_result/<id>](#post-evaluationsync_resultid)
- [worker](#worker)
  - [POST /task](#post-task)
  - [GET /task/results/<evaluation_id>](#get-taskresultsevaluation_id)
- [stats](#stats)
  - [GET /stats](#get-stats)
  - [GET /stats/node](#get-statsnode)
- [network](#network)
  - [GET /network](#get-network)
  - [GET /network/peers](#get-networkpeers)
  - [POST /network/gossip](#post-networkgossip)

## /evaluation

Endpoint used to make requests and query project evaluations. 

### POST /evaluation
**Objective**: Starts a new evaluation and returns the evaluation ID. Projects can be passed via HTTP using the respective access token or through a zip file with the projects. Task redistribution is then performed.

**Response**:
- **201 Request successful**:
  ```json
  {"id": "uuid"} 
  ```
- **400 Invalid request**:
  ```json
  {"error": "Invalid request"}
  ```

### GET /evaluation
**Objective**: Returns to the client a list of all evaluation IDs performed

**Response**:
- **200 OK**:
  ```json
  {"evaluations": ["uuid", ...]}
  ```

### GET /evaluation/<id\>
**Objective**: Returns to the client specific information about an evaluation

**Response**:
- **200 OK**:
  ```json
  {
    "percent_passed": float, 
    "percent_failed": float,
    "percent_passed_per_project": {"project_id": float, ...},
    "percent_failed_per_project": {"project_id": float, ...}, 
    "percent_passed_per_module": {"module_path": float, ...}, 
    "percent_failed_per_module": {"module_path": float, ...}, 
    "executed": int, 
    "in_progress": 0 or 1, 
    "pending": int, 
    "nota_final": int,
    "elapsed_seconds": float 
  }
  ```
- **404 Not found**:
  ```json
  {"error": "not found"}
  ```

### POST /evaluation/sync_result/<id\>
**Objective**: Auxiliary endpoint for use only by nodes with the purpose of synchronizing results and timer for evaluation result consistency

**Response**:
- **200 OK**:
  ```json
  {"status": "ok"}
  ```

## /worker

Endpoint used to assign tasks to nodes and receive task processing results

### POST /task
**Objective**: Multiple test modules are sent to a node to run pytest on them, the modules are then stored in a temporary directory.

**Response**:
- **200 OK**:
  ```json
  {"status": "ack"}
  ```
- **400 Invalid request**:
  ```json
  {"error": "missing evaluation_id"}
  ```

### GET /task/results/<evaluation_id\>
**Objective**: Returns the results of tests run on previously provided modules, if the evaluation is not yet in the node's results it waits until it appears in the results

**Response**:
- **200 OK**:
  ```json
  [
    {
      "project_id": "string",
      "module_path": "string",
      "passed": int,
      "failed": int,
      "errors": int,
      "pytest_stdout": "string",
      "pytest_stderr": "string",
      "total": int
    },
    ...
  ]
  ```

## /stats 

Endpoint used to access statistics from system startup and also from a specific node

### GET /stats
**Objective**: Returns global system statistics


**Response**:
- **200 OK**:
  ```json
  {
    "all": {
      "failed": int, 
      "passed": int, 
      "projects": int, 
      "evaluations": int 
    },
    "nodes": [
      {
        "address": "string",
        "failed": int,
        "passed": int,
        "projects": int,
        "modules": int,
        "evaluations": ["uuid", ...]
      },
      ...
    ]
  }
  ```

### GET /stats/node_stats
**Objective**: Internal auxiliary endpoint to access a node's statistics

**Response**:
- **200 OK**:
  ```json
  {
    "address": "string",
    "failed": int,
    "passed": int,
    "projects": int,
    "modules": int,
    "evaluations": ["uuid", ...]
  }
  ```

## /network

Endpoint focused on obtaining P2P network information

### GET /network
**Objective**: Returns the nodes known by each node within the P2P network

**Response**:
- **200 OK**:
  ```json
  {
    "node_address": ["peer_address", ...],
    ...
  }
  ```


### GET /network/peers
**Objective**: Returns the nodes known by a specific node, internal use.

**Response**:
- **200 OK**:
  ```json
  {"peers": ["address", ...]}
  ```

### POST /network/gossip
**Objective**: Used for node discovery in the network, internal use.

**Response**:
- **200 OK**:
  ```json
  {"status": "ok"}
  ```