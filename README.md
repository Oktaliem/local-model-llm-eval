# LLM & AI Agent Evaluation Framework

A comprehensive Streamlit application for evaluating AI agents and Large Language Models (LLMs) with multiple evaluation metrics, benchmarking capabilities, and observability features.

## What is LLM as a Judge?

LLM as a Judge uses large language models (LLMs) to evaluate the outputs of other AI systems or language models. Instead of relying solely on human reviewers or traditional metrics, this approach leverages the advanced reasoning capabilities of LLMs to assess criteria such as:

- Accuracy and correctness
- Relevance to the question
- Clarity and coherence
- Completeness
- Helpfulness

## Features

### Feature Categories

This framework provides evaluation capabilities for two main use cases:

#### 🤖 LLM Evaluation Features
Evaluate text outputs from Large Language Models (responses, answers, generated content)

- **🔀 Manual Pairwise Comparison**: Compare two LLM responses to determine which one is better
- **🤖 Auto Pairwise Comparison**: Automatically generate responses from two different models and judge them
- **📊 Single Response Grading**: Evaluate a single LLM response with detailed feedback and scoring
- **🎯 Comprehensive Evaluation**: Multi-metric evaluation with accuracy, relevance, coherence, hallucination detection, and toxicity checking
- **🎓 Skills Evaluation**: Domain-specific skill assessments (mathematics, coding, reasoning, general) for LLM responses
- **📦 Batch Evaluation**: Upload datasets (JSON/CSV) and evaluate multiple LLM test cases at once
- **👤 Human Evaluation**: Add human annotations and compare with LLM judgments

#### 🤖 AI Agent Evaluation Features
Evaluate agent behavior, decisions, and multi-step actions in AI agent systems

- **🔀 Router Evaluation**: Evaluate routing decisions and tool selection in AI agent systems
  - Assesses tool/function selection accuracy
  - Analyzes routing paths and decision trees
  - Metrics: Tool Accuracy, Routing Quality, Reasoning Quality
- **🛤️ Trajectory Evaluation**: Evaluate multi-step action sequences, agent trajectories, and reasoning chains
  - Analyzes step-by-step agent behavior
  - Metrics: Step Quality, Path Efficiency, Reasoning Chain, Planning Quality

#### 📊 Reporting & Analytics Features
View, analyze, and manage evaluation results

- **📈 Advanced Analytics**: Comprehensive analytics and visualizations for all evaluation data
- **💾 Saved Judgments & Dashboard**: View, filter, and search all saved evaluations

#### ⚙️ Configuration & Setup Features
Customize and configure evaluation workflows

- **📋 Evaluation Templates**: Reusable evaluation configurations and industry-specific templates
- **🎯 Custom Metrics**: User-defined evaluation metrics with custom scoring functions for LLM responses

#### 💻 Code Analysis Features
Static code analysis and quality assessment with SonarQube-like capabilities

- **💻 Code-Based Evaluation**: Comprehensive static code analysis
  - **Multi-language Support**: 
    - Backend: Python, JavaScript (Node.js), TypeScript, Java, Go
    - Web: JavaScript, TypeScript, HTML, CSS
    - iOS: Swift, Objective-C
    - Android: Kotlin, Java
  - **Syntax Checking**: AST parsing (Python) or pattern-based validation (other languages)
  - **Execution Testing**: Safe subprocess execution with timeout (Python, JavaScript, Swift)
  - **Quality Metrics**: Lines of code, functions, classes, complexity, maintainability, readability
  - **Security Vulnerability Detection** (SonarQube-like):
    - SQL injection risks
    - XSS (Cross-Site Scripting) risks
    - Hardcoded credentials (passwords, API keys, secrets)
    - Insecure function usage (eval, os.system, subprocess with shell=True)
    - Weak cryptography (MD5, SHA1)
    - Unsafe deserialization (pickle.loads, yaml.load)
    - Severity levels: BLOCKER, CRITICAL, MAJOR
  - **Code Smell Detection** (SonarQube-like):
    - Long methods/functions (>50 lines)
    - Large classes (>300 lines)
    - Too many parameters (>7)
    - Duplicate code
    - Unused variables
    - Magic numbers
    - Empty catch/except blocks
    - Severity levels: MAJOR, MINOR, INFO
  - **Advanced Metrics**:
    - Cyclomatic complexity
    - Cognitive complexity
    - Technical debt ratio
  - **Score Calculation**: Overall score penalizes security vulnerabilities and code smells
  - Does not use LLM as a judge (uses static analysis)

#### 🧪 Testing & Experimentation Features
Experimental and comparative testing capabilities

- **🧪 A/B Testing**: Compare different models/configurations with statistical significance testing

#### 🔌 Integration Features
Programmatic access and integration

- **🔌 REST API**: Programmatic access to all evaluation features with authentication and webhooks

### Feature Summary

| Category | Count | Features |
|----------|-------|----------|
| **LLM Evaluation** | 7 | Pairwise, Auto Compare, Single, Comprehensive, Skills, Batch, Human |
| **AI Agent Evaluation** | 2 | Router Evaluation, Trajectory Evaluation |
| **Reporting & Analytics** | 2 | Advanced Analytics, Saved Judgments & Dashboard |
| **Configuration & Setup** | 2 | Evaluation Templates, Custom Metrics |
| **Code Analysis** | 1 | Code-Based Evaluation |
| **Testing & Experimentation** | 1 | A/B Testing |
| **Integration** | 1 | REST API |
| **Total** | **16** | All features listed above |

**Note:** Both Router and Trajectory Evaluation use LLM as a judge, but they evaluate **agent behavior** (decisions, actions, trajectories) rather than just text outputs. Code-Based Evaluation uses static analysis and does not use LLM as a judge.

### Advanced Features
- **💾 Enhanced Database Storage**: Save all judgments with structured metrics and evaluation traces
- **📊 Metrics Dashboard**: Visualize aggregate statistics and performance trends
- **🔍 Evaluation Tracing**: Track evaluation steps, model calls, and execution paths for observability
- **⏹️ Stop Button**: Cancel running evaluations at any time
- **📝 Detailed Feedback**: Get comprehensive evaluations with reasoning and explanations
- **⚙️ Model Selection**: Choose from available Ollama models (llama3, mistral, llama2, etc.)
- **🐳 Docker Support**: Run the app in a containerized environment with persistent storage
- **🔧 Configurable**: Customize Ollama host URL and database paths
- **🔐 API Authentication**: API key-based authentication with rate limiting
- **🔔 Webhook Support**: Receive notifications when evaluations complete

## Installation

1. Clone or navigate to this repository:
```bash
cd llm-judge-simple-app
```

2. Install Ollama:
   
   Download and install Ollama from https://ollama.ai
   
   Or use package managers:
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

3. Start Ollama and pull a model:
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

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

This framework provides **three different ways** to evaluate LLMs, each suited for different use cases:

### Three Ways to Evaluate LLMs

```
┌─────────────────────────────────────────────────────────────────┐
│ METHOD 1: Web Portal (Streamlit UI)                             │
├─────────────────────────────────────────────────────────────────┤
│ • Interactive web interface                                    │
│ • Direct Python function calls (no HTTP)                       │
│ • Used by: Human users, manual testing                          │
│ • Access: http://localhost:8501                                │
│ • Code: frontend/app.py                                         │
│                                                                 │
│ Example: User clicks "Evaluate" button in browser             │
│          → Calls evaluate_comprehensive() directly             │
│          → No HTTP, no API, direct function call               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ METHOD 2: REST API (Direct HTTP)                               │
├─────────────────────────────────────────────────────────────────┤
│ • Programmatic access via HTTP                                  │
│ • Can use curl, Postman, any HTTP client                         │
│ • Used by: External applications, automation                    │
│ • Access: http://localhost:8000                                │
│ • Code: backend/api_server.py                                  │
│                                                                 │
│ Example: curl -X POST http://localhost:8000/api/v1/...        │
│          → HTTP request                                         │
│          → FastAPI processes it                                  │
│          → Returns JSON response                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ METHOD 3: Python SDK (api_client.py)                           │
├─────────────────────────────────────────────────────────────────┤
│ • Wrapper around REST API                                       │
│ • Simple Python functions                                       │
│ • Used by: Python developers, scripts, CI/CD                    │
│ • Access: Import api_client.py                                  │
│ • Code: api_client.py                                           │
│                                                                 │
│ Example: client.evaluate_comprehensive(...)                   │
│          → SDK makes HTTP request to REST API                  │
│          → Converts JSON to Python dict                        │
│          → Returns easy-to-use Python object                   │
└─────────────────────────────────────────────────────────────────┘
```

#### Comparison Table

| Method | Interface | Access | Use Case | Code Location |
|--------|-----------|--------|----------|---------------|
| **1. Web Portal** | Browser UI | `http://localhost:8501` | Human users, manual testing | `frontend/app.py` |
| **2. REST API** | HTTP endpoints | `http://localhost:8000` | External apps, automation | `backend/api_server.py` |
| **3. Python SDK** | Python functions | Import `api_client.py` | Python scripts, CI/CD | `api_client.py` |

#### Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│ METHOD 1: Web Portal                                        │
│ frontend/app.py                                              │
│   ↓ Direct Python imports                                    │
│   ↓ from core.services import EvaluationService              │
│   ↓ from backend.services import ...                         │
│   ↓ Direct function calls (no HTTP)                          │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ All methods use the same
                          │ core evaluation services
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Core Services (core/services/)                               │
│ • EvaluationService                                          │
│ • Evaluation strategies                                      │
│ • LLM integration                                            │
│ • Database operations                                        │
└─────────────────────────────────────────────────────────────┘
                          ▲
                          │
┌─────────────────────────────────────────────────────────────┐
│ METHOD 2: REST API                                           │
│ backend/api_server.py                                         │
│   ↓ HTTP requests                                            │
│   ↓ POST /api/v1/evaluations/comprehensive                   │
│   ↓ FastAPI routes                                           │
│   ↓ Calls core services                                      │
└─────────────────────────────────────────────────────────────┘
                          ▲
                          │
┌─────────────────────────────────────────────────────────────┐
│ METHOD 3: Python SDK                                         │
│ api_client.py                                                │
│   ↓ Python function calls                                    │
│   ↓ client.evaluate_comprehensive(...)                       │
│   ↓ Makes HTTP requests                                      │
│   ↓ To REST API (Method 2)                                   │
└─────────────────────────────────────────────────────────────┘
```

#### Key Differences

**Method 1 (Web Portal):**
- ✅ No HTTP overhead
- ✅ Fastest (direct function calls)
- ✅ Interactive UI with visualizations
- ✅ Designed for human users
- ✅ Browser-based interface (no client-side installation if using Docker)

**Method 2 (REST API):**
- ✅ Language agnostic (any HTTP client)
- ✅ Can use curl, Postman, JavaScript, Go, etc.
- ✅ Standard REST interface

**Method 3 (Python SDK):**
- ✅ Easiest for Python developers
- ✅ No HTTP knowledge needed
- ✅ Type-safe Python functions
- ✅ Automatic authentication handling

> **Note**: All three methods use the same core evaluation services, so they produce identical results. The difference is only in how you access them.

---

### Option 1: Run Directly (Local)

Run the Streamlit app:
```bash
# From project root
streamlit run frontend/app.py
```

The app will open in your browser at `http://localhost:8501`

**Note**: The API server can be run separately:
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

**Note:** The database file (`llm_judge.db`) will be created automatically when you save your first judgment. It will be stored at:
- Inside container: `/app/data/llm_judge.db`
- On host machine: `./data/llm_judge.db`

**Note:** For Docker, make sure Ollama is running on your host machine. The container connects to Ollama using `host.docker.internal:11434` (macOS/Windows) or you may need to use `--network host` on Linux.

### Option 3: Run API Server

The framework includes a REST API server for programmatic access.

1. **Run API server with Docker Compose:**
   ```bash
   # Start both Streamlit app and API server
   docker-compose up -d
   
   # Or start only the API server
   docker-compose up -d llm-judge-api
   
   # API will be available at http://localhost:8000
   # Swagger docs at http://localhost:8000/docs
   ```

2. **Run API server locally:**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Run API server
   uvicorn api_server:app --host 0.0.0.0 --port 8000
   ```

3. **Access API:**
   - API Base URL: `http://localhost:8000`
   - Interactive API docs (Swagger): `http://localhost:8000/docs`
   - Alternative docs (ReDoc): `http://localhost:8000/redoc`
   - Health check: `http://localhost:8000/health`

4. **Create an API key:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/keys" \
     -H "Content-Type: application/json" \
     -d '{"description": "My API key"}'
   ```

5. **Use the Python SDK:**
   ```python
   from api_client import EvaluationClient
   
   client = EvaluationClient(api_key="your_api_key", base_url="http://localhost:8000")
   
   # Evaluate a response
   result = client.evaluate_comprehensive(
       question="What is AI?",
       response="AI is artificial intelligence..."
   )
   print(f"Overall Score: {result['overall_score']:.2f}/10")
   ```

See the [API Documentation](#api-documentation) section below for detailed API usage.

**Configure Ollama Host:**
- Set `OLLAMA_HOST` environment variable to point to your Ollama instance
- Default: `http://localhost:11434` (local)
- Docker default: `http://host.docker.internal:11434` (host machine from container)
- Remote: `http://your-ollama-server:11434`

## How to Use

### Manual Pairwise Comparison
1. Select "🔀 Manual Pairwise Comparison" from the sidebar navigation
2. Enter a question or task
3. Enter two different responses (Response A and Response B)
4. (Optional) Expand "⚙️ Advanced Options" to enable:
   - **Conservative Position Bias Mitigation**: Calls judge twice with swapped positions. Only declares a win if both evaluations agree, else tie. More accurate but uses 2x API calls (MT-Bench paper recommendation). See [Position Bias Guide](documentation/POSITION_BIAS_GUIDE.md) for detailed trade-offs and when to use each approach.
5. (Optional) Toggle "Save to DB" checkbox (enabled by default)
6. Click "⚖️ Judge Responses"
7. While running, you'll see:
   - Status indicator showing progress
   - **⏹️ Stop** button to cancel the operation
   - **🔄 Refresh Status** button to manually check progress
8. Review the judgment, scores, and reasoning when complete
   - If Conservative Position Bias Mitigation is enabled, you'll see detailed results from both evaluations with explicit response labels and conversion notes

### Auto Pairwise Comparison
1. Select "🤖 Auto Pairwise Comparison" from the sidebar navigation
2. Enter a question or task
3. Select Model A (will generate Response A)
4. Select Model B (will generate Response B)
5. (Optional) Expand "⚙️ Advanced Options" to enable:
   - **Conservative Position Bias Mitigation**: Calls judge twice with swapped positions. Only declares a win if both evaluations agree, else tie. More accurate but uses 2x API calls (MT-Bench paper recommendation). See [Position Bias Guide](documentation/POSITION_BIAS_GUIDE.md) for detailed trade-offs and when to use each approach.
6. (Optional) Toggle "Save to DB" checkbox (enabled by default)
7. Click "🚀 Generate & Judge"
8. The app will:
   - Generate Response A using Model A (with status indicator)
   - Generate Response B using Model B (with status indicator)
   - Judge both responses (with status indicator, shows "2 evaluations" if Conservative mode is enabled)
   - Show stop buttons during each step
9. Review the generated responses and judgment
   - If Conservative Position Bias Mitigation is enabled, you'll see detailed results from both evaluations with explicit response labels and conversion notes

### Single Response Grading
1. Select "📊 Single Response Grading" from the sidebar navigation
2. Enter a question or task
3. Enter the response to evaluate
4. (Optional) Add custom evaluation criteria
5. (Optional) Toggle "Save to DB" checkbox (enabled by default)
6. Click "📊 Evaluate Response"
7. While running, you'll see:
   - Status indicator showing progress
   - **⏹️ Stop** button to cancel the operation
8. Review the score, strengths, weaknesses, and detailed feedback

### Comprehensive Evaluation
1. Select "🎯 Comprehensive Evaluation" from the sidebar navigation
2. Select task type (general, qa, summarization, code, translation, creative)
3. Enter a question or task
4. Enter the response to evaluate
5. (Optional) Enable "Use Reference Answer" and provide a reference for more accurate evaluation
6. Click "🎯 Run Comprehensive Evaluation"
7. The app will evaluate across 5 metrics:
   - **Accuracy**: Factual correctness (0-10)
   - **Relevance**: How well it addresses the question (0-10)
   - **Coherence**: Clarity and logical structure (0-10)
   - **Hallucination**: Detection of false/fabricated information (0-10, inverted)
   - **Toxicity**: Detection of harmful/inappropriate content (0-10, inverted)
8. Review the overall score and detailed metrics breakdown
9. View the evaluation trace for observability

### Code-Based Evaluation
1. Select "💻 Code-Based Evaluation" from the sidebar navigation (under "Code Analysis" section)
2. Select programming language:
   - **Backend**: Python, JavaScript (Node.js), TypeScript, Java, Go
   - **Web**: JavaScript, TypeScript, HTML, CSS
   - **iOS**: Swift, Objective-C
   - **Android**: Kotlin, Java
3. Enter or paste code to evaluate
4. (Optional) Provide test inputs and expected output
5. Click "💻 Evaluate Code"
6. Review comprehensive results:
   - **Syntax Check**: Valid/invalid, errors, warnings, complexity
   - **Execution Test**: Success/failure, output, execution time (for supported languages)
   - **Quality Metrics**: Lines of code, functions, classes, maintainability, readability scores
   - **Security Vulnerabilities**: SQL injection, XSS, hardcoded secrets, insecure patterns
     - Severity levels: BLOCKER, CRITICAL, MAJOR
     - Grouped by severity with line numbers
   - **Code Smells**: Long methods, large classes, duplicate code, unused variables, magic numbers
     - Severity levels: MAJOR, MINOR, INFO
     - Grouped by severity with line numbers
   - **Advanced Metrics**: Cyclomatic complexity, cognitive complexity, technical debt ratio
