## User Guide

This guide explains how to use the web UI to run different types of evaluations.

For installation and running the app, see **`docs/GETTING_STARTED.md`**.

---

## How to Use

### Manual Pairwise Comparison

1. Select "🔀 Manual Pairwise Comparison" from the sidebar navigation  
2. Enter a question or task  
3. Enter two different responses (Response A and Response B)  
4. (Optional) Expand "⚙️ Advanced Options" to enable:
   - **Conservative Position Bias Mitigation**: Calls judge twice with swapped positions. Only declares a win if both evaluations agree, else tie. More accurate but uses 2x API calls (MT-Bench paper recommendation). See `documentation/POSITION_BIAS_GUIDE.md` for detailed trade-offs and when to use each approach.
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
5. (Optional) Expand "⚙️ Advanced Options" to enable conservative position bias mitigation  
6. (Optional) Toggle "Save to DB" checkbox (enabled by default)  
7. Click "🚀 Generate & Judge"  
8. The app will:
   - Generate Response A using Model A (with status indicator)
   - Generate Response B using Model B (with status indicator)
   - Judge both responses (with status indicator, shows "2 evaluations" if Conservative mode is enabled)
   - Show stop buttons during each step
9. Review the generated responses and judgment

### Single Response Grading

1. Select "📊 Single Response Grading" from the sidebar navigation  
2. Enter a question or task  
3. Enter the response to evaluate  
4. (Optional) Add custom evaluation criteria  
5. (Optional) Toggle "Save to DB" checkbox (enabled by default)  
6. Click "📊 Evaluate Response"  
7. While running, you'll see a status indicator and a **⏹️ Stop** button  
8. Review the score, strengths, weaknesses, and detailed feedback

### Comprehensive Evaluation

1. Select "🎯 Comprehensive Evaluation" from the sidebar navigation  
2. Select task type (general, qa, summarization, code, translation, creative)  
3. Enter a question or task  
4. Enter the response to evaluate  
5. (Optional) Enable "Use Reference Answer" and provide a reference for more accurate evaluation  
6. Click "🎯 Run Comprehensive Evaluation"  
7. The app will evaluate across 5 metrics:
   - **Accuracy** (0–10)
   - **Relevance** (0–10)
   - **Coherence** (0–10)
   - **Hallucination** (0–10, inverted)
   - **Toxicity** (0–10, inverted)
8. Review the overall score and detailed metrics breakdown  
9. View the evaluation trace for observability

### Code-Based Evaluation

1. Select "💻 Code-Based Evaluation" from the sidebar navigation (under "Code Analysis")  
2. Select programming language:
   - Backend: Python, JavaScript (Node.js), TypeScript, Java, Go
   - Web: JavaScript, TypeScript, HTML, CSS
   - iOS: Swift, Objective-C
   - Android: Kotlin, Java
3. Enter or paste code to evaluate  
4. (Optional) Provide test inputs and expected output  
5. Click "💻 Evaluate Code"  
6. Review:
   - Syntax check
   - Execution test (for supported languages)
   - Quality metrics
   - Security vulnerabilities
   - Code smells
   - Advanced metrics  
7. View overall code evaluation score (adjusted for security issues and code smells)

### Batch Evaluation

1. Select "📦 Batch Evaluation" from the sidebar navigation  
2. Prepare a dataset file:
   - JSON: array of objects with `question`, `response`, and optional `reference`
   - CSV: columns `question`, `response`, `reference`
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
2. Choose mode:
   - New Evaluation
   - Compare with LLM Judgment
   - View All Annotations
3. For New Evaluation:
   - Enter annotator name and email (optional)
   - Select evaluation type (comprehensive, single, pairwise)
   - Enter question and response(s)
   - Rate metrics (0–10) for comprehensive evaluations
   - Add feedback (optional)
   - Click "💾 Save Human Annotation"
4. For Comparison:
   - Select an LLM judgment
   - View human annotations and agreement metrics

### Router Evaluation

1. Select "🔀 Router Evaluation" from the sidebar navigation  
2. Choose evaluation mode:
   - Evaluate Router Decision
   - View All Router Evaluations
