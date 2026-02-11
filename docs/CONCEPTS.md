## Core Concepts

This document explains key concepts behind the framework: **LLM as a Judge**, evaluation metrics, and all evaluation types including pairwise comparison, comprehensive evaluation, skills evaluation, code evaluation, router evaluation, trajectory evaluation, human evaluation, batch evaluation, A/B testing, evaluation templates, and custom metrics.

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

Detailed metric definitions live in [`docs/DATABASE.md`](docs/DATABASE.md). This section summarizes the ideas.

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

1. **Correctness (0–10)** – Accuracy of the response  
2. **Completeness (0–10)** – How complete the solution is  
3. **Clarity (0–10)** – How clear and well-structured the response is  
4. **Proficiency (0–10)** – Overall skill level demonstrated

Overall score is the average of all four metrics.  

### Trajectory Evaluation Metrics

Four dimensions:

1. **Step Quality (0–10)** – Quality of each individual step  
2. **Path Efficiency (0–10)** – Efficiency of the overall path  
3. **Reasoning Chain (0–10)** – Logical progression between steps  
4. **Planning Quality (0–10)** – Quality and completeness of planning  

---

## Evaluation Types Overview

The framework supports multiple evaluation approaches:

- **LLM-Based Evaluations**: Use an LLM judge model to evaluate responses
  - Pairwise Comparison (manual and auto)
  - Single Response Grading
  - Comprehensive Evaluation (5-metric assessment)
  - Skills Evaluation (domain-specific)
  - Router Evaluation (tool selection)
  - Trajectory Evaluation (multi-step sequences)

- **Static Analysis**: Code evaluation without LLM judges
  - Code-Based Evaluation (syntax, execution, security, quality)

- **Comparison & Testing**: Statistical and comparative methods
  - Batch Evaluation (process multiple cases)
  - A/B Testing (statistical comparison)

- **Configuration & Customization**: Reusable and custom evaluation setups
  - Evaluation Templates (industry-specific configurations)
  - Custom Metrics (user-defined scoring)

- **Human-in-the-Loop**: Human annotations and validation
  - Human Evaluation (compare human vs LLM judgments)

For practical usage instructions, see [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md).

---

## Skills Evaluation

Skills Evaluation assesses **domain-specific capabilities** of AI systems across specialized skill areas.

### Why It Matters

Different domains require different evaluation criteria:

- **Mathematics**: Problem-solving accuracy, solution completeness, step-by-step reasoning
- **Coding**: Code correctness, algorithm efficiency, best practices
- **Reasoning**: Logical consistency, argument structure, evidence quality
- **General**: Broad knowledge, communication, helpfulness

Skills Evaluation provides targeted assessment for specific domains rather than generic quality metrics.

### What It Evaluates

The LLM judge analyzes:

- Question/task in the specific skill domain
- Response to evaluate
- Optional reference answer for comparison
- Domain context (e.g., algebra, Python, logical puzzles)

It then scores **Correctness**, **Completeness**, **Clarity**, and **Proficiency**, providing domain-specific feedback.

### Use Cases

- Evaluate AI performance in specialized domains
- Compare models on domain-specific tasks
- Assess educational AI systems
- Benchmark coding assistants
- Test mathematical reasoning capabilities

---

## Code Evaluation

Code Evaluation uses **static and dynamic analysis** to assess code quality, security, and correctness—**without requiring an LLM judge model**.

### Why It Matters

Code quality assessment requires different approaches than text evaluation:

- **Syntax validation**: Does the code compile/parse?
- **Execution testing**: Does it run correctly with test inputs?
- **Security vulnerabilities**: SQL injection, XSS, hardcoded secrets
- **Code smells**: Long methods, duplicate code, magic numbers
- **Quality metrics**: Complexity, maintainability, technical debt

### What It Analyzes

Code Evaluation performs:

1. **Syntax Check**: Validates code structure and identifies errors
2. **Execution Test**: Runs code with provided test inputs (for supported languages)
3. **Quality Metrics**: Lines of code, functions, classes, maintainability scores
4. **Security Analysis**: Detects vulnerabilities (BLOCKER, CRITICAL, MAJOR severity)
5. **Code Smells**: Identifies anti-patterns (MAJOR, MINOR, INFO severity)
6. **Advanced Metrics**: Cyclomatic complexity, cognitive complexity, technical debt ratio

### Supported Languages

- **Backend**: Python, JavaScript (Node.js), TypeScript, Java, Go
- **Web**: JavaScript, TypeScript, HTML, CSS
- **Mobile**: Swift, Objective-C (iOS), Kotlin, Java (Android)

### When to Use

- Evaluate code generation models
- Assess code quality in educational contexts
- Security auditing of generated code
- Code review automation
- Technical debt assessment

---

## Batch Evaluation

Batch Evaluation enables **processing multiple test cases** efficiently from datasets (JSON/CSV files).

### Why It Matters

Individual evaluations are useful for exploration, but systematic evaluation requires:

- **Scalability**: Evaluate hundreds or thousands of test cases
- **Consistency**: Same evaluation settings across all cases
- **Efficiency**: Automated processing with progress tracking
- **Aggregation**: View overall statistics and trends

### How It Works

1. **Prepare Dataset**: JSON array or CSV file with `question`, `response`, and optional `reference` fields
2. **Configure Evaluation**: Choose evaluation type (comprehensive or single), task type, judge model
3. **Run Batch**: System processes all cases sequentially with progress tracking
4. **Review Results**: Aggregate metrics, detailed per-case results, export capabilities

### Use Cases

- Benchmark model performance on standard datasets
- Evaluate model updates across test suites
- Process evaluation datasets from research papers
- Quality assurance testing at scale
- Regression testing for model improvements

---

## A/B Testing

A/B Testing provides **statistical comparison** of two variants (models, configurations, or prompts) to determine which performs better.

### Why It Matters

Simple comparisons don't reveal statistical significance:

- **Statistical Validity**: Determine if differences are meaningful or random
- **Confidence Intervals**: Understand uncertainty in results
- **Effect Size**: Measure practical significance, not just statistical
- **Multiple Tests**: T-test, Mann-Whitney U test for different data distributions

### How It Works