7. View overall code evaluation score (adjusted for security issues and code smells)

### Batch Evaluation
1. Select "📦 Batch Evaluation" from the sidebar navigation
2. Prepare a dataset file:
   - **JSON format**: Array of objects with `question`, `response`, and optionally `reference` fields
   - **CSV format**: Columns: `question`, `response`, `reference`
3. Upload your dataset file
4. Review the loaded test cases
5. Select evaluation type (comprehensive or single)
6. Select task type (if using comprehensive)
7. Configure run name and enable "Save to DB"
8. Click "🚀 Start Batch Evaluation"
9. Monitor progress in real-time
10. View aggregate metrics and detailed results
11. Export results as JSON or CSV

### Human Evaluation
1. Select "👤 Human Evaluation" from the sidebar navigation
2. Choose evaluation mode:
   - **New Evaluation**: Create human annotations with ratings
   - **Compare with LLM Judgment**: Compare human vs LLM evaluations side-by-side
   - **View All Annotations**: Browse all human annotations
3. For New Evaluation:
   - Enter annotator name and email (optional)
   - Select evaluation type (comprehensive, single, pairwise)
   - Enter question and response(s)
   - Rate metrics (0-10 scale) for comprehensive evaluations
   - Add feedback (optional)
   - Click "💾 Save Human Annotation"
4. For Comparison:
   - Select an LLM judgment to compare
   - View human annotations for that judgment
   - See inter-annotator agreement metrics (if multiple annotators)

### Router Evaluation
1. Select "🔀 Router Evaluation" from the sidebar navigation
2. Choose evaluation mode:
   - **Evaluate Router Decision**: Evaluate a routing decision
   - **View All Router Evaluations**: Browse saved evaluations
3. For Router Decision Evaluation:
   - Enter query/request
   - Add context (optional)
   - Configure available tools (1-20 tools with names and descriptions)
   - Select the tool that was chosen
   - (Optional) Specify expected tool for accuracy comparison
   - Enter routing strategy (optional)
   - Click "⚖️ Evaluate Router Decision"
4. Review metrics:
   - **Tool Accuracy**: Was the correct tool selected? (0-10)
   - **Routing Quality**: How well does routing align with query? (0-10)
   - **Reasoning Quality**: How logical is the decision? (0-10)
   - **Overall Score**: Average of all three metrics

### Skills Evaluation
1. Select "🎓 Skills Evaluation" from the sidebar navigation
2. Choose evaluation mode:
   - **Evaluate Skill**: Create a skill-specific evaluation
   - **View All Skills Evaluations**: Browse saved evaluations
3. For Skill Evaluation:
   - Select skill type (mathematics, coding, reasoning, general)
   - Enter domain (optional, e.g., algebra, python, logical_puzzles)
   - Enter question/task
   - Enter response to evaluate
   - (Optional) Provide reference answer for comparison
   - Click "⚖️ Evaluate Skill"
4. Review metrics:
   - **Correctness**: Is the information accurate? (0-10)
   - **Completeness**: Is the solution complete? (0-10)
   - **Clarity**: Is the response clear? (0-10)
   - **Proficiency**: Overall skill level? (0-10)
   - **Overall Score**: Average of all four metrics
5. Filter evaluations by skill type when viewing all

### Trajectory Evaluation

Trajectory Evaluation assesses multi-step action sequences, agent trajectories, and reasoning chains. This is useful for evaluating AI agents that perform complex tasks requiring multiple steps.

#### Step-by-Step Guide

1. **Select "🛤️ Trajectory Evaluation"** from the sidebar navigation

2. **Choose evaluation mode:**
   - **Evaluate Trajectory**: Create a new trajectory evaluation
   - **View All Trajectory Evaluations**: Browse saved evaluations

3. **Fill in the form:**

   **a. Task Description** (Required)
   - Describe the overall task or goal the agent was trying to accomplish
   - Example: "Help a user book a flight from New York to Paris"
   - This provides context for the evaluation

   **b. Trajectory Type** (Optional)
   - Categorize the trajectory for easier filtering later
   - Options: `action_sequence`, `reasoning_chain`, `planning_path`, `tool_usage`, `other`
   - Leave empty if not needed

   **c. Actual Trajectory** (Required)
   - Choose input mode:
     - **JSON Format** (Recommended): Paste trajectory as JSON array
     - **Manual Entry**: Enter steps one by one using expandable forms
   
   **JSON Format Example:**
   ```json
   [
     {
       "action": "search_flights",
       "description": "Search for available flights from NYC to Paris on the requested date"
     },
     {
       "action": "filter_results",
       "description": "Filter flights by price range and departure time preferences"
     },
     {
       "action": "select_flight",
       "description": "Select the best matching flight option based on user criteria"
     },
     {
       "action": "book_flight",
       "description": "Complete the booking process with user payment information"
     }
   ]
   ```
   
   **Manual Entry:**
   - Specify number of steps (1-50)
   - For each step, enter:
     - **Action/Step Name**: Brief identifier (e.g., "search_flights")
     - **Description/Reasoning**: What the step does and why

   **d. Expected Trajectory** (Optional)
   - Check "Include Expected Trajectory for Comparison" to provide an ideal trajectory
   - Use the same format (JSON or Manual Entry) as the actual trajectory
   - The evaluator will compare actual vs. expected to assess performance
   - Example: If the agent should have checked user preferences first, include that in expected

   **e. Judge Model**
   - Select the LLM model that will evaluate the trajectory
   - Popular choices: `llama3`, `mistral`, `gpt-oss-safeguard:20b`
   - The judge model analyzes the trajectory and generates scores

   **f. Save to Database**
   - Check this box (default: checked) to save results for later analysis
   - Uncheck if you only want a temporary evaluation

4. **Click "⚖️ Evaluate Trajectory"**
   - The system will use the judge model to evaluate your trajectory
   - Evaluation may take 10-30 seconds depending on trajectory length

5. **Review Results:**
   - **Step Quality** (0-10): How good is each individual step?
   - **Path Efficiency** (0-10): How efficient is the overall path?
   - **Reasoning Chain** (0-10): How logical is the step-by-step reasoning?
   - **Planning Quality** (0-10): How well was the trajectory planned?
   - **Overall Score**: Average of all four metrics
   - **Detailed Judgment**: Text explanation of the evaluation

#### Example Use Cases

**Customer Service Bot:**
```json
Task: "Handle customer complaint about delayed order"
Trajectory:
[
  {"action": "greet_customer", "description": "Acknowledge the customer's concern"},
  {"action": "lookup_order", "description": "Retrieve order details from database"},
  {"action": "check_status", "description": "Verify current order status and shipping info"},
  {"action": "apologize", "description": "Provide sincere apology for the delay"},
  {"action": "offer_solution", "description": "Propose compensation or resolution"}
]
```

**Code Generation Agent:**
```json
Task: "Generate a Python function to calculate factorial"
Trajectory:
[
  {"action": "analyze_requirement", "description": "Understand the factorial calculation requirement"},
  {"action": "design_algorithm", "description": "Plan recursive or iterative approach"},
  {"action": "write_code", "description": "Implement the factorial function"},
  {"action": "add_error_handling", "description": "Include input validation and edge cases"},
  {"action": "test_function", "description": "Verify function works with test cases"}
]
```

#### Tips

- **Be Specific**: Clear action names and detailed descriptions help the judge model understand the trajectory
- **Include Context**: The task description should explain what the agent was trying to achieve
- **Use Expected Trajectory**: When you know the ideal path, include it for more accurate evaluation
- **Trajectory Type**: Use consistent types for easier filtering and analysis later
- **Save Results**: Keep evaluations saved to track improvements over time

6. **Filter evaluations by trajectory type** when viewing all saved evaluations

### A/B Testing
1. Select "🧪 A/B Testing" from the sidebar navigation
2. Choose a mode:
   - **Create New A/B Test**: Set up a new comparison test
   - **Run A/B Test**: Execute a saved test
   - **View Test Results**: Analyze completed test results
3. For Creating a Test:
   - Enter test name and optional description
   - Configure Variant A:
     - Set variant name (e.g., "Llama3")
     - Choose evaluation type (comprehensive or pairwise)
     - Select model for generating responses (if needed)
     - Set task type for comprehensive evaluation
   - Configure Variant B (same options as Variant A)
   - Add test cases:
     - **Manual Entry**: Enter questions and optional responses
     - **Upload JSON/CSV**: Upload file with test cases
   - Click "💾 Create A/B Test"
4. For Running a Test:
   - Select a test from the dropdown
   - Review test configuration
   - Choose judge model
   - Click "▶️ Run A/B Test"
   - Monitor progress bar
   - Use "⏹️ Stop" to cancel if needed
5. For Viewing Results:
   - Select a completed test
   - Review summary statistics (wins, ties)
   - View statistical analysis:
     - **T-Test**: Independent samples t-test
     - **Mann-Whitney U Test**: Non-parametric alternative
     - **Effect Size**: Cohen's d with interpretation
     - **Confidence Intervals**: 95% CI for mean difference
   - View visualizations:
     - **Box Plot**: Score distribution comparison
     - **Pie Chart**: Win rate distribution
   - Review detailed results table
   - Export results as CSV

