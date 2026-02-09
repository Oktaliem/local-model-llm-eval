<h1 align="center"><img src="https://user-images.githubusercontent.com/26521948/72658109-63a1d400-39e7-11ea-9667-c652586b4508.png" alt="Apache JMeter logo" /></h1>
<h4 align="center">SOFTWARE TESTING ENTHUSIAST</h4>
<br>

# Local Model LLM & AI Agent Evaluation Framework

A comprehensive **local-first** evaluation framework for AI agents and Large Language Models (LLMs), built with **Streamlit** (web UI), **FastAPI** (REST API), **Ollama** (local LLMs), and **SQLite** (persistence).

Evaluate models and agents with **LLM-as-a-judge**, static code analysis, rich metrics, and analytics – all running on your own machine.

---

## What is LLM as a Judge?

LLM-as-a-judge uses one model to evaluate the outputs of other models or agents.  
Instead of only using traditional metrics, it leverages an LLM to score and explain:

- Accuracy and correctness
- Relevance to the question
- Clarity and coherence
- Completeness
- Helpfulness and safety  

See **[`docs/CONCEPTS.md`](docs/CONCEPTS.md)** for conceptual details.

---

## Key Features (Overview)

- **LLM Evaluation**
  - Manual and automatic pairwise comparison
  - Single response grading and 5-metric comprehensive evaluation
  - Skills evaluation (math, coding, reasoning, general)
  - Batch evaluation from JSON/CSV
  - Human evaluation and comparison vs. LLM judgments

- **AI Agent Evaluation**
  - Router evaluation (tool selection quality)
  - Trajectory evaluation (multi-step reasoning and actions)

- **Analytics & Configuration**
  - Advanced analytics dashboard
  - Saved judgments & history
  - Evaluation templates (industry-specific)
  - Custom metrics with custom scales

- **Code & Testing**
  - Static and dynamic code evaluation (multi-language)
  - Security and code smell detection (SonarQube-style)
  - A/B testing with statistical analysis

- **Integrations**
  - REST API with API keys and rate limiting
  - Python SDK (`api_client.py`)
  - Webhooks for `evaluation.completed` events

For the full list and details, see **[`docs/USER_GUIDE.md`](docs/USER_GUIDE.md)** and **[`docs/API.md`](docs/API.md)**.

---

## Quickstart

### 1. Install prerequisites

- Python 3.8+  
- [Ollama](https://ollama.ai) installed and running  
- At least one local model pulled (e.g. `ollama pull llama3`)  
- (Optional) Docker + Docker Compose

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit app

```bash
streamlit run frontend/app.py
```

Open `http://localhost:8501` in your browser.

### 4. (Optional) Run with Docker

```bash
docker-compose build
docker-compose up -d
```

See **[`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md)** for full instructions (API server, manual Docker, DB checks, etc.).

---

## Architecture (High-Level)

- **Streamlit frontend** (`frontend/app.py`) – UI for all 16 features in 6 categories  
- **FastAPI backend** (`backend/api_server.py`) – REST API, auth, rate limiting, webhooks  
- **Shared core** (`core/`) – evaluation strategies, services, LLM adapters, DB repositories  
- **SQLite database** – judgments, human annotations, router/skills/trajectory runs, A/B tests, templates, custom metrics  
- **Docker support** – containerized deployment with persistent volumes

See **[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)** and **[`docs/DATABASE.md`](docs/DATABASE.md)** for details.

---

## Documentation

- **Getting Started**: [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md)  
- **User Guide (Web UI)**: [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md)  
- **Concepts & Metrics**: [`docs/CONCEPTS.md`](docs/CONCEPTS.md)  
- **API & Python SDK**: [`docs/API.md`](docs/API.md)  
- **Architecture**: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)  
- **Database & Metrics Schema**: [`docs/DATABASE.md`](docs/DATABASE.md)  
- **Testing**: [`docs/TESTING.md`](docs/TESTING.md)  
- **Troubleshooting**: [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)  

---

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.

