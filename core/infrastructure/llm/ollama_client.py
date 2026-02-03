"""Ollama LLM client adapter"""
import ollama
from typing import Dict, Any, Optional, List
from core.common.settings import settings
from core.common.sanitize import sanitize_model_output
from core.infrastructure.llm.retry import RetryPolicy


class OllamaAdapter:
    """Adapter for Ollama LLM client"""

    def __init__(self, host: Optional[str] = None):
        self.host = host or settings.ollama_host
        self._client = None
        self.retry_policy = RetryPolicy()

    @property
    def client(self):
        if self._client is None:
            self._client = ollama.Client(host=self.host)
        return self._client

    def chat(self, model: str, messages: List[Dict[str, str]], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if options is None:
            options = {}
        default_options = {"temperature": 0.3, "timeout": 300}
        default_options.update(options)

        def _call(effective_options: Dict[str, Any]):
            # Merge retry-provided options (e.g., num_predict) over our defaults
            merged_options = dict(default_options)
            merged_options.update(effective_options or {})
            return self.client.chat(model=model, messages=messages, options=merged_options)

        response = self.retry_policy.execute(_call, base_options=default_options)
        content = self._extract_content(response)
        if content:
            content = sanitize_model_output(content)
            if isinstance(response, dict):
                response.setdefault("message", {})["content"] = content
            elif hasattr(response, "message"):
                if isinstance(response.message, dict):
                    response.message["content"] = content
                elif hasattr(response.message, "content"):
                    response.message.content = content
        else:
            # Ensure message dict exists even when there's no content
            if isinstance(response, dict):
                response.setdefault("message", {})
        return response

    def _extract_content(self, response: Any) -> str:
        try:
            if isinstance(response, dict):
                return response.get("message", {}).get("content", "")
            if hasattr(response, "message"):
                msg = response.message
                if isinstance(msg, dict):
                    return msg.get("content", "")
                if hasattr(msg, "content"):
                    return msg.content
            return ""
        except Exception:
            return ""

    def list_models(self) -> List[str]:
        """List available Ollama models.
        
        Returns:
            List of model names (e.g., ['llama3', 'mistral', 'gpt-oss-safeguard:20b'])
        """
        try:
            models_response = self.client.list()
            model_names = []
            
            # Handle different response formats
            if isinstance(models_response, dict):
                models_list = models_response.get("models", [])
            elif hasattr(models_response, "models"):
                models_list = models_response.models
            elif isinstance(models_response, list):
                models_list = models_response
            else:
                return []
            
            # Extract model names
            for model in models_list:
                if isinstance(model, dict):
                    name = model.get("name") or model.get("model")
                    if name:
                        model_names.append(name)
                elif hasattr(model, "name"):
                    model_names.append(model.name)
                elif hasattr(model, "model"):
                    model_names.append(model.model)
                else:
                    # Try string conversion
                    name = str(model)
                    if name and name != "None":
                        model_names.append(name)
            
            # Filter out empty names and return unique list
            return list(dict.fromkeys([name for name in model_names if name]))
        except Exception as e:
            # Log error but don't raise - let caller handle empty list
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to list Ollama models: {str(e)}")
            return []


