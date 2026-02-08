## Getting Started

This framework is a Streamlit + FastAPI application for evaluating AI agents and Large Language Models (LLMs) locally using Ollama.

It supports:
- **Web UI (Streamlit)**
- **REST API (FastAPI)**
- **Python SDK (`api_client.py`)**

Use this guide to get from zero to a running app.

---

## Installation

### 1. Clone or navigate to this repository

```bash
cd llm-judge-simple-app
```

### 2. Install Ollama

Download and install Ollama from `https://ollama.ai`

Or use package managers:

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
```

### 3. Start Ollama and pull a model

```bash
# Start Ollama (usually runs automatically after installation)
ollama serve

# Pull a model (in a new terminal)
ollama pull llama3
# or
ollama pull mistral
# or
ollama pull llama2
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## Three Ways to Use the Framework

This framework provides **three different ways** to evaluate LLMs, each suited for different use cases:

```text
┌─────────────────────────────────────────────────────────────────┐
│ METHOD 1: Web Portal (Streamlit UI)                             │
├─────────────────────────────────────────────────────────────────┤
│ • Interactive web interface                                     │
│ • Direct Python function calls (no HTTP)                        │
│ • Used by: Human users, manual testing                          │
│ • Access: http://localhost:8501                                 │
│ • Code: frontend/app.py                                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ METHOD 2: REST API (Direct HTTP)                               │
├─────────────────────────────────────────────────────────────────┤
│ • Programmatic access via HTTP                                 │
│ • Used by: External applications, automation                   │
│ • Access: http://localhost:8000                                │
│ • Code: backend/api_server.py                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ METHOD 3: Python SDK (api_client.py)                           │
├─────────────────────────────────────────────────────────────────┤
│ • Wrapper around REST API                                      │
│ • Used by: Python developers, scripts, CI/CD                   │
│ • Access: Import api_client.py                                 │
│ • Code: api_client.py                                          │
└─────────────────────────────────────────────────────────────────┘
```

### Comparison Table

| Method | Interface | Access | Use Case | Code Location |
|--------|-----------|--------|----------|---------------|
| **1. Web Portal** | Browser UI | `http://localhost:8501` | Human users, manual testing | `frontend/app.py` |
| **2. REST API** | HTTP endpoints | `http://localhost:8000` | External apps, automation | `backend/api_server.py` |
| **3. Python SDK** | Python functions | Import `api_client.py` | Python scripts, CI/CD | `api_client.py` |

---

## Running the App

### Option 1: Run Directly (Local)

Run the Streamlit app:

```bash
# From project root
streamlit run frontend/app.py
```

The app will open in your browser at `http://localhost:8501`.

Run the API server separately (optional but recommended):

```bash
# From project root
uvicorn backend.api_server:app --host 0.0.0.0 --port 8000
```

### Option 2: Run with Docker (Recommended)

1. **Build and run with Docker Compose:**

```bash
# Build the Docker image
docker-compose build

# Start the container in detached mode
docker-compose up -d

# View logs (follow mode)
docker-compose logs -f

# Check container status
docker-compose ps

# Stop the container
docker-compose down

# Rebuild after code changes
docker-compose build && docker-compose up -d

# Restart without rebuilding
docker-compose restart
```

2. **Or build and run manually:**

```bash
# Build the image
docker build -t llm-judge-app .

# Run the container
docker run -d \
  -p 8501:8501 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  -v $(pwd)/data:/app/data \
  --name llm-judge-app \
  llm-judge-app
```

3. **Access the app:**

- Open your browser at `http://localhost:8501`
- The database will be persisted in the `./data` directory

4. **Verify database:**

```bash
# Check if database exists
./check-db.sh

# Or manually check
docker exec llm-judge-app ls -lh /app/data/
ls -lh ./data/

# View database contents (if sqlite3 is installed)
sqlite3 ./data/llm_judge.db ".tables"
```

**Note:** The database file (`llm_judge.db`) will be created automatically when you save your first judgment.

### Option 3: Run API Server Only

Run API server with Docker Compose:

```bash
# Start both Streamlit app and API server
docker-compose up -d

# Or start only the API server
docker-compose up -d llm-judge-api
```

Run API server locally:

```bash
pip install -r requirements.txt
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

---

## Requirements

- Python 3.8+ (or Docker)
- Ollama installed and running
- At least one Ollama model pulled (e.g., `llama3`, `mistral`, `llama2`)
- Docker and Docker Compose (for containerized deployment)

---

## Configuring Ollama Host

Set `OLLAMA_HOST` environment variable to point to your Ollama instance:

- Local: `http://localhost:11434`
- Docker default (macOS/Windows): `http://host.docker.internal:11434`
- Docker (Linux): use `--network host` or configure accordingly
- Remote: `http://your-ollama-server:11434`

