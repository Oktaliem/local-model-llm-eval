"""Additional unit tests for OllamaAdapter to reach 100% coverage"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from core.infrastructure.llm.ollama_client import OllamaAdapter


class TestOllamaAdapterComplete:
    """Additional test cases for OllamaAdapter"""
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_sanitizes_content(self, mock_client_class):
        """Test that chat sanitizes content"""
        mock_client = Mock()
        mock_response = {
            "message": {
                "content": "Test <think>hidden</think> response"
            }
        }
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        adapter.retry_policy.execute = Mock(return_value=mock_response)
        
        result = adapter.chat(
            model="llama3",
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        # Content should be sanitized (redacted_reasoning blocks removed)
        assert "<think>" not in result["message"]["content"]
        assert "hidden" not in result["message"]["content"]
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_merges_options_correctly(self, mock_client_class):
        """Test that chat merges retry options correctly"""
        mock_client = Mock()
        mock_response = {"message": {"content": "Test"}}
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        # Mock retry policy to pass options
        def mock_execute(func, base_options=None, *args, **kwargs):
            # Simulate retry passing num_predict
            options = dict(base_options) if base_options else {}
            options["num_predict"] = 512
            return func(options)
        
        adapter.retry_policy.execute = mock_execute
        
        result = adapter.chat(
            model="llama3",
            messages=[{"role": "user", "content": "Hello"}],
            options={"temperature": 0.5}
        )
        
        # Verify client.chat was called with merged options
        mock_client.chat.assert_called_once()
        call_kwargs = mock_client.chat.call_args[1]
        assert "options" in call_kwargs
        assert call_kwargs["options"]["temperature"] == 0.5
        assert call_kwargs["options"]["num_predict"] == 512
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_updates_dict_message_content(self, mock_client_class):
        """Test chat updates dict message with content attribute (line 43)"""
        mock_client = Mock()
        # Create response with dict message
        mock_response = {
            "message": {
                "content": "Original"
            }
        }
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        adapter.retry_policy.execute = Mock(return_value=mock_response)
        # Mock extract_content to return sanitized content
        adapter._extract_content = Mock(return_value="Sanitized")
        
        result = adapter.chat(
            model="llama3",
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        # Content should be updated in dict message (line 43)
        assert result["message"]["content"] == "Sanitized"
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_updates_object_with_dict_message_content(self, mock_client_class):
        """Test chat updates response object whose message is a dict (covers line 43)."""
        # Create a response object whose .message is a dict
        mock_response_obj = Mock()
        mock_response_obj.message = {"content": "Original"}

        mock_client = Mock()
        mock_client.chat.return_value = mock_response_obj
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        adapter.retry_policy.execute = Mock(return_value=mock_response_obj)
        # Force _extract_content to return a sanitized value
        adapter._extract_content = Mock(return_value="Sanitized")
        
        result = adapter.chat(
            model="llama3",
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        # Ensure the dict stored in response.message was updated
        assert isinstance(result.message, dict)
        assert result.message["content"] == "Sanitized"
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_updates_response_object(self, mock_client_class):
        """Test that chat updates response object with sanitized content"""
        # Create a mock response object (not dict)
        mock_message = Mock()
        mock_message.content = "Test <think>hidden</think> response"
        mock_response_obj = Mock()
        mock_response_obj.message = mock_message
        
        mock_client = Mock()
        mock_client.chat.return_value = mock_response_obj
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        adapter.retry_policy.execute = Mock(return_value=mock_response_obj)
        
        result = adapter.chat(
            model="llama3",
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        # Content should be sanitized
        assert "<think>" not in result.message.content
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_with_dict_message(self, mock_client_class):
        """Test chat with dict message structure"""
        mock_client = Mock()
        mock_response = {
            "message": {
                "content": "Test response"
            }
        }
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        adapter.retry_policy.execute = Mock(return_value=mock_response)
        
        result = adapter.chat(
            model="llama3",
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        assert result == mock_response
    
    def test_extract_content_from_dict_message(self):
        """Test extracting content from dict message"""
        adapter = OllamaAdapter()
        response = {
            "message": {
                "content": "Test content"
            }
        }
        content = adapter._extract_content(response)
        assert content == "Test content"
    
    def test_extract_content_from_dict_with_nested_message(self):
        """Test extracting content from nested dict structure"""
        adapter = OllamaAdapter()
        response = {
            "message": {
                "content": "Nested content"
            }
        }
        content = adapter._extract_content(response)
        assert content == "Nested content"
    
    def test_extract_content_from_object_with_dict_message(self):
        """Test extracting content from object with dict message"""
        adapter = OllamaAdapter()
        mock_message = {"content": "Dict message content"}
        mock_response = Mock()
        mock_response.message = mock_message
        
        content = adapter._extract_content(mock_response)
        assert content == "Dict message content"
    
    def test_extract_content_exception_handling(self):
        """Test extract_content handles exceptions gracefully"""
        adapter = OllamaAdapter()
        # Pass something that will cause an exception
        class BadObject:
            @property
            def message(self):
                raise Exception("Test exception")
        
        content = adapter._extract_content(BadObject())
        assert content == ""

