"""Application settings (lightweight env-based)"""
import os


class Settings:
    """Simple settings loader using environment variables"""

    def __init__(self):
        """Initialize settings from environment variables with defaults."""
        self.ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.db_name: str = os.getenv("DB_NAME", "llm_judge.db")
        self.db_path: str = os.getenv("DB_PATH", "data/llm_judge.db")


# Lazy initialization for settings instance
_settings_instance = None


def _get_settings():
    """Get or create the settings instance (lazy initialization)"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance


# Module-level settings instance for backward compatibility
settings = Settings()
