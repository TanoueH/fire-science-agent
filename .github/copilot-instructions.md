# AI Coding Agent Guidelines for Fire Science Agent

Welcome to the Fire Science Agent codebase! This document provides essential guidelines for AI coding agents to be productive in this project. Follow these instructions to understand the architecture, workflows, and conventions.

---

## 🚀 Big Picture Overview

The Fire Science Agent is a **multi-agent framework** for intelligent fire detection in tunnels. It integrates:
- **Physical sensors** and *soft sensors*
- **Fuzzy logic** and **machine learning**
- **FastAPI** for custom tools (e.g., `PredictFireTool`)
- **Docker Compose** for reproducibility

### System Workflow
1. **Curator**: Normalizes sensor data.
2. **Researcher**: Searches literature and technical standards.
3. **Web Scraper**: Extracts summaries from reports.
4. **Analyst**: Predicts risk using fuzzy logic and ML.
5. **Reporter**: Generates automatic reports in Markdown.

---

## 📂 Key Directories and Files

- **`src/`**: Core logic for agents and tools.
  - `main.py`: Entry point for the application.
  - `agents.yaml`: Configuration for multi-agent orchestration.
  - `tasks.yaml`: Definitions of agent tasks.
  - `custom_tool.py`: Example of a custom FastAPI tool.
- **`data/`**: Contains sensor data and outputs.
- **`Dockerfile`** and **`docker-compose.yml`**: Docker setup for reproducibility.
- **`requirements.txt`**: Python dependencies.

---

## 🛠 Developer Workflows

### 1. **Setup**
- Use Python 3.11 and install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Start the application with Docker Compose:
  ```bash
  docker-compose up
  ```

### 2. **Testing**
- Run unit tests:
  ```bash
  pytest
  ```

### 3. **Debugging**
- Use the interactive Swagger UI at `http://localhost:8000/docs`.
- Logs can be accessed via Docker Compose:
  ```bash
  docker-compose logs
  ```

---

## 📏 Project-Specific Conventions

- **Agent Configuration**: Define agents and their tasks in `agents.yaml` and `tasks.yaml`.
- **Custom Tools**: Add FastAPI tools in `src/custom_tool.py`.
- **Data Flow**: Sensor data is normalized by the `Curator` agent before being processed by others.
- **Dockerized Development**: Always use Docker Compose for consistent environments.

---

## 🔗 Integration Points

- **CrewAI**: Orchestrates multi-agent workflows.
- **FastAPI**: Provides RESTful endpoints for tools.
- **Docker Compose**: Ensures reproducibility across environments.
- **GitHub Actions**: Automates CI/CD workflows.

---

## 🧠 Examples

### Adding a New Agent
1. Define the agent in `agents.yaml`:
   ```yaml
   - name: NewAgent
     type: Researcher
     tasks:
       - task_name: AnalyzeData
   ```
2. Implement the agent logic in `src/`.

### Adding a New Endpoint
1. Create a new route in `src/custom_tool.py`:
   ```python
   @app.get("/new-endpoint")
   def new_endpoint():
       return {"message": "Hello, world!"}
   ```

---

By following these guidelines, AI coding agents can contribute effectively to the Fire Science Agent project. If you encounter any ambiguities, consult the `README.md` or ask for clarification.