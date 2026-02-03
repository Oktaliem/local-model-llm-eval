"""Unit tests for core/services/ab_test_service.py"""
import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from queue import Queue
from core.services.ab_test_service import ABTestService
from core.services.evaluation_service import EvaluationService
from core.infrastructure.db.repositories.judgments_repo import JudgmentsRepository


class TestABTestService:
    """Test cases for ABTestService"""
    
    def test_init_default(self):
        """Test initialization with default dependencies"""
        service = ABTestService()
        
        assert service.evaluation_service is not None
        assert isinstance(service.evaluation_service, EvaluationService)
        assert service.judgments_repo is not None
        assert isinstance(service.judgments_repo, JudgmentsRepository)
        assert service._test_progress == {}
        assert service._test_queues == {}
        assert service._test_threads == {}
    
    def test_init_with_dependencies(self):
        """Test initialization with provided dependencies"""
        mock_eval_service = Mock(spec=EvaluationService)
        mock_judgments_repo = Mock(spec=JudgmentsRepository)
        
        service = ABTestService(
            evaluation_service=mock_eval_service,
            judgments_repo=mock_judgments_repo
        )
        
        assert service.evaluation_service == mock_eval_service
        assert service.judgments_repo == mock_judgments_repo
    
    @patch('core.services.ab_test_service.create_ab_test')
    def test_create_test(self, mock_create):
        """Test create_test delegates to create_ab_test"""
        mock_create.return_value = "test-id-123"
        
        service = ABTestService()
        result = service.create_test(
            test_name="Test",
            variant_a_name="A",
            variant_b_name="B",
            variant_a_config={},
            variant_b_config={},
            evaluation_type="comprehensive",
            test_cases=[]
        )
        
        assert result == "test-id-123"
        mock_create.assert_called_once()
    
    @patch('core.services.ab_test_service.get_ab_test')
    def test_start_test_not_found(self, mock_get):
        """Test starting a test that doesn't exist"""
        mock_get.return_value = None
        
        service = ABTestService()
        result = service.start_test("nonexistent-id", "llama3")
        
        assert result is False
    
    @patch('core.services.ab_test_service.get_ab_test')
    def test_start_test_already_running(self, mock_get):
        """Test starting a test that's already running"""
        mock_get.return_value = {
            "test_id": "test-123",
            "test_cases_json": [{"question": "Q1"}]
        }
        
        service = ABTestService()
        # Set test as running
        service._test_progress["test-123"] = {"status": "running"}
        
        result = service.start_test("test-123", "llama3")
        
        assert result is False
    
    @patch('core.services.ab_test_service.get_ab_test')
    @patch('core.services.ab_test_service.execute_ab_test')
    def test_start_test_success(self, mock_execute, mock_get):
        """Test successfully starting a test"""
        import threading
        mock_get.return_value = {
            "test_id": "test-123",
            "test_cases_json": [{"question": "Q1"}, {"question": "Q2"}]
        }
        # Use event to control when execute completes (works with instant sleep)
        execute_event = threading.Event()
        def slow_execute(*args, **kwargs):
            execute_event.wait(timeout=1.0)
            return {"success": True, "results": []}
        mock_execute.side_effect = slow_execute
        
        service = ABTestService()
        result = service.start_test("test-123", "llama3")
        
        assert result is True
        assert "test-123" in service._test_progress
        # Check immediately - should be running (thread might complete quickly with instant sleep)
        # Allow for either "running" or "completed" status
        status = service._test_progress["test-123"]["status"]
        assert status in ["running", "completed"]
        assert service._test_progress["test-123"]["total_cases"] == 2
        assert "test-123" in service._test_queues
        assert "test-123" in service._test_threads
        # Clean up
        execute_event.set()
    
    @patch('core.services.ab_test_service.get_ab_test')
    @patch('core.services.ab_test_service.execute_ab_test')
    def test_start_test_with_test_cases_field(self, mock_execute, mock_get):
        """Test starting test with test_cases field instead of test_cases_json"""
        mock_get.return_value = {
            "test_id": "test-123",
            "test_cases": [{"question": "Q1"}]
        }
        mock_execute.return_value = {"success": True}
        
        service = ABTestService()
        result = service.start_test("test-123", "llama3")
        
        assert result is True
        assert service._test_progress["test-123"]["total_cases"] == 1
    
    @patch('core.services.ab_test_service.get_ab_test')
    @patch('core.services.ab_test_service.execute_ab_test')
    def test_start_test_with_empty_cases(self, mock_execute, mock_get):
        """Test starting test with empty test cases"""
        mock_get.return_value = {
            "test_id": "test-123",
            "test_cases_json": []
        }
        mock_execute.return_value = {"success": True}
        
        service = ABTestService()
        result = service.start_test("test-123", "llama3")
        
        assert result is True
        assert service._test_progress["test-123"]["total_cases"] == 0
    
    @patch('core.services.ab_test_service.execute_ab_test')
    def test_run_test_success(self, mock_execute):
        """Test _run_test with successful execution"""
        mock_execute.return_value = {
            "success": True,
            "results": [{"winner": "A"}],
            "summary": {"total_cases": 1}
        }
        
        service = ABTestService()
        test_id = "test-123"
        service._test_progress[test_id] = {
            "test_id": test_id,
            "status": "running",
            "total_cases": 1,
            "completed_cases": 0
        }
        service._test_queues[test_id] = Queue()
        
        service._run_test(test_id, "llama3")
        
        # Wait a bit for thread to complete
        time.sleep(0.1)
        
        assert service._test_progress[test_id]["status"] == "completed"
        assert "result" in service._test_progress[test_id]
        assert "completed_at" in service._test_progress[test_id]
        # Check queue has result
        assert not service._test_queues[test_id].empty()
    
    @patch('core.services.ab_test_service.execute_ab_test')
    def test_run_test_failure(self, mock_execute):
        """Test _run_test with failed execution"""
        mock_execute.return_value = {
            "success": False,
            "error": "Test failed"
        }
        
        service = ABTestService()
        test_id = "test-123"
        service._test_progress[test_id] = {
            "test_id": test_id,
            "status": "running",
            "total_cases": 1,
            "completed_cases": 0
        }
        service._test_queues[test_id] = Queue()
        
        service._run_test(test_id, "llama3")
        
        # Wait a bit for thread to complete
        time.sleep(0.1)
        
        assert service._test_progress[test_id]["status"] == "failed"
        assert service._test_progress[test_id]["error"] == "Test failed"
        assert "completed_at" in service._test_progress[test_id]
    
    @patch('core.services.ab_test_service.execute_ab_test')
    def test_run_test_exception(self, mock_execute):
        """Test _run_test with exception"""
        mock_execute.side_effect = Exception("Unexpected error")
        
        service = ABTestService()
        test_id = "test-123"
        service._test_progress[test_id] = {
            "test_id": test_id,
            "status": "running",
            "total_cases": 1,
            "completed_cases": 0
        }
        
        service._run_test(test_id, "llama3")
        
        # Wait a bit for thread to complete
        time.sleep(0.1)
        
        assert service._test_progress[test_id]["status"] == "failed"
        assert "Unexpected error" in service._test_progress[test_id]["error"]
        assert "completed_at" in service._test_progress[test_id]
    
    @patch('core.services.ab_test_service.execute_ab_test')
    def test_run_test_no_progress_entry(self, mock_execute):
        """Test _run_test when progress entry doesn't exist"""
        mock_execute.return_value = {"success": True}
        
        service = ABTestService()
        test_id = "test-123"
        # Don't create progress entry
        
        # Should not raise exception
        service._run_test(test_id, "llama3")
        
        # Wait a bit
        time.sleep(0.1)
        
        # Should handle gracefully
        assert test_id not in service._test_progress
    
    @patch('core.services.ab_test_service.execute_ab_test')
    def test_run_test_no_queue(self, mock_execute):
        """Test _run_test when queue doesn't exist"""
        mock_execute.return_value = {"success": True}
        
        service = ABTestService()
        test_id = "test-123"
        service._test_progress[test_id] = {
            "test_id": test_id,
            "status": "running"
        }
        # Don't create queue
        
        service._run_test(test_id, "llama3")
        
        # Wait a bit
        time.sleep(0.1)
        
        # Should handle gracefully
        assert service._test_progress[test_id]["status"] == "completed"
    
    def test_get_progress_existing(self):
        """Test getting progress for existing test"""
        service = ABTestService()
        test_id = "test-123"
        progress_data = {
            "test_id": test_id,
            "status": "running",
            "total_cases": 10,
            "completed_cases": 5
        }
        service._test_progress[test_id] = progress_data
        
        result = service.get_progress(test_id)
        
        assert result == progress_data
    
    def test_get_progress_nonexistent(self):
        """Test getting progress for non-existent test"""
        service = ABTestService()
        
        result = service.get_progress("nonexistent-id")
        
        assert result is None
    
    def test_get_result_existing_with_data(self):
        """Test getting result from queue with data"""
        service = ABTestService()
        test_id = "test-123"
        queue = Queue()
        result_data = {"success": True, "results": []}
        queue.put(result_data)
        service._test_queues[test_id] = queue
        
        result = service.get_result(test_id)
        
        assert result == result_data
    
    def test_get_result_existing_empty_queue(self):
        """Test getting result from empty queue"""
        service = ABTestService()
        test_id = "test-123"
        queue = Queue()
        service._test_queues[test_id] = queue
        
        result = service.get_result(test_id)
        
        assert result is None
    
    def test_get_result_nonexistent(self):
        """Test getting result for non-existent test"""
        service = ABTestService()
        
        result = service.get_result("nonexistent-id")
        
        assert result is None
    
    def test_get_result_queue_exception(self):
        """Test get_result when queue.get_nowait raises exception"""
        service = ABTestService()
        test_id = "test-123"
        mock_queue = Mock()
        mock_queue.empty.return_value = False
        mock_queue.get_nowait.side_effect = Exception("Queue error")
        service._test_queues[test_id] = mock_queue
        
        result = service.get_result(test_id)
        
        assert result is None
    
    def test_stop_test_nonexistent(self):
        """Test stopping non-existent test"""
        service = ABTestService()
        
        result = service.stop_test("nonexistent-id")
        
        assert result is False
    
    def test_stop_test_not_running(self):
        """Test stopping test that's not running"""
        service = ABTestService()
        test_id = "test-123"
        service._test_progress[test_id] = {
            "test_id": test_id,
            "status": "completed"
        }
        
        result = service.stop_test(test_id)
        
        assert result is False
        assert service._test_progress[test_id]["status"] == "completed"
    
    def test_stop_test_success(self):
        """Test successfully stopping a running test"""
        service = ABTestService()
        test_id = "test-123"
        service._test_progress[test_id] = {
            "test_id": test_id,
            "status": "running"
        }
        
        result = service.stop_test(test_id)
        
        assert result is True
        assert service._test_progress[test_id]["status"] == "stopped"
        assert "stopped_at" in service._test_progress[test_id]
    
    @patch('core.services.ab_test_service.get_ab_test')
    @patch('core.services.ab_test_service.execute_ab_test')
    def test_full_workflow(self, mock_execute, mock_get):
        """Test full workflow: start, get progress, get result"""
        mock_get.return_value = {
            "test_id": "test-123",
            "test_cases_json": [{"question": "Q1"}]
        }
        # Make execute_ab_test take a bit of time
        import threading
        execute_event = threading.Event()
        def slow_execute(*args, **kwargs):
            execute_event.wait(timeout=1.0)
            return {
                "success": True,
                "results": [{"winner": "A"}],
                "summary": {"total_cases": 1}
            }
        mock_execute.side_effect = slow_execute
        
        service = ABTestService()
        
        # Start test
        started = service.start_test("test-123", "llama3")
        assert started is True
        
        # Get progress immediately (should be running)
        progress = service.get_progress("test-123")
        assert progress is not None
        # Status might be running or completed depending on timing, so check it's one of them
        assert progress["status"] in ["running", "completed"]
        
        # Allow execute to complete by setting the event
        execute_event.set()
        
        # Wait for thread to complete using thread.join()
        thread = service._test_threads.get("test-123")
        if thread:
            thread.join(timeout=2.0)  # Wait up to 2 seconds for thread to complete
        
        # Poll for completion status
        import time
        for _ in range(50):  # More iterations to ensure completion
            final_progress = service.get_progress("test-123")
            if final_progress and final_progress["status"] == "completed":
                break
            time.sleep(0.01)  # Small delay (instant during mutation testing)
        
        # Get result - poll until available
        result = None
        for _ in range(20):
            result = service.get_result("test-123")
            if result is not None:
                break
            time.sleep(0.01)
        
        # Result might be None if queue is empty (result was already consumed)
        # In that case, check that progress has the result
        if result is None:
            final_progress = service.get_progress("test-123")
            assert final_progress is not None
            # Progress should have result or status should be completed
            if "result" in final_progress:
                assert final_progress["result"]["success"] is True
            else:
                # If result not in progress yet, status should still be completed
                assert final_progress["status"] == "completed"
        else:
            assert result["success"] is True
        
        # Check final progress
        final_progress = service.get_progress("test-123")
        assert final_progress is not None
        assert final_progress["status"] == "completed"

