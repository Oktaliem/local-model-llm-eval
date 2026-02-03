"""
Evaluation functions - compatibility layer for functions from frontend/app.py

This module provides a compatibility layer for evaluation functions
that are still in frontend/app.py. As we refactor, these will be moved here
or replaced with EvaluationService calls.

TODO: Gradually move functions here and update callers.
"""
import sys
import os
import importlib.util

# Import from core services (new architecture)
from core.services.llm_service import generate_response
from core.services.judgment_service import judge_pairwise, save_judgment
from backend.services.skills_evaluation_service import evaluate_skill

# Import from frontend/app.py (which has all the functions)
# We need to load it as a module since it's not in a package
frontend_app_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'frontend',
    'app.py'
)

if os.path.exists(frontend_app_path):
    try:
        spec = importlib.util.spec_from_file_location("frontend_app", frontend_app_path)
        frontend_app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(frontend_app)
        
        # Import all evaluation functions from frontend/app.py
        judge_single = frontend_app.judge_single
        evaluate_comprehensive = frontend_app.evaluate_comprehensive
        evaluate_code_comprehensive = frontend_app.evaluate_code_comprehensive
        evaluate_router_decision = frontend_app.evaluate_router_decision
        # evaluate_skill now uses the new service layer (imported above)
        # evaluate_skill = frontend_app.evaluate_skill  # Replaced by service
        evaluate_trajectory = frontend_app.evaluate_trajectory
        evaluate_with_custom_metric = frontend_app.evaluate_with_custom_metric
        process_batch_evaluation = frontend_app.process_batch_evaluation
        create_ab_test = frontend_app.create_ab_test
        get_ab_test = frontend_app.get_ab_test
        execute_ab_test = frontend_app.execute_ab_test
        get_ollama_client = frontend_app.get_ollama_client
        get_available_models = frontend_app.get_available_models
        _frontend_app_loaded = True
    except Exception:
        # If frontend/app.py fails to load (e.g., missing dependencies), fall through to root app.py
        _frontend_app_loaded = False
else:
    _frontend_app_loaded = False

if not _frontend_app_loaded:
    # Fallback: try importing from root app.py (for backward compatibility during migration)
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    try:
        from app import (
            judge_single,
            evaluate_comprehensive,
            evaluate_code_comprehensive,
            evaluate_router_decision,
            # evaluate_skill now uses the new service layer (imported above)
            evaluate_trajectory,
            evaluate_with_custom_metric,
            process_batch_evaluation,
            create_ab_test,
            get_ab_test,
            execute_ab_test,
            get_ollama_client,
            get_available_models,
        )
    except ImportError:
        # If neither is available, these will fail at runtime
        pass

__all__ = [
    'generate_response',  # From core.services.llm_service
    'judge_pairwise',  # From core.services.judgment_service
    'save_judgment',  # From core.services.judgment_service
    'judge_single',
    'evaluate_comprehensive',
    'evaluate_code_comprehensive',
    'evaluate_router_decision',
    'evaluate_skill',
    'evaluate_trajectory',
    'evaluate_with_custom_metric',
    'process_batch_evaluation',
    'create_ab_test',
    'get_ab_test',
    'execute_ab_test',
    'get_ollama_client',
    'get_available_models',
]