### Evaluation Templates
1. Select "📋 Evaluation Templates" from the sidebar navigation
2. Choose a mode:
   - **Browse Templates**: View all available templates (predefined and custom)
   - **Create New Template**: Create custom evaluation configurations
   - **Manage Templates**: View and delete custom templates
3. For Browsing:
   - Filter by evaluation type (comprehensive, code_evaluation, etc.)
   - Filter by industry (healthcare, finance, legal, etc.)
   - View template details and configuration
4. For Creating:
   - Enter template name and description
   - Select evaluation type and industry (optional)
   - Configure template settings:
     - **Comprehensive**: Set metric weights, task type, custom prompts
     - **Code Evaluation**: Set quality weights, strict mode, security checks
   - Create template
5. For Using Templates:
   - Select template in Comprehensive Evaluation (from sidebar navigation)
   - Template configuration automatically applied
   - Task type and metric weights set from template
6. Predefined Templates:
   - Healthcare - Medical Accuracy
   - Finance - Regulatory Compliance
   - Legal - Case Analysis
   - Education - Learning Effectiveness
   - Code Review - Production Ready
   - General Purpose - Balanced

### Custom Metrics
1. Select "🎯 Custom Metrics" from the sidebar navigation
2. Choose a mode:
   - **Browse Metrics**: View all custom metrics with filtering
   - **Create New Metric**: Define custom evaluation metrics
   - **Evaluate with Metric**: Evaluate responses using custom metrics
   - **Manage Metrics**: View and deactivate custom metrics
3. For Creating a Metric:
   - Enter metric name and description
   - Select evaluation type and domain (optional)
   - Define the metric (what it measures and how)
   - Configure scoring scale (min-max)
   - Add criteria as JSON (optional)
   - Add scoring function description (optional)
   - Set metric weight
   - Create metric
4. For Evaluating with Metric:
   - Select an active custom metric
   - Enter question and response
   - Optionally provide reference answer
   - Run evaluation
   - View score (on metric scale) and normalized score (0-10)
   - Review detailed explanation
5. Features:
   - Custom scoring scales (e.g., 0-10, 1-5, 0-100)
   - Domain-specific criteria
   - Usage tracking
   - Soft delete (deactivation)
   - JSON criteria support

### Advanced Analytics
1. Select "📈 Advanced Analytics" from the sidebar navigation
2. View overview metrics showing total evaluations by type
3. Select from six analytics views:
   - **Time Series Analysis**: Track performance over time with line charts and rolling averages
   - **Comparative Analytics**: Compare different evaluation types side-by-side
   - **Aggregate Statistics**: View detailed statistics for each evaluation type
   - **Performance Heatmaps**: Visualize metrics across different dimensions
   - **Model Comparison**: Compare performance across different judge models
   - **Export Data**: Export evaluation data in CSV or JSON format
4. Use interactive charts to explore trends and patterns
5. Export data for further analysis in external tools

## API Documentation

The framework provides a REST API for programmatic access to all evaluation features.

### Authentication

All API endpoints (except `/health` and `/api/v1/keys`) require authentication using an API key.

**Create an API Key:**
```bash
curl -X POST "http://localhost:8000/api/v1/keys" \
  -H "Content-Type: application/json" \
  -d '{"description": "My API key"}'
```

**Use API Key:**
Include the API key in the `Authorization` header:
```bash
curl -X GET "http://localhost:8000/api/v1/evaluations" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Rate Limiting

- Default: 100 requests per hour per API key
- Configurable via `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW` environment variables
- Returns `429 Too Many Requests` when limit is exceeded

### API Endpoints

#### Health Check
- `GET /health` - Check API health (no auth required)

#### API Key Management
- `POST /api/v1/keys` - Create a new API key (no auth required)
- `GET /api/v1/keys` - List all API keys (requires auth)

#### Evaluation Endpoints

**Comprehensive Evaluation:**
```bash
POST /api/v1/evaluations/comprehensive
{
  "question": "What is AI?",
  "response": "AI is artificial intelligence...",
  "judge_model": "llama3",
  "save_to_db": true
}
```

**Code Evaluation:**
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

**Note:** Code evaluation does not use a judge model - it uses static analysis. The API accepts `language` parameter (default: "python") and supports multiple languages: python, javascript, typescript, swift, kotlin, java, go, html, css, objective-c.

**Router Evaluation:**
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

**Skills Evaluation:**
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

**Trajectory Evaluation:**
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

**Manual Pairwise Comparison:**
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

**A/B Testing:**
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

**Evaluation Templates:**
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

# Get specific template
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

**Custom Metrics:**
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

# Get specific metric
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

#### Data Retrieval Endpoints

- `GET /api/v1/evaluations?evaluation_type=comprehensive&limit=50` - Get evaluations
- `GET /api/v1/analytics/overview` - Get analytics overview

#### Webhook Management

- `POST /api/v1/webhooks` - Create a webhook
- `GET /api/v1/webhooks` - List all webhooks
- `DELETE /api/v1/webhooks/{webhook_id}` - Delete a webhook

**Create Webhook:**
```bash
POST /api/v1/webhooks
{
  "url": "https://your-server.com/webhook",
  "events": ["evaluation.completed"],
  "secret": "your_webhook_secret"
}
```

### Python SDK

The framework includes a Python SDK for easy integration:

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

# Code evaluation (static analysis, no judge model needed)
result = client.evaluate_code(
    code="def hello(): return 'world'",
    language="python"  # Options: python, javascript, typescript, swift, kotlin, java, go, html, css, objective-c
)
# Returns: syntax check, execution test, quality metrics, security vulnerabilities, code smells, advanced metrics

# Router evaluation
result = client.evaluate_router(
    query="Calculate 2+2",
    available_tools=[{"name": "calculator", "description": "Calculates"}],
    selected_tool="calculator"
)

# Skills evaluation
result = client.evaluate_skills(
    skill_type="mathematics",
    question="2+2=?",
    response="4"
)

# Trajectory evaluation
result = client.evaluate_trajectory(
    task_description="Process order",
    trajectory=[{"action": "step1", "description": "First step"}]
)

# Pairwise comparison
result = client.evaluate_pairwise(
    question="Explain AI",
    response_a="AI is...",
    response_b="AI means..."
)

# Get evaluations
evaluations = client.get_evaluations(evaluation_type="comprehensive", limit=10)

# Get analytics
analytics = client.get_analytics_overview()

# Webhook management
webhook = client.create_webhook(
    url="https://your-server.com/webhook",
    events=["evaluation.completed"]
)
```

### Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These provide:
- Complete API reference
- Interactive testing interface
- Request/response schemas
- Authentication testing

### Webhooks

Webhooks allow you to receive notifications when evaluations complete.

**Supported Events:**
- `evaluation.completed` - Fired when any evaluation completes

**Webhook Payload:**
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

**Webhook Signature:**
If a secret is provided, webhooks include an `X-Webhook-Signature` header with HMAC-SHA256 signature for verification.

### CI/CD Integration

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

### Saved Judgments & Dashboard
1. Select "💾 Saved Judgments & Dashboard" from the sidebar navigation
2. View metrics dashboard with aggregate statistics (for comprehensive evaluations)
3. View all your saved judgments from the database
4. Filter by judgment type (pairwise_manual, pairwise_auto, single, comprehensive, code_evaluation, batch_comprehensive, batch_single)
5. Adjust the number of judgments to display
6. Expand any judgment to see full details:
   - For comprehensive evaluations: View all metrics, detailed explanations, and evaluation trace
   - For code evaluations: View syntax, execution, and quality metrics
   - For other types: View judgment text and responses
   - View human annotations linked to judgments (if any)
7. Delete individual judgments or export all as JSON

## Example Use Cases

- **A/B Testing**: Compare different versions of AI-generated content
- **Quality Assessment**: Evaluate the quality of AI responses with comprehensive metrics
- **Model Comparison**: Compare outputs from different AI models (using Auto Pairwise Comparison)
- **Content Review**: Get detailed feedback on generated content with hallucination and toxicity detection
- **Educational Feedback**: Evaluate student responses or explanations with skills evaluation
- **Prompt Engineering**: Test different prompts with the same model
- **Model Benchmarking**: Systematically evaluate model performance across multiple metrics
- **AI Agent Evaluation**: Assess reasoning, routing, and action capabilities of AI agents
- **Router Validation**: Evaluate tool selection and routing decisions in multi-agent systems
- **Skill Assessment**: Evaluate domain-specific skills (mathematics, coding, reasoning)
- **Code Quality**: Evaluate code correctness, quality, and maintainability
- **Human-in-the-Loop**: Add human annotations and compare with LLM judgments
- **Safety Testing**: Detect hallucinations and toxic content in AI outputs
- **Batch Testing**: Evaluate multiple test cases from benchmark datasets
- **A/B Testing**: Statistically compare different models or configurations
- **Template-Based Evaluation**: Use industry-specific templates for consistent evaluations (healthcare, finance, legal, etc.)
- **Reusable Configurations**: Create and share evaluation templates across teams
- **Custom Metrics**: Define domain-specific evaluation metrics tailored to your needs
- **Flexible Scoring**: Create metrics with custom scales and scoring functions

