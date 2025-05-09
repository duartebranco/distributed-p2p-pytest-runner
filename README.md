# CD PROJECT

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

## Project Structure

The project is organized as follows:

```
distributed-testing-system
├── src
│   ├── api                # Contains the API endpoints for evaluation, stats, and network
│   ├── core               # Core functionality including node management and task distribution
│   └── utils              # Utility functions for handling ZIP files and GitHub interactions
├── tests                  # Unit tests for the API, core functionality, and utilities
├── Dockerfile             # Dockerfile for building the application image
├── docker-compose.yml     # Configuration for running the application in Docker
├── requirements.txt       # Project dependencies
├── protocolo.pdf          # Documentation of the P2P communication protocol
├── relatorio.pdf          # Project report summarizing implementation and results
└── README.md              # Overview and setup instructions for the project
```

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd distributed-testing-system
   ```

2. **Install Dependencies**
   It is recommended to use a virtual environment. Install the required packages using:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   You can run the application using Docker:
   ```bash
   docker-compose up
   ```

   Alternatively, you can run the application locally:
   ```bash
   python src/main.py
   ```

## Usage

### API Endpoints

- **POST /evaluation**
  - Submit a ZIP file or a list of GitHub repository URLs for evaluation.
  
- **GET /evaluation/<id>**
  - Check the status of a specific evaluation by its ID.

- **GET /stats**
  - Retrieve statistical information about the tests executed across all nodes.

- **GET /network**
  - Get information about the connected nodes in the P2P network.