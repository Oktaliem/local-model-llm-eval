## Database & Metrics

This document describes the SQLite schema, stored data, and evaluation metrics.

---

## Database Overview

The app automatically saves judgments and related data to a SQLite database (`llm_judge.db`).

- **Local**: Stored in the project root directory  
- **Docker**: Stored in `./data/llm_judge.db` (volume-mounted on the host)

The database is created automatically on first save.

---

## Tables

### `judgments`

Each LLM judgment includes:

- Question/task  
- Responses (A and B)  
- Models used (for auto-generated responses)  
- Judge model  
- Full judgment text  
- Judgment type (pairwise_manual, pairwise_auto, single, comprehensive, code_evaluation, batch_comprehensive, batch_single)  
- **Evaluation ID** (UUID)  
- **Metrics JSON** (structured metrics for comprehensive evaluations)  
- **Trace JSON** (evaluation trace for observability)  
- Timestamp  

### `human_annotations`

Human annotations include:

- Annotation ID (UUID)  
- Judgment ID (link to LLM judgment, optional)  
- Annotator name and email  
- Question and response(s)  
- Evaluation type (comprehensive, single, pairwise)  
- Scores: accuracy, relevance, coherence, hallucination, toxicity, overall  
- Feedback text  
- Timestamps  

### `router_evaluations`

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

### `skills_evaluations`

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

### `trajectory_evaluations`

Trajectory evaluations include:

- Evaluation ID (UUID)  
- Task description  
- Trajectory JSON (array of steps with action and description)  
- Expected trajectory JSON (optional)  
- Trajectory type (action_sequence, reasoning_chain, planning_path, tool_usage, other)  
- Metrics: step_quality_score, path_efficiency_score, reasoning_chain_score, planning_quality_score, overall_score  
- Judgment text and metrics JSON  
- Trace JSON  
- Timestamp  

### `evaluation_runs`

Batch evaluation runs include:

- Run ID (UUID)  
- Run name and dataset name  
- Total cases and completed cases  
- Status (running, completed, failed)  
- Results JSON  
- Timestamps  

### `ab_tests`

A/B tests include:

- Test ID (UUID)  
- Test name and description  
- Variant A and B names and configurations (JSON)  
- Evaluation type (comprehensive, pairwise)  
- Test cases (JSON array)  
- Status (pending, running, completed, failed)  
- Total cases and completed cases  
- Variant A/B wins and ties counts  
- Results JSON (per-test-case results)  
- Statistical analysis JSON (t-test, Mann–Whitney, effect size, etc.)  
- Timestamps (created, started, completed)  

### `evaluation_templates`

Evaluation templates include:

- Template ID (UUID)  
- Template name and description  
- Industry category (healthcare, finance, legal, education, software, general)  
- Evaluation type (comprehensive, code_evaluation, router, skills, trajectory)  
- Template configuration (JSON) – metric weights, quality weights, prompts, etc.  
- Is predefined flag (system vs user templates)  
- Created by  
- Usage count  
- Timestamps (created, updated)  

### `custom_metrics`

Custom metrics include:

- Metric ID (UUID)  
- Metric name and description  
- Domain category (healthcare, finance, legal, education, software, general, other)  
- Evaluation type (comprehensive, code_evaluation, router, skills, trajectory, general)  
- Metric definition  
- Scoring function description (optional)  
- Criteria JSON (structured evaluation criteria)  
- Weight (for weighted scoring)  
- Scale min/max (custom scoring scale)  
- Created by  
- Usage count  
- Is active flag (soft delete)  
- Timestamps (created, updated)  

---

## Metric Definitions

### Comprehensive Evaluation Metrics

- **Accuracy score** and explanation  
- **Relevance score** and explanation  
- **Coherence score** and explanation  
- **Hallucination score** and explanation (+ risk score)  
- **Toxicity score** and explanation (+ risk score)  
- **Overall score** – average of all metrics  

### Router Evaluation Metrics

- **Tool Accuracy score (0–10)**  
- **Routing Quality score (0–10)**  
- **Reasoning Quality score (0–10)**  
- **Overall score** – average of all three  

### Skills Evaluation Metrics

- **Correctness score (0–10)**  
- **Completeness score (0–10)**  
- **Clarity score (0–10)**  
- **Proficiency score (0–10)**  
- **Overall score** – average of all four  

### Trajectory Evaluation Metrics

- **Step Quality score (0–10)**  
- **Path Efficiency score (0–10)**  
- **Reasoning Chain score (0–10)**  
- **Planning Quality score (0–10)**  
- **Overall score** – average of all four  

---

## Database Features in the UI

From the **Saved Judgments & Dashboard** page, you can:

- View all saved judgments  
- View aggregate metrics for comprehensive evaluations  
- Filter by judgment type  
- Inspect detailed metrics and traces  
- View linked human annotations  
- View router, skills, and trajectory evaluations  
- Delete individual judgments  
- Export all judgments as JSON  