## Troubleshooting

### Container won't start
- Check if port 8501 is already in use: `lsof -i :8501`
- Stop any existing Streamlit processes
- Check Docker logs: `docker logs llm-judge-app`

### Can't connect to Ollama
- Verify Ollama is running: `ollama list`
- Check `OLLAMA_HOST` environment variable
- For Docker, ensure Ollama is accessible from the container

### Stop button not working
- The stop button prevents results from being shown/saved
- The Ollama API call may still complete in the background
- Refresh the page if the operation seems stuck

### Database not found
- Database is created automatically on first save
- Check `./data/` directory exists (Docker) or project root (local)
- Verify write permissions

## Requirements

- Python 3.8+ (or Docker)
- Ollama installed and running
- At least one Ollama model pulled (e.g., llama3, mistral, llama2)
- Docker and Docker Compose (for containerized deployment)

## Database

The app automatically saves all judgments to a SQLite database (`llm_judge.db`) in the project directory. 

### Database Schema

#### judgments Table
Each judgment includes:
- Question/task
- Responses (A and B)
- Models used (for auto-generated responses)
- Judge model
- Full judgment text
- Judgment type (pairwise_manual, pairwise_auto, single, comprehensive, code_evaluation, batch_comprehensive, batch_single)
- **Evaluation ID** (UUID for tracking)
- **Metrics JSON** (structured metrics for comprehensive evaluations)
- **Trace JSON** (evaluation trace for observability)
- Timestamp

#### human_annotations Table
Human annotations include:
- Annotation ID (UUID)
- Judgment ID (link to LLM judgment, optional)
- Annotator name and email
- Question and response(s)
- Evaluation type (comprehensive, single, pairwise)
- Scores: accuracy, relevance, coherence, hallucination, toxicity, overall
- Feedback text
- Timestamps

#### router_evaluations Table
Router evaluations include:
- Evaluation ID (UUID)
- Query/request and context
- Available tools (JSON array)
- Selected tool and expected tool
- Routing strategy
- Metrics: tool_accuracy_score, routing_quality_score, reasoning_score, overall_score
- Judgment text and metrics JSON
- Routing path JSON and trace JSON
- Timestamp

#### skills_evaluations Table
Skills evaluations include:
- Evaluation ID (UUID)
- Skill type (mathematics, coding, reasoning, general)
- Question and response
- Reference answer (optional)
- Domain (optional)
- Metrics: correctness_score, completeness_score, clarity_score, proficiency_score, overall_score
- Skill metrics JSON and judgment text
- Trace JSON
- Timestamp

#### trajectory_evaluations Table
Trajectory evaluations include:
- Evaluation ID (UUID)
- Task description
- Trajectory JSON (array of steps with action and description)
- Expected trajectory JSON (optional, for comparison)
- Trajectory type (action_sequence, reasoning_chain, planning_path, tool_usage, other)
- Metrics: step_quality_score, path_efficiency_score, reasoning_chain_score, planning_quality_score, overall_score
- Judgment text and metrics JSON
- Trace JSON
- Timestamp

#### evaluation_runs Table
Batch evaluation runs include:
- Run ID (UUID)
- Run name and dataset name
- Total cases and completed cases
- Status (running, completed, failed)
- Results JSON
- Timestamps

#### ab_tests Table
A/B tests include:
- Test ID (UUID)
- Test name and description
- Variant A and B names and configurations (JSON)
- Evaluation type (comprehensive, pairwise)
- Test cases (JSON array)
- Status (pending, running, completed, failed)
- Total cases and completed cases
- Variant A/B wins and ties counts
- Results JSON (detailed results for each test case)
- Statistical analysis JSON (T-test, Mann-Whitney, effect size, etc.)
- Timestamps (created, started, completed)

#### evaluation_templates Table
Evaluation templates include:
- Template ID (UUID)
- Template name and description
- Industry category (healthcare, finance, legal, education, software, general)
- Evaluation type (comprehensive, code_evaluation, router, skills, trajectory)
- Template configuration (JSON) - metric weights, quality weights, prompts, etc.
- Is predefined flag (system templates vs user-created)
- Created by (user or system)
- Usage count (tracks how many times template used)
- Timestamps (created, updated)

#### custom_metrics Table
Custom metrics include:
- Metric ID (UUID)
- Metric name and description
- Domain category (healthcare, finance, legal, education, software, general, other)
- Evaluation type (comprehensive, code_evaluation, router, skills, trajectory, general)
- Metric definition (detailed description of what the metric measures)
- Scoring function description (optional)
- Criteria JSON (structured criteria for evaluation)
- Weight (for weighted scoring)
- Scale min/max (custom scoring scale)
- Created by (user or API)
- Usage count (tracks how many times metric used)
- Is active flag (soft delete support)
- Timestamps (created, updated)

### Evaluation Metrics

**Comprehensive Evaluation Metrics:**
- Accuracy score and explanation
- Relevance score and explanation
- Coherence score and explanation
- Hallucination score, risk score, and explanation
- Toxicity score, risk score, and explanation
- Overall score (average of all metrics)

**Router Evaluation Metrics:**
- Tool Accuracy score (0-10)
- Routing Quality score (0-10)
- Reasoning Quality score (0-10)
- Overall score (average of all three)

**Skills Evaluation Metrics:**
- Correctness score (0-10)
- Completeness score (0-10)
- Clarity score (0-10)
- Proficiency score (0-10)
- Overall score (average of all four)

**Trajectory Evaluation Metrics:**
- Step Quality score (0-10)
- Path Efficiency score (0-10)
- Reasoning Chain score (0-10)
- Planning Quality score (0-10)
- Overall score (average of all four)

### Database Features

You can:
- View all saved judgments in "Saved Judgments & Dashboard" (from sidebar navigation)
- View aggregate metrics dashboard for comprehensive evaluations
- Filter by judgment type (pairwise_manual, pairwise_auto, single, comprehensive, code_evaluation, batch_comprehensive, batch_single)
- View detailed metrics and traces for comprehensive evaluations
- View human annotations linked to judgments
- View router evaluations and skills evaluations
- Delete individual judgments
- Export all judgments as JSON

The database file is created automatically on first use and is stored:
- **Local**: In the project root directory
- **Docker**: In the `./data` directory (persisted on host machine)

## Configuration

### Environment Variables

- **OLLAMA_HOST**: Ollama server URL (default: `http://localhost:11434`)
  - Local: `http://localhost:11434`
  - Docker (macOS/Windows): `http://host.docker.internal:11434`
  - Docker (Linux): Use `--network host` or configure accordingly
  - Remote: `http://your-ollama-server:11434`

- **DB_NAME**: Database file name (default: `llm_judge.db`)
- **DB_PATH**: Full path to database file (default: same as DB_NAME)

### Docker Configuration

The Docker setup includes:
- **Persistent database storage** in `./data` directory (mapped to host)
- **Configurable Ollama host** via environment variable
- **Health checks** for container monitoring
- **Automatic restart** on failure
- **Network configuration** for accessing host Ollama service
- **Volume mounting** for data persistence

### Docker Quick Start

```bash
# 1. Ensure Ollama is running on your host machine
ollama serve

# 2. Pull at least one model
ollama pull llama3

# 3. Build and start the container
docker-compose build
docker-compose up -d

# 4. Check container status
docker-compose ps

# 5. View logs
docker-compose logs -f

# 6. Access the app
# Open http://localhost:8501 in your browser
```

### Docker Troubleshooting

**Container won't start:**
```bash
# Check if port 8501 is in use
lsof -i :8501

# Remove existing container if needed
docker rm -f llm-judge-app

# Check Docker logs
docker-compose logs
```

**Can't connect to Ollama from container:**
- Ensure Ollama is running: `ollama list`
- For macOS/Windows: `host.docker.internal:11434` should work automatically
- For Linux: You may need to use `--network host` or configure Docker networking
- Check environment variable: `docker exec llm-judge-app env | grep OLLAMA_HOST`

## Stop Button Feature

The app includes a **⏹️ Stop** button that appears during evaluations:

- **How it works**: Operations run in background threads, allowing you to cancel them
- **When it appears**: Automatically shown when an evaluation is running
- **What it does**: 
  - Sets a stop flag to cancel the operation
  - Prevents results from being displayed or saved
  - Shows a "stopped" message
- **Limitation**: The Ollama API call itself cannot be interrupted mid-execution, but results will be ignored if you click stop
- **Auto-refresh**: The page automatically refreshes every 2 seconds to check for completion

## Evaluation Metrics Explained

### Comprehensive Evaluation Metrics

The framework evaluates responses across five key dimensions:

1. **Accuracy (0-10)**: Measures factual correctness and truthfulness
   - High scores indicate accurate, factually correct information
   - Low scores indicate inaccuracies or false information

2. **Relevance (0-10)**: Measures how well the response addresses the question
   - High scores indicate direct, on-topic responses
   - Low scores indicate off-topic or irrelevant content

3. **Coherence (0-10)**: Measures clarity, logical structure, and readability
   - High scores indicate clear, well-organized responses
   - Low scores indicate confusing or poorly structured content

4. **Hallucination (0-10, inverted)**: Detects false or fabricated information
   - High scores indicate minimal hallucinations
   - Low scores indicate likely false information or unsupported claims
   - Also includes a risk score (higher = more risk)

5. **Toxicity (0-10, inverted)**: Detects harmful, biased, or inappropriate content
   - High scores indicate safe, appropriate content
   - Low scores indicate toxic or harmful language
   - Also includes a risk score (higher = more risk)

**Overall Score**: Average of all five metrics

### Router Evaluation Metrics

The framework evaluates routing decisions across three dimensions:

1. **Tool Accuracy (0-10)**: Measures if the correct/best tool was selected
   - High scores indicate the optimal tool was chosen
   - Low scores indicate wrong or suboptimal tool selection

2. **Routing Quality (0-10)**: Measures how well the routing decision aligns with the query
   - High scores indicate perfect alignment between query and tool
   - Low scores indicate poor alignment or mismatch

3. **Reasoning Quality (0-10)**: Measures the logical soundness of the routing decision
   - High scores indicate clear, logical reasoning
   - Low scores indicate illogical or unclear reasoning

**Overall Score**: Average of all three metrics

### Skills Evaluation Metrics

The framework evaluates domain-specific skills across four dimensions:

1. **Correctness (0-10)**: Measures accuracy of the response
   - High scores indicate correct information/answers
   - Low scores indicate incorrect information

2. **Completeness (0-10)**: Measures how complete the solution is
   - High scores indicate fully complete solutions
   - Low scores indicate incomplete or partial solutions

3. **Clarity (0-10)**: Measures how clear and well-structured the response is
   - High scores indicate extremely clear explanations
   - Low scores indicate unclear or confusing content

4. **Proficiency (0-10)**: Measures overall skill level demonstrated
   - High scores indicate expert-level skills
   - Low scores indicate basic or poor skills

**Overall Score**: Average of all four metrics

### Trajectory Evaluation Metrics

The framework evaluates multi-step trajectories across four dimensions:

1. **Step Quality (0-10)**: Measures how good each individual step is
   - High scores indicate optimal, well-executed steps
   - Low scores indicate poor or incorrect steps
   - Evaluates the quality of each action/step in the sequence

2. **Path Efficiency (0-10)**: Measures how efficient the overall path is
   - High scores indicate optimal path with minimal steps and no backtracking
   - Low scores indicate inefficient path with unnecessary steps
   - Evaluates whether the trajectory takes the most direct route

3. **Reasoning Chain (0-10)**: Measures how logical the step-by-step reasoning is
   - High scores indicate perfect logical progression with clear reasoning
   - Low scores indicate poor reasoning or illogical progression
   - Evaluates the logical flow between steps

4. **Planning Quality (0-10)**: Measures how well the trajectory was planned
   - High scores indicate excellent planning that considers all factors
   - Low scores indicate poor planning with missing considerations
   - Evaluates foresight and comprehensive planning

**Overall Score**: Average of all four metrics

## Understanding Router Evaluation

### What is Router Evaluation?

Router Evaluation is a specialized evaluation feature designed to assess how well AI agents make routing decisions when selecting tools or functions to handle user queries. In AI agent systems, a **router** is the component that decides which tool to use for a given request.

### Why Router Evaluation Matters

AI agents often have access to multiple tools (functions, APIs, services). The router must select the correct tool for each query. Poor routing decisions lead to:

- **Wrong Tool Selection**: Selecting an inappropriate tool (e.g., using `email_sender` for a math calculation)
- **Inefficient Routing**: Choosing a suboptimal tool that works but is slower or more expensive
- **User Frustration**: Failed tasks and poor user experience
- **System Reliability Issues**: Unpredictable behavior in production

### Real-World Use Cases

1. **Testing Router Before Deployment**
   - Validate that your router correctly selects tools for common queries
   - Identify routing failures before they reach production
   - Establish quality baselines

2. **Comparing Routing Strategies**
   - Test different routing algorithms (keyword-based, semantic similarity, ML models)
   - Measure performance differences between strategies
   - Choose the best routing approach for your use case

3. **Debugging Routing Failures**
   - Investigate why wrong tools are selected
   - Identify patterns in routing mistakes
   - Improve router logic based on evaluation insights

4. **A/B Testing Router Improvements**
   - Compare old vs. new router versions
   - Measure improvement in routing accuracy
   - Validate that changes don't regress performance

5. **Quality Assurance for Production**
   - Run Router Evaluation on test cases before deploying changes
   - Ensure routing scores meet quality thresholds
   - Monitor routing performance over time

### How Router Evaluation Works

Router Evaluation uses an LLM judge model to evaluate routing decisions across three dimensions:

1. **Tool Accuracy**: Was the correct/best tool selected?
2. **Routing Quality**: How well does the routing decision align with the query?
3. **Reasoning Quality**: How logical is the routing decision?

The judge model analyzes:
- The user query/request
- Available tools and their descriptions
- The selected tool
- Optional: Expected tool (for accuracy comparison)
- Optional: Routing strategy used

The evaluation produces scores (0-10) for each metric and a detailed judgment explaining the reasoning.

### Example: E-commerce AI Agent

Imagine an AI agent with these tools:
- `product_search` - Find products in catalog
- `add_to_cart` - Add items to shopping cart
- `checkout` - Process payment
- `customer_service` - Handle complaints
- `order_tracking` - Track order status

Router Evaluation helps verify:
- ✅ "Show me laptops" → `product_search` (correct)
- ✅ "I want to buy this" → `add_to_cart` (correct)
- ✅ "Where is my order?" → `order_tracking` (correct)
- ❌ "This product is broken" → `product_search` (wrong, should be `customer_service`)

### Router Evaluation and MCP (Model Context Protocol)

Router Evaluation is highly relevant for systems using **MCP (Model Context Protocol)**, a standardized protocol for AI assistants to connect to external tools and data sources.

**How they relate:**
- **MCP provides tools**: MCP servers expose tools that AI agents can use
- **Router Evaluation tests tool selection**: Evaluates whether the agent correctly selects MCP tools
- **Critical for MCP systems**: When using MCP, you need to ensure your router correctly selects from available MCP tools

**Example with MCP tools:**
```
Available MCP Tools:
- mcp_filesystem_read - Read files
- mcp_database_query - Query database
- mcp_web_search - Search the web
- mcp_calculator_compute - Perform calculations

Query: "What is 15 × 23?"
Selected Tool: mcp_calculator_compute ✅
Expected Tool: mcp_calculator_compute ✅
→ Router Evaluation: 10/10 (perfect routing!)
```

Router Evaluation works with any tool system (MCP, function calling, custom APIs) and helps ensure reliable tool selection regardless of the underlying protocol.

### Where the Analysis Comes From

The detailed judgment text in Router Evaluation is generated by an **LLM judge model** (the model you select, e.g., `gpt-oss-safeguard:20b`, `llama3`). The process:

1. **Input Collection**: Your query, available tools, selected tool, and optional context
2. **Prompt Construction**: System builds an evaluation prompt with criteria and guidelines
3. **LLM Evaluation**: The judge model analyzes the routing decision and generates scores + explanations
4. **Score Parsing**: System extracts numeric scores from the LLM's response
5. **Display**: Full judgment text is shown with detailed reasoning

The analysis is **not hardcoded**—it's dynamically generated by the LLM judge, which acts as an automated evaluator similar to a human reviewer.

## Understanding Human Evaluation

### What is Human Evaluation?

Human Evaluation enables human-in-the-loop evaluation by allowing annotators to create manual evaluations and compare them with LLM-generated judgments. This feature bridges the gap between automated LLM evaluations and human judgment.

### Why Human Evaluation Matters

While LLM-as-a-Judge is powerful and scalable, human evaluation provides:

1. **Ground Truth Validation**: Human annotators provide authoritative judgments that can validate or challenge LLM evaluations
2. **Quality Control**: Identify cases where LLM judges make mistakes or miss nuances
3. **Bias Detection**: Discover systematic biases in LLM evaluations
4. **Training Data**: Collect human-labeled data to improve LLM judges
5. **Inter-Annotator Agreement**: Measure consistency between multiple human evaluators
6. **Regulatory Compliance**: Some domains require human oversight of AI decisions

### Use Cases

1. **Validating LLM Judgments**
   - Compare human annotations with LLM evaluations
   - Identify discrepancies and edge cases
   - Build confidence in automated evaluation systems

2. **Building Evaluation Datasets**
   - Collect human-labeled evaluation data
   - Create gold-standard test sets
   - Train or fine-tune LLM judges

