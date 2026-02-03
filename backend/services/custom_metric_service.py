"""
Custom Metric service for managing custom evaluation metrics.
Extracted from app.py to separate backend concerns.
"""
import sqlite3
import json
import os
import uuid
import re
import time
from typing import List, Dict, Any, Optional

# Database path - default to data/ directory
DB_NAME = os.getenv("DB_NAME", "llm_judge.db")
DB_PATH = os.getenv("DB_PATH", "data/llm_judge.db")


def create_custom_metric(
    metric_name: str,
    evaluation_type: str,
    metric_definition: str,
    metric_description: Optional[str] = None,
    domain: Optional[str] = None,
    scoring_function: Optional[str] = None,
    criteria_json: Optional[Dict[str, Any]] = None,
    weight: float = 1.0,
    scale_min: float = 0.0,
    scale_max: float = 10.0,
    created_by: Optional[str] = None
) -> str:
    """Create a new custom evaluation metric.
    
    Returns:
        metric_id: Unique identifier for the metric
    """
    metric_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO custom_metrics 
        (metric_id, metric_name, metric_description, domain, evaluation_type,
         metric_definition, scoring_function, criteria_json, weight,
         scale_min, scale_max, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        metric_id,
        metric_name,
        metric_description,
        domain,
        evaluation_type,
        metric_definition,
        scoring_function,
        json.dumps(criteria_json) if criteria_json else None,
        weight,
        scale_min,
        scale_max,
        created_by
    ))
    
    conn.commit()
    conn.close()
    return metric_id


def get_custom_metric(metric_id: str) -> Optional[Dict[str, Any]]:
    """Get a custom metric by metric_id."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT * FROM custom_metrics WHERE metric_id = ?', (metric_id,))
    row = c.fetchone()
    
    if row:
        columns = [description[0] for description in c.description]
        result = dict(zip(columns, row))
        if result.get('criteria_json'):
            result['criteria_json'] = json.loads(result['criteria_json'])
        result['is_active'] = bool(result['is_active'])
    else:
        result = None
    
    conn.close()
    return result


def get_all_custom_metrics(
    evaluation_type: Optional[str] = None,
    domain: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Get all custom metrics, optionally filtered."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    query = 'SELECT * FROM custom_metrics WHERE 1=1'
    params = []
    
    if evaluation_type:
        query += ' AND evaluation_type = ?'
        params.append(evaluation_type)
    
    if domain:
        query += ' AND domain = ?'
        params.append(domain)
    
    if is_active is not None:
        query += ' AND is_active = ?'
        params.append(1 if is_active else 0)
    
    query += ' ORDER BY usage_count DESC, created_at DESC LIMIT ?'
    params.append(limit)
    
    c.execute(query, params)
    
    columns = [description[0] for description in c.description]
    metrics = []
    for row in c.fetchall():
        metric = dict(zip(columns, row))
        if metric.get('criteria_json'):
            metric['criteria_json'] = json.loads(metric['criteria_json'])
        metric['is_active'] = bool(metric['is_active'])
        metrics.append(metric)
    
    conn.close()
    return metrics


def delete_custom_metric(metric_id: str) -> bool:
    """Delete a custom metric (soft delete by setting is_active = 0)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT metric_id FROM custom_metrics WHERE metric_id = ?', (metric_id,))
    if not c.fetchone():
        conn.close()
        return False
    
    # Soft delete
    c.execute('''
        UPDATE custom_metrics 
        SET is_active = 0, updated_at = CURRENT_TIMESTAMP
        WHERE metric_id = ?
    ''', (metric_id,))
    
    conn.commit()
    conn.close()
    return True


def evaluate_with_custom_metric(
    metric_id: str,
    question: str,
    response: str,
    reference: Optional[str] = None,
    judge_model: str = "llama3"
) -> Dict[str, Any]:
    """Evaluate a response using a custom metric.
    
    NOTE: This function depends on get_ollama_client from app.py.
    TODO: Extract to use llm_eval infrastructure.
    
    Returns:
        Dictionary with score, explanation, and metadata
    """
    start_time = time.time()
    metric = get_custom_metric(metric_id)
    if not metric or not metric.get('is_active'):
        return {
            "success": False,
            "error": "Metric not found or inactive"
        }
    
    # Use OllamaAdapter from core infrastructure
    from core.infrastructure.llm.ollama_client import OllamaAdapter
    
    # Build evaluation prompt from metric definition
    prompt = f"""Evaluate the following response based on this custom metric:

METRIC: {metric['metric_name']}
DESCRIPTION: {metric.get('metric_description', metric['metric_definition'])}

METRIC DEFINITION:
{metric['metric_definition']}

{f"CRITERIA: {json.dumps(metric.get('criteria_json', {}), indent=2)}" if metric.get('criteria_json') else ""}

Question: {question}
Response: {response}
{f"Reference: {reference}" if reference else ""}

Please evaluate the response on a scale of {metric['scale_min']}-{metric['scale_max']} based on the metric definition above.

Provide:
1. Score: [number between {metric['scale_min']} and {metric['scale_max']}]
2. Explanation: [detailed explanation of how the response meets or fails to meet the metric criteria]
3. Strengths: [what the response does well according to this metric]
4. Weaknesses: [areas where the response could improve according to this metric]
"""
    
    try:
        ollama_adapter = OllamaAdapter()
        response_obj = ollama_adapter.chat(
            model=judge_model,
            messages=[
                {"role": "system", "content": f"You are an expert evaluator specializing in: {metric.get('domain', 'general evaluation')}"},
                {"role": "user", "content": prompt}
            ],
            options={
                "temperature": 0.3,
                "num_predict": 65536,  # 65,536 tokens for very detailed, more complete evaluations
            }
        )
        
        evaluation_text = ollama_adapter._extract_content(response_obj)
        
        # Extract score (look for number in the response)
        score_match = re.search(r'\b([0-9]+\.?[0-9]*)\b', evaluation_text)
        score = float(score_match.group()) if score_match else metric['scale_min']
        
        # Clamp score to scale
        score = max(metric['scale_min'], min(metric['scale_max'], score))
        
        # Normalize to 0-10 if needed
        if metric['scale_max'] != 10.0:
            normalized_score = (score - metric['scale_min']) / (metric['scale_max'] - metric['scale_min']) * 10.0
        else:
            normalized_score = score
        
        execution_time = time.time() - start_time
        
        return {
            "success": True,
            "metric_id": metric_id,
            "metric_name": metric['metric_name'],
            "score": score,
            "normalized_score": normalized_score,
            "explanation": evaluation_text,
            "scale": {
                "min": metric['scale_min'],
                "max": metric['scale_max']
            },
            "execution_time": execution_time
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "metric_id": metric_id
        }

