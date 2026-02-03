"""Unit tests for strategy error paths to reach 100% coverage"""
import pytest
import sys
from unittest.mock import patch
from core.domain.strategies.code_eval import CodeEvalStrategy
from core.domain.strategies.custom_metric_eval import CustomMetricStrategy
from core.domain.strategies.comprehensive import ComprehensiveStrategy
from core.domain.models import EvaluationRequest

# Create mock app module if it doesn't exist
if 'app' not in sys.modules:
    from unittest.mock import MagicMock
    mock_app = MagicMock()
    sys.modules['app'] = mock_app


class TestCodeEvalStrategyErrors:
    """Test error paths for CodeEvalStrategy"""
    
    def test_evaluate_missing_code(self):
        """Test code evaluation with missing code"""
        strategy = CodeEvalStrategy()
        request = EvaluationRequest(
            evaluation_type="code",
            question="Test",
            response=None,
            response_a=None,
            judge_model="llama3",
            options={}
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert "code is required" in result.error
    
    @patch('backend.services.evaluation_functions.evaluate_code_comprehensive')
    def test_evaluate_with_error(self, mock_evaluate):
        """Test code evaluation with error from app function"""
        mock_evaluate.return_value = {
            "success": False,
            "error": "Code evaluation failed"
        }
        strategy = CodeEvalStrategy()
        request = EvaluationRequest(
            evaluation_type="code",
            question="Test",
            response="print('hello')",
            judge_model="llama3"
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert result.error == "Code evaluation failed"


class TestCustomMetricStrategyErrors:
    """Test error paths for CustomMetricStrategy"""
    
    def test_evaluate_missing_metric_id(self):
        """Test custom metric evaluation with missing metric_id"""
        strategy = CustomMetricStrategy()
        request = EvaluationRequest(
            evaluation_type="custom_metric",
            question="Test",
            response="Test response",
            judge_model="llama3",
            options={}
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert "metric_id is required" in result.error
    
    def test_evaluate_missing_response(self):
        """Test custom metric evaluation with missing response"""
        strategy = CustomMetricStrategy()
        request = EvaluationRequest(
            evaluation_type="custom_metric",
            question="Test",
            response=None,
            response_a=None,
            judge_model="llama3",
            options={"metric_id": "test_metric"}
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert "response is required" in result.error
    
    @patch('backend.services.evaluation_functions.evaluate_with_custom_metric')
    def test_evaluate_with_error(self, mock_evaluate):
        """Test custom metric evaluation with error from app function"""
        mock_evaluate.return_value = {
            "success": False,
            "error": "Custom metric evaluation failed"
        }
        strategy = CustomMetricStrategy()
        request = EvaluationRequest(
            evaluation_type="custom_metric",
            question="Test",
            response="Test response",
            judge_model="llama3",
            options={"metric_id": "test_metric"}
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert result.error == "Custom metric evaluation failed"


class TestComprehensiveStrategyErrors:
    """Test error paths for ComprehensiveStrategy"""
    
    @patch('backend.services.evaluation_functions.evaluate_comprehensive')
    def test_evaluate_with_error(self, mock_evaluate):
        """Test comprehensive evaluation with error from app function"""
        mock_evaluate.return_value = {
            "success": False,
            "error": "Comprehensive evaluation failed"
        }
        strategy = ComprehensiveStrategy()
        request = EvaluationRequest(
            evaluation_type="comprehensive",
            question="Test",
            response="Test response",
            judge_model="llama3"
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert result.error == "Comprehensive evaluation failed"


