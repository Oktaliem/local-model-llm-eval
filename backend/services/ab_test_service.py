"""
A/B Testing service for managing A/B tests.
Extracted from app.py to separate backend concerns.
"""
import sqlite3
import json
import os
import uuid
from typing import List, Dict, Any, Optional, Callable

# Database path - default to data/ directory
DB_NAME = os.getenv("DB_NAME", "llm_judge.db")
DB_PATH = os.getenv("DB_PATH", "data/llm_judge.db")

# Import dependencies
from core.services.evaluation_service import EvaluationService
from core.infrastructure.llm.ollama_client import OllamaAdapter
from backend.services.statistics import calculate_statistical_significance


def create_ab_test(
    test_name: str,
    variant_a_name: str,
    variant_b_name: str,
    variant_a_config: Dict[str, Any],
    variant_b_config: Dict[str, Any],
    evaluation_type: str,
    test_cases: List[Dict[str, Any]],
    test_description: Optional[str] = None
) -> str:
    """Create a new A/B test in the database.
    
    Returns:
        test_id: Unique identifier for the test
    """
    test_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO ab_tests 
        (test_id, test_name, test_description, variant_a_name, variant_b_name,
         variant_a_config, variant_b_config, evaluation_type, test_cases_json, total_cases)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        test_id,
        test_name,
        test_description,
        variant_a_name,
        variant_b_name,
        json.dumps(variant_a_config),
        json.dumps(variant_b_config),
        evaluation_type,
        json.dumps(test_cases),
        len(test_cases)
    ))
    
    conn.commit()
    conn.close()
    return test_id


def get_ab_test(test_id: str) -> Optional[Dict[str, Any]]:
    """Get an A/B test by test_id."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT * FROM ab_tests WHERE test_id = ?', (test_id,))
    row = c.fetchone()
    
    if row:
        columns = [description[0] for description in c.description]
        result = dict(zip(columns, row))
        # Parse JSON fields
        result['variant_a_config'] = json.loads(result['variant_a_config'])
        result['variant_b_config'] = json.loads(result['variant_b_config'])
        result['test_cases_json'] = json.loads(result['test_cases_json'])
        if result.get('results_json'):
            result['results_json'] = json.loads(result['results_json'])
        if result.get('statistical_analysis_json'):
            result['statistical_analysis_json'] = json.loads(result['statistical_analysis_json'])
    else:
        result = None
    
    conn.close()
    return result


def get_all_ab_tests(limit=50) -> List[Dict[str, Any]]:
    """Get all A/B tests from the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM ab_tests 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (limit,))
    
    columns = [description[0] for description in c.description]
    tests = []
    for row in c.fetchall():
        test = dict(zip(columns, row))
        # Parse JSON fields
        test['variant_a_config'] = json.loads(test['variant_a_config'])
        test['variant_b_config'] = json.loads(test['variant_b_config'])
        test['test_cases_json'] = json.loads(test['test_cases_json'])
        if test.get('results_json'):
            test['results_json'] = json.loads(test['results_json'])
        if test.get('statistical_analysis_json'):
            test['statistical_analysis_json'] = json.loads(test['statistical_analysis_json'])
        tests.append(test)
    
    conn.close()
    return tests


def update_ab_test_progress(test_id: str, completed_cases: int, variant_a_wins: int = 0,
                            variant_b_wins: int = 0, ties: int = 0, status: str = "running"):
    """Update A/B test progress."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        UPDATE ab_tests 
        SET completed_cases = ?, variant_a_wins = ?, variant_b_wins = ?, ties = ?, status = ?
        WHERE test_id = ?
    ''', (completed_cases, variant_a_wins, variant_b_wins, ties, status, test_id))
    
    conn.commit()
    conn.close()


def save_ab_test_results(test_id: str, results: List[Dict[str, Any]], 
                        statistical_analysis: Dict[str, Any], status: str = "completed"):
    """Save A/B test results and statistical analysis."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Calculate wins from results
    variant_a_wins = sum(1 for r in results if r.get('winner') == 'A')
    variant_b_wins = sum(1 for r in results if r.get('winner') == 'B')
    ties = sum(1 for r in results if r.get('winner') == 'tie')
    
    c.execute('''
        UPDATE ab_tests 
        SET results_json = ?, statistical_analysis_json = ?, 
            variant_a_wins = ?, variant_b_wins = ?, ties = ?,
            status = ?, completed_at = CURRENT_TIMESTAMP
        WHERE test_id = ?
    ''', (
        json.dumps(results),
        json.dumps(statistical_analysis),
        variant_a_wins,
        variant_b_wins,
        ties,
        status,
        test_id
    ))
    
    conn.commit()
    conn.close()


