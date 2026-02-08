## API Reference

The framework exposes a REST API and a Python SDK for programmatic access to all evaluation features.

---

## Authentication

All API endpoints (except `/health` and `/api/v1/keys`) require authentication using an API key.

**Create an API Key:**

```bash
curl -X POST "http://localhost:8000/api/v1/keys" \
  -H "Content-Type: application/json" \
  -d '{"description": "My API key"}'
```

**Use API Key:**

```bash
curl -X GET "http://localhost:8000/api/v1/evaluations" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## Rate Limiting

- Default: 100 requests per hour per API key  
- Configurable via `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW` environment variables  
- Returns `429 Too Many Requests` when limit is exceeded

---

## Core Endpoints

### Health Check

- `GET /health` – API health (no auth required)

### API Key Management

- `POST /api/v1/keys` – Create a new API key (no auth required)  
- `GET /api/v1/keys` – List all API keys (requires auth)

### Evaluation Endpoints

#### Comprehensive Evaluation

```bash
POST /api/v1/evaluations/comprehensive
{
  "question": "What is AI?",
  "response": "AI is artificial intelligence...",
  "judge_model": "llama3",
  "save_to_db": true
}
```

#### Code Evaluation

```bash
POST /api/v1/evaluations/code
{
  "code": "def hello(): return 'world'",
  "language": "python",
  "test_inputs": ["5"],
  "expected_output": "5",
  "save_to_db": true
}
```

Code evaluation uses static analysis and execution; it does **not** require a judge model. Supported languages include `python`, `javascript`, `typescript`, `swift`, `kotlin`, `java`, `go`, `html`, `css`, `objective-c`.

#### Router Evaluation

```bash
POST /api/v1/evaluations/router
{
  "query": "Calculate 2+2",
  "available_tools": [
    {"name": "calculator", "description": "Performs calculations"}
  ],
  "selected_tool": "calculator",
  "expected_tool": "calculator",
  "judge_model": "llama3",
  "save_to_db": true
}
```

#### Skills Evaluation

```bash
POST /api/v1/evaluations/skills
{
  "skill_type": "mathematics",
  "question": "Solve: x² + 5x + 6 = 0",
  "response": "x = -2 or x = -3",
  "reference_answer": "x = -2, -3",
  "domain": "algebra",
  "judge_model": "llama3",
  "save_to_db": true
}
```

#### Trajectory Evaluation

```bash
POST /api/v1/evaluations/trajectory
{
  "task_description": "Process a customer order",
  "trajectory": [
    {"action": "receive_order", "description": "Receive customer order"},
    {"action": "process_payment", "description": "Process payment"}
  ],
  "trajectory_type": "action_sequence",
  "judge_model": "llama3",
  "save_to_db": true
}
```

#### Manual Pairwise Comparison

```bash
POST /api/v1/evaluations/pairwise
{
  "question": "Explain quantum computing",
  "response_a": "Quantum computing uses qubits...",
  "response_b": "Quantum computing leverages quantum mechanics...",
  "judge_model": "llama3",
  "save_to_db": true
}
```

---

## A/B Testing Endpoints

```bash
# Create A/B test
POST /api/v1/ab-tests
{
  "test_name": "Llama3 vs Mistral",
  "variant_a_name": "Llama3",
  "variant_b_name": "Mistral",
  "variant_a_config": {"model_a": "llama3", "task_type": "general"},
  "variant_b_config": {"model_b": "mistral", "task_type": "general"},
  "evaluation_type": "comprehensive",
  "test_cases": [
    {"question": "What is AI?"},
    {"question": "Explain machine learning"}
  ]
}

# List all A/B tests
GET /api/v1/ab-tests?limit=50

# Get specific test
GET /api/v1/ab-tests/{test_id}

# Run A/B test
POST /api/v1/ab-tests/{test_id}/run
{
  "test_id": "test-uuid",
  "judge_model": "llama3"
}
```

---

## Templates & Custom Metrics

### Evaluation Templates

```bash
# Create template
POST /api/v1/templates
{
  "template_name": "My Custom Template",
  "evaluation_type": "comprehensive",
  "industry": "healthcare",
  "template_config": {
    "metrics": {
      "accuracy": {"weight": 0.4},
      "relevance": {"weight": 0.3},
      "coherence": {"weight": 0.2},
      "hallucination": {"weight": 0.1}
    },
    "task_type": "technical"
  }
}

