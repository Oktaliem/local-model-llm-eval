"""Targeted tests to kill surviving Settings mutants."""
import os
from unittest.mock import patch

from core.common.settings import Settings


def test_settings_defaults_are_applied_when_env_missing():
    """Ensure defaults are used when environment variables are absent."""
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings()
    assert settings.ollama_host == "http://localhost:11434"
    assert settings.db_name == "llm_judge.db"
    assert settings.db_path == "data/llm_judge.db"


def test_get_settings_uses_cached_instance_when_present(monkeypatch):
    """Verify _get_settings returns cached instance even if env changes."""
    from core.common import settings as settings_module

    original_instance = settings_module._settings_instance
    try:
        monkeypatch.setenv("OLLAMA_HOST", "http://first:11434")
        cached = Settings()
        settings_module._settings_instance = cached

        # Change env; cached instance should still be returned unchanged.
        monkeypatch.setenv("OLLAMA_HOST", "http://second:11434")
        result = settings_module._get_settings()

        assert result is cached
        assert result.ollama_host == "http://first:11434"
    finally:
        settings_module._settings_instance = original_instance
