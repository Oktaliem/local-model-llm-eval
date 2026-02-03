"""Unit tests for A/B test service"""
import pytest
import json
import sqlite3
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from backend.services.ab_test_service import (
    create_ab_test,
    get_ab_test,
    get_all_ab_tests,
    update_ab_test_progress,
    save_ab_test_results,
    execute_ab_test
)


class TestABTestService:
    """Test cases for A/B test service functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        """Set up test database for each test"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        # Create schema
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS ab_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id TEXT UNIQUE,
                test_name TEXT,
                test_description TEXT,
                variant_a_name TEXT,
                variant_b_name TEXT,
                variant_a_config TEXT,
                variant_b_config TEXT,
                evaluation_type TEXT,
                test_cases_json TEXT,
                total_cases INTEGER,
                completed_cases INTEGER DEFAULT 0,
                variant_a_wins INTEGER DEFAULT 0,
                variant_b_wins INTEGER DEFAULT 0,
                ties INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                results_json TEXT,
                statistical_analysis_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        
        monkeypatch.setenv("DB_PATH", db_path)
        # Reload module to pick up new DB_PATH
        import importlib
        import backend.services.ab_test_service
        importlib.reload(backend.services.ab_test_service)
        
        self.test_db = db_path
        yield
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_create_ab_test(self):
        """Test creating an A/B test"""
        test_id = create_ab_test(
            test_name="Test AB Test",
            variant_a_name="Variant A",
            variant_b_name="Variant B",
            variant_a_config={"model": "model-a"},
            variant_b_config={"model": "model-b"},
            evaluation_type="comprehensive",
            test_cases=[{"question": "Test question"}]
        )
        
        assert test_id is not None
        assert isinstance(test_id, str)
        assert len(test_id) > 0
    
    def test_create_ab_test_with_description(self):
        """Test creating A/B test with description"""
        test_id = create_ab_test(
            test_name="Test",
            variant_a_name="A",
            variant_b_name="B",
            variant_a_config={},
            variant_b_config={},
            evaluation_type="pairwise",
            test_cases=[],
            test_description="Test description"
        )
        
        test = get_ab_test(test_id)
        assert test is not None
        assert test["test_description"] == "Test description"
    
    def test_get_ab_test_existing(self):
        """Test getting an existing A/B test"""
        test_id = create_ab_test(
            test_name="Get Test",
            variant_a_name="A",
            variant_b_name="B",
            variant_a_config={"key": "value"},
            variant_b_config={"key2": "value2"},
            evaluation_type="comprehensive",
            test_cases=[{"question": "Q1"}, {"question": "Q2"}]
        )
        
        test = get_ab_test(test_id)
        
        assert test is not None
        assert test["test_id"] == test_id
        assert test["test_name"] == "Get Test"
        assert test["variant_a_config"] == {"key": "value"}
        assert test["variant_b_config"] == {"key2": "value2"}
        assert test["test_cases_json"] == [{"question": "Q1"}, {"question": "Q2"}]
    
    def test_get_ab_test_with_results_json(self):
        """Test getting A/B test with results_json"""
        test_id = create_ab_test(
                test_name="Test",
            variant_a_name="A",
            variant_b_name="B",
            variant_a_config={},
            variant_b_config={},
            evaluation_type="comprehensive",
            test_cases=[]
        )
        
        # Manually add results_json
        conn = sqlite3.connect(self.test_db)
        c = conn.cursor()
        c.execute('''
            UPDATE ab_tests 
            SET results_json = ?, statistical_analysis_json = ?
            WHERE test_id = ?
        ''', (json.dumps([{"result": "data"}]), json.dumps({"analysis": "data"}), test_id))
        conn.commit()
        conn.close()
        
        test = get_ab_test(test_id)
        assert test["results_json"] == [{"result": "data"}]
        assert test["statistical_analysis_json"] == {"analysis": "data"}
    
    def test_get_ab_test_nonexistent(self):
        """Test getting a non-existent A/B test"""
        test = get_ab_test("nonexistent-id")
        assert test is None
    
    def test_get_all_ab_tests(self):
        """Test getting all A/B tests"""
        # Create multiple tests
        create_ab_test(
            test_name="Test 1",
            variant_a_name="A",
            variant_b_name="B",
            variant_a_config={},
            variant_b_config={},
            evaluation_type="comprehensive",
            test_cases=[]
        )
        create_ab_test(
            test_name="Test 2",
            variant_a_name="A",
            variant_b_name="B",
            variant_a_config={},
            variant_b_config={},
            evaluation_type="pairwise",
            test_cases=[]
        )
        
        tests = get_all_ab_tests(limit=10)
        
        assert isinstance(tests, list)
        assert len(tests) >= 2
    
    def test_get_all_ab_tests_with_limit(self):
        """Test limiting number of tests returned"""
        for i in range(5):
            create_ab_test(
                test_name=f"Test {i}",
                variant_a_name="A",
                variant_b_name="B",
                variant_a_config={},
                variant_b_config={},
                evaluation_type="comprehensive",
                test_cases=[]
            )
        
        limited = get_all_ab_tests(limit=3)
        assert len(limited) <= 3
    
    def test_get_all_ab_tests_with_results(self):
        """Test getting tests with results_json"""
        test_id = create_ab_test(
            test_name="Test",
            variant_a_name="A",
            variant_b_name="B",
            variant_a_config={},
            variant_b_config={},
            evaluation_type="comprehensive",
            test_cases=[]
        )
        
        # Add results
        conn = sqlite3.connect(self.test_db)
        c = conn.cursor()
        c.execute('''
            UPDATE ab_tests 
            SET results_json = ?, statistical_analysis_json = ?
            WHERE test_id = ?
        ''', (json.dumps([{"result": 1}]), json.dumps({"stat": 1}), test_id))
        conn.commit()
        conn.close()
        
        tests = get_all_ab_tests()
        test = next((t for t in tests if t["test_id"] == test_id), None)
        assert test is not None
        assert test["results_json"] == [{"result": 1}]
    
    def test_update_ab_test_progress(self):
        """Test updating A/B test progress"""
        test_id = create_ab_test(
            test_name="Progress Test",
            variant_a_name="A",
            variant_b_name="B",
            variant_a_config={},
            variant_b_config={},
            evaluation_type="comprehensive",
            test_cases=[{"question": "Q1"}, {"question": "Q2"}]
        )
        
        update_ab_test_progress(
            test_id=test_id,
            completed_cases=2,
            variant_a_wins=1,
            variant_b_wins=1,
            ties=0,
            status="running"
        )
        
        test = get_ab_test(test_id)
        assert test["completed_cases"] == 2
        assert test["variant_a_wins"] == 1
        assert test["variant_b_wins"] == 1
        assert test["ties"] == 0
        assert test["status"] == "running"
    
    def test_save_ab_test_results(self):
        """Test saving A/B test results"""
        test_id = create_ab_test(
            test_name="Results Test",
            variant_a_name="A",
            variant_b_name="B",
            variant_a_config={},
            variant_b_config={},
            evaluation_type="comprehensive",
            test_cases=[]
        )
        
        results = [
            {"winner": "A", "score_a": 9.0, "score_b": 7.0},
            {"winner": "B", "score_a": 6.0, "score_b": 8.0},
            {"winner": "tie", "score_a": 7.5, "score_b": 7.5}
        ]
        statistical_analysis = {"p_value": 0.05, "significant": True}
        
        save_ab_test_results(test_id, results, statistical_analysis, status="completed")
        
        test = get_ab_test(test_id)
        assert test["status"] == "completed"
        assert test["variant_a_wins"] == 1
        assert test["variant_b_wins"] == 1
        assert test["ties"] == 1
        assert test["results_json"] == results
        assert test["statistical_analysis_json"] == statistical_analysis
    
    def test_save_ab_test_results_calculates_wins(self):
        """Test that save_ab_test_results calculates wins correctly"""
        test_id = create_ab_test(
            test_name="Wins Test",
            variant_a_name="A",
            variant_b_name="B",
            variant_a_config={},
            variant_b_config={},
            evaluation_type="comprehensive",
            test_cases=[]
        )
        
        results = [
            {"winner": "A"},
            {"winner": "A"},
            {"winner": "B"},
            {"winner": "tie"}
        ]
        
        save_ab_test_results(test_id, results, {}, status="completed")
        
        test = get_ab_test(test_id)
        assert test["variant_a_wins"] == 2
        assert test["variant_b_wins"] == 1
        assert test["ties"] == 1
    
    @patch('backend.services.ab_test_service.get_ab_test')
    def test_execute_ab_test_not_found(self, mock_get):
        """Test executing non-existent A/B test"""
        mock_get.return_value = None
        
        result = execute_ab_test("nonexistent-id")
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    @patch('backend.services.ab_test_service.get_ab_test')
    @patch('backend.services.ab_test_service.EvaluationService')
    @patch('backend.services.ab_test_service.OllamaAdapter')
    def test_execute_ab_test_comprehensive_with_responses(self, mock_ollama, mock_eval_service, mock_get):
        """Test executing comprehensive A/B test with provided responses"""
        test_data = {
            "test_id": "test-123",
            "variant_a_config": {"task_type": "qa"},
            "variant_b_config": {"task_type": "qa"},
            "evaluation_type": "comprehensive",
            "test_cases_json": [
                {"question": "Q1", "response_a": "Response A1", "response_b": "Response B1"}
            ]
        }
        mock_get.return_value = test_data
        
        mock_service = Mock()
        mock_eval_service.return_value = mock_service
        mock_service.evaluate.return_value = {
            "success": True,
            "scores": {"overall_score": 8.5}
        }
        
        result = execute_ab_test("test-123")
        
        assert result["success"] is True
        assert len(result["results"]) == 1
        assert result["summary"]["total_cases"] == 1
    
    @patch('backend.services.ab_test_service.get_ab_test')
    @patch('backend.services.ab_test_service.EvaluationService')
    @patch('backend.services.ab_test_service.OllamaAdapter')
    def test_execute_ab_test_comprehensive_with_model_generation(self, mock_ollama_class, mock_eval_service, mock_get):
        """Test executing comprehensive A/B test with model generation"""
        test_data = {
            "test_id": "test-123",
            "variant_a_config": {"model_a": "llama3", "task_type": "qa"},
            "variant_b_config": {"model_b": "mistral", "task_type": "qa"},
            "evaluation_type": "comprehensive",
            "test_cases_json": [
                {"question": "Q1"}
            ]
        }
        mock_get.return_value = test_data
        
        mock_ollama = Mock()
        mock_ollama_class.return_value = mock_ollama
        mock_ollama.chat.return_value = {"message": {"content": "Generated response"}}
        mock_ollama._extract_content.return_value = "Generated response"
        
        mock_service = Mock()
        mock_eval_service.return_value = mock_service
        mock_service.evaluate.return_value = {
            "success": True,
            "scores": {"overall_score": 8.5}
        }
        
        result = execute_ab_test("test-123")
        
        assert result["success"] is True
        mock_ollama.chat.assert_called()
    
    @patch('backend.services.ab_test_service.get_ab_test')
    @patch('backend.services.ab_test_service.EvaluationService')
    @patch('backend.services.ab_test_service.OllamaAdapter')
    def test_execute_ab_test_comprehensive_fallback_response(self, mock_ollama_class, mock_eval_service, mock_get):
        """Test comprehensive A/B test with fallback to test_case response"""
        test_data = {
            "test_id": "test-123",
            "variant_a_config": {},
            "variant_b_config": {},
            "evaluation_type": "comprehensive",
            "test_cases_json": [
                {"question": "Q1", "response": "Fallback response"}
            ]
        }
        mock_get.return_value = test_data
        
        mock_service = Mock()
        mock_eval_service.return_value = mock_service
        mock_service.evaluate.return_value = {
            "success": True,
            "scores": {"overall_score": 7.5}
        }
        
        result = execute_ab_test("test-123")
        
        assert result["success"] is True
    
    @patch('backend.services.ab_test_service.get_ab_test')
    @patch('backend.services.ab_test_service.EvaluationService')
    @patch('backend.services.ab_test_service.OllamaAdapter')
    def test_execute_ab_test_comprehensive_eval_failure(self, mock_ollama_class, mock_eval_service, mock_get):
        """Test comprehensive A/B test with evaluation failure"""
        test_data = {
            "test_id": "test-123",
            "variant_a_config": {},
            "variant_b_config": {},
            "evaluation_type": "comprehensive",
            "test_cases_json": [
                {"question": "Q1", "response_a": "A", "response_b": "B"}
            ]
        }
        mock_get.return_value = test_data
        
        mock_service = Mock()
        mock_eval_service.return_value = mock_service
        mock_service.evaluate.return_value = {
            "success": False,
            "error": "Evaluation failed"
        }
        
        result = execute_ab_test("test-123")
        
        assert result["success"] is True
        # Should handle failure gracefully with score 0
        assert result["results"][0]["score_a"] == 0
    
    @patch('backend.services.ab_test_service.get_ab_test')
    @patch('backend.services.ab_test_service.EvaluationService')
    @patch('backend.services.ab_test_service.OllamaAdapter')
    def test_execute_ab_test_pairwise_with_responses(self, mock_ollama_class, mock_eval_service, mock_get):
        """Test executing pairwise A/B test with provided responses"""
        test_data = {
            "test_id": "test-123",
            "variant_a_config": {},
            "variant_b_config": {},
            "evaluation_type": "pairwise",
            "test_cases_json": [
                {"question": "Q1", "response_a": "Response A", "response_b": "Response B"}
            ]
        }
        mock_get.return_value = test_data
        
        mock_service = Mock()
        mock_eval_service.return_value = mock_service
        mock_service.evaluate.return_value = {
            "success": True,
            "winner": "A"
        }
        
        result = execute_ab_test("test-123")
        
        assert result["success"] is True
        assert result["results"][0]["winner"] == "A"
        assert result["results"][0]["score_a"] == 10
        assert result["results"][0]["score_b"] == 5
    
    @patch('backend.services.ab_test_service.get_ab_test')
    @patch('backend.services.ab_test_service.EvaluationService')
    @patch('backend.services.ab_test_service.OllamaAdapter')
    def test_execute_ab_test_pairwise_winner_b(self, mock_ollama_class, mock_eval_service, mock_get):
        """Test pairwise A/B test with B as winner"""
        test_data = {
            "test_id": "test-123",
            "variant_a_config": {},
            "variant_b_config": {},
            "evaluation_type": "pairwise",
            "test_cases_json": [
                {"question": "Q1", "response_a": "A", "response_b": "B"}
            ]
        }
        mock_get.return_value = test_data
        
        mock_service = Mock()
        mock_eval_service.return_value = mock_service
        mock_service.evaluate.return_value = {
            "success": True,
            "winner": "B"
        }
        
        result = execute_ab_test("test-123")
        
        assert result["results"][0]["winner"] == "B"
        assert result["results"][0]["score_a"] == 5
        assert result["results"][0]["score_b"] == 10
    
    @patch('backend.services.ab_test_service.get_ab_test')
    @patch('backend.services.ab_test_service.EvaluationService')
    @patch('backend.services.ab_test_service.OllamaAdapter')
    def test_execute_ab_test_pairwise_tie(self, mock_ollama_class, mock_eval_service, mock_get):
        """Test pairwise A/B test with tie"""
        test_data = {
            "test_id": "test-123",
            "variant_a_config": {},
            "variant_b_config": {},
            "evaluation_type": "pairwise",
            "test_cases_json": [
                {"question": "Q1", "response_a": "A", "response_b": "B"}
            ]
        }
        mock_get.return_value = test_data
        
        mock_service = Mock()
        mock_eval_service.return_value = mock_service
        mock_service.evaluate.return_value = {
            "success": True,
            "winner": "tie"
        }
        
        result = execute_ab_test("test-123")
        
        assert result["results"][0]["winner"] == "tie"
        assert result["results"][0]["score_a"] == 7.5
        assert result["results"][0]["score_b"] == 7.5
    
    @patch('backend.services.ab_test_service.get_ab_test')
    @patch('backend.services.ab_test_service.EvaluationService')
    @patch('backend.services.ab_test_service.OllamaAdapter')
    def test_execute_ab_test_pairwise_eval_failure(self, mock_ollama_class, mock_eval_service, mock_get):
        """Test pairwise A/B test with evaluation failure"""
        test_data = {
            "test_id": "test-123",
            "variant_a_config": {},
            "variant_b_config": {},
            "evaluation_type": "pairwise",
            "test_cases_json": [
                {"question": "Q1", "response_a": "A", "response_b": "B"}
            ]
        }
        mock_get.return_value = test_data
        
        mock_service = Mock()
        mock_eval_service.return_value = mock_service
        mock_service.evaluate.return_value = {
            "success": False
        }
        
        result = execute_ab_test("test-123")
        
        assert result["results"][0]["winner"] == "tie"
    
    @patch('backend.services.ab_test_service.get_ab_test')
    @patch('backend.services.ab_test_service.EvaluationService')
    @patch('backend.services.ab_test_service.OllamaAdapter')
    def test_execute_ab_test_pairwise_generate_responses(self, mock_ollama_class, mock_eval_service, mock_get):
        """Test pairwise A/B test with response generation"""
        test_data = {
            "test_id": "test-123",
            "variant_a_config": {"model_a": "llama3"},
            "variant_b_config": {"model_b": "mistral"},
            "evaluation_type": "pairwise",
            "test_cases_json": [
                {"question": "Q1"}
            ]
        }
        mock_get.return_value = test_data
        
        mock_ollama = Mock()
        mock_ollama_class.return_value = mock_ollama
        mock_ollama.chat.return_value = {"message": {"content": "Generated"}}
        mock_ollama._extract_content.return_value = "Generated"
        
        mock_service = Mock()
        mock_eval_service.return_value = mock_service
        mock_service.evaluate.return_value = {
            "success": True,
            "winner": "A"
        }
        
        result = execute_ab_test("test-123")
        
        assert result["success"] is True
        assert mock_ollama.chat.call_count >= 2  # At least 2 calls for A and B
    
    @patch('backend.services.ab_test_service.get_ab_test')
    @patch('backend.services.ab_test_service.EvaluationService')
    @patch('backend.services.ab_test_service.OllamaAdapter')
    def test_execute_ab_test_default_evaluation_type(self, mock_ollama_class, mock_eval_service, mock_get):
        """Test executing A/B test with default evaluation type"""
        test_data = {
            "test_id": "test-123",
            "variant_a_config": {},
            "variant_b_config": {},
            "evaluation_type": "other",
            "test_cases_json": [
                {"question": "Q1", "response_a": "A", "response_b": "B"}
            ]
        }
        mock_get.return_value = test_data
        
        result = execute_ab_test("test-123")
        
        assert result["success"] is True
        assert result["results"][0]["score_a"] == 7.0
        assert result["results"][0]["score_b"] == 7.0
    
    @patch('backend.services.ab_test_service.get_ab_test')
    @patch('backend.services.ab_test_service.EvaluationService')
    @patch('backend.services.ab_test_service.OllamaAdapter')
    def test_execute_ab_test_with_stop_flag(self, mock_ollama_class, mock_eval_service, mock_get):
        """Test executing A/B test with stop flag"""
        test_data = {
            "test_id": "test-123",
            "variant_a_config": {},
            "variant_b_config": {},
            "evaluation_type": "comprehensive",
            "test_cases_json": [
                {"question": "Q1", "response_a": "A", "response_b": "B"},
                {"question": "Q2", "response_a": "A2", "response_b": "B2"}
            ]
        }
        mock_get.return_value = test_data
        
        mock_service = Mock()
        mock_eval_service.return_value = mock_service
        mock_service.evaluate.return_value = {
            "success": True,
            "scores": {"overall_score": 8.0}
        }
        
        call_count = [0]
        def stop_flag():
            call_count[0] += 1
            # Return True after first iteration (stop after processing first case)
            return call_count[0] > 1
        
        result = execute_ab_test("test-123", stop_flag=stop_flag)
        
        assert result["success"] is True
        # Should stop after first case
        assert len(result["results"]) == 1
    
    @patch('backend.services.ab_test_service.get_ab_test')
    @patch('backend.services.ab_test_service.EvaluationService')
    @patch('backend.services.ab_test_service.OllamaAdapter')
    def test_execute_ab_test_with_progress_callback(self, mock_ollama_class, mock_eval_service, mock_get):
        """Test executing A/B test with progress callback"""
        test_data = {
            "test_id": "test-123",
            "variant_a_config": {},
            "variant_b_config": {},
            "evaluation_type": "comprehensive",
            "test_cases_json": [
                {"question": "Q1", "response_a": "A", "response_b": "B"},
                {"question": "Q2", "response_a": "A2", "response_b": "B2"}
            ]
        }
        mock_get.return_value = test_data
        
        mock_service = Mock()
        mock_eval_service.return_value = mock_service
        mock_service.evaluate.return_value = {
            "success": True,
            "scores": {"overall_score": 8.0}
        }
        
        callback_calls = []
        def progress_callback(current, total):
            callback_calls.append((current, total))
        
        result = execute_ab_test("test-123", progress_callback=progress_callback)
        
        assert result["success"] is True
        assert len(callback_calls) == 2
        assert callback_calls[0] == (1, 2)
        assert callback_calls[1] == (2, 2)
    
    @patch('backend.services.ab_test_service.get_ab_test')
    @patch('backend.services.ab_test_service.EvaluationService')
    @patch('backend.services.ab_test_service.calculate_statistical_significance')
    def test_execute_ab_test_statistical_analysis(self, mock_stats, mock_eval_service, mock_get):
        """Test statistical analysis in A/B test execution"""
        test_data = {
            "test_id": "test-123",
            "variant_a_config": {},
            "variant_b_config": {},
            "evaluation_type": "comprehensive",
            "test_cases_json": [
                {"question": "Q1", "response_a": "A", "response_b": "B"},
                {"question": "Q2", "response_a": "A2", "response_b": "B2"}
            ]
        }
        mock_get.return_value = test_data
        
        mock_service = Mock()
        mock_eval_service.return_value = mock_service
        mock_service.evaluate.return_value = {
            "success": True,
            "scores": {"overall_score": 8.0}
        }
        
        mock_stats.return_value = {"p_value": 0.03, "significant": True}
        
        result = execute_ab_test("test-123")
        
        assert result["success"] is True
        assert "statistical_analysis" in result
        assert result["statistical_analysis"]["significant"] is True
        mock_stats.assert_called_once()
    
    @patch('backend.services.ab_test_service.get_ab_test')
    @patch('backend.services.ab_test_service.EvaluationService')
    def test_execute_ab_test_insufficient_data(self, mock_eval_service, mock_get):
        """Test A/B test with insufficient data for statistical analysis"""
        test_data = {
            "test_id": "test-123",
            "variant_a_config": {},
            "variant_b_config": {},
            "evaluation_type": "comprehensive",
            "test_cases_json": [
                {"question": "Q1", "response_a": "A", "response_b": "B"}
            ]
        }
        mock_get.return_value = test_data
        
        mock_service = Mock()
        mock_eval_service.return_value = mock_service
        mock_service.evaluate.return_value = {
            "success": True,
            "scores": {"overall_score": 8.0}
        }
        
        result = execute_ab_test("test-123")
        
        assert result["success"] is True
        assert result["statistical_analysis"]["valid"] is False
        assert "Insufficient data" in result["statistical_analysis"]["error"]
    
    @patch('backend.services.ab_test_service.get_ab_test')
    @patch('backend.services.ab_test_service.EvaluationService')
    def test_execute_ab_test_exception_handling(self, mock_eval_service, mock_get):
        """Test exception handling in A/B test execution"""
        test_id = create_ab_test(
            test_name="Exception Test",
            variant_a_name="A",
            variant_b_name="B",
            variant_a_config={},
            variant_b_config={},
            evaluation_type="comprehensive",
            test_cases=[{"question": "Q1", "response_a": "A", "response_b": "B"}]
        )
        
        test_data = {
            "test_id": test_id,
            "variant_a_config": {},
            "variant_b_config": {},
            "evaluation_type": "comprehensive",
            "test_cases_json": [
                {"question": "Q1", "response_a": "A", "response_b": "B"}
            ]
        }
        mock_get.return_value = test_data
        
        mock_service = Mock()
        mock_eval_service.return_value = mock_service
        mock_service.evaluate.side_effect = Exception("Test error")
        
        result = execute_ab_test(test_id)
        
        assert result["success"] is False
        assert "error" in result
        assert "Test error" in result["error"]
        
        # Check that status was updated to failed
        test = get_ab_test(test_id)
        assert test["status"] == "failed"
    
    @patch('backend.services.ab_test_service.get_ab_test')
    @patch('backend.services.ab_test_service.EvaluationService')
    def test_execute_ab_test_winner_determination(self, mock_eval_service, mock_get):
        """Test winner determination logic"""
        test_data = {
            "test_id": "test-123",
            "variant_a_config": {},
            "variant_b_config": {},
            "evaluation_type": "comprehensive",
            "test_cases_json": [
                {"question": "Q1", "response_a": "A", "response_b": "B"}
            ]
        }
        mock_get.return_value = test_data
        
        mock_service = Mock()
        mock_eval_service.return_value = mock_service
        mock_service.evaluate.side_effect = [
            {"success": True, "scores": {"overall_score": 9.0}},  # A
            {"success": True, "scores": {"overall_score": 7.0}}   # B
        ]
        
        result = execute_ab_test("test-123")
        
        assert result["results"][0]["winner"] == "A"
        assert result["summary"]["variant_a_wins"] == 1
        assert result["summary"]["variant_b_wins"] == 0
    
    @patch('backend.services.ab_test_service.get_ab_test')
    @patch('backend.services.ab_test_service.EvaluationService')
    def test_execute_ab_test_response_truncation(self, mock_eval_service, mock_get):
        """Test that responses are truncated in results"""
        long_response = "A" * 300  # Longer than 200 chars
        test_data = {
            "test_id": "test-123",
            "variant_a_config": {},
            "variant_b_config": {},
            "evaluation_type": "comprehensive",
            "test_cases_json": [
                {"question": "Q1", "response_a": long_response, "response_b": "B"}
            ]
        }
        mock_get.return_value = test_data
        
        mock_service = Mock()
        mock_eval_service.return_value = mock_service
        mock_service.evaluate.return_value = {
            "success": True,
            "scores": {"overall_score": 8.0}
        }
        
        result = execute_ab_test("test-123")
        
        assert len(result["results"][0]["response_a"]) == 200
        assert result["results"][0]["response_b"] == "B"
    
    @patch('backend.services.ab_test_service.get_ab_test')
    @patch('backend.services.ab_test_service.EvaluationService')
    def test_execute_ab_test_non_string_response(self, mock_eval_service, mock_get):
        """Test handling non-string responses"""
        test_data = {
            "test_id": "test-123",
            "variant_a_config": {},
            "variant_b_config": {},
            "evaluation_type": "comprehensive",
            "test_cases_json": [
                {"question": "Q1", "response_a": 12345, "response_b": "B"}
            ]
        }
        mock_get.return_value = test_data
        
        mock_service = Mock()
        mock_eval_service.return_value = mock_service
        mock_service.evaluate.return_value = {
            "success": True,
            "scores": {"overall_score": 8.0}
        }
        
        result = execute_ab_test("test-123")
        
        assert isinstance(result["results"][0]["response_a"], str)
        assert len(result["results"][0]["response_a"]) <= 200
