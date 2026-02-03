"""Unit tests for Settings class"""
import os
import pytest
from unittest.mock import patch

from core.common.settings import Settings, settings, _get_settings


class TestSettings:
    """Test cases for Settings initialization"""
    
    def test_settings_default_values(self):
        """Test Settings with no environment variables (uses defaults)"""
        with patch.dict(os.environ, {}, clear=True):
            test_settings = Settings()
            
            assert test_settings.ollama_host == "http://localhost:11434"
            assert test_settings.db_name == "llm_judge.db"
            assert test_settings.db_path == "data/llm_judge.db"
    
    def test_settings_from_environment(self):
        """Test Settings with environment variables"""
        with patch.dict(os.environ, {
            "OLLAMA_HOST": "http://custom:11434",
            "DB_NAME": "custom.db",
            "DB_PATH": "/custom/path.db"
        }, clear=True):
            test_settings = Settings()
            
            assert test_settings.ollama_host == "http://custom:11434"
            assert test_settings.db_name == "custom.db"
            assert test_settings.db_path == "/custom/path.db"
    
    def test_settings_partial_environment(self):
        """Test Settings with some environment variables set"""
        with patch.dict(os.environ, {
            "OLLAMA_HOST": "http://partial:11434"
        }, clear=True):
            test_settings = Settings()
            
            assert test_settings.ollama_host == "http://partial:11434"
            assert test_settings.db_name == "llm_judge.db"  # Default
            assert test_settings.db_path == "data/llm_judge.db"  # Default
    
    def test_settings_ollama_host_default(self):
        """Test that OLLAMA_HOST defaults to http://localhost:11434"""
        with patch.dict(os.environ, {}, clear=True):
            test_settings = Settings()
            
            assert test_settings.ollama_host == "http://localhost:11434"
            assert isinstance(test_settings.ollama_host, str)
    
    def test_settings_db_name_default(self):
        """Test that DB_NAME defaults to llm_judge.db"""
        with patch.dict(os.environ, {}, clear=True):
            test_settings = Settings()
            
            assert test_settings.db_name == "llm_judge.db"
            assert isinstance(test_settings.db_name, str)
    
    def test_settings_db_path_default(self):
        """Test that DB_PATH defaults to data/llm_judge.db"""
        with patch.dict(os.environ, {}, clear=True):
            test_settings = Settings()
            
            assert test_settings.db_path == "data/llm_judge.db"
            assert isinstance(test_settings.db_path, str)
    
    def test_settings_all_attributes_set(self):
        """Test that all settings attributes are set during initialization"""
        with patch.dict(os.environ, {}, clear=True):
            test_settings = Settings()
            
            assert hasattr(test_settings, 'ollama_host')
            assert hasattr(test_settings, 'db_name')
            assert hasattr(test_settings, 'db_path')
            assert isinstance(test_settings.ollama_host, str)
            assert isinstance(test_settings.db_name, str)
            assert isinstance(test_settings.db_path, str)
    
    def test_settings_environment_override_ollama_host(self):
        """Test that OLLAMA_HOST environment variable overrides default"""
        with patch.dict(os.environ, {"OLLAMA_HOST": "http://override:11434"}, clear=True):
            test_settings = Settings()
            
            assert test_settings.ollama_host == "http://override:11434"
            assert test_settings.ollama_host != "http://localhost:11434"
    
    def test_settings_environment_override_db_name(self):
        """Test that DB_NAME environment variable overrides default"""
        with patch.dict(os.environ, {"DB_NAME": "override.db"}, clear=True):
            test_settings = Settings()
            
            assert test_settings.db_name == "override.db"
            assert test_settings.db_name != "llm_judge.db"
    
    def test_settings_environment_override_db_path(self):
        """Test that DB_PATH environment variable overrides default"""
        with patch.dict(os.environ, {"DB_PATH": "/override/path.db"}, clear=True):
            test_settings = Settings()
            
            assert test_settings.db_path == "/override/path.db"
            assert test_settings.db_path != "data/llm_judge.db"


class TestGetSettingsFunction:
    """Test cases for _get_settings function"""
    
    def test_get_settings_creates_instance(self):
        """Test that _get_settings creates a Settings instance when None"""
        from core.common import settings as settings_module
        
        # Store original
        original_instance = settings_module._settings_instance
        
        try:
            # Set to None to force creation
            settings_module._settings_instance = None
            
            # Call _get_settings
            result = settings_module._get_settings()
            
            # Verify instance was created
            assert result is not None
            assert settings_module._settings_instance is not None
            assert hasattr(result, 'ollama_host')
            assert hasattr(result, 'db_name')
            assert hasattr(result, 'db_path')
        finally:
            # Restore original
            settings_module._settings_instance = original_instance
    
    def test_get_settings_returns_cached_instance(self):
        """Test that _get_settings returns cached instance on subsequent calls"""
        from core.common import settings as settings_module
        
        # Store original
        original_instance = settings_module._settings_instance
        
        try:
            # Set to None to force creation
            settings_module._settings_instance = None
            
            # Call twice
            result1 = settings_module._get_settings()
            result2 = settings_module._get_settings()
            
            # Should be same instance
            assert result1 is result2
        finally:
            # Restore original
            settings_module._settings_instance = original_instance


class TestModuleLevelSettings:
    """Test cases for module-level settings object"""
    
    def test_module_settings_exists(self):
        """Test that module-level settings object exists"""
        assert settings is not None
    
    def test_module_settings_has_ollama_host(self):
        """Test that settings has ollama_host attribute"""
        assert hasattr(settings, 'ollama_host')
        assert isinstance(settings.ollama_host, str)
        assert len(settings.ollama_host) > 0
    
    def test_module_settings_has_db_name(self):
        """Test that settings has db_name attribute"""
        assert hasattr(settings, 'db_name')
        assert isinstance(settings.db_name, str)
        assert len(settings.db_name) > 0
    
    def test_module_settings_has_db_path(self):
        """Test that settings has db_path attribute"""
        assert hasattr(settings, 'db_path')
        assert isinstance(settings.db_path, str)
        assert len(settings.db_path) > 0
