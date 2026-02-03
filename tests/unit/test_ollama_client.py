"""Unit tests for OllamaAdapter"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from core.infrastructure.llm.ollama_client import OllamaAdapter
from core.common.settings import settings


class TestOllamaAdapter:
    """Test cases for OllamaAdapter"""
    
    def test_adapter_initialization_default(self):
        """Test adapter initialization with default host"""
        adapter = OllamaAdapter()
        assert adapter.host == settings.ollama_host
        assert adapter._client is None
        assert adapter.retry_policy is not None
    
    def test_adapter_initialization_custom_host(self):
        """Test adapter initialization with custom host"""
        custom_host = "http://custom:11434"
        adapter = OllamaAdapter(host=custom_host)
        assert adapter.host == custom_host
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_client_property_lazy_initialization(self, mock_client_class):
        """Test that client is lazily initialized"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        assert adapter._client is None
        
        # Access client property
        client = adapter.client
        assert adapter._client is not None
        assert adapter._client == mock_client
        mock_client_class.assert_called_once_with(host=settings.ollama_host)
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_client_property_cached(self, mock_client_class):
        """Test that client is cached after first access"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        client1 = adapter.client
        client2 = adapter.client
        
        assert client1 is client2
        mock_client_class.assert_called_once()
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_success(self, mock_client_class):
        """Test successful chat call"""
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

    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_passes_messages_to_client(self, mock_client_class):
        """Test that messages are passed through to the client chat call."""
        mock_client = Mock()
        mock_response = {"message": {"content": "Response"}}
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client

        adapter = OllamaAdapter()

        def capture_execute(func, base_options=None, *args, **kwargs):
            return func({"num_predict": 768})

        adapter.retry_policy.execute = capture_execute

        messages = [{"role": "user", "content": "Hello"}]
        adapter.chat(model="llama3", messages=messages)

        assert mock_client.chat.call_args.kwargs["messages"] == messages

    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_passes_model_to_client(self, mock_client_class):
        """Test that model is passed through to the client chat call."""
        mock_client = Mock()
        mock_response = {"message": {"content": "Response"}}
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client

        adapter = OllamaAdapter()

        def capture_execute(func, base_options=None, *args, **kwargs):
            return func({"num_predict": 768})

        adapter.retry_policy.execute = capture_execute

        adapter.chat(model="llama3", messages=[{"role": "user", "content": "Hello"}])

        assert mock_client.chat.call_args.kwargs["model"] == "llama3"

    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_sets_message_when_missing(self, mock_client_class):
        """Test that response message dict is created when missing."""
        mock_client = Mock()
        response = {}
        mock_client.chat.return_value = response
        mock_client_class.return_value = mock_client

        adapter = OllamaAdapter()
        adapter.retry_policy.execute = Mock(return_value=response)

        result = adapter.chat(model="llama3", messages=[{"role": "user", "content": "Hello"}])

        assert "message" in result
        assert isinstance(result["message"], dict)
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_with_options(self, mock_client_class):
        """Test chat call with custom options"""
        mock_client = Mock()
        mock_response = {"message": {"content": "Response"}}
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        adapter.retry_policy.execute = Mock(return_value=mock_response)
        
        result = adapter.chat(
            model="llama3",
            messages=[{"role": "user", "content": "Hello"}],
            options={"temperature": 0.5}
        )
        
        assert result == mock_response
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_default_options_are_set(self, mock_client_class):
        """Test that default options (temperature, timeout) are set correctly"""
        mock_client = Mock()
        mock_response = {"message": {"content": "Response"}}
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        
        # Capture the base_options passed to retry_policy.execute
        captured_base_options = None
        def capture_execute(func, base_options=None, *args, **kwargs):
            nonlocal captured_base_options
            captured_base_options = base_options
            # Call the function with test options
            test_options = {"num_predict": 768}
            return func(test_options)
        
        adapter.retry_policy.execute = capture_execute
        
        adapter.chat(
            model="llama3",
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        # Verify default options are set correctly
        assert captured_base_options is not None
        assert captured_base_options.get("temperature") == 0.3
        assert captured_base_options.get("timeout") == 300
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_custom_options_override_defaults(self, mock_client_class):
        """Test that custom options override default options"""
        mock_client = Mock()
        mock_response = {"message": {"content": "Response"}}
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        
        # Capture the base_options passed to retry_policy.execute
        captured_base_options = None
        def capture_execute(func, base_options=None, *args, **kwargs):
            nonlocal captured_base_options
            captured_base_options = base_options
            test_options = {"num_predict": 768}
            return func(test_options)
        
        adapter.retry_policy.execute = capture_execute
        
        adapter.chat(
            model="llama3",
            messages=[{"role": "user", "content": "Hello"}],
            options={"temperature": 0.8, "timeout": 600}
        )
        
        # Verify custom options override defaults
        assert captured_base_options is not None
        assert captured_base_options.get("temperature") == 0.8
        assert captured_base_options.get("timeout") == 600
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_partial_options_merge_with_defaults(self, mock_client_class):
        """Test that partial custom options merge with defaults"""
        mock_client = Mock()
        mock_response = {"message": {"content": "Response"}}
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        
        # Capture the base_options passed to retry_policy.execute
        captured_base_options = None
        def capture_execute(func, base_options=None, *args, **kwargs):
            nonlocal captured_base_options
            captured_base_options = base_options
            test_options = {"num_predict": 768}
            return func(test_options)
        
        adapter.retry_policy.execute = capture_execute
        
        # Only override temperature, timeout should remain default
        adapter.chat(
            model="llama3",
            messages=[{"role": "user", "content": "Hello"}],
            options={"temperature": 0.9}
        )
        
        # Verify partial override works
        assert captured_base_options is not None
        assert captured_base_options.get("temperature") == 0.9
        assert captured_base_options.get("timeout") == 300  # Default preserved
    
    def test_extract_content_from_dict(self):
        """Test extracting content from dict response"""
        adapter = OllamaAdapter()
        response = {
            "message": {
                "content": "Test content"
            }
        }
        content = adapter._extract_content(response)
        assert content == "Test content"
    
    def test_extract_content_from_object(self):
        """Test extracting content from object response"""
        adapter = OllamaAdapter()
        
        # Mock object with message attribute
        mock_message = Mock()
        mock_message.content = "Test content"
        mock_response = Mock()
        mock_response.message = mock_message
        
        content = adapter._extract_content(mock_response)
        assert content == "Test content"
    
    def test_extract_content_empty(self):
        """Test extracting content from empty response"""
        adapter = OllamaAdapter()
        content = adapter._extract_content({})
        assert content == ""

    def test_extract_content_missing_message_key_returns_empty(self):
        """Test extracting content when message key is missing."""
        adapter = OllamaAdapter()
        content = adapter._extract_content({"not_message": {}})
        assert content == ""
    
    def test_extract_content_exception_handling(self):
        """Test that exceptions in extract_content are handled"""
        adapter = OllamaAdapter()
        # Pass something that will cause an exception
        content = adapter._extract_content(None)
        assert content == ""
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_list_models_success(self, mock_client_class):
        """Test listing models successfully"""
        mock_client = Mock()
        mock_client.list.return_value = {
            "models": [
                {"name": "llama3"},
                {"name": "mistral"}
            ]
        }
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        models = adapter.list_models()
        
        assert "llama3" in models
        assert "mistral" in models
        assert len(models) == 2
        assert "XXXX" not in models
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_list_models_empty(self, mock_client_class):
        """Test listing models when none exist"""
        mock_client = Mock()
        mock_client.list.return_value = {"models": []}
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        models = adapter.list_models()
        
        assert models == []
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_list_models_exception(self, mock_client_class):
        """Test listing models when exception occurs"""
        mock_client = Mock()
        mock_client.list.side_effect = Exception("Connection error")
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        models = adapter.list_models()
        
        assert models == []
    
    def test_list_models_verifies_models_key_default(self, caplog):
        """Test that models.get() defaults to empty list"""
        adapter = OllamaAdapter()
        adapter.client.list = Mock(return_value={})  # No "models" key
        
        models = adapter.list_models()
        
        # Verify default is used (mutation: models.get("models", None) would fail)
        assert models == []
        assert "Failed to list Ollama models" not in caplog.text
    
    def test_list_models_verifies_list_comprehension(self):
        """Test that list comprehension extracts names correctly"""
        adapter = OllamaAdapter()
        adapter.client.list = Mock(return_value={
            "models": [
                {"name": "llama3"},
                {"name": "mistral"},
                {"name": "phi"}
            ]
        })
        
        models = adapter.list_models()
        
        # Verify list comprehension works (mutation: m["name"] -> m["text"] would fail)
        assert models == ["llama3", "mistral", "phi"]
        assert len(models) == 3
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_verifies_options_default(self, mock_client_class):
        """Test that options defaults to empty dict"""
        mock_client = Mock()
        mock_response = {"message": {"content": "Test"}}
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        
        # Capture base_options passed to retry_policy.execute
        captured_base_options = None
        def capture_execute(func, base_options=None, *args, **kwargs):
            nonlocal captured_base_options
            captured_base_options = base_options
            # Call func with empty effective_options
            return func({})
        
        adapter.retry_policy.execute = capture_execute
        
        adapter.chat(model="llama3", messages=[{"role": "user", "content": "Hello"}]  # No options
        )
        
        # Verify options was set to {} (mutation: options = None would fail)
        # This is verified by default_options being created correctly
        assert captured_base_options is not None
        assert captured_base_options["temperature"] == 0.3
        assert captured_base_options["timeout"] == 300
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_verifies_default_options_dict(self, mock_client_class):
        """Test that default_options dict is created correctly"""
        mock_client = Mock()
        mock_response = {"message": {"content": "Test"}}
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        
        # Capture base_options
        captured_base_options = None
        def capture_execute(func, base_options=None, *args, **kwargs):
            nonlocal captured_base_options
            captured_base_options = base_options
            return func({})
        
        adapter.retry_policy.execute = capture_execute
        
        adapter.chat(model="llama3", messages=[{"role": "user", "content": "Hello"}])
        
        # Verify default_options dict is created (mutation: default_options = {} would fail)
        assert captured_base_options is not None
        assert captured_base_options["temperature"] == 0.3
        assert captured_base_options["timeout"] == 300
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_verifies_options_update(self, mock_client_class):
        """Test that options.update() merges correctly"""
        mock_client = Mock()
        mock_response = {"message": {"content": "Test"}}
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        
        captured_base_options = None
        def capture_execute(func, base_options=None, *args, **kwargs):
            nonlocal captured_base_options
            captured_base_options = base_options
            return func({})
        
        adapter.retry_policy.execute = capture_execute
        
        adapter.chat(
            model="llama3",
            messages=[{"role": "user", "content": "Hello"}],
            options={"temperature": 0.5}
        )
        
        # Verify options.update() was used (mutation: default_options = options would fail)
        assert captured_base_options["temperature"] == 0.5  # Custom value
        assert captured_base_options["timeout"] == 300  # Default preserved
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_verifies_merged_options_dict_copy(self, mock_client_class):
        """Test that merged_options is a copy of default_options"""
        mock_client = Mock()
        mock_response = {"message": {"content": "Test"}}
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        
        # Capture what's passed to client.chat
        captured_chat_options = None
        original_chat = mock_client.chat
        def capture_chat(*args, **kwargs):
            nonlocal captured_chat_options
            captured_chat_options = kwargs.get("options", {})
            return original_chat(*args, **kwargs)
        mock_client.chat = capture_chat
        
        def mock_execute(func, base_options=None, *args, **kwargs):
            # Pass retry options
            return func({"num_predict": 768})
        
        adapter.retry_policy.execute = mock_execute
        
        adapter.chat(model="llama3", messages=[{"role": "user", "content": "Hello"}])
        
        # Verify dict() copy is used and retry options are merged (mutation: merged_options = default_options would fail)
        assert captured_chat_options is not None
        assert captured_chat_options["temperature"] == 0.3  # From default_options
        assert captured_chat_options["timeout"] == 300  # From default_options
        assert captured_chat_options["num_predict"] == 768  # From retry effective_options
    
    def test_chat_verifies_content_conditional(self):
        """Test that content sanitization only happens when content exists"""
        adapter = OllamaAdapter()
        
        # Test with content
        response_with_content = {"message": {"content": "Test <think>content</think>"}}
        adapter.retry_policy.execute = Mock(return_value=response_with_content)
        result1 = adapter.chat(model="llama3", messages=[{"role": "user", "content": "Hello"}])
        # Verify content was sanitized (mutation: if content -> if not content would fail)
        assert "<think>" not in result1["message"]["content"]
        
        # Test without content
        response_no_content = {"message": {"content": ""}}
        adapter.retry_policy.execute = Mock(return_value=response_no_content)
        result2 = adapter.chat(model="llama3", messages=[{"role": "user", "content": "Hello"}])
        # Verify no sanitization when empty (mutation: if content -> if True would fail)
        assert result2["message"]["content"] == ""
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_chat_verifies_setdefault_usage(self, mock_client_class):
        """Test that setdefault is used for dict response"""
        mock_client = Mock()
        # Response with content so sanitization happens and setdefault is called
        response = {"message": {"content": "Test <think>content</think>"}}
        mock_client.chat.return_value = response
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        adapter.retry_policy.execute = Mock(return_value=response)
        
        result = adapter.chat(model="llama3", messages=[{"role": "user", "content": "Hello"}])
        
        # Verify setdefault was used (mutation: response["message"] = {} would fail)
        # When content exists and is sanitized, setdefault ensures message dict exists
        assert "message" in result
        assert isinstance(result["message"], dict)
        assert "<think>" not in result["message"]["content"]  # Sanitized
        assert "XXXX" not in result["message"]["content"]
    
    def test_chat_verifies_message_dict_path(self):
        """Test that message dict path is handled correctly"""
        adapter = OllamaAdapter()
        response = Mock()
        response.message = {"content": "Test"}
        adapter.retry_policy.execute = Mock(return_value=response)
        
        result = adapter.chat(model="llama3", messages=[{"role": "user", "content": "Hello"}])
        
        # Verify dict path is used (mutation: isinstance(response.message, list) would fail)
        assert result.message["content"] == "Test"
    
    def test_chat_verifies_message_attr_path(self):
        """Test that message attribute path is handled correctly"""
        adapter = OllamaAdapter()
        mock_message = Mock()
        mock_message.content = "Test"
        response = Mock()
        response.message = mock_message
        adapter.retry_policy.execute = Mock(return_value=response)
        
        result = adapter.chat(model="llama3", messages=[{"role": "user", "content": "Hello"}])
        
        # Verify attribute path is used (mutation: hasattr(response.message, "text") would fail)
        assert result.message.content == "Test"
    
    def test_extract_content_verifies_dict_path(self):
        """Test that dict path is checked first"""
        adapter = OllamaAdapter()
        response = {"message": {"content": "Dict content"}}
        content = adapter._extract_content(response)
        # Verify isinstance(response, dict) is checked (mutation: isinstance(response, list) would fail)
        assert content == "Dict content"
    
    def test_extract_content_verifies_hasattr_check(self):
        """Test that hasattr is used to check message attribute"""
        adapter = OllamaAdapter()
        mock_message = Mock()
        mock_message.content = "Attr content"
        response = Mock()
        response.message = mock_message
        content = adapter._extract_content(response)
        # Verify hasattr check (mutation: hasattr(response, "text") would fail)
        assert content == "Attr content"
    
    def test_extract_content_verifies_exception_handling(self):
        """Test that exceptions return empty string"""
        adapter = OllamaAdapter()
        # Object that raises exception
        class BadResponse:
            @property
            def message(self):
                raise Exception("Test")
        
        content = adapter._extract_content(BadResponse())
        # Verify exception returns "" (mutation: return None would fail)
        assert content == ""


class TestListModelsResponseFormats:
    """Tests for different response formats in list_models"""
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_list_models_response_with_models_attribute(self, mock_client_class):
        """Test list_models with response object having .models attribute (lines 75-76)"""
        mock_client = Mock()
        
        # Create a response object with .models attribute (not a dict)
        class ModelsResponse:
            def __init__(self):
                self.models = [{"name": "llama3"}, {"name": "mistral"}]
        
        mock_client.list.return_value = ModelsResponse()
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        models = adapter.list_models()
        
        assert "llama3" in models
        assert "mistral" in models
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_list_models_response_is_list(self, mock_client_class):
        """Test list_models when response is directly a list (lines 77-78)"""
        mock_client = Mock()
        
        # Return a list directly instead of a dict
        mock_client.list.return_value = [{"name": "llama3"}, {"name": "phi"}]
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        models = adapter.list_models()
        
        assert "llama3" in models
        assert "phi" in models
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_list_models_response_unknown_type(self, mock_client_class):
        """Test list_models with unknown response type returns empty list (lines 79-80)"""
        mock_client = Mock()
        
        # Return something that's not dict, list, or has .models attribute
        mock_client.list.return_value = "unexpected string response"
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        models = adapter.list_models()
        
        assert models == []
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_list_models_model_with_name_attribute(self, mock_client_class):
        """Test list_models with model objects having .name attribute (lines 88-89)"""
        mock_client = Mock()
        
        # Create model objects with .name attribute
        class ModelObj:
            def __init__(self, name):
                self.name = name
        
        mock_client.list.return_value = {
            "models": [ModelObj("llama3"), ModelObj("mistral")]
        }
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        models = adapter.list_models()
        
        assert "llama3" in models
        assert "mistral" in models
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_list_models_model_with_model_attribute(self, mock_client_class):
        """Test list_models with model objects having .model attribute (lines 90-91)"""
        mock_client = Mock()
        
        # Create model objects with .model attribute (not .name)
        class ModelObj:
            def __init__(self, model):
                self.model = model
        
        mock_client.list.return_value = {
            "models": [ModelObj("llama3"), ModelObj("phi")]
        }
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        models = adapter.list_models()
        
        assert "llama3" in models
        assert "phi" in models
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_list_models_model_string_conversion(self, mock_client_class):
        """Test list_models with model objects using string conversion (lines 92-96)"""
        mock_client = Mock()
        
        # Create objects that have no name/model attributes but can be stringified
        class StringModel:
            def __init__(self, value):
                self._value = value
            
            def __str__(self):
                return self._value
        
        mock_client.list.return_value = {
            "models": [StringModel("llama3"), StringModel("codellama")]
        }
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        models = adapter.list_models()
        
        assert "llama3" in models
        assert "codellama" in models
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_list_models_model_string_conversion_skips_none(self, mock_client_class):
        """Test list_models string conversion skips 'None' strings (line 95 condition)"""
        mock_client = Mock()
        
        # Create object that stringifies to "None"
        class NoneStringModel:
            def __str__(self):
                return "None"
        
        class ValidModel:
            def __str__(self):
                return "llama3"
        
        mock_client.list.return_value = {
            "models": [NoneStringModel(), ValidModel()]
        }
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        models = adapter.list_models()
        
        assert "llama3" in models
        assert "None" not in models
    
    @patch('core.infrastructure.llm.ollama_client.ollama.Client')
    def test_list_models_model_string_conversion_skips_empty(self, mock_client_class):
        """Test list_models string conversion skips empty strings (line 95 condition)"""
        mock_client = Mock()
        
        # Create object that stringifies to empty string
        class EmptyStringModel:
            def __str__(self):
                return ""
        
        class ValidModel:
            def __str__(self):
                return "mistral"
        
        mock_client.list.return_value = {
            "models": [EmptyStringModel(), ValidModel()]
        }
        mock_client_class.return_value = mock_client
        
        adapter = OllamaAdapter()
        models = adapter.list_models()
        
        assert "mistral" in models
        assert "" not in models
        assert len(models) == 1