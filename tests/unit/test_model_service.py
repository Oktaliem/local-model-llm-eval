"""
Unit tests for backend.services.model_service
"""
import pytest
from unittest.mock import patch, MagicMock
from backend.services.model_service import get_available_models


class TestModelService:
    """Test suite for model_service functions"""
    
    @patch('backend.services.model_service.OllamaAdapter')
    def test_get_available_models_success(self, mock_adapter_class):
        """Test getting available models successfully"""
        mock_adapter = MagicMock()
        mock_adapter.list_models.return_value = ["llama3", "mistral", "gpt-oss-safeguard:20b"]
        mock_adapter_class.return_value = mock_adapter
        
        models = get_available_models()
        
        assert models == ["llama3", "mistral", "gpt-oss-safeguard:20b"]
        mock_adapter.list_models.assert_called_once()
    
    @patch('backend.services.model_service.OllamaAdapter')
    def test_get_available_models_empty(self, mock_adapter_class):
        """Test getting available models when list is empty"""
        mock_adapter = MagicMock()
        mock_adapter.list_models.return_value = []
        mock_adapter_class.return_value = mock_adapter
        
        models = get_available_models()
        
        assert models == []
    
    @patch('backend.services.model_service.OllamaAdapter')
    def test_get_available_models_exception(self, mock_adapter_class):
        """Test getting available models when exception occurs"""
        mock_adapter = MagicMock()
        mock_adapter.list_models.side_effect = Exception("Connection error")
        mock_adapter_class.return_value = mock_adapter
        
        models = get_available_models()
        
        assert models == []
    
    @patch('backend.services.model_service.OllamaAdapter')
    def test_get_available_models_adapter_init_exception(self, mock_adapter_class):
        """Test getting available models when adapter initialization fails"""
        mock_adapter_class.side_effect = Exception("Init error")
        
        models = get_available_models()
        
        assert models == []