3. **Quality Assurance**
   - Human reviewers spot-check LLM evaluations
   - Ensure evaluation quality meets standards
   - Catch errors before they impact decisions

4. **Research and Analysis**
   - Study differences between human and LLM judgments
   - Analyze inter-annotator agreement
   - Research evaluation methodology

5. **Regulatory and Compliance**
   - Meet requirements for human oversight
   - Document human review processes
   - Provide audit trails

### How Human Evaluation Works

Human Evaluation supports three modes:

#### 1. New Evaluation
Create standalone human annotations:
- Enter annotator information (name, email)
- Select evaluation type (comprehensive, single, pairwise)
- Provide question and response(s)
- Rate metrics (0-10 scale for comprehensive evaluations)
- Add optional feedback/notes
- Save annotation to database

#### 2. Compare with LLM Judgment
Compare human annotations with existing LLM evaluations:
- Select an LLM judgment from saved evaluations
- View existing human annotations for that judgment
- Add new human annotations linked to the LLM judgment
- See side-by-side comparison of human vs. LLM scores
- View inter-annotator agreement metrics (when multiple annotators evaluate the same judgment)

#### 3. View All Annotations
Browse and manage all human annotations:
- Filter by annotator, evaluation type, date range
- View annotation details and metrics
- See linked LLM judgments
- Export annotation data

### Evaluation Types Supported

Human Evaluation supports the same evaluation types as LLM evaluations:

1. **Comprehensive Evaluation**: Multi-metric evaluation with:
   - Accuracy (0-10)
   - Relevance (0-10)
   - Coherence (0-10)
   - Hallucination (0-10, inverted)
   - Toxicity (0-10, inverted)
   - Optional feedback text

2. **Single Response Grading**: Evaluate a single response with:
   - Overall score (0-10)
   - Strengths
   - Weaknesses
   - Detailed feedback

3. **Manual Pairwise Comparison**: Compare two responses with:
   - Winner selection (Response A, Response B, or Tie)
   - Score for each response (0-10)
   - Reasoning/explanation

### Inter-Annotator Agreement

When multiple human annotators evaluate the same LLM judgment, the system calculates:

- **Agreement Metrics**: Measures of consistency between annotators
- **Score Differences**: Statistical analysis of rating variations
- **Consensus Indicators**: Whether annotators agree on key metrics

This helps identify:
- Ambiguous cases where annotators disagree
- Clear cases with high agreement
- Potential issues with evaluation criteria
- Training needs for annotators

### Best Practices

1. **Clear Guidelines**: Provide annotators with clear evaluation criteria and examples
2. **Multiple Annotators**: Have 2-3 annotators evaluate the same cases for reliability
3. **Regular Calibration**: Periodically review annotations together to ensure consistency
4. **Edge Case Documentation**: Document difficult cases and how they were handled
5. **Iterative Improvement**: Use human feedback to refine LLM evaluation prompts

### Integration with LLM Evaluations

Human Evaluation is designed to work seamlessly with LLM evaluations:

- **Linked Annotations**: Human annotations can be linked to specific LLM judgments
- **Comparison Views**: Side-by-side comparison of human and LLM scores
- **Discrepancy Analysis**: Identify cases where humans and LLMs disagree
- **Unified Storage**: Both human and LLM evaluations stored in the same database
- **Analytics Integration**: Human annotations included in analytics and reporting

This integration enables comprehensive evaluation workflows that combine the scalability of LLM judges with the accuracy and nuance of human judgment.

## Understanding Trajectory Evaluation

### What is Trajectory Evaluation?

**Trajectory Evaluation** assesses the quality of multi-step action sequences performed by AI agents. A **trajectory** is the sequence of steps an AI agent takes to complete a task. Think of it as evaluating the "journey" or "path" the agent took, not just the final result.

### Simple Analogy

Imagine you're evaluating how someone navigates from point A to point B:
- **Router Evaluation** asks: "Did they choose the right vehicle?" (car, bike, or walk?)
- **Trajectory Evaluation** asks: "How well did they drive? Did they take the best route? Were their turns smooth and logical?"

### Real-World Example: Your Flight Booking

In your example, you evaluated a flight booking trajectory:

**Task**: "Help a user book a flight from New York to Paris"

**Trajectory** (the steps the agent took):
1. `search_flights` - Search for available flights
2. `filter_results` - Filter by price and departure time
3. `book_flight` - Complete the booking with payment

**What Trajectory Evaluation Assesses:**
- ✅ **Step Quality (8/10)**: Each step is good, but could include more detail (seat selection, confirmation)
- ✅ **Path Efficiency (9/10)**: The path is logical and direct - no unnecessary steps
- ✅ **Reasoning Chain (9/10)**: Clear logic - search → filter → book
- ⚠️ **Planning Quality (7/10)**: Missing some considerations (user preferences, dates, insurance)

### Why Trajectory Evaluation Matters

AI agents often perform complex tasks that require multiple steps. Trajectory Evaluation helps you understand:

1. **Is the agent taking the right steps?**
   - Example: For booking a flight, should it check user preferences first?

2. **Is the order of steps logical?**
   - Example: Should it search flights before filtering, or filter before searching?

3. **Is the path efficient?**
   - Example: Did it take unnecessary steps or backtrack unnecessarily?

4. **Is the planning comprehensive?**
   - Example: Did it consider all important factors (dates, budget, preferences)?

### Use Cases

1. **Evaluating AI Assistants**
   - Customer service bots that handle multi-step requests
   - Virtual assistants that perform complex tasks
   - Chatbots that need to coordinate multiple actions

2. **Testing Agent Workflows**
   - E-commerce agents (search → filter → add to cart → checkout)
   - Travel agents (search → compare → book → confirm)
   - Code generation agents (analyze → design → implement → test)

3. **Debugging Agent Behavior**
   - Why did the agent fail? Which step went wrong?
   - Is the agent taking unnecessary steps?
   - Is the reasoning chain logical?

4. **Comparing Agent Versions**
   - Version A: Takes 5 steps, scores 7/10
   - Version B: Takes 3 steps, scores 9/10
   - Which is better?

5. **Training and Improvement**
   - Identify weak points in agent trajectories
   - Improve planning and reasoning
   - Optimize step sequences

### How It Works

1. **You Provide:**
   - **Task Description**: What the agent was trying to accomplish
   - **Actual Trajectory**: The sequence of steps the agent actually took
   - **Expected Trajectory** (optional): The ideal sequence of steps

2. **The System Evaluates:**
   - Uses an LLM judge model to analyze the trajectory
   - Scores four dimensions: Step Quality, Path Efficiency, Reasoning Chain, Planning Quality
   - Generates detailed explanations for each score

3. **You Get:**
   - Numerical scores (0-10) for each metric
   - Overall score (average)
   - Detailed judgment explaining why each score was given
   - Actionable feedback for improvement

### Trajectory vs. Router Evaluation

These are related but different:

| **Router Evaluation** | **Trajectory Evaluation** |
|----------------------|---------------------------|
| Evaluates **which tool** to use | Evaluates **how well** the agent uses tools |
| Single decision point | Multi-step sequence |
| "Should I use calculator or search?" | "How well did the agent calculate?" |
| Tool selection accuracy | Step-by-step quality |

**Example:**
- **Router Evaluation**: "For 'calculate 2+2', did the agent choose the calculator tool?" ✅
- **Trajectory Evaluation**: "How well did the agent: 1) parse the request, 2) select calculator, 3) execute calculation, 4) format result?" 📊

### Example: Customer Service Bot

**Task**: "Handle customer complaint about delayed order"

**Good Trajectory** (would score high):
1. `greet_customer` - Acknowledge concern
2. `lookup_order` - Retrieve order details
3. `check_status` - Verify shipping status
4. `apologize` - Provide sincere apology
5. `offer_solution` - Propose compensation

**Poor Trajectory** (would score low):
1. `offer_solution` - Jump to solution without context ❌
2. `lookup_order` - Check order after offering solution ❌
3. `greet_customer` - Greet at the end (wrong order) ❌

Trajectory Evaluation would identify:
- Wrong step order (should greet first)
- Missing steps (no apology)
- Poor reasoning (offering solution before understanding problem)

### Key Takeaway

**Trajectory Evaluation** answers: "How well did the AI agent perform the sequence of steps to complete a task?"

