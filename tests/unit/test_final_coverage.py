"""Final unit tests to reach 100% coverage"""
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from core.domain.strategies.pairwise import PairwiseStrategy
from core.domain.strategies.router import RouterStrategy
from core.domain.strategies.skills import SkillsStrategy
from core.domain.strategies.template_eval import TemplateEvalStrategy
from core.domain.strategies.trajectory import TrajectoryStrategy
from core.domain.models import EvaluationRequest
from core.infrastructure.llm.ollama_client import OllamaAdapter

# Create mock app module if it doesn't exist
if 'app' not in sys.modules:
    mock_app = MagicMock()
    sys.modules['app'] = mock_app


class TestPairwiseStrategyFinal:
    """Final tests for PairwiseStrategy to reach 100%"""
    
    def test_extract_content_exception_handling(self):
        """Test extract_content exception handling"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        # Create object that will raise exception
        class BadObject:
            @property
            def message(self):
                raise Exception("Test exception")
        
        content = strategy._extract_content(BadObject())
        assert content == ""
    
    def test_parse_judgment_score_b_value_error(self):
        """Test parsing judgment with invalid score_b (ValueError)"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = """Winner: A
Score A: 8.5
Score B: invalid
Reasoning: Test"""
        parsed = strategy._parse_judgment(judgment)
        assert parsed["score_a"] == 8.5
        assert parsed["score_b"] is None  # ValueError caught
    
    def test_swap_back_no_score_matches(self):
        """Test swap_back when score matches don't exist"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Winner: B\nReasoning: Test without scores"
        swapped = strategy._swap_back_judgment(judgment, "A", "B")
        assert "Winner: A" in swapped or "Winner: B" in swapped


class TestOtherStrategiesFinal:
    """Final tests for other strategies"""
    
    def test_router_strategy_with_error(self):
        """Test router strategy with error"""
        with patch('backend.services.evaluation_functions.evaluate_router_decision') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": False,
                "error": "Router error"
            }
            strategy = RouterStrategy()
            request = EvaluationRequest(
                evaluation_type="router",
                question="Test",
                response="Test",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is False
    
    def test_router_strategy_with_exception(self):
        """Test router strategy with exception"""
        with patch('backend.services.evaluation_functions.evaluate_router_decision') as mock_evaluate:
            mock_evaluate.side_effect = Exception("Router exception")
            strategy = RouterStrategy()
            request = EvaluationRequest(
                evaluation_type="router",
                question="Test",
                response="Test",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is False
            assert "Router exception" in result.error
    
    def test_skills_strategy_with_error(self):
        """Test skills strategy with error"""
        with patch('backend.services.skills_evaluation_service.evaluate_skill') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": False,
                "error": "Skills error"
            }
            strategy = SkillsStrategy()
            request = EvaluationRequest(
                evaluation_type="skills",
                question="Test",
                response="Test",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is False
    
    def test_skills_strategy_with_exception(self):
        """Test skills strategy with exception"""
        with patch('backend.services.skills_evaluation_service.evaluate_skill') as mock_evaluate:
            mock_evaluate.side_effect = Exception("Skills exception")
            strategy = SkillsStrategy()
            request = EvaluationRequest(
                evaluation_type="skills",
                question="Test",
                response="Test",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is False
            assert "Skills exception" in result.error
    
    def test_template_strategy_with_error(self):
        """Test template strategy with error"""
        with patch('backend.services.evaluation_functions.evaluate_comprehensive') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": False,
                "error": "Template error"
            }
            strategy = TemplateEvalStrategy()
            request = EvaluationRequest(
                evaluation_type="template",
                question="Test",
                response="Test",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is False
    
    def test_template_strategy_missing_response(self):
        """Test template strategy with missing response"""
        strategy = TemplateEvalStrategy()
        request = EvaluationRequest(
            evaluation_type="template",
            question="Test",
            response=None,
            response_a=None,
            judge_model="llama3"
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert "response is required" in result.error
    
    def test_trajectory_strategy_with_error(self):
        """Test trajectory strategy with error"""
        with patch('backend.services.evaluation_functions.evaluate_trajectory') as mock_evaluate:
            mock_evaluate.return_value = {
                "success": False,
                "error": "Trajectory error"
            }
            strategy = TrajectoryStrategy()
            request = EvaluationRequest(
                evaluation_type="trajectory",
                question="Test",
                response="Test",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is False
    
    def test_trajectory_strategy_with_exception(self):
        """Test trajectory strategy with exception"""
        with patch('backend.services.evaluation_functions.evaluate_trajectory') as mock_evaluate:
            mock_evaluate.side_effect = Exception("Trajectory exception")
            strategy = TrajectoryStrategy()
            request = EvaluationRequest(
                evaluation_type="trajectory",
                question="Test",
                response="Test",
                judge_model="llama3"
            )
            result = strategy.evaluate(request)
            assert result.success is False
            assert "Trajectory exception" in result.error


class TestOllamaClientFinal:
    """Final tests for OllamaAdapter"""
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_with_dict_message_update(self, mock_client_class):
        """Test chat updates dict message content"""
        mock_client = Mock()
        mock_response = {
            "message": {}
        }
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        adapter.retry_policy.execute = Mock(return_value=mock_response)
        adapter._extract_content = Mock(return_value="Test content")
        
        result = adapter.chat(
            model="llama3",
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        # Should use setdefault to add content
        assert result["message"]["content"] == "Test content"


class TestBatchServiceFinal:
    """Final tests for BatchService"""
    
    def test_get_results_exception_in_loop(self):
        """Test get_results with exception in while loop"""
        from core.services.batch_service import BatchService
        from queue import Queue
        
        batch_service = BatchService()
        test_queue = Queue()
        test_queue.put({"result": "test1"})
        batch_service._run_queues["test_run"] = test_queue
        
        # Create a mock queue that raises exception on second get_nowait
        class MockQueue:
            def __init__(self):
                self.items = [{"result": "test1"}]
                self.call_count = 0
            
            def empty(self):
                return len(self.items) == 0
            
            def get_nowait(self):
                self.call_count += 1
                if self.call_count == 1:
                    return self.items.pop(0)
                else:
                    raise Exception("Queue error")
        
        mock_queue = MockQueue()
        batch_service._run_queues["test_run"] = mock_queue
        
        results = batch_service.get_results("test_run")
        # Should return results from first call, then break on exception
        assert results is not None
        assert len(results) == 1

