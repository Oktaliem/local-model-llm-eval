"""
Data service for retrieving evaluation data from the database.
Extracted from app.py to separate backend concerns.
"""
import sqlite3
import json
import os
import uuid
from typing import List, Dict, Any, Optional

# Database path - default to data/ directory
DB_NAME = os.getenv("DB_NAME", "llm_judge.db")
DB_PATH = os.getenv("DB_PATH", "data/llm_judge.db")


def get_all_judgments(limit=50):
    """Get all judgments from the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM judgments 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (limit,))
    
    columns = [description[0] for description in c.description]
    judgments = [dict(zip(columns, row)) for row in c.fetchall()]
    
    conn.close()
    return judgments


def delete_judgment(judgment_id: int):
    """Delete a judgment from the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('DELETE FROM judgments WHERE id = ?', (judgment_id,))
    
    conn.commit()
    conn.close()


def save_judgment(question: str, response_a: str, response_b: str, 
                 model_a: str, model_b: str, judge_model: str, 
                 judgment: str, judgment_type: str,
                 evaluation_id: Optional[str] = None,
                 metrics_json: Optional[str] = None,
                 trace_json: Optional[str] = None) -> int:
    """Save a judgment to the database with enhanced fields."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO judgments 
        (evaluation_id, question, response_a, response_b, model_a, model_b, judge_model, judgment, judgment_type, metrics_json, trace_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (evaluation_id, question, response_a, response_b, model_a, model_b, judge_model, judgment, judgment_type, metrics_json, trace_json))
    
    conn.commit()
    judgment_id = c.lastrowid
    conn.close()
    return judgment_id


def get_router_evaluations(limit=50) -> List[Dict[str, Any]]:
    """Get all router evaluations from the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM router_evaluations 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (limit,))
    
    columns = [description[0] for description in c.description]
    evaluations = [dict(zip(columns, row)) for row in c.fetchall()]
    
    conn.close()
    return evaluations


def get_skills_evaluations(limit=50, skill_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all skills evaluations from the database, optionally filtered by skill type."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if skill_type:
        c.execute('''
            SELECT * FROM skills_evaluations 
            WHERE skill_type = ?
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (skill_type, limit))
    else:
        c.execute('''
        SELECT * FROM skills_evaluations 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (limit,))
    
    columns = [description[0] for description in c.description]
    evaluations = [dict(zip(columns, row)) for row in c.fetchall()]
    
    conn.close()
    return evaluations


def get_trajectory_evaluations(limit=50, trajectory_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all trajectory evaluations from the database, optionally filtered by trajectory type."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if trajectory_type:
        c.execute('''
            SELECT * FROM trajectory_evaluations 
            WHERE trajectory_type = ?
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (trajectory_type, limit))
    else:
        c.execute('''
            SELECT * FROM trajectory_evaluations 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
    
    columns = [description[0] for description in c.description]
    evaluations = [dict(zip(columns, row)) for row in c.fetchall()]
    
    conn.close()
    return evaluations


def save_router_evaluation(
    query: str,
    available_tools: List[Dict[str, Any]],
    selected_tool: str,
    tool_accuracy_score: float,
    routing_quality_score: float,
    reasoning_score: float,
    overall_score: float,
    judgment_text: str,
    metrics_json: str,
    trace_json: str,
    evaluation_id: str,
    context: Optional[str] = None,
    expected_tool: Optional[str] = None,
    routing_strategy: Optional[str] = None,
    routing_path_json: Optional[str] = None
) -> int:
    """Save a router evaluation to the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    available_tools_json = json.dumps(available_tools)
    
    c.execute('''
        INSERT INTO router_evaluations 
        (evaluation_id, query, context, available_tools_json, selected_tool, expected_tool,
         routing_strategy, tool_accuracy_score, routing_quality_score, reasoning_score,
         overall_score, judgment_text, metrics_json, routing_path_json, trace_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (evaluation_id, query, context, available_tools_json, selected_tool, expected_tool,
          routing_strategy, tool_accuracy_score, routing_quality_score, reasoning_score,
          overall_score, judgment_text, metrics_json, routing_path_json or "{}", trace_json))
    
    conn.commit()
    eval_id = c.lastrowid
    conn.close()
    return eval_id


def save_skills_evaluation(
    skill_type: str,
    question: str,
    response: str,
    correctness_score: float,
    completeness_score: float,
    clarity_score: float,
    proficiency_score: float,
    overall_score: float,
    judgment_text: str,
    skill_metrics_json: str,
    trace_json: str,
    evaluation_id: str,
    reference_answer: Optional[str] = None,
    domain: Optional[str] = None
) -> int:
    """Save a skills evaluation to the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO skills_evaluations 
        (evaluation_id, skill_type, question, response, reference_answer, domain,
         skill_metrics_json, proficiency_score, correctness_score, completeness_score,
         clarity_score, overall_score, judgment_text, trace_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (evaluation_id, skill_type, question, response, reference_answer, domain,
          skill_metrics_json, proficiency_score, correctness_score, completeness_score,
          clarity_score, overall_score, judgment_text, trace_json))
    
    conn.commit()
    eval_id = c.lastrowid
    conn.close()
    return eval_id


def save_trajectory_evaluation(
    task_description: str,
    trajectory: List[Dict[str, Any]],
    step_quality_score: float,
    path_efficiency_score: float,
    reasoning_chain_score: float,
    planning_quality_score: float,
    overall_score: float,
    judgment_text: str,
    metrics_json: str,
    trace_json: str,
    evaluation_id: str,
    expected_trajectory: Optional[List[Dict[str, Any]]] = None,
    trajectory_type: Optional[str] = None
) -> int:
    """Save a trajectory evaluation to the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    trajectory_json = json.dumps(trajectory)
    expected_trajectory_json = json.dumps(expected_trajectory) if expected_trajectory else None
    
    c.execute('''
        INSERT INTO trajectory_evaluations 
        (evaluation_id, task_description, trajectory_json, expected_trajectory_json, trajectory_type,
         step_quality_score, path_efficiency_score, reasoning_chain_score, planning_quality_score,
         overall_score, judgment_text, metrics_json, trace_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (evaluation_id, task_description, trajectory_json, expected_trajectory_json, trajectory_type,
          step_quality_score, path_efficiency_score, reasoning_chain_score, planning_quality_score,
          overall_score, judgment_text, metrics_json, trace_json))
    
    conn.commit()
    eval_id = c.lastrowid
    conn.close()
    return eval_id


def get_human_annotations(limit=50, judgment_id: Optional[int] = None, 
                         evaluation_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get human annotations, optionally filtered by judgment_id or evaluation_id."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if judgment_id:
        c.execute('''
            SELECT * FROM human_annotations 
            WHERE judgment_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (judgment_id, limit))
    elif evaluation_id:
        c.execute('''
            SELECT * FROM human_annotations 
            WHERE evaluation_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (evaluation_id, limit))
    else:
        c.execute('''
            SELECT * FROM human_annotations 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
    
    columns = [description[0] for description in c.description]
    annotations = [dict(zip(columns, row)) for row in c.fetchall()]
    
    conn.close()
    return annotations


def save_human_annotation(
    annotator_name: str,
    question: str,
    evaluation_type: str,
    accuracy_score: Optional[float] = None,
    relevance_score: Optional[float] = None,
    coherence_score: Optional[float] = None,
    hallucination_score: Optional[float] = None,
    toxicity_score: Optional[float] = None,
    overall_score: Optional[float] = None,
    response: Optional[str] = None,
    response_a: Optional[str] = None,
    response_b: Optional[str] = None,
    feedback_text: Optional[str] = None,
    ratings_json: Optional[str] = None,
    judgment_id: Optional[int] = None,
    evaluation_id: Optional[str] = None,
    annotator_email: Optional[str] = None
) -> int:
    """Save a human annotation to the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    annotation_id = str(uuid.uuid4())
    
    # Calculate overall score if not provided
    if overall_score is None:
        scores = [s for s in [accuracy_score, relevance_score, coherence_score] if s is not None]
        if scores:
            # For hallucination and toxicity, lower is better, so invert them
            if hallucination_score is not None:
                scores.append(10 - hallucination_score)
            if toxicity_score is not None:
                scores.append(10 - toxicity_score)
            overall_score = sum(scores) / len(scores) if scores else None
    
    c.execute('''
        INSERT INTO human_annotations 
        (annotation_id, judgment_id, evaluation_id, annotator_name, annotator_email,
         question, response, response_a, response_b, evaluation_type,
         accuracy_score, relevance_score, coherence_score, hallucination_score, 
         toxicity_score, overall_score, feedback_text, ratings_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (annotation_id, judgment_id, evaluation_id, annotator_name, annotator_email,
          question, response, response_a, response_b, evaluation_type,
          accuracy_score, relevance_score, coherence_score, hallucination_score,
          toxicity_score, overall_score, feedback_text, ratings_json))
    
    conn.commit()
    annotation_db_id = c.lastrowid
    conn.close()
    return annotation_db_id


def get_annotations_for_comparison(judgment_id: Optional[int] = None,
                                   evaluation_id: Optional[str] = None) -> Dict[str, Any]:
    """Get human annotations and corresponding LLM judgments for comparison."""
    result = {
        'human_annotations': [],
        'llm_judgments': []
    }
    
    # Get human annotations
    if judgment_id:
        result['human_annotations'] = get_human_annotations(limit=100, judgment_id=judgment_id)
    elif evaluation_id:
        result['human_annotations'] = get_human_annotations(limit=100, evaluation_id=evaluation_id)
    
    # Get LLM judgments
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if judgment_id:
        c.execute('SELECT * FROM judgments WHERE id = ?', (judgment_id,))
        row = c.fetchone()
        if row:
            columns = [description[0] for description in c.description]
            result['llm_judgments'] = [dict(zip(columns, row))]
    elif evaluation_id:
        c.execute('SELECT * FROM judgments WHERE evaluation_id = ?', (evaluation_id,))
        columns = [description[0] for description in c.description]
        result['llm_judgments'] = [dict(zip(columns, row)) for row in c.fetchall()]
    
    conn.close()
    return result


def calculate_agreement_metrics(annotations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate inter-annotator agreement metrics."""
    if len(annotations) < 2:
        return {
            'num_annotators': len(annotations),
            'agreement_available': False,
            'message': 'Need at least 2 annotations to calculate agreement'
        }
    
    # Extract scores for each metric
    metrics = ['accuracy_score', 'relevance_score', 'coherence_score', 
               'overall_score', 'hallucination_score', 'toxicity_score']
    
    agreement_data = {}
    
    for metric in metrics:
        scores = [a.get(metric) for a in annotations if a.get(metric) is not None]
        if len(scores) >= 2:
            mean_score = sum(scores) / len(scores)
            variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
            std_dev = variance ** 0.5
            agreement_data[metric] = {
                'mean': round(mean_score, 2),
                'std_dev': round(std_dev, 2),
                'variance': round(variance, 2),
                'min': round(min(scores), 2),
                'max': round(max(scores), 2),
                'range': round(max(scores) - min(scores), 2)
            }
    
    return {
        'num_annotators': len(annotations),
        'agreement_available': True,
        'metrics': agreement_data
    }


def save_evaluation_run(run_id: str, run_name: str, dataset_name: str, 
                       total_cases: int, status: str = "running") -> int:
    """Save or update an evaluation run."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT OR REPLACE INTO evaluation_runs 
        (run_id, run_name, dataset_name, total_cases, completed_cases, status, created_at)
        VALUES (?, ?, ?, ?, 0, ?, CURRENT_TIMESTAMP)
    ''', (run_id, run_name, dataset_name, total_cases, status))
    
    conn.commit()
    run_db_id = c.lastrowid
    conn.close()
    return run_db_id


def update_evaluation_run(run_id: str, completed_cases: int, status: str, 
                         results_json: Optional[str] = None):
    """Update an evaluation run progress."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if status == "completed":
        c.execute('''
            UPDATE evaluation_runs 
            SET completed_cases = ?, status = ?, results_json = ?, completed_at = CURRENT_TIMESTAMP
            WHERE run_id = ?
        ''', (completed_cases, status, results_json, run_id))
    else:
        c.execute('''
            UPDATE evaluation_runs 
            SET completed_cases = ?, status = ?
            WHERE run_id = ?
        ''', (completed_cases, status, run_id))
    
    conn.commit()
    conn.close()


def get_evaluation_run(run_id: str) -> Optional[Dict[str, Any]]:
    """Get an evaluation run by run_id."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT * FROM evaluation_runs WHERE run_id = ?', (run_id,))
    row = c.fetchone()
    
    if row:
        columns = [description[0] for description in c.description]
        result = dict(zip(columns, row))
        if result.get('results_json'):
            result['results_json'] = json.loads(result['results_json'])
    else:
        result = None
    
    conn.close()
    return result


def get_all_evaluation_data(limit=1000) -> Dict[str, Any]:
    """Aggregate all evaluation data from all tables for analytics."""
    data = {
        "judgments": [],
        "comprehensive": [],
        "code_evaluations": [],
        "router_evaluations": [],
        "skills_evaluations": [],
        "trajectory_evaluations": [],
        "human_annotations": []
    }
    
    # Get judgments
    judgments = get_all_judgments(limit=limit)
    data["judgments"] = judgments
    
    # Get comprehensive evaluations
    comprehensive = [j for j in judgments if j.get("judgment_type") in ["comprehensive", "batch_comprehensive"]]
    for j in comprehensive:
        try:
            if j.get("metrics_json"):
                metrics = json.loads(j.get("metrics_json", "{}"))
                data["comprehensive"].append({
                    "id": j.get("id"),
                    "evaluation_id": j.get("evaluation_id"),
                    "judge_model": j.get("judge_model"),
                    "created_at": j.get("created_at"),
                    "overall_score": metrics.get("overall_score", 0),
                    "accuracy": metrics.get("accuracy", {}).get("score", 0),
                    "relevance": metrics.get("relevance", {}).get("score", 0),
                    "coherence": metrics.get("coherence", {}).get("score", 0),
                    "hallucination": metrics.get("hallucination", {}).get("score", 0),
                    "toxicity": metrics.get("toxicity", {}).get("score", 0)
                })
        except:
            pass
    
    # Get code evaluations
    code_evals = [j for j in judgments if j.get("judgment_type") == "code_evaluation"]
    for j in code_evals:
        try:
            if j.get("metrics_json"):
                metrics = json.loads(j.get("metrics_json", "{}"))
                data["code_evaluations"].append({
                    "id": j.get("id"),
                    "evaluation_id": j.get("evaluation_id"),
                    "judge_model": j.get("judge_model"),
                    "created_at": j.get("created_at"),
                    "overall_score": metrics.get("overall_score", 0),
                    "syntax_valid": metrics.get("syntax", {}).get("valid", False),
                    "execution_success": metrics.get("execution", {}).get("success", False),
                    "maintainability": metrics.get("quality", {}).get("maintainability", 0),
                    "readability": metrics.get("quality", {}).get("readability", 0)
                })
        except:
            pass
    
    # Get router evaluations
    router_evals = get_router_evaluations(limit=limit)
    for eval_item in router_evals:
        data["router_evaluations"].append({
            "id": eval_item.get("id"),
            "evaluation_id": eval_item.get("evaluation_id"),
            "created_at": eval_item.get("created_at"),
            "tool_accuracy": eval_item.get("tool_accuracy_score", 0),
            "routing_quality": eval_item.get("routing_quality_score", 0),
            "reasoning": eval_item.get("reasoning_score", 0),
            "overall_score": eval_item.get("overall_score", 0)
        })
    
    # Get skills evaluations
    skills_evals = get_skills_evaluations(limit=limit)
    for eval_item in skills_evals:
        data["skills_evaluations"].append({
            "id": eval_item.get("id"),
            "evaluation_id": eval_item.get("evaluation_id"),
            "skill_type": eval_item.get("skill_type"),
            "domain": eval_item.get("domain"),
            "created_at": eval_item.get("created_at"),
            "correctness": eval_item.get("correctness_score", 0),
            "completeness": eval_item.get("completeness_score", 0),
            "clarity": eval_item.get("clarity_score", 0),
            "proficiency": eval_item.get("proficiency_score", 0),
            "overall_score": eval_item.get("overall_score", 0)
        })
    
    # Get trajectory evaluations
    trajectory_evals = get_trajectory_evaluations(limit=limit)
    for eval_item in trajectory_evals:
        data["trajectory_evaluations"].append({
            "id": eval_item.get("id"),
            "evaluation_id": eval_item.get("evaluation_id"),
            "trajectory_type": eval_item.get("trajectory_type"),
            "created_at": eval_item.get("created_at"),
            "step_quality": eval_item.get("step_quality_score", 0),
            "path_efficiency": eval_item.get("path_efficiency_score", 0),
            "reasoning_chain": eval_item.get("reasoning_chain_score", 0),
            "planning_quality": eval_item.get("planning_quality_score", 0),
            "overall_score": eval_item.get("overall_score", 0)
        })
    
    # Get human annotations
    human_anns = get_human_annotations(limit=limit)
    for ann in human_anns:
        data["human_annotations"].append({
            "id": ann.get("id"),
            "annotator_name": ann.get("annotator_name"),
            "evaluation_type": ann.get("evaluation_type"),
            "created_at": ann.get("created_at"),
            "overall_score": ann.get("overall_score", 0),
            "accuracy": ann.get("accuracy_score"),
            "relevance": ann.get("relevance_score"),
            "coherence": ann.get("coherence_score")
        })
    
    return data