It's not about:
- ❌ Whether the final answer is correct (that's Skills Evaluation)
- ❌ Which tool to use (that's Router Evaluation)
- ❌ The quality of text output (that's Comprehensive Evaluation)

It's about:
- ✅ The quality of the step-by-step process
- ✅ The efficiency of the path taken
- ✅ The logic of the reasoning chain
- ✅ The comprehensiveness of the planning

Think of it as evaluating the **"how"** rather than the **"what"** or **"which"**.

## Notes

- The app uses Ollama, which runs locally on your machine - **no API keys needed!**
- Ollama must be running (usually starts automatically after installation)
- The app connects to Ollama at the URL specified by `OLLAMA_HOST` environment variable
- Popular models for judging: `llama3`, `mistral`, `llama2`, `codellama`
- Temperature is set to 0.2-0.3 for consistent, focused evaluations
- All processing happens locally - **your data stays on your machine**
- Database storage is optional - you can disable saving with the "Save to DB" checkbox
- When using Docker, the database is persisted in the `./data` directory on your host machine
- The app runs completely offline once set up (no internet required after initial installation)
- Stop button allows you to cancel long-running evaluations
- Comprehensive evaluations take longer (5 separate LLM calls) but provide detailed metrics
- Evaluation traces are stored for observability and debugging

## Architecture

### Project Structure

The codebase is organized into clear frontend and backend separation:

```
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

### Modular Architecture and Design Patterns

- **Layers**: Presentation (Streamlit UI) ←→ Application Services ←→ Domain (strategies, prompts, models) ←→ Infrastructure (LLM adapters, DB, webhooks)
- **Separation**: Frontend (UI) and Backend (API) are clearly separated with shared core business logic
- **API server** reuses Application Services; no UI logic in services
- **Backend services** handle data retrieval, analytics, and business operations independently

**Design patterns used:**
- **Strategy**: Pluggable evaluation types (pairwise, single, comprehensive, code, router, skills, trajectory, templates, custom-metrics)
- **Factory**: `StrategyFactory` creates strategies and wires the LLM adapter
- **Adapter**: `OllamaAdapter` provides a stable `chat()` with retry policy
- **Repository**: DB access via repositories (e.g., `JudgmentsRepository`)
- **Facade**: `EvaluationService` orchestrates strategies, timing, and persistence
- **Retry Policy**: Reduces `num_predict` on retries (768 → 512) for reliability
- **Observer (API)**: Webhooks for `evaluation.completed`

**Request flow (pairwise)**: 
UI → EvaluationService → Strategy → LLM Adapter → sanitize/parse → Repository → UI/API/Webhook

### Components

1. **Streamlit Frontend** (`frontend/app.py`): Web-based UI for all evaluation features
   - Sidebar navigation with 16 features, organized into 6 categories:
     - **LLM Evaluation** (7): Manual Pairwise Comparison, Auto Pairwise Comparison, Single Response Grading, Comprehensive Evaluation, Skills Evaluation, Batch Evaluation, Human Evaluation
     - **AI Agent Evaluation** (2): Router Evaluation, Trajectory Evaluation
     - **Reporting & Analytics** (2): Advanced Analytics, Saved Judgments & Dashboard
     - **Configuration & Setup** (2): Evaluation Templates, Custom Metrics
     - **Code Analysis** (1): Code-Based Evaluation
     - **Testing & Experimentation** (1): A/B Testing
   - Modular UI pages in `core/ui/pages/`
   - Imports from backend services for data operations

2. **REST API Server** (`backend/api_server.py`): FastAPI-based API for programmatic access
   - All evaluation endpoints
   - API key authentication
   - Rate limiting
   - Webhook support
   - Interactive Swagger/ReDoc documentation
   - Uses backend services for business logic

3. **Backend Services** (`backend/services/`): Backend-specific business logic
   - `data_service.py`: Data retrieval operations
   - `analytics_service.py`: Analytics and statistics
   - `ab_test_service.py`: A/B testing operations
   - `template_service.py`: Template management
   - `custom_metric_service.py`: Custom metrics management

4. **Shared Core** (`core/`): Business logic used by both UI and API
   - `services/`: Application services (evaluation, batch processing)
   - `domain/`: Evaluation strategies and domain models
   - `infrastructure/`: LLM adapters, database repositories

5. **Ollama Integration**: Local LLM inference for both generation and evaluation

6. **SQLite Database**: Persistent storage with enhanced schema:
   - `judgments` table: LLM evaluations
   - `human_annotations` table: Human evaluations
   - `router_evaluations` table: Router/tool selection evaluations
   - `skills_evaluations` table: Skill-specific evaluations
   - `trajectory_evaluations` table: Multi-step trajectory evaluations
   - `evaluation_runs` table: Batch evaluation tracking
   - `ab_tests` table: A/B testing configurations and results
   - `evaluation_templates` table: Reusable evaluation configurations
   - `custom_metrics` table: User-defined evaluation metrics
5. **Docker Containerization**: Isolated, reproducible deployment environment
   - Separate containers for Streamlit app and API server
   - Shared database volume

## Testing

The project includes a comprehensive end-to-end (E2E) testing framework using Playwright and the Page Object Model (POM) pattern.

### Test Framework Features

- **Page Object Model**: Encapsulated page interactions for maintainability
- **Visual Regression Testing**: Screenshot comparison for UI consistency
- **Navigation Testing**: Automated tests for all 16 navigation pages organized in 6 categories
- **Playwright**: Modern browser automation with reliable selectors

### Setup Testing Environment

1. **Install testing dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers:**
   ```bash
   python -m playwright install chromium
   ```

### Running Tests

**Run functional tests:**
```bash
# Run all functional tests
pytest tests/e2e/functional/ -v

# Run specific functional test
pytest tests/e2e/functional/test_all_navigation.py -v

# Headed mode (see browser)
HEADLESS=false pytest tests/e2e/functional/test_all_navigation.py -v
```

**Run visual regression tests:**
```bash
# Create/update baselines (first time or after UI changes)
pytest tests/e2e/visual/test_visual_navigation.py --update-baseline -v

# Compare with baselines
pytest tests/e2e/visual/test_visual_navigation.py -v
```

**Run all E2E tests:**
```bash
pytest tests/e2e/ -v
```

### Test Coverage

- ✅ **Navigation Tests**: All 16 pages organized in 6 categories (LLM Evaluation: 7, AI Agent Evaluation: 2, Reporting & Analytics: 2, Configuration & Setup: 2, Code Analysis: 1, Testing & Experimentation: 1)
- ✅ **Visual Regression Tests**: Full page layouts, sidebar navigation, main layout
- ✅ **Page Object Models**: Reusable page classes for easy test maintenance

### Test Structure

```
tests/
├── e2e/                    # E2E test cases
│   ├── functional/         # Functional E2E tests
│   │   ├── test_all_navigation.py      # Navigation tests for all pages
│   │   ├── test_pairwise_comparison.py
│   │   ├── test_auto_compare_models.py
│   │   └── test_single_grading.py
│   ├── visual/            # Visual regression tests
│   │   ├── test_visual_navigation.py   # Visual regression tests
│   │   ├── screenshots/   # Test screenshots
│   │   └── visual_baselines/  # Baseline images for visual regression
│   ├── pages/             # Page Object Model classes (shared)
│   │   ├── base_page.py
│   │   ├── pairwise_page.py
│   │   ├── auto_compare_page.py
│   │   └── navigation.py
│   └── utils/             # Test utilities (shared)
│       ├── test_data.py
│       └── visual_testing.py   # Visual comparison utilities
```

### Configuration

Environment variables for testing:
- `TEST_BASE_URL`: Base URL for Streamlit app (default: http://localhost:8501)
- `TEST_API_BASE_URL`: Base URL for API server (default: http://localhost:8000)
- `HEADLESS`: Run browser in headless mode (default: true)
- `SLOW_MO`: Slow down operations by milliseconds (default: 0)
- `TEST_TIMEOUT`: Default timeout in milliseconds (default: 30000)

### Test Reports

- **HTML Reports**: Generated in `reports/report.html` after test execution
- **Screenshots**: Saved to `tests/e2e/visual/screenshots/` on failures or when explicitly taken
- **Visual Baselines**: Stored in `tests/e2e/visual/visual_baselines/` for regression comparison

For detailed testing documentation, see [tests/README.md](tests/README.md).

### Data Flow

**Web UI Flow:**
1. User inputs question/response → Streamlit UI
2. Evaluation request → Ollama API (judge model)
3. LLM evaluation → Structured metrics and trace
4. Results → SQLite database + UI display
5. Dashboard → Aggregate statistics and visualization

**API Flow:**
1. Client sends request → REST API (with API key)
2. API validates and rate limits → Evaluation functions
3. Evaluation request → Ollama API (judge model)
4. LLM evaluation → Structured metrics and trace
5. Results → SQLite database + JSON response
6. Webhook notification → Client's webhook URL (if configured)

### Evaluation Types

The framework supports multiple evaluation approaches:

- **LLM as a Judge**: Pairwise comparison, auto model comparison, single response grading
- **Comprehensive Evaluation**: Multi-metric assessment (5 metrics)
- **Code-Based Evaluation**: Syntax, execution, and quality analysis
- **Batch Evaluation**: Process multiple test cases from datasets
- **Human Evaluation**: Human-in-the-loop annotations and comparisons
- **Router Evaluation**: Tool selection and routing decision assessment
- **Skills Evaluation**: Domain-specific skill assessments
- **Trajectory Evaluation**: Multi-step action sequence and reasoning chain assessment
- **A/B Testing**: Statistical comparison of models/configurations with significance testing
- **Evaluation Templates**: Reusable evaluation configurations and industry-specific templates
- **Custom Metrics**: User-defined evaluation metrics with custom scoring functions
- **Advanced Analytics**: Comprehensive analytics and visualizations for all evaluation data

