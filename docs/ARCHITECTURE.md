## Architecture

This document describes the overall architecture, project structure, and main components of the framework.

---

## Project Structure

The codebase follows a clear separation between frontend, backend, and shared core logic:

```text
llm-evaluation-simple-app/
├── frontend/                    # UI Components
│   └── app.py                  # Streamlit entry point
│
├── backend/                    # Backend Components
│   ├── api_server.py           # FastAPI entry point
│   ├── api/                    # API-specific code
│   │   ├── routes/             # API route handlers
│   │   └── middleware/         # Auth, rate limiting, CORS
│   └── services/               # Backend-specific services
│       ├── data_service.py     # Data retrieval
│       ├── analytics_service.py # Analytics
│       ├── ab_test_service.py  # A/B testing
│       ├── template_service.py # Template management
│       └── custom_metric_service.py # Custom metrics
│
├── core/                      # Shared Core (Business Logic)
│   ├── common/                 # Shared utilities (settings, sanitize, timing)
│   ├── domain/                 # Business logic, strategies
│   │   ├── models.py           # Domain models
│   │   ├── factory.py          # Strategy factory
│   │   └── strategies/         # Evaluation strategies
│   ├── infrastructure/         # DB, LLM adapters
│   │   ├── llm/               # Ollama client, retry policy
│   │   └── db/                # Database connection, repositories
│   ├── services/              # Application services (used by both UI and API)
│   │   ├── evaluation_service.py
│   │   ├── batch_service.py
│   │   └── ab_test_service.py
│   └── ui/                    # UI pages (modular Streamlit pages)
│       └── pages/              # Individual feature pages
│
├── api_client.py              # Python SDK
├── api_examples.py            # API usage examples
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## Layered Design

The architecture is organized into layers:

- **Presentation** – Streamlit UI (frontend)  
- **Application Services** – Orchestration and high-level operations (`core/services`, `backend/services`)  
- **Domain** – Strategies, prompts, domain models (`core/domain`)  
- **Infrastructure** – LLM adapters, database, webhooks (`core/infrastructure`)  

Key principles:

- Frontend (UI) and Backend (API) share core business logic  
- API server reuses application services; services contain **no UI logic**  
- Backend services handle data retrieval, analytics, and other backend-only operations  

---

## Design Patterns

The implementation uses several classic patterns:

- **Strategy** – Pluggable evaluation types:
  - Pairwise, single, comprehensive, code, router, skills, trajectory  
  - Templates, custom metrics, etc.
- **Factory** – `StrategyFactory` builds strategies and wires the LLM adapter  
- **Adapter** – `OllamaAdapter` provides a stable `chat()` interface with retry policy  
- **Repository** – Encapsulated DB access (`JudgmentsRepository`, etc.)  
- **Facade** – `EvaluationService` coordinates strategies, timing, and persistence  
- **Observer (API)** – Webhooks for `evaluation.completed` events  
- **Retry Policy** – Reduces `num_predict` on retries (e.g., 768 → 512) for reliability  

Typical request flow for pairwise evaluation:

```text
UI / API → EvaluationService → Strategy → LLM Adapter → sanitize/parse → Repository → UI/API/Webhook
```

---

## Components

### Streamlit Frontend (`frontend/app.py`)

- Web-based UI for all evaluation features  
- Sidebar navigation with 16 features in 6 categories:
  - LLM Evaluation (7)
  - AI Agent Evaluation (2)
  - Reporting & Analytics (2)
  - Configuration & Setup (2)
  - Code Analysis (1)
  - Testing & Experimentation (1)
- Modular Streamlit pages in `core/ui/pages/`  
- Calls shared services and backend services for data and analytics

### REST API Server (`backend/api_server.py`)

- FastAPI-based API for programmatic access  
- Provides all evaluation endpoints  
- Implements API key authentication and rate limiting  
- Supports webhooks and interactive Swagger/ReDoc docs  
- Uses backend and core services for business logic

### Backend Services (`backend/services/`)

- `data_service.py` – Data retrieval operations  
- `analytics_service.py` – Analytics and statistics  
- `ab_test_service.py` – A/B testing orchestration  
- `template_service.py` – Template management  
- `custom_metric_service.py` – Custom metric management  

### Shared Core (`core/`)

- `services/` – Application services used by both UI and API  
- `domain/` – Strategy implementations and domain models  
- `infrastructure/` – LLM adapters, database repositories, integration code  

### LLM Integration

- **Ollama** used for local LLM inference (generation and evaluation)  
- `core/infrastructure/llm` contains adapters and retry logic  
- All LLM calls go through a single abstraction for consistency and observability

### Database

- SQLite database with multiple tables:
  - `judgments`, `human_annotations`, `router_evaluations`, `skills_evaluations`, `trajectory_evaluations`, `evaluation_runs`, `ab_tests`, `evaluation_templates`, `custom_metrics`  
- See `docs/DATABASE.md` for details.

### Docker

- Docker + Docker Compose for containerized deployment  
- Separate services for Streamlit and API  
- Shared volume for database persistence  

---

## Data Flow (High-Level)

### Web UI Flow

1. User inputs question/response in Streamlit UI  
2. UI calls application services (and Ollama via adapter)  
3. LLM evaluation produces structured metrics and trace  
4. Results are stored in SQLite and rendered in the UI  
5. Dashboards and analytics read from the same database

### API Flow

1. Client sends request to REST API (with API key)  
2. API validates, rate-limits, and forwards to application services  
3. Services call Ollama and database through core infrastructure  
4. Results are stored and returned as JSON  
5. Optional webhook notifications are fired on completion

---

## Evaluation Types (Overview)

The framework supports:

- **LLM as a Judge** – Pairwise comparison, auto model comparison, single response grading  
- **Comprehensive Evaluation** – Multi-metric assessment (5 metrics)  
- **Code-Based Evaluation** – Static and dynamic code analysis  
- **Batch Evaluation** – Multiple test cases from datasets  
- **Human Evaluation** – Human annotations and comparisons  
- **Router Evaluation** – Tool selection and routing assessment  
- **Skills Evaluation** – Domain-specific skill scoring  
- **Trajectory Evaluation** – Multi-step action and reasoning assessment  
- **A/B Testing** – Statistical comparison of models/configurations  
- **Evaluation Templates** – Reusable configs and industry-specific templates  
- **Custom Metrics** – User-defined metrics and scoring functions  
- **Advanced Analytics** – Dashboards and visual analytics  

