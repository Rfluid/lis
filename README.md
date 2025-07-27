# Lis Secretary Agent

**Lis** stands for **"Lean Interactive Secretary"**. It is a personal assistant agent that can manage your calendar and schedule meetings for you. It also stands for:

- **Lightweight Intelligent Support**
- **Life Information Specialist**
- **Language-Integrated Secretary**
- **Lifestyle Integration Scheduler**

...and more, depending on your use case.

## Features

- **Intelligent Calendar Management**: Create, update, and delete calendar events.
- **Event Retrieval**: Fetch and display your schedule based on various criteria.
- **Natural Language Understanding**: Interact with Lis using conversational language.
- **Contextual Awareness**: Lis adapts its tone and actions based on the conversation flow.
- **Error Handling**: Robust error management to ensure smooth operation.
- **RAG Integration**: Retrieve information from a vector database for general queries.
- **Docker Support**: Easily set up and run the application using Docker Compose.

## Installation

### Prerequisites

- Python 3.12
- Docker (for Docker-based setup)

### Create a Virtual Environment

```bash
python3 -m venv venv
```

### Activate the Virtual Environment

```bash
# On Linux/macOS
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### Install Dependencies

Install the necessary Python dependencies from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Usage

Before running the application, ensure you have set up your `.env` file and placed the required data files in the `data/` and `prompts/` directories as described in the "Environment Variables" and "Required Files" sections.

### Running Locally (without Docker)

You can run the backend and frontend separately for local development.

1.  **Start the Backend Server (FastAPI)**
    This command starts the backend server using Uvicorn, typically on `http://127.0.0.1:8000`.

    ```bash
    make run
    # Or directly with uvicorn:
    # uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
    ```

2.  **Start the Frontend UI (Streamlit)**
    This command launches the Streamlit UI, typically at `http://localhost:8501`, and connects to the backend defined by `API_URL` in your `.env` file.

    ```bash
    streamlit run frontend.py
    ```

### Running with Docker Compose

Docker Compose simplifies the setup by orchestrating both the backend and frontend services.

1.  **Build the Docker Image**
    First, build the Docker image for the Lis application:

    ```bash
    docker build -t lis:latest .
    ```

2.  **Run in Production Mode**
    This will start the backend (on port `8000`) and frontend (on port `8501`) containers in production mode.

    ```bash
    make prod
    # Or directly:
    # docker compose up
    ```

3.  **Run in Development Mode (with Live Reload)**
    For development with live code changes, use the development Docker Compose file. This mounts your local project directory into the container.

    ```bash
    make dev
    # Or directly:
    # docker-compose -f docker-compose.dev.yml up -d --build
    ```

4.  **Stop the Containers**
    To stop and remove the running Docker containers:

    ```bash
    make prod-down # For production containers
    # Or:
    make dev-down # For development containers
    # Or directly:
    # docker compose down --remove-orphans
    ```

    > **Note:** Make sure your `.env` file contains paths appropriate for the Docker environment (e.g., `DATA_DIR=/app/data`).

## Environment Variables

This project uses environment variables for configuration. Copy the `example.env` file to create your `.env` file in the root directory and modify it:

```bash
cp example.env .env
```

## Required Files

Make sure to include your own configuration files in the specified directories:

### `data/` Directory

This directory holds sensitive or changeable data required by the application.

- **`data/service-account.google.json`**:
    - **Purpose**: This file contains the credentials for your Google Service Account, which Lis uses to authenticate and interact with the Google Calendar API.
    - **How to get it**: You need to create a service account in your Google Cloud Project, enable the Google Calendar API, and then generate and download its JSON key file.
    - **Example**: A template is provided at `data/service-account.google.example.json`.
- **`data/calendars.json`**:
    - **Purpose**: This JSON file defines the calendars Lis should be aware of and their corresponding ICS (iCalendar) URLs. Lis will fetch events from these URLs when querying calendars.
    - **Format**: It's a list of objects, each with a `name` (for display/identification) and a `url` (the ICS feed URL).
    - **Example**: A template is provided at `data/calendars.example.json`.

### `prompts/` Directory

This directory stores the Markdown-based prompt templates used by the LLMs.

- **`prompts/system.md`**:
    - **Purpose**: Contains the core system instructions for Lis. This prompt defines Lis's role, core principles (human-like interaction, calendar management, conversational flow), personality guidelines, and example behaviors. It acts as the foundational context for the agent's reasoning.
    - **Example**: A template is provided at `prompts/system.example.md`.
- **`prompts/evaluate_tools.md`**:
    - **Purpose**: This prompt guides the LLM on how to select the appropriate tool (`search_calendars`, `rag`, `generate_response`, `get_current_date`) based on user input and chat history. It includes rules, redundancy prevention, and error prevention guidelines for tool selection.
    - **Example**: A template is provided at `prompts/evaluate_tools.example.md`.
- **`prompts/error_handler.md`**:
    - **Purpose**: This prompt is used when an error occurs during agent execution. It provides instructions to the LLM on how to handle the error and avoid repeating it in subsequent attempts.
    - **Example**: A template is provided at `prompts/error_handler.example.md`.

## Project Structure

- `src/`: Source code of the application
- `tests/`: Test files for the application
- `data/`: Persistent data required by the application (e.g., calendar configurations, service account keys)
- `prompts/`: Prompt templates for the agent's LLMs
- `frontend.py`: Entry point for the Streamlit user interface
- `requirements.txt`: Python dependencies for the project
- `Makefile`: Terminal task definitions for common operations (e.g., `run`, `prod`, `dev`)
- `.env`: Environment configuration variables (e.g., API keys, database URIs)
- `README.md`: Project documentation
- `.dockerignore`: Specifies files and directories to ignore when building Docker images
- `docker-compose.yml`: Docker Compose configuration for production deployment
- `docker-compose.dev.yml`: Docker Compose configuration for development deployment with live reload
- `Dockerfile`: Dockerfile for building the application image

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for discussion.

## License

This project is licensed under the MIT License. See the [LICENSE](https://mit-license.org/) file for details.

## Contact

For any inquiries, please contact the maintainers at:
[ruy.vieiraneto@gmail.com](mailto:ruy.vieiraneto@gmail.com)
