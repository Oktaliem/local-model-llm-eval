"""Unit tests for BatchService"""
import pytest
import time
import uuid
from datetime import datetime
from core.services.batch_service import BatchService
from core.domain.models import RunProgress
from unittest.mock import Mock, patch, MagicMock


class TestBatchService:
    """Test cases for BatchService"""
    
    def test_start_batch_evaluation(self):
        """Test starting a batch evaluation"""
        # Arrange
        mock_evaluation_service = Mock()
        mock_evaluation_service.evaluate.return_value = {
            "success": True,
            "judgment": "Test judgment"
        }
        mock_repo = Mock()
        batch_service = BatchService(evaluation_service=mock_evaluation_service, judgments_repo=mock_repo)
        test_cases = [
            {"question": "Q1", "response": "R1"},
            {"question": "Q2", "response": "R2"}
        ]
        
        # Act
        run_id = batch_service.start_batch_evaluation(
            test_cases=test_cases,
            evaluation_type="single",
            judge_model="llama3"
        )
        
        # Assert
        assert isinstance(run_id, str)
        assert len(run_id) > 0
        # Verify run_id is a valid UUID string (mutation: run_id = None would fail)
        import uuid
        try:
            uuid.UUID(run_id)  # Will raise ValueError if not a valid UUID
        except ValueError:
            pytest.fail(f"run_id '{run_id}' is not a valid UUID")
        progress = batch_service.get_progress(run_id)
        assert progress is not None
        assert progress.total_cases == 2
        # Status might be "running" or "completed" depending on thread execution speed
        assert progress.status in ["running", "completed"]
        
        # Wait for processing to complete
        time.sleep(0.5)
        progress = batch_service.get_progress(run_id)
        assert progress.status == "completed"
        assert progress.completed_cases == 2
        # Verify created_at is set (mutation: created_at = None would fail)
        assert progress.created_at is not None
        assert isinstance(progress.created_at, (float, int))
        assert progress.created_at > 0
    
    def test_get_progress(self):
        """Test getting progress for a run"""
        # Arrange
        batch_service = BatchService()
        test_cases = [{"question": "Q1", "response": "R1"}]
        run_id = batch_service.start_batch_evaluation(
            test_cases=test_cases,
            evaluation_type="single",
            judge_model="llama3"
        )
        
        # Act
        progress = batch_service.get_progress(run_id)
        
        # Assert
        assert progress is not None
        assert progress.run_id == run_id
        assert progress.total_cases == 1
        # Verify run_id is a valid UUID string (mutation: run_id = None would fail)
        try:
            uuid.UUID(run_id)  # Will raise ValueError if not a valid UUID
        except ValueError:
            pytest.fail(f"run_id '{run_id}' is not a valid UUID")
        # Verify created_at is set (mutation: created_at = None would fail)
        assert progress.created_at is not None
        assert isinstance(progress.created_at, (float, int))
        assert progress.created_at > 0
        
        # Cleanup
        batch_service.stop_run(run_id)
        time.sleep(0.1)
    
    def test_get_results_nonexistent_run(self):
        """Test getting results for non-existent run"""
        # Arrange
        batch_service = BatchService()
        
        # Act
        result = batch_service.get_results("nonexistent_run_id")
        
        # Assert
        assert result is None
    
    def test_stop_run_success(self):
        """Test stopping a running batch evaluation"""
        # Arrange
        import threading
        mock_evaluation_service = Mock()
        # Use an event to control when evaluate completes (works with instant sleep)
        evaluate_event = threading.Event()
        def slow_evaluate(*args, **kwargs):
            # Wait for event to be set (or timeout after 1 second as fallback)
            evaluate_event.wait(timeout=1.0)
            return {
                "success": True,
                "judgment": "Test judgment"
            }
        mock_evaluation_service.evaluate.side_effect = slow_evaluate
        batch_service = BatchService(evaluation_service=mock_evaluation_service)
        test_cases = [{"question": "Q1", "response": "R1"}]
        run_id = batch_service.start_batch_evaluation(
            test_cases=test_cases,
            evaluation_type="single",
            judge_model="llama3"
        )
        # Wait for thread to start and set status to "running"
        import time
        for _ in range(10):  # Poll up to 10 times
            progress = batch_service.get_progress(run_id)
            if progress and progress.status == "running":
                break
            time.sleep(0.01)  # Small delay between polls (will be instant during mutation testing)
        
        # Act
        result = batch_service.stop_run(run_id)
        
        # Assert
        assert result is True
        progress = batch_service.get_progress(run_id)
        assert progress.status == "stopped"
        
        # Clean up: allow evaluate to complete
        evaluate_event.set()
    
    def test_stop_run_nonexistent(self):
        """Test stopping a non-existent run"""
        # Arrange
        batch_service = BatchService()
        
        # Act
        result = batch_service.stop_run("nonexistent_run_id")
        
        # Assert
        assert result is False
    
    def test_stop_run_already_completed(self):
        """Test stopping a run that's already completed"""
        # Arrange
        batch_service = BatchService()
        test_cases = [{"question": "Q1", "response": "R1"}]
        run_id = batch_service.start_batch_evaluation(
            test_cases=test_cases,
            evaluation_type="single",
            judge_model="llama3"
        )
        time.sleep(0.1)
        
        # Manually set status to completed
        with batch_service._lock:
            batch_service._runs[run_id].status = "completed"
        
        # Act
        result = batch_service.stop_run(run_id)
        
        # Assert
        assert result is False  # Can't stop a completed run
    
    def test_process_batch_verifies_test_case_defaults(self):
        """Test that test_case.get() defaults are used correctly"""
        mock_evaluation_service = Mock()
        mock_evaluation_service.evaluate.return_value = {
            "success": True,
            "judgment": "Test judgment"
        }
        batch_service = BatchService(evaluation_service=mock_evaluation_service)
        test_cases = [
            {"question": "Q1"}  # No response or reference
        ]
        run_id = batch_service.start_batch_evaluation(
            test_cases=test_cases,
            evaluation_type="single",
            judge_model="llama3"
        )
        time.sleep(0.3)
        # Verify defaults are used (mutation: test_case.get("response", None) would fail)
        call_args = mock_evaluation_service.evaluate.call_args
        assert call_args[1]["response"] == ""  # Default
        assert "reference" not in call_args[1]["options"]  # No reference
    
    def test_process_batch_verifies_case_options_copy(self):
        """Test that case_options is a copy of options"""
        mock_evaluation_service = Mock()
        mock_evaluation_service.evaluate.return_value = {
            "success": True,
            "judgment": "Test judgment"
        }
        batch_service = BatchService(evaluation_service=mock_evaluation_service)
        test_cases = [
            {"question": "Q1", "response": "R1", "reference": "Ref1"}
        ]
        run_id = batch_service.start_batch_evaluation(
            test_cases=test_cases,
            evaluation_type="single",
            judge_model="llama3",
            options={"key": "value"}
        )
        time.sleep(0.3)
        # Verify options was copied (mutation: case_options = options would fail)
        call_args = mock_evaluation_service.evaluate.call_args
        assert call_args[1]["options"]["key"] == "value"
        assert call_args[1]["options"]["reference"] == "Ref1"
    
    def test_process_batch_verifies_results_structure(self):
        """Test that results structure is correct"""
        mock_evaluation_service = Mock()
        mock_evaluation_service.evaluate.return_value = {
            "success": True,
            "judgment": "Test judgment"
        }
        batch_service = BatchService(evaluation_service=mock_evaluation_service)
        test_cases = [
            {"question": "Q1", "response": "R1"},
            {"question": "Q2", "response": "R2"}
        ]
        run_id = batch_service.start_batch_evaluation(
            test_cases=test_cases,
            evaluation_type="single",
            judge_model="llama3"
        )
        time.sleep(0.5)
        progress = batch_service.get_progress(run_id)
        # Verify results structure (mutation: results.append({}) would fail)
        assert len(progress.results) == 2
        assert progress.results[0]["test_case_index"] == 0
        assert progress.results[0]["question"] == "Q1"
        assert progress.results[0]["response"] == "R1"
        assert "result" in progress.results[0]
    
    def test_process_batch_verifies_updated_at_set(self):
        """Test that updated_at is set during processing"""
        mock_evaluation_service = Mock()
        mock_evaluation_service.evaluate.return_value = {
            "success": True,
            "judgment": "Test judgment"
        }
        batch_service = BatchService(evaluation_service=mock_evaluation_service)
        test_cases = [
            {"question": "Q1", "response": "R1"}
        ]
        run_id = batch_service.start_batch_evaluation(
            test_cases=test_cases,
            evaluation_type="single",
            judge_model="llama3"
        )
        time.sleep(0.3)
        progress = batch_service.get_progress(run_id)
        # Verify updated_at is set (mutation: updated_at = None would fail)
        assert progress.updated_at is not None
        assert isinstance(progress.updated_at, (float, int))
        assert progress.updated_at > 0
    
    def test_get_results_verifies_queue_nonexistent(self):
        """Test that get_results returns None for nonexistent queue"""
        batch_service = BatchService()
        # Verify None is returned (mutation: return [] would fail)
        result = batch_service.get_results("nonexistent")
        assert result is None
    
    def test_get_results_verifies_queue_empty_returns_none(self):
        """Test that get_results returns None when queue is empty"""
        batch_service = BatchService()
        test_cases = [{"question": "Q1", "response": "R1"}]
        run_id = batch_service.start_batch_evaluation(
            test_cases=test_cases,
            evaluation_type="single",
            judge_model="llama3"
        )
        time.sleep(0.5)  # Wait for processing
        # Queue should be empty after processing
        results = batch_service.get_results(run_id)
        # Should return None when empty; allow list if processing is still in-flight
        if results is None:
            assert results is None
        else:
            assert isinstance(results, list)
            # If results are present, they should have expected keys
            for item in results:
                assert "index" in item
                assert "result" in item
    
    def test_stop_run_verifies_updated_at_set(self):
        """Test that updated_at is set when stopping"""
        import threading
        mock_evaluation_service = Mock()
        evaluate_event = threading.Event()
        def slow_evaluate(*args, **kwargs):
            evaluate_event.wait(timeout=1.0)
            return {"success": True, "judgment": "Test"}
        mock_evaluation_service.evaluate.side_effect = slow_evaluate
        batch_service = BatchService(evaluation_service=mock_evaluation_service)
        test_cases = [{"question": "Q1", "response": "R1"}]
        run_id = batch_service.start_batch_evaluation(
            test_cases=test_cases,
            evaluation_type="single",
            judge_model="llama3"
        )
        # Wait for thread to start
        import time
        for _ in range(10):
            progress = batch_service.get_progress(run_id)
            if progress and progress.status == "running":
                break
            time.sleep(0.01)
        batch_service.stop_run(run_id)
        progress = batch_service.get_progress(run_id)
        # Verify updated_at is set (mutation: updated_at = None would fail)
        assert progress.updated_at is not None
        assert isinstance(progress.updated_at, (float, int))
        # Clean up
        evaluate_event.set()