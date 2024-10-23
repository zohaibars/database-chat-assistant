# Chat Bot Project

This project implements a chat bot using LangChain and LlamaIndex, with a FastAPI backend.

## Project Structure

```bash
├── app
│   ├── chat_bot.py                 # Redmine data base assistant
│   ├── evaluators
│   │   └── dataset.ipynb           # creating eval datasets on langsmith
│   ├── langchainService
│   │   ├── database_retriver.py
│   │   ├── langchain_util.py
│   │   ├── prompts.py
│   │   ├── sql_agent_graph.py      # main file for Redmine db assistant
│   │   ├── summary_chain
│   │   └── test_nodebooks
│   ├── llamaIndex
│   │   ├── llamaIndexAgentDoc.py
│   │   ├── llamaIndexAgent.py
│   │   ├── llamaIndex_utils.py
│   │   └── rnd
│   ├── main.py                     # main fast api entry point
│   └── utils
│       ├── chat_bot_utils.py
│       ├── connections.py
│       ├── db_info.py
│       ├── models.py
│       └── settings.py
├── docker-compose.yml
├── Dockerfile
├── env_example.txt
├── poetry.lock
├── pyproject.toml
├── README.md
```

## Prerequisites

- Python 3.10 or higher
- Poetry for dependency management
- Docker and Docker Compose (optional, for containerized deployment)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. Install Poetry if you haven't already:
   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Set up environment variables:
   - Copy `env_example.txt` to `.env`
   - Fill in the required environment variables in the `.env` file

4. Set up python environment
    ```python
    python3 -m venv venv
    # Activate venvironment
    . venv/bin/activate
    ```
## Running the Application

### Using Poetry

1. If you've added new dependencies or updated existing ones, update the lock file:
   ```
   poetry lock
   ```

2. Install dependencies:
   ```
   poetry install
   ```

4. Run the FastAPI application:
   ```
   poetry run uvicorn app.main:app --reload --reload-delay 1 --log-level debug --reload-dir app/ --host 0.0.0.0 --port 8080
   ```

   Alternatively, you can run the application with:
   ```
   poetry run python app/main.py
   ```

5. To add new dependencies:
   ```
   poetry add <package-name>
   ```

6. To update dependencies:
   ```
   poetry update
   ```

### Using Docker

1. Build and start the Docker containers:
   ```
   docker-compose up --build
   ```

## Project Components

- `app/main.py`: Entry point of the FastAPI application
- `app/chat_bot.py`: Main chat bot logic
- `app/langchainService/`: LangChain related services and utilities
- `app/llamaIndex/`: LlamaIndex integration components
- `app/utils/`: Utility functions and configurations
- `app/evaluators/`: Evaluation scripts and notebooks

## Configuration

Adjust the settings in `app/utils/settings.py` and environment variables as needed.

## Redmine endpoint 

```python

@app.post("/ask/lang")
async def ask_lang_agent(request: userInput):
    response = ask_lang(query=request.question)
    return response["output"]
```
