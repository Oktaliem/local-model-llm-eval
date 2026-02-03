"""Additional unit tests for EvaluationService to reach 100% coverage"""
import pytest
from unittest.mock import Mock, patch
from core.services.evaluation_service import EvaluationService
from core.domain.models import EvaluationRequest, EvaluationResult
from core.infrastructure.db.repositories.judgments_repo import JudgmentsRepository


class TestEvaluationServiceComplete:
    """Additional test cases for EvaluationService"""
    
    def test_save_result_with_trace(self):
        """Test _save_result with trace data"""
        mock_repo = Mock()
        evaluation_service = EvaluationService(judgments_repo=mock_repo)
        result = EvaluationResult(
            success=True,
            evaluation_type="pairwise",
            judgment="Test judgment",
            trace=[{"step": "test", "data": "value"}],
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
        evaluation_service._save_result(result, request)
        mock_repo.save.assert_called_once()
        call_args = mock_repo.save.call_args[1]
        assert call_args["trace_json"] is not None
        import json
        assert json.loads(call_args["trace_json"]) == [{"step": "test", "data": "value"}]
    
    def test_save_result_with_exception(self):
        """Test _save_result when save fails"""
        mock_repo = Mock()
        mock_repo.save.side_effect = Exception("Database error")
        evaluation_service = EvaluationService(judgments_repo=mock_repo)
        result = EvaluationResult(
            success=True,
            evaluation_type="pairwise",
            judgment="Test judgment",
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
        # Should not raise exception, just print warning
        evaluation_service._save_result(result, request)
        mock_repo.save.assert_called_once()