3. For Router Decision Evaluation:
   - Enter query/request
   - Add context (optional)
   - Configure available tools (1–20)
   - Select the tool that was chosen
   - (Optional) Specify expected tool
   - Enter routing strategy (optional)
   - Click "⚖️ Evaluate Router Decision"
4. Review metrics:
   - Tool Accuracy (0–10)
   - Routing Quality (0–10)
   - Reasoning Quality (0–10)
   - Overall Score (average)

### Skills Evaluation

1. Select "🎓 Skills Evaluation" from the sidebar navigation  
2. Choose evaluation mode:
   - Evaluate Skill
   - View All Skills Evaluations
3. For Skill Evaluation:
   - Select skill type (mathematics, coding, reasoning, general)
   - Enter domain (optional)
   - Enter question/task
   - Enter response to evaluate
   - (Optional) Provide reference answer
   - Click "⚖️ Evaluate Skill"
4. Review:
   - Correctness
   - Completeness
   - Clarity
   - Proficiency
   - Overall Score

### Trajectory Evaluation

Trajectory Evaluation assesses multi-step action sequences, agent trajectories, and reasoning chains.

1. Select "🛤️ Trajectory Evaluation" from the sidebar  
2. Choose mode:
   - Evaluate Trajectory
   - View All Trajectory Evaluations
3. Fill in:
   - Task Description
   - Trajectory Type (optional)
   - Actual Trajectory (JSON or manual)
   - Expected Trajectory (optional)
   - Judge model
   - Save to DB flag
4. Click "⚖️ Evaluate Trajectory"  
5. Review:
   - Step Quality
   - Path Efficiency
   - Reasoning Chain
   - Planning Quality
   - Overall Score
   - Detailed judgment text

### A/B Testing

1. Select "🧪 A/B Testing" from the sidebar  
2. Choose mode:
   - Create New A/B Test
   - Run A/B Test
   - View Test Results
3. Configure variants (models, evaluation type, task type)  
4. Add test cases (manual or JSON/CSV)  
5. Run the test with a chosen judge model  
6. Review statistical analysis, visualizations, and exports

### Evaluation Templates

1. Select "📋 Evaluation Templates" from the sidebar  
2. Browse, create, or manage templates  
3. For creation:
   - Name, description, evaluation type, optional industry
   - Configure metrics, weights, prompts
4. Use templates directly from Comprehensive Evaluation by selecting them.

### Custom Metrics

1. Select "🎯 Custom Metrics" from the sidebar  
2. Browse, create, evaluate with, or manage metrics  
3. Define:
   - Metric name, description
   - Evaluation type, domain (optional)
   - Scale (min/max), weight
   - Criteria JSON and scoring description (optional)
4. Run evaluations with custom metrics and view normalized scores and explanations.

### Advanced Analytics

1. Select "📈 Advanced Analytics" from the sidebar  
2. Explore:
   - Time series analysis
   - Comparative analytics
   - Aggregate statistics
   - Performance heatmaps
   - Model comparison
   - Export data

---

## Saved Judgments & Dashboard

1. Select "💾 Saved Judgments & Dashboard" from the sidebar  
2. View metrics dashboard with aggregate statistics (for comprehensive evaluations)  
3. Browse all saved judgments from the database  
4. Filter by judgment type (pairwise_manual, pairwise_auto, single, comprehensive, code_evaluation, batch_comprehensive, batch_single)  
5. Adjust the number of judgments to display  
6. Expand any judgment to see full details, including metrics, explanations, traces, and human annotations  
7. Delete individual judgments or export all as JSON

---

## Example Use Cases

- A/B testing of models and prompts  
- Quality assessment of AI responses  
- Model comparison across metrics  
- Educational feedback and skills evaluation  
- Prompt engineering experiments  
- Agent routing and trajectory evaluation  
- Code quality and security checks  
- Human-in-the-loop evaluation workflows  
- Safety testing (hallucination and toxicity)  
- Batch testing on benchmark datasets  
- Template-based, domain-specific evaluation  
- Custom domain metrics and scoring

---

## Stop Button Behavior

The app includes a **⏹️ Stop** button during evaluations:

- Runs evaluations in background threads  
- Stop sets a flag that prevents results from being displayed or saved  
- The underlying Ollama call may still complete, but results are ignored  
- The page auto-refreshes every 2 seconds to check for completion  

