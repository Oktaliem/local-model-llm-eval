"""Unit tests for EvaluationService"""
import pytest
from core.services.evaluation_service import EvaluationService
from core.domain.models import EvaluationRequest, EvaluationResult
from unittest.mock import Mock, patch, MagicMock


class TestEvaluationService:
    """Test cases for EvaluationService"""
    
    def test_evaluate_success(self):
        """Test successful evaluation"""
        # Arrange
        mock_strategy = Mock()
        mock_strategy.evaluate.return_value = EvaluationResult(
            success=True,
            evaluation_type="pairwise",
            judgment="Test judgment",
            evaluation_id="test-id"
        )
        mock_factory = Mock()
        mock_factory.get.return_value = mock_strategy
        evaluation_service = EvaluationService(strategy_factory=mock_factory)
        
        # Act
        result = evaluation_service.evaluate(
            evaluation_type="pairwise",
            question="Test question",
            judge_model="llama3",
            response_a="Response A",
            response_b="Response B"
        )
        
        # Assert
        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["judgment"] == "Test judgment"
        mock_factory.get.assert_called_once_with("pairwise")
        mock_strategy.evaluate.assert_called_once()
    
    def test_evaluate_with_save_to_db(self):
        """Test evaluation with save_to_db=True"""
        # Arrange
        mock_strategy = Mock()
        mock_strategy.evaluate.return_value = EvaluationResult(
            success=True,
            evaluation_type="pairwise",
            judgment="Test judgment",
            evaluation_id="test-id"
        )
        mock_factory = Mock()
        mock_factory.get.return_value = mock_strategy
        mock_repo = Mock()
        evaluation_service = EvaluationService(strategy_factory=mock_factory, judgments_repo=mock_repo)
        
        # Act
        result = evaluation_service.evaluate(
            evaluation_type="pairwise",
            question="Test question",
            judge_model="llama3",
            response_a="Response A",
            response_b="Response B",
            save_to_db=True
        )
        
        # Assert
        assert result["success"] is True
        mock_repo.save.assert_called_once()
    
    def test_evaluate_with_error(self):
        """Test evaluation with error"""
        # Arrange
        mock_strategy = Mock()
        mock_strategy.evaluate.return_value = EvaluationResult(
            success=False,
            evaluation_type="pairwise",
            error="Test error",
            evaluation_id="test-id"
        )
        mock_factory = Mock()
        mock_factory.get.return_value = mock_strategy
        evaluation_service = EvaluationService(strategy_factory=mock_factory)
        
        # Act
        result = evaluation_service.evaluate(
            evaluation_type="pairwise",
            question="Test question",
            judge_model="llama3",
            response_a="Response A",
            response_b="Response B"
        )
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "Test error"
    
    def test_save_result(self):
        """Test _save_result method"""
        # Arrange
        mock_repo = Mock()
        evaluation_service = EvaluationService(judgments_repo=mock_repo)
        result = EvaluationResult(
            success=True,
            evaluation_type="pairwise",
            judgment="Test judgment",
            score_a=8.5,
            score_b=7.5,
            evaluation_id="test-id"
        )
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            judge_model="llama3",
            evaluation_id="test-id"
        )
        
        # Act
        evaluation_service._save_result(result, request)
        
        # Assert
        mock_repo.save.assert_called_once()
        call_args = mock_repo.save.call_args
        assert call_args[1]["question"] == "Test question"
        assert call_args[1]["judgment"] == "Test judgment"
    
    def test_result_to_dict(self):
        """Test _result_to_dict method"""
        # Arrange
        evaluation_service = EvaluationService()
        result = EvaluationResult(
            success=True,
            evaluation_type="pairwise",
            judgment="Test judgment",
            winner="A",
            score_a=8.5,
            score_b=7.5,
            scores={"accuracy": 9.0},
            reasoning="Test reasoning",
            trace=[{"step": "test"}],
            execution_time=1.5,
            evaluation_id="test-id"
        )
        
        # Act
        result_dict = evaluation_service._result_to_dict(result)
        
        # Assert
        assert isinstance(result_dict, dict)
        assert result_dict["success"] is True
        assert result_dict["judgment"] == "Test judgment"
        assert result_dict["winner"] == "A"
        assert result_dict["score_a"] == 8.5
        assert result_dict["score_b"] == 7.5
        assert result_dict["scores"] == {"accuracy": 9.0}
        assert result_dict["reasoning"] == "Test reasoning"
        assert result_dict["trace"] == [{"step": "test"}]
        assert result_dict["execution_time"] == 1.5
        assert result_dict["evaluation_id"] == "test-id"
    
    def test_evaluate_verifies_uuid_generation(self):
        """Test that evaluation_id is generated as UUID string"""
        import uuid
        mock_strategy = Mock()
        # Strategy returns result with evaluation_id from request
        def mock_evaluate(request):
            return EvaluationResult(
                success=True,
                evaluation_type="pairwise",
                judgment="Test judgment",
                evaluation_id=request.evaluation_id  # Use the ID from request
            )
        mock_strategy.evaluate.side_effect = mock_evaluate
        mock_factory = Mock()
        mock_factory.get.return_value = mock_strategy
        evaluation_service = EvaluationService(strategy_factory=mock_factory)
        
        result = evaluation_service.evaluate(
            evaluation_type="pairwise",
            question="Test question",
            judge_model="llama3",
            response_a="Response A",
            response_b="Response B"
        )
        
        # Verify evaluation_id is a valid UUID (mutation: evaluation_id = None would fail)
        assert "evaluation_id" in result
        try:
            uuid.UUID(result["evaluation_id"])
        except (ValueError, TypeError):
            pytest.fail(f"evaluation_id '{result['evaluation_id']}' is not a valid UUID")
    
    def test_evaluate_verifies_options_default(self):
        """Test that options defaults to empty dict"""
        mock_strategy = Mock()
        mock_strategy.evaluate.return_value = EvaluationResult(
            success=True,
            evaluation_type="pairwise",
            judgment="Test judgment"
        )
        mock_factory = Mock()
        mock_factory.get.return_value = mock_strategy
        evaluation_service = EvaluationService(strategy_factory=mock_factory)
        
        result = evaluation_service.evaluate(
            evaluation_type="pairwise",
            question="Test question",
            judge_model="llama3",
            response_a="Response A",
            response_b="Response B"
            # options not provided
        )
        
        # Verify options was set to {} (mutation: options = None would fail)
        call_args = mock_strategy.evaluate.call_args
        request = call_args[0][0]
        assert request.options == {}
    
    def test_save_result_verifies_judgment_text_fallback(self):
        """Test that judgment_text falls back to reasoning or empty string"""
        mock_repo = Mock()
        evaluation_service = EvaluationService(judgments_repo=mock_repo)
        
        # Test with judgment
        result1 = EvaluationResult(
            success=True,
            evaluation_type="pairwise",
            judgment="Test judgment",
            evaluation_id="test-id"
        )
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            judge_model="llama3",
            evaluation_id="test-id"
        )
        evaluation_service._save_result(result1, request)
        call_args = mock_repo.save.call_args
        assert call_args[1]["judgment"] == "Test judgment"
        
        # Test with reasoning (no judgment)
        mock_repo.reset_mock()
        result2 = EvaluationResult(
            success=True,
            evaluation_type="pairwise",
            reasoning="Test reasoning",
            evaluation_id="test-id"
        )
        evaluation_service._save_result(result2, request)
        call_args = mock_repo.save.call_args
        assert call_args[1]["judgment"] == "Test reasoning"  # Falls back to reasoning
        
        # Test with neither (empty string)
        mock_repo.reset_mock()
        result3 = EvaluationResult(
            success=True,
            evaluation_type="pairwise",
            evaluation_id="test-id"
        )
        evaluation_service._save_result(result3, request)
        call_args = mock_repo.save.call_args
        assert call_args[1]["judgment"] == ""  # Falls back to empty string
    
    def test_save_result_verifies_metrics_json_conditional(self):
        """Test that metrics_json is only set when metrics exist"""
        mock_repo = Mock()
        evaluation_service = EvaluationService(judgments_repo=mock_repo)
        
        # Test with metrics
        result1 = EvaluationResult(
            success=True,
            evaluation_type="pairwise",
            score_a=8.5,
            score_b=7.5,
            evaluation_id="test-id"
        )
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            judge_model="llama3",
            evaluation_id="test-id"
        )
        evaluation_service._save_result(result1, request)
        call_args = mock_repo.save.call_args
        assert call_args[1]["metrics_json"] is not None
        import json
        metrics = json.loads(call_args[1]["metrics_json"])
        assert "score_a" in metrics
        assert "score_b" in metrics
        
        # Test without metrics
        mock_repo.reset_mock()
        result2 = EvaluationResult(
            success=True,
            evaluation_type="pairwise",
            evaluation_id="test-id"
        )
        evaluation_service._save_result(result2, request)
        call_args = mock_repo.save.call_args
        assert call_args[1]["metrics_json"] is None  # No metrics, so None
    
    def test_save_result_verifies_trace_json_conditional(self):
        """Test that trace_json is only set when trace exists"""
        mock_repo = Mock()
        evaluation_service = EvaluationService(judgments_repo=mock_repo)
        
        # Test with trace
        result1 = EvaluationResult(
            success=True,
            evaluation_type="pairwise",
            trace=[{"step": "test"}],
            evaluation_id="test-id"
        )
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            judge_model="llama3",
            evaluation_id="test-id"
        )
        evaluation_service._save_result(result1, request)
        call_args = mock_repo.save.call_args
        assert call_args[1]["trace_json"] is not None
        import json
        trace = json.loads(call_args[1]["trace_json"])
        assert trace == [{"step": "test"}]
        
        # Test without trace
        mock_repo.reset_mock()
        result2 = EvaluationResult(
            success=True,
            evaluation_type="pairwise",
            evaluation_id="test-id"
        )
        evaluation_service._save_result(result2, request)
        call_args = mock_repo.save.call_args
        assert call_args[1]["trace_json"] is None  # No trace, so None
    
    def test_save_result_verifies_response_defaults(self):
        """Test that response_a and response_b default to empty strings"""
        mock_repo = Mock()
        evaluation_service = EvaluationService(judgments_repo=mock_repo)
        result = EvaluationResult(
            success=True,
            evaluation_type="pairwise",
            evaluation_id="test-id"
        )
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            judge_model="llama3",
            response_a=None,  # None
            response_b=None,  # None
            evaluation_id="test-id"
        )
        evaluation_service._save_result(result, request)
        call_args = mock_repo.save.call_args
        # Verify defaults to empty string (mutation: response_a or "" -> response_a would fail)
        assert call_args[1]["response_a"] == ""
        assert call_args[1]["response_b"] == ""
    
    def test_save_result_verifies_model_defaults(self):
        """Test that model_a and model_b default to empty strings"""
        mock_repo = Mock()
        evaluation_service = EvaluationService(judgments_repo=mock_repo)
        result = EvaluationResult(
            success=True,
            evaluation_type="pairwise",
            evaluation_id="test-id"
        )
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            judge_model="llama3",
            options={},  # Empty options
            evaluation_id="test-id"
        )
        evaluation_service._save_result(result, request)
        call_args = mock_repo.save.call_args
        # Verify defaults to empty string (mutation: options.get("model_a", None) would fail)
        assert call_args[1]["model_a"] == ""
        assert call_args[1]["model_b"] == ""
    
    def test_save_result_verifies_evaluation_id_fallback(self):
        """Test that evaluation_id falls back to request.evaluation_id"""
        mock_repo = Mock()
        evaluation_service = EvaluationService(judgments_repo=mock_repo)
        result = EvaluationResult(
            success=True,
            evaluation_type="pairwise"
            # No evaluation_id
        )
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            judge_model="llama3",
            evaluation_id="request-id"
        )
        evaluation_service._save_result(result, request)
        call_args = mock_repo.save.call_args
        # Verify falls back to request.evaluation_id (mutation: result.evaluation_id or None would fail)
        assert call_args[1]["evaluation_id"] == "request-id"
    
    def test_save_result_handles_exception(self):
        """Test that exceptions in _save_result are caught"""
        mock_repo = Mock()
        mock_repo.save.side_effect = Exception("Database error")
        evaluation_service = EvaluationService(judgments_repo=mock_repo)
        result = EvaluationResult(
            success=True,
            evaluation_type="pairwise",
            evaluation_id="test-id"
        )
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            judge_model="llama3",
            evaluation_id="test-id"
        )
        # Should not raise exception (mutation: except Exception -> pass would fail)
        evaluation_service._save_result(result, request)
        # Exception was caught and handled