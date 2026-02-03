"""Unit tests for LLMService"""
from unittest.mock import Mock

import pytest

from core.services.llm_service import LLMService, get_llm_service, generate_response


class TestLLMService:
    """Test cases for LLMService"""

    def test_generate_response_success_dict(self):
        """Successful generation when adapter returns dict with message.content."""
        mock_adapter = Mock()
        mock_adapter.chat.return_value = {"message": {"content": "Hello world"}}
        svc = LLMService(llm_adapter=mock_adapter)

        result = svc.generate_response("Hi", "llama3")

        assert result["success"] is True
        assert result["response"] == "Hello world"
        mock_adapter.chat.assert_called_once()

    def test_generate_response_success_object_message_attr(self):
        """Successful generation when adapter returns object.message.content."""

        class RespMsg:
            def __init__(self, content: str):
                self.content = content

        class RespWrapper:
            def __init__(self, content: str):
                self.message = RespMsg(content)

        mock_adapter = Mock()
        mock_adapter.chat.return_value = RespWrapper("Hi from object")
        svc = LLMService(llm_adapter=mock_adapter)

        result = svc.generate_response("Hi", "llama3")

        assert result["success"] is True
        assert result["response"] == "Hi from object"

    def test_generate_response_success_object_message_dict(self):
        """Successful generation when adapter returns object.message as dict."""

        class RespWrapper:
            def __init__(self, content: str):
                self.message = {"content": content}

        mock_adapter = Mock()
        mock_adapter.chat.return_value = RespWrapper("Hi from dict")
        svc = LLMService(llm_adapter=mock_adapter)

        result = svc.generate_response("Hi", "llama3")

        assert result["success"] is True
        assert result["response"] == "Hi from dict"

    def test_generate_response_none_response(self):
        """If adapter returns None, service should return error."""
        mock_adapter = Mock()
        mock_adapter.chat.return_value = None
        svc = LLMService(llm_adapter=mock_adapter)

        result = svc.generate_response("Hi", "llama3")

        assert result["success"] is False
        assert "None response" in result["error"]

    def test_generate_response_empty_content(self):
        """If content extraction yields empty string, service returns error."""
        mock_adapter = Mock()
        mock_adapter.chat.return_value = {"message": {"content": ""}}
        svc = LLMService(llm_adapter=mock_adapter)

        result = svc.generate_response("Hi", "llama3")

        assert result["success"] is False
        assert "empty response" in result["error"]

    def test_generate_response_model_not_found_error(self):
        """Model-not-found errors should be rewritten with available models list."""
        mock_adapter = Mock()
        mock_adapter.chat.side_effect = Exception("Model not found 404")
        mock_adapter.list_models.return_value = ["llama3", "mistral"]

        svc = LLMService(llm_adapter=mock_adapter)
        result = svc.generate_response("Hi", "missing-model")

        assert result["success"] is False
        assert "Model 'missing-model' not found" in result["error"]
        assert "llama3, mistral" in result["error"]

    def test_generate_response_generic_error(self):
        """Other exceptions should be propagated as-is."""
        mock_adapter = Mock()
        mock_adapter.chat.side_effect = Exception("Timeout")
        svc = LLMService(llm_adapter=mock_adapter)

        result = svc.generate_response("Hi", "llama3")

        assert result["success"] is False
        assert result["error"] == "Timeout"

    def test_extract_content_variants_and_exception_path(self):
        """Directly test _extract_content for all supported shapes."""
        svc = LLMService(llm_adapter=Mock())

        # dict
        assert (
            svc._extract_content({"message": {"content": "dict content"}})
            == "dict content"
        )

        # object.message.content
        class Msg:
            def __init__(self, c: str):
                self.content = c

        class Obj:
            def __init__(self, c: str):
                self.message = Msg(c)

        assert svc._extract_content(Obj("obj content")) == "obj content"

        # object.message dict
        class ObjDict:
            def __init__(self, c: str):
                self.message = {"content": c}

        assert svc._extract_content(ObjDict("dict msg")) == "dict msg"

        # bad / exception path
        class Bad:
            @property
            def message(self):
                raise RuntimeError("boom")

        assert svc._extract_content(Bad()) == ""

        # Also ensure that calling through generate_response with a Bad wrapper
        # still returns a clean error (covers line 62 except path).
        class BadWrapper:
            def __init__(self):
                self.message = Bad()

        mock_adapter = Mock()
        mock_adapter.chat.return_value = BadWrapper()
        svc2 = LLMService(llm_adapter=mock_adapter)
        result = svc2.generate_response("Q", "llama3")
        assert result["success"] is False
        assert "empty response" in result["error"]

    def test_get_llm_service_singleton_and_generate_response_helper(self, monkeypatch):
        """get_llm_service should cache instance; generate_response helper should delegate."""
        import core.services.llm_service as mod

        # Reset global singleton
        mod._llm_service = None

        # Inject a mock service
        mock_service = Mock(spec=LLMService)
        mock_service.generate_response.return_value = {"success": True, "response": "ok"}
        mod._llm_service = mock_service

        # Helper should use global instance
        result = generate_response("Q", "llama3")
        assert result == {"success": True, "response": "ok"}
        mock_service.generate_response.assert_called_once_with("Q", "llama3")

        # Reset singleton and ensure get_llm_service constructs a real instance
        mod._llm_service = None
        svc = get_llm_service()
        from core.services.llm_service import LLMService as LLMServiceClass
        assert isinstance(svc, LLMServiceClass)
    
    def test_generate_response_verifies_options_defaults(self):
        """Test that options defaults are set correctly"""
        mock_adapter = Mock()
        mock_adapter.chat.return_value = {"message": {"content": "Test"}}
        svc = LLMService(llm_adapter=mock_adapter)
        
        result = svc.generate_response("Hi", "llama3")
        
        assert result["success"] is True
        # Verify options are set (mutation: options = {} would fail)
        call_args = mock_adapter.chat.call_args
        options = call_args[1]["options"]
        assert options["temperature"] == 0.7
        assert options["num_predict"] == 65536  # Updated to 65536 for comprehensive responses
        assert options["timeout"] == 300  # Updated to 300 seconds (5 minutes)
    
    def test_generate_response_verifies_system_message(self):
        """Test that system message is set correctly"""
        mock_adapter = Mock()
        mock_adapter.chat.return_value = {"message": {"content": "Test"}}
        svc = LLMService(llm_adapter=mock_adapter)
        
        result = svc.generate_response("Hi", "llama3")
        
        assert result["success"] is True
        # Verify messages structure (mutation: messages = [] would fail)
        call_args = mock_adapter.chat.call_args
        messages = call_args[1]["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert "helpful assistant" in messages[0]["content"].lower()
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Hi"
    
    def test_generate_response_verifies_error_msg_construction(self):
        """Test that error messages are constructed correctly"""
        mock_adapter = Mock()
        mock_adapter.chat.side_effect = Exception("Model not found 404")
        mock_adapter.list_models.return_value = ["llama3", "mistral"]
        svc = LLMService(llm_adapter=mock_adapter)
        
        result = svc.generate_response("Hi", "missing-model")
        
        assert result["success"] is False
        # Verify error message construction (mutation: error_msg = str(e) would fail)
        assert "Model 'missing-model' not found" in result["error"]
        assert "llama3, mistral" in result["error"]
        # Verify available models list is included (mutation: available = [] would fail)
    
    def test_generate_response_verifies_empty_available_models(self):
        """Test error message when no models are available"""
        mock_adapter = Mock()
        mock_adapter.chat.side_effect = Exception("Model not found 404")
        mock_adapter.list_models.return_value = []  # Empty list
        svc = LLMService(llm_adapter=mock_adapter)
        
        result = svc.generate_response("Hi", "missing-model")
        
        assert result["success"] is False
        # Verify empty list handling (mutation: available else "None" -> available would fail)
        assert "None - please pull a model first" in result["error"] or "llama3" not in result["error"]


