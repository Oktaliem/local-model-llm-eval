"""
Unit tests for backend.services.custom_metric_service imports
Tests that the service correctly uses OllamaAdapter instead of get_ollama_client
"""
import pytest
from unittest.mock import patch, MagicMock
from backend.services.custom_metric_service import evaluate_with_custom_metric


class TestCustomMetricServiceImports:
    """Test suite for custom_metric_service import updates"""
    
    @patch('backend.services.custom_metric_service.get_custom_metric')
    @patch('core.infrastructure.llm.ollama_client.OllamaAdapter')
    def test_evaluate_with_custom_metric_uses_ollama_adapter(self, mock_adapter_class, mock_get_metric):
        """Test that evaluate_with_custom_metric uses OllamaAdapter"""
        # Setup mock metric
        mock_get_metric.return_value = {
            'metric_id': 'test-metric',
            'metric_name': 'Test Metric',
            'metric_description': 'Test description',
            'metric_definition': 'Test definition',
            'scale_min': 0,
            'scale_max': 10,
            'is_active': True,
            'domain': 'general'
        }
        
        # Setup mock adapter
        mock_adapter = MagicMock()
        mock_response = {
            "message": {
                "content": "Score: 8.5\nExplanation: Good response"
            }
        }
        mock_adapter.chat.return_value = mock_response
        mock_adapter._extract_content.return_value = "Score: 8.5\nExplanation: Good response"
        mock_adapter_class.return_value = mock_adapter
        
        result = evaluate_with_custom_metric(
            metric_id='test-metric',
            question='Test question',
            response='Test response',
            judge_model='llama3'
        )
        
        # Verify OllamaAdapter was used
        mock_adapter_class.assert_called_once()
        mock_adapter.chat.assert_called_once()
        mock_adapter._extract_content.assert_called_once()
        
        # Verify result
        assert result['success'] == True
        assert 'score' in result
        assert 'explanation' in result
    
    @patch('backend.services.custom_metric_service.get_custom_metric')
    @patch('core.infrastructure.llm.ollama_client.OllamaAdapter')
    def test_evaluate_with_custom_metric_extracts_content_correctly(self, mock_adapter_class, mock_get_metric):
        """Test that content extraction uses OllamaAdapter's _extract_content method"""
        mock_get_metric.return_value = {
            'metric_id': 'test-metric',
            'metric_name': 'Test Metric',
            'metric_description': 'Test description',
            'metric_definition': 'Test definition',
            'scale_min': 0,
            'scale_max': 10,
            'is_active': True,
            'domain': 'general'
        }
        
        mock_adapter = MagicMock()
        mock_response = {"message": {"content": "Score: 7.5"}}
        mock_adapter.chat.return_value = mock_response
        mock_adapter._extract_content.return_value = "Score: 7.5"
        mock_adapter_class.return_value = mock_adapter
        
        result = evaluate_with_custom_metric(
            metric_id='test-metric',
            question='Test question',
            response='Test response',
            judge_model='llama3'
        )
        
        # Verify _extract_content was called with the response
        mock_adapter._extract_content.assert_called_once_with(mock_response)
        
        assert result['success'] == True

