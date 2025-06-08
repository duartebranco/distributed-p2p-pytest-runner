# CD PROJECT

## Usage

Please change the .env according to the machines IP and the necessity to run nodes in another machine.

   ```sh
   # Host IP is this machine's local IP address
   # use `$ hostname -I` to find it
   HOST_IP=192.168.0.2

   # This is the seed nodes, it should always give the own's machine IP and port
   SEED_NODES=192.168.0.2:7000
   
   # If you want to use more than one machine,
   # you need to add the IP and port of the new machine
   # like this:
   # SEED_NODES=192.168.0.2:7000,192.168.0.7:7000
   ```

For each change in the .env file, you need to restart the terminal or run `source .env` to apply the changes

### Docker

Start the system with docker (main way).

Build with docker:

   ```sh
   # build for the first time
   docker-compose build --no-cache
   # start system
   docker-compose --env-file .env up --build -d
   # stop
   docker-compose down --rmi all --volumes --remove-orphans
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