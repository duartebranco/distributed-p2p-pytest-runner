# CD PROJECT

## Usage

### Docker

Start the system with docker (main way).

Build with docker:

   ```sh
   # start system
   docker-compose --env-file .env up --build -d
   # stop
   docker-compose down --rmi all --volumes --remove-orphans
   ```

All the curl commands should use the host's local network ip and not the loopback's.
Too allow more than one machine in the same LAN to communicate:
    
   ```sh
    node3_1  |  * Running on http://127.0.0.1:7002
    node3_1  |  * Running on http://192.168.0.2:7002
    
    curl -X GET http://192.168.0.2:7000/network
   ```

## Project Structure

The project is organized as follows:

```
distributed-testing-system
├── src
│   ├── api                # Contains the API endpoints for evaluation, stats, and network and new ones
│   ├── core               # Core functionality including node management and task distribution
│   ├── utils              # Utility functions for handling ZIP files and GitHub interactions
│   └── main.py            # Entry point for running the server and CLI commands
├── .env                   # Environment variables for Docker and manual runs
├── Dockerfile             # Dockerfile for building the application image
├── docker-compose.yml     # Configuration for running the application in Docker
├── entrypoint.sh          # Script to set up environment and launch the Flask server in Docker
├── requirements.txt       # Project dependencies
├── Endpoints.md           # Documentation of the P2P communication protocol
├── relatorio.pdf          # Project report summarizing implementation and results
└── README.md              # Overview and setup instructions for the project
```