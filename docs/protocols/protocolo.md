# Protocolo usado neste projeto

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

Endpoint usado para realizar pedidos e consultar avaliações de projetos.

### POST /evaluation
**Objetivo**: Começa uma nova avaliação e devolve o id da avaliação em questão, os projetos passados podem ser através de http passando o respetivo token de acesso ou através de um ficheiro zip com os projetos. Em seguida é feita a redistribuição das tarefas.

**Resposta**:
- **201 Pedido realizado com sucesso**:
  ```json
  {"id": "uuid"}
  ```
- **400 Pedido Inválido**:
  ```json
  {"error": "Invalid request"}
  ```

### GET /evaluation
**Objetivo**: Devolve ao cliente a listagem de todos os ids das avaliações realizadas

**Resposta**:
- **200 OK**:
  ```json
  {"evaluations": ["uuid", ...]}
  ```

### GET /evaluation/<id\>
**Objetivo**: Devolve ao cliente informações específicas de uma avaliação

**Resposta**:
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
- **404 Não existe**:
  ```json
  {"error": "not found"}
  ```

### POST /evaluation/sync_result/<id\>
**Objetivo**: Endpoint auxiliar com uso só para os nodes com o objetivo de sincronizar os resultados e o temporizador para a consistência dos resultados das avaliações

**Resposta**:
- **200 OK**:
  ```json
  {"status": "ok"}
  ```

## /worker

Endpoint usado para associar tarefas aos nodes e receber os resultados do processamento das tarefas

### POST /task
**Objetivo**: São enviados vários módulos de teste ao um node para correr o pytest sobre estes, os módulos são guardados em seguida numa diretória temporária.

**Resposta**:
- **200 OK**:
  ```json
  {"status": "ack"}
  ```
- **400 Pedido Inválido**:
  ```json
  {"error": "missing evaluation_id"}
  ```

### GET /task/results/<evaluation_id\>
**Objetivo**: Retorna os resultados dos testes corridos sobre os módulos anteriormente fornecidos, se a avaliação ainda não está nos resultados do node espera até aparecer nos resultados

**Resposta**:
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

Endpoint usado para aceder as estatísticas desde do início do sistema e também de um node específico

### GET /stats
**Objetivo**: Retorna as estatísticas globais do sistema


**Resposta**:
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
**Objetivo**: Endpoint interno auxiliar para aceder as estatísticas de um node

**Resposta**:
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

Endpoint focado em obter informações da rede P2P

### GET /network
**Objetivo**: Retorna os nodes conhecidos por cada node dentro da rede P2P

**Resposta**:
- **200 OK**:
  ```json
  {
    "node_address": ["peer_address", ...],
    ...
  }
  ```


### GET /network/peers
**Objetivo**: Retorna os nodes conhecidos por um node específico, uso interno.

**Resposta**:
- **200 OK**:
  ```json
  {"peers": ["address", ...]}
  ```

### POST /network/gossip
**Objetivo**: Usado para descoberta de nodes na rede, uso interno.

**Resposta**:
- **200 OK**:
  ```json
  {"status": "ok"}
  ```