def execute_ab_test(test_id: str, judge_model: str = "llama3", 
                   progress_callback: Optional[Callable] = None,
                   stop_flag: Optional[Callable[[], bool]] = None) -> Dict[str, Any]:
    """Execute an A/B test by running evaluations for both variants.
    
    Args:
        test_id: ID of the A/B test to execute
        judge_model: Model to use for judging comparisons
        progress_callback: Optional callback function for progress updates (current, total)
        stop_flag: Optional callable that returns True if execution should stop
    
    Returns:
        Dictionary with test results and statistical analysis
    """
    # Get test configuration
    test = get_ab_test(test_id)
    if not test:
        return {"success": False, "error": "Test not found"}
    
    # Update status to running
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE ab_tests 
        SET status = 'running', started_at = CURRENT_TIMESTAMP
        WHERE test_id = ?
    ''', (test_id,))
    conn.commit()
    conn.close()
    
    variant_a_config = test['variant_a_config']
    variant_b_config = test['variant_b_config']
    evaluation_type = test['evaluation_type']
    test_cases = test['test_cases_json']
    
    # Initialize services
    evaluation_service = EvaluationService()
    ollama_adapter = OllamaAdapter()
    
    results = []
    scores_a = []
    scores_b = []
    
    try:
        for idx, test_case in enumerate(test_cases):
            # Check stop flag (replaces Streamlit session state)
            if stop_flag and stop_flag():
                break
            
            question = test_case.get('question', '')
            
            # Get responses for variant A
            if evaluation_type == 'comprehensive':
                # For comprehensive, we need to generate or get response A
                if 'response_a' in test_case:
                    response_a = test_case['response_a']
                elif 'model_a' in variant_a_config:
                    # Generate response using model A
                    model_a = variant_a_config.get('model_a', 'llama3')
                    response = ollama_adapter.chat(
                        model=model_a,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant. Provide clear, accurate, and helpful responses."},
                            {"role": "user", "content": question}
                        ],
                        options={"temperature": 0.7}
                    )
                    response_a = ollama_adapter._extract_content(response)
                else:
                    response_a = test_case.get('response', '')
                
                # Evaluate variant A using EvaluationService
                eval_a = evaluation_service.evaluate(
                    evaluation_type="comprehensive",
                    question=question,
                    judge_model=judge_model,
                    response=response_a,
                    options={
                        "reference": test_case.get('reference'),
                        "task_type": variant_a_config.get('task_type', 'general'),
                        "include_additional_properties": True
                    },
                    save_to_db=False
                )
                score_a = eval_a.get('scores', {}).get('overall_score', 0) if eval_a.get('success') else 0
                
                # Get responses for variant B
                if 'response_b' in test_case:
                    response_b = test_case['response_b']
                elif 'model_b' in variant_b_config:
                    # Generate response using model B
                    model_b = variant_b_config.get('model_b', 'llama3')
                    response = ollama_adapter.chat(
                        model=model_b,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant. Provide clear, accurate, and helpful responses."},
                            {"role": "user", "content": question}
                        ],
                        options={"temperature": 0.7}
                    )
                    response_b = ollama_adapter._extract_content(response)
                else:
                    response_b = test_case.get('response', '')
                
                # Evaluate variant B using EvaluationService
                eval_b = evaluation_service.evaluate(
                    evaluation_type="comprehensive",
                    question=question,
                    judge_model=judge_model,
                    response=response_b,
                    options={
                        "reference": test_case.get('reference'),
                        "task_type": variant_b_config.get('task_type', 'general'),
                        "include_additional_properties": True
                    },
                    save_to_db=False
                )
                score_b = eval_b.get('scores', {}).get('overall_score', 0) if eval_b.get('success') else 0
                
            elif evaluation_type == 'pairwise':
                # For pairwise, we need both responses
                response_a = test_case.get('response_a', '')
                response_b = test_case.get('response_b', '')
                
                if not response_a or not response_b:
                    # Generate responses if not provided
                    if not response_a and 'model_a' in variant_a_config:
                        model_a = variant_a_config.get('model_a', 'llama3')
                        response = ollama_adapter.chat(
                            model=model_a,
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant. Provide clear, accurate, and helpful responses."},
                                {"role": "user", "content": question}
                            ],
                            options={"temperature": 0.7}
                        )
                        response_a = ollama_adapter._extract_content(response)
                    if not response_b and 'model_b' in variant_b_config:
                        model_b = variant_b_config.get('model_b', 'llama3')
                        response = ollama_adapter.chat(
                            model=model_b,
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant. Provide clear, accurate, and helpful responses."},
                                {"role": "user", "content": question}
                            ],
                            options={"temperature": 0.7}
                        )
                        response_b = ollama_adapter._extract_content(response)
                
                # Judge pairwise using EvaluationService
                judgment = evaluation_service.evaluate(
                    evaluation_type="pairwise",
                    question=question,
                    judge_model=judge_model,
                    response_a=response_a,
                    response_b=response_b,
                    options={},
                    save_to_db=False
                )
                
                winner = judgment.get('winner', 'tie') if judgment.get('success') else 'tie'
                
                # Assign scores based on winner
                if winner == 'A':
                    score_a = 10
                    score_b = 5
                elif winner == 'B':
                    score_a = 5
                    score_b = 10
                else:
                    score_a = 7.5
                    score_b = 7.5
                
                eval_a = {"scores": {"overall_score": score_a}}
                eval_b = {"scores": {"overall_score": score_b}}
                
            else:
                # Default: use single response evaluation
                response_a = test_case.get('response_a', test_case.get('response', ''))
                response_b = test_case.get('response_b', test_case.get('response', ''))
                
                # Simple scoring - could be enhanced
                score_a = 7.0
                score_b = 7.0
                eval_a = {"scores": {"overall_score": score_a}}
                eval_b = {"scores": {"overall_score": score_b}}
            
            scores_a.append(score_a)
            scores_b.append(score_b)
            
            # Determine winner
            if score_a > score_b:
                winner = 'A'
            elif score_b > score_a:
                winner = 'B'
            else:
                winner = 'tie'
            
            results.append({
                "test_case_index": idx,
                "question": question,
                "response_a": response_a[:200] if isinstance(response_a, str) else str(response_a)[:200],
                "response_b": response_b[:200] if isinstance(response_b, str) else str(response_b)[:200],
                "score_a": score_a,
                "score_b": score_b,
                "winner": winner,
                "evaluation_a": eval_a,
                "evaluation_b": eval_b
            })
            
            # Update progress
            update_ab_test_progress(
                test_id=test_id,
                completed_cases=idx + 1,
                variant_a_wins=sum(1 for r in results if r['winner'] == 'A'),
                variant_b_wins=sum(1 for r in results if r['winner'] == 'B'),
                ties=sum(1 for r in results if r['winner'] == 'tie'),
                status='running'
            )
            
            # Call progress callback if provided
            if progress_callback:
                progress_callback(idx + 1, len(test_cases))
        
        # Calculate statistical significance
        if len(scores_a) >= 2 and len(scores_b) >= 2:
            statistical_analysis = calculate_statistical_significance(scores_a, scores_b)
        else:
            statistical_analysis = {
                "valid": False,
                "error": "Insufficient data for statistical analysis"
            }
        
        # Save results
        save_ab_test_results(test_id, results, statistical_analysis, status='completed')
        
        return {
            "success": True,
            "test_id": test_id,
            "results": results,
            "statistical_analysis": statistical_analysis,
            "summary": {
                "total_cases": len(results),
                "variant_a_wins": sum(1 for r in results if r['winner'] == 'A'),
                "variant_b_wins": sum(1 for r in results if r['winner'] == 'B'),
                "ties": sum(1 for r in results if r['winner'] == 'tie'),
                "avg_score_a": sum(scores_a) / len(scores_a) if scores_a else 0,
                "avg_score_b": sum(scores_b) / len(scores_b) if scores_b else 0
            }
        }
        
    except Exception as e:
        # Update status to failed
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            UPDATE ab_tests 
            SET status = 'failed'
            WHERE test_id = ?
        ''', (test_id,))
        conn.commit()
        conn.close()
        
        return {
            "success": False,
            "error": str(e),
            "test_id": test_id
        }