1. **Create Test**: Define Variant A and Variant B (models, evaluation types, configurations)
2. **Add Test Cases**: Manual entry or upload JSON/CSV with questions
3. **Run Test**: Execute evaluations for both variants on all test cases
4. **Statistical Analysis**: 
   - T-test (parametric) and Mann-Whitney U test (non-parametric)
   - Effect size (Cohen's d) with interpretation
   - Confidence intervals for mean differences
5. **Visualization**: Box plots, pie charts, detailed results tables

### Use Cases

- Compare model versions before deployment
- Test prompt engineering changes
- Evaluate configuration improvements
- Validate router algorithm changes
- Measure impact of template modifications

---

## Evaluation Templates

Evaluation Templates provide **reusable evaluation configurations** with industry-specific settings and metric weights.

### Why It Matters

Different industries and use cases require different evaluation priorities:

- **Healthcare**: Medical accuracy is critical, creativity less important
- **Finance**: Regulatory compliance and precision over style
- **Legal**: Case analysis accuracy and citation quality
- **Education**: Learning effectiveness and clarity
- **Code Review**: Production readiness, security, maintainability

Templates standardize evaluation settings across teams and projects.

### What Templates Include

- **Metric Weights**: Adjust importance of accuracy, relevance, coherence, etc.
- **Task Type**: Optimize for QA, summarization, code, translation, creative
- **Custom Prompts**: Industry-specific evaluation criteria
- **Quality Thresholds**: Minimum acceptable scores
- **Predefined Templates**: System-provided templates for common industries
- **Custom Templates**: User-created templates for specific needs

### Use Cases

- Standardize evaluation across team members
- Apply industry-specific evaluation criteria
- Reuse proven evaluation configurations
- Maintain consistency in long-term projects
- Share evaluation best practices

---

## Custom Metrics

Custom Metrics enable **user-defined evaluation dimensions** tailored to specific domains, use cases, or requirements.

### Why It Matters

Standard metrics may not capture domain-specific concerns:

- **Domain-Specific**: Healthcare empathy, legal citation quality, educational engagement
- **Use Case-Specific**: Customer satisfaction, brand alignment, technical accuracy
- **Flexible Scoring**: Custom scales (0–10, 1–5, 0–100) and scoring functions
- **Weighted Integration**: Combine custom metrics with standard metrics

### What Custom Metrics Include

- **Metric Definition**: What the metric measures and how
- **Scoring Scale**: Custom min/max range (e.g., 0–10, 1–5, 0–100)
- **Evaluation Criteria**: Structured JSON criteria for consistent scoring
- **Scoring Function**: Description of how scores are calculated
- **Weight**: Importance relative to other metrics
- **Domain Categorization**: Healthcare, finance, legal, education, software, general

### Use Cases

- Define domain-specific quality dimensions
- Measure brand-specific attributes
- Evaluate specialized use cases
- Create proprietary evaluation frameworks
- Extend standard metrics with custom dimensions

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

---

## Pairwise Comparison

Pairwise Comparison evaluates **which of two responses is better** for a given question or task.

### Types

1. **Manual Pairwise**: You provide both responses (Response A and Response B)
2. **Auto Pairwise**: System generates responses using two different models, then judges them

### What It Evaluates

The LLM judge compares:
- Which response better answers the question
- Quality, accuracy, and helpfulness differences
- Relative strengths and weaknesses

### Position Bias Mitigation

The framework supports **Conservative Position Bias Mitigation** (MT-Bench recommendation):
- Calls judge twice with swapped response positions
- Only declares a winner if both evaluations agree
- Otherwise declares a tie
- More accurate but uses 2x API calls

### Use Cases

- Compare model outputs side-by-side
- Evaluate prompt engineering changes
- Test model improvements
- Benchmark model performance

---

## Single Response Grading

Single Response Grading provides **overall quality assessment** of a single response without comparison.

### What It Evaluates

The LLM judge assesses:
- Overall score (0–10)
- Strengths of the response
- Weaknesses and areas for improvement
- Detailed feedback and suggestions

### Custom Criteria

You can provide custom evaluation criteria to focus on specific aspects (e.g., "Focus on technical accuracy" or "Emphasize clarity for beginners").

### Use Cases

- Quick quality checks
- Educational feedback
- Content review
- Iterative improvement

---

## Comprehensive Evaluation

Comprehensive Evaluation provides **multi-dimensional assessment** across five key metrics for thorough quality analysis.

### The Five Metrics

1. **Accuracy**: Factual correctness and truthfulness
2. **Relevance**: How well the response addresses the question
3. **Coherence**: Clarity, logical structure, and readability
4. **Hallucination** (inverted): Detection of false or fabricated information
5. **Toxicity** (inverted): Detection of harmful, biased, or inappropriate content

### Task Types

Optimized prompts for different task types:
- **General**: Broad knowledge and communication
- **QA**: Question-answering accuracy
- **Summarization**: Summary quality and completeness
- **Code**: Code explanation and technical accuracy
- **Translation**: Translation quality and fidelity
- **Creative**: Creativity and originality

### Reference Answers

Optional reference answers enable more accurate evaluation by providing ground truth for comparison.

### Use Cases

- Comprehensive quality assessment
- Safety and accuracy auditing
- Model benchmarking
- Content quality assurance
- Regulatory compliance checking

---

## Notes

- The app uses **Ollama**, running locally – **no external API keys needed**  
- All LLM calls and data processing happen on your machine  
- Database persistence is optional and can be disabled via the UI  
- The app can run fully offline once dependencies and models are installed  
- Evaluation traces are stored for observability and debugging  
- Code Evaluation uses static analysis and does **not** require an LLM judge model  

