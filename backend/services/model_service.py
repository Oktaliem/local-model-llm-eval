"""
Model service for managing Ollama models.
Extracted from app.py to separate backend concerns.
"""
from core.infrastructure.llm.ollama_client import OllamaAdapter


def get_available_models():
    """Get list of available Ollama models."""
    try:
        adapter = OllamaAdapter()
        return adapter.list_models()
    except Exception as e:
        # Don't show error, just return empty list
        # The caller will handle showing appropriate message
        return []

