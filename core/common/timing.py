"""Execution time tracking utilities"""
import time
from functools import wraps


def track_execution_time(func):
    """Decorator to track execution time of a function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        if isinstance(result, dict):
            result["execution_time"] = execution_time
        return result
    return wrapper


