"""Final tests for remaining coverage gaps"""
import pytest
from unittest.mock import Mock, patch
from core.domain.strategies.pairwise import PairwiseStrategy
from core.infrastructure.llm.ollama_client import OllamaAdapter
from core.domain.models import EvaluationRequest
from core.infrastructure.llm.ollama_client import OllamaAdapter


class TestPairwiseRemaining:
    """Tests for remaining pairwise coverage"""
    
    def test_extract_content_exception_path(self):
        """Test extract_content exception handling (line 137)"""
        adapter = Mock()
        strategy = PairwiseStrategy(adapter)
        # Test the path where hasattr(response, "message") is False
        # This should hit the return "" at line 137
        content = strategy._extract_content("not an object with message")
        assert content == ""
    
    def test_extract_content_no_message_attribute(self):
        """Test extract_content when object has no message attribute"""
        adapter = Mock()
        strategy = PairwiseStrategy(adapter)
        # Object without message attribute
        class NoMessage:
            pass
        
        content = strategy._extract_content(NoMessage())
        assert content == ""
    
    def test_parse_judgment_score_a_value_error(self):
        """Test parsing judgment with invalid score_a (line 153-154)"""
        adapter = Mock()
        strategy = PairwiseStrategy(adapter)
        # Use a value that matches the regex [0-9.]+ but fails float() conversion
        # The regex will match "8.5.5" but float("8.5.5") raises ValueError
        judgment = """Winner: A
Score A: 8.5.5
Score B: 7.5
Reasoning: Test"""
        parsed = strategy._parse_judgment(judgment)
        # ValueError should be caught, score_a should be None
        assert parsed["score_a"] is None  # ValueError caught at line 153-154
        assert parsed["score_b"] == 7.5
    
    def test_parse_judgment_score_b_value_error(self):
        """Test parsing judgment with invalid score_b (line 159-160)"""
        adapter = Mock()
        strategy = PairwiseStrategy(adapter)
        # Use a value that matches the regex but fails float() conversion
        judgment = """Winner: A
Score A: 8.5
Score B: 7.5.5
Reasoning: Test"""
        parsed = strategy._parse_judgment(judgment)
        assert parsed["score_a"] == 8.5
        assert parsed["score_b"] is None  # ValueError caught at line 159-160


class TestOllamaClientRemaining:
    """Tests for remaining ollama_client coverage"""
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_updates_dict_message_content_path(self, mock_client_class):
        """Test chat updates dict message content (line 43)"""
        mock_client = Mock()
        # Create response with dict message (not empty, has content key)
        mock_response = {
            "message": {
                "content": "Original content"
            }
        }
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        adapter.retry_policy.execute = Mock(return_value=mock_response)
        # Mock extract_content to return sanitized content
        adapter._extract_content = Mock(return_value="Sanitized content")
        
        result = adapter.chat(
            model="llama3",
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        # Should update content in dict message (line 43: response.message["content"] = content)
        assert result["message"]["content"] == "Sanitized content"


class TestBatchServiceRemaining:
    """Tests for remaining batch_service coverage"""
    
    def test_get_results_exception_handling(self):
        """Test get_results exception handling (lines 88-89)"""
        from core.services.batch_service import BatchService
        from queue import Queue
        
        batch_service = BatchService()
        # Create a queue that will raise exception on get_nowait
        class ExceptionQueue:
            def __init__(self):
                self._empty = False
                self._items = [{"result": "test1"}]  # Has one item
            
            def empty(self):
                return len(self._items) == 0
            
            def get_nowait(self):
                if self._items:
                    item = self._items.pop(0)
                    # Raise exception to trigger line 88-89
                    raise Exception("Queue exception")
                raise Exception("Empty")
        
        exception_queue = ExceptionQueue()
        batch_service._run_queues["test_run"] = exception_queue
        
        results = batch_service.get_results("test_run")
        # Should return None when exception occurs (lines 88-89: except Exception: break)
        assert results is None

