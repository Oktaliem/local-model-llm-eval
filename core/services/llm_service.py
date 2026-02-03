"""LLM service for generating responses"""
from typing import Dict, Any
from core.infrastructure.llm.ollama_client import OllamaAdapter
from core.common.settings import settings


class LLMService:
    """Service for LLM operations like generating responses"""
    
    def __init__(self, llm_adapter: OllamaAdapter = None):
        self.llm_adapter = llm_adapter or OllamaAdapter()
    
    def generate_response(self, question: str, model: str) -> Dict[str, Any]:
        """Generate a response from an LLM model.
        
        Args:
            question: The question or prompt to send to the model
            model: The model name to use
            
        Returns:
            Dict with 'success' (bool) and either 'response' (str) or 'error' (str)
        """
        try:
            response = self.llm_adapter.chat(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Provide clear, accurate, and helpful responses."},
                    {"role": "user", "content": question}
                ],
                options={
                    "temperature": 0.7,  # Slightly higher temperature for more varied responses
                    "num_predict": 65536,  # 65,536 tokens for much longer, more complete responses
                    "timeout": 300  # 5 minute timeout for longer responses
                }
            )
            # Check if response is None or empty
            if response is None:
                return {"success": False, "error": "Received None response from model. The model may not be responding."}
            # Safely extract content from response
            content = self._extract_content(response)
            if not content:
                return {"success": False, "error": "Received empty response from model. The model may not have generated any content."}
            return {"success": True, "response": content}
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "404" in error_msg:
                available = self.llm_adapter.list_models()
                error_msg = f"Model '{model}' not found. Available models: {', '.join(available) if available else 'None - please pull a model first'}"
            return {"success": False, "error": error_msg}
    
    def _extract_content(self, response: Any) -> str:
        """Safely extract content from response, handling different response structures."""
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


# Global instance for convenience
_llm_service = None

def get_llm_service() -> LLMService:
    """Get the global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

def generate_response(question: str, model: str) -> Dict[str, Any]:
    """Convenience function to generate a response from an LLM model.
    
    Args:
        question: The question or prompt to send to the model
        model: The model name to use
        
    Returns:
        Dict with 'success' (bool) and either 'response' (str) or 'error' (str)
    """
    return get_llm_service().generate_response(question, model)


