## Core Concepts

This document explains key concepts behind the framework: **LLM as a Judge**, evaluation metrics, router evaluation, human evaluation, and trajectory evaluation.

---

## What is LLM as a Judge?

LLM as a Judge uses large language models (LLMs) to evaluate the outputs of other AI systems or language models.

Instead of relying solely on human reviewers or traditional metrics, this approach leverages the reasoning capabilities of LLMs to assess:

- Accuracy and correctness  
- Relevance to the question  
- Clarity and coherence  
- Completeness  
- Helpfulness

---

## Evaluation Metrics (High-Level)

Detailed metric definitions live in `docs/DATABASE.md`. This section summarizes the ideas.

### Comprehensive Evaluation Metrics

Five dimensions:

1. **Accuracy (0–10)** – Factual correctness  
2. **Relevance (0–10)** – How well the response addresses the question  
3. **Coherence (0–10)** – Clarity and logical structure  
4. **Hallucination (0–10, inverted)** – Degree of fabricated / unsupported content  
5. **Toxicity (0–10, inverted)** – Degree of harmful / inappropriate content  

Overall score is the average of all metrics.

### Router Evaluation Metrics

Three dimensions:

1. **Tool Accuracy (0–10)** – Was the correct/best tool selected?  
2. **Routing Quality (0–10)** – Alignment between query and selected tool  
3. **Reasoning Quality (0–10)** – Logical soundness of the routing decision  

### Skills Evaluation Metrics

Four dimensions:

1. **Correctness (0–10)**  
2. **Completeness (0–10)**  
3. **Clarity (0–10)**  
4. **Proficiency (0–10)**  

### Trajectory Evaluation Metrics

Four dimensions:

1. **Step Quality (0–10)** – Quality of each individual step  
2. **Path Efficiency (0–10)** – Efficiency of the overall path  
3. **Reasoning Chain (0–10)** – Logical progression between steps  
4. **Planning Quality (0–10)** – Quality and completeness of planning  

---

## Router Evaluation

Router Evaluation assesses how well an AI **selects tools or functions** for a given user query.

### Why It Matters

AI agents with multiple tools must choose correctly:

- Wrong tools → incorrect behavior  
- Suboptimal tools → higher cost or latency  
- Poor routing → user frustration and unreliable systems  

Router Evaluation helps:

- Test router behavior before deployment  
- Compare routing strategies (keyword, embeddings, ML)  
- Debug routing failures  
- A/B test router changes  
- Monitor routing quality over time

### What It Looks At

The LLM judge analyzes:

- User query/request  
- Available tools (names + descriptions)  
- Selected tool  
- Optional expected tool  
- Optional routing strategy description  

It then scores **Tool Accuracy**, **Routing Quality**, and **Reasoning Quality**, and returns detailed reasoning text.

---

## Human Evaluation

Human Evaluation enables human-in-the-loop evaluation, complementing LLM-based judgments.

### Why Human Evaluation

Humans provide:

- Ground-truth validation of LLM judgments  
- Quality control and error detection  
- Bias detection in automated evaluators  
- Training data for improving LLM judges  
- Inter-annotator agreement analysis  
- Auditability and regulatory compliance

### Modes

1. **New Evaluation** – Create standalone annotations  
2. **Compare with LLM Judgment** – Side-by-side comparison of human vs LLM scores and explanations  
3. **View All Annotations** – Browse, filter, and export human annotations

Human Evaluation supports the same evaluation types as LLM evaluations: comprehensive, single response, and manual pairwise.

Inter-annotator agreement metrics help identify ambiguous cases and calibration needs.

---

## Trajectory Evaluation

Trajectory Evaluation analyzes **multi-step action sequences** executed by agents.

A **trajectory** is the ordered set of steps an agent takes to complete a task.

### Intuition

- Router Evaluation: “Did the agent choose the right tool?”  
- Trajectory Evaluation: “How good was the **path** it took to solve the task?”  

This includes:

- Whether steps are appropriate and well-ordered  
- Whether the path is efficient  
- Whether the reasoning chain is logical  
- Whether planning is comprehensive

### Inputs

- Task description  
- Actual trajectory (JSON array or manual entry)  
- Optional expected trajectory (ideal path)  
- Judge model and configuration

### Outputs

- Scores for Step Quality, Path Efficiency, Reasoning Chain, Planning Quality  
- Overall score (average)  
- Detailed judgment text with actionable feedback

---

## Notes

- The app uses **Ollama**, running locally – **no external API keys needed**  
- All LLM calls and data processing happen on your machine  
- Database persistence is optional and can be disabled via the UI  
- The app can run fully offline once dependencies and models are installed  
- Evaluation traces are stored for observability and debugging  