# List templates
GET /api/v1/templates?evaluation_type=comprehensive&industry=healthcare

# Get template
GET /api/v1/templates/{template_id}

# Delete template
DELETE /api/v1/templates/{template_id}

# Apply template
POST /api/v1/templates/{template_id}/apply
{
  "template_id": "template-uuid",
  "evaluation_data": {
    "question": "Test",
    "response": "Test response"
  }
}
```

### Custom Metrics

```bash
# Create custom metric
POST /api/v1/custom-metrics
{
  "metric_name": "Empathy Score",
  "evaluation_type": "general",
  "metric_definition": "Measures empathy in responses",
  "scale_min": 0.0,
  "scale_max": 10.0,
  "weight": 1.0
}

# List metrics
GET /api/v1/custom-metrics?evaluation_type=general&domain=healthcare

# Get metric
GET /api/v1/custom-metrics/{metric_id}

# Deactivate metric
DELETE /api/v1/custom-metrics/{metric_id}

# Evaluate with metric
POST /api/v1/custom-metrics/{metric_id}/evaluate
{
  "metric_id": "metric-uuid",
  "question": "Test question",
  "response": "Test response",
  "judge_model": "llama3"
}
```

---

## Data Retrieval & Analytics

### Data Retrieval

- `GET /api/v1/evaluations?evaluation_type=comprehensive&limit=50` – Get evaluations  
- `GET /api/v1/analytics/overview` – Get analytics overview

### Webhook Management

- `POST /api/v1/webhooks` – Create a webhook  
- `GET /api/v1/webhooks` – List all webhooks  
- `DELETE /api/v1/webhooks/{webhook_id}` – Delete a webhook

**Example:**

```bash
POST /api/v1/webhooks
{
  "url": "https://your-server.com/webhook",
  "events": ["evaluation.completed"],
  "secret": "your_webhook_secret"
}
```

Webhook payload example:

```json
{
  "event": "evaluation.completed",
  "timestamp": "2024-01-01T12:00:00",
  "data": {
    "type": "comprehensive",
    "evaluation_id": "uuid",
    "overall_score": 8.5
  }
}
```

If a secret is provided, webhooks include an `X-Webhook-Signature` header with HMAC-SHA256 signature for verification.

---

## Python SDK

The `api_client.py` module provides a high-level Python SDK.

```python
from api_client import EvaluationClient

# Initialize client
client = EvaluationClient(
    api_key="your_api_key",
    base_url="http://localhost:8000"
)

# Comprehensive evaluation
result = client.evaluate_comprehensive(
    question="What is machine learning?",
    response="Machine learning is..."
)
print(f"Overall Score: {result['overall_score']:.2f}/10")

# Code evaluation (static analysis)
result = client.evaluate_code(
    code="def hello(): return 'world'",
    language="python",
)

# Router evaluation
router_result = client.evaluate_router(
    query="Calculate 2+2",
    available_tools=[{"name": "calculator", "description": "Calculates"}],
    selected_tool="calculator",
)

# Skills, trajectory, pairwise
skills_result = client.evaluate_skills(
    skill_type="mathematics",
    question="2+2=?",
    response="4",
)

traj_result = client.evaluate_trajectory(
    task_description="Process order",
    trajectory=[{"action": "step1", "description": "First step"}],
)

pairwise_result = client.evaluate_pairwise(
    question="Explain AI",
    response_a="AI is...",
    response_b="AI means...",
)

# Data and analytics
evaluations = client.get_evaluations(evaluation_type="comprehensive", limit=10)
analytics = client.get_analytics_overview()

# Webhooks
webhook = client.create_webhook(
    url="https://your-server.com/webhook",
    events=["evaluation.completed"],
)
```

---

## Interactive API Docs

FastAPI automatically exposes interactive documentation:

- Swagger UI: `http://localhost:8000/docs`  
- ReDoc: `http://localhost:8000/redoc`

These provide:

- Complete API reference  
- Interactive testing interface  
- Request/response schemas  
- Authentication testing

---

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Evaluate Model

on: [push]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Evaluation
        run: |
          pip install -r requirements.txt
          python api_examples.py
```

