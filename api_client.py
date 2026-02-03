"""
Python SDK for LLM & AI Agent Evaluation Framework API

Example usage:
    from api_client import EvaluationClient
    
    client = EvaluationClient(api_key="your_api_key", base_url="http://localhost:8000")
    
    # Comprehensive evaluation
    result = client.evaluate_comprehensive(
        question="What is AI?",
        response="AI is artificial intelligence..."
    )
    
    # Code evaluation
    result = client.evaluate_code(code="def hello(): return 'world'")
    
    # Router evaluation
    result = client.evaluate_router(
        query="Calculate 2+2",
        available_tools=[{"name": "calculator", "description": "Performs calculations"}],
        selected_tool="calculator"
    )
"""

import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime


class EvaluationClient:
    """Client for interacting with the Evaluation Framework API."""
    
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        """
        Initialize the client.
        
        Args:
            api_key: Your API key
            base_url: Base URL of the API server (default: http://localhost:8000)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}{endpoint}"
        with httpx.Client(timeout=300.0) as client:  # 5 minute timeout for evaluations
            response = client.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        return self._request("GET", "/health")
    
    def evaluate_comprehensive(
        self,
        question: str,
        response: str,
        judge_model: str = "llama3",
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """Evaluate a response using comprehensive metrics."""
        return self._request(
            "POST",
            "/api/v1/evaluations/comprehensive",
            json={
                "question": question,
                "response": response,
                "judge_model": judge_model,
                "save_to_db": save_to_db
            }
        )
    
    def evaluate_code(
        self,
        code: str,
        test_input: Optional[str] = None,
        expected_output: Optional[str] = None,
        judge_model: str = "llama3",
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """Evaluate Python code."""
        return self._request(
            "POST",
            "/api/v1/evaluations/code",
            json={
                "code": code,
                "test_input": test_input,
                "expected_output": expected_output,
                "judge_model": judge_model,
                "save_to_db": save_to_db
            }
        )
    
    def evaluate_router(
        self,
        query: str,
        available_tools: List[Dict[str, str]],
        selected_tool: str,
        context: Optional[str] = None,
        expected_tool: Optional[str] = None,
        routing_strategy: Optional[str] = None,
        judge_model: str = "llama3",
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """Evaluate router/tool selection decision."""
        return self._request(
            "POST",
            "/api/v1/evaluations/router",
            json={
                "query": query,
                "available_tools": available_tools,
                "selected_tool": selected_tool,
                "context": context,
                "expected_tool": expected_tool,
                "routing_strategy": routing_strategy,
                "judge_model": judge_model,
                "save_to_db": save_to_db
            }
        )
    
    def evaluate_skills(
        self,
        skill_type: str,
        question: str,
        response: str,
        reference_answer: Optional[str] = None,
        domain: Optional[str] = None,
        judge_model: str = "llama3",
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """Evaluate domain-specific skills."""
        return self._request(
            "POST",
            "/api/v1/evaluations/skills",
            json={
                "skill_type": skill_type,
                "question": question,
                "response": response,
                "reference_answer": reference_answer,
                "domain": domain,
                "judge_model": judge_model,
                "save_to_db": save_to_db
            }
        )
    
    def evaluate_trajectory(
        self,
        task_description: str,
        trajectory: List[Dict[str, str]],
        expected_trajectory: Optional[List[Dict[str, str]]] = None,
        trajectory_type: Optional[str] = None,
        judge_model: str = "llama3",
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """Evaluate multi-step trajectory/action sequence."""
        return self._request(
            "POST",
            "/api/v1/evaluations/trajectory",
            json={
                "task_description": task_description,
                "trajectory": trajectory,
                "expected_trajectory": expected_trajectory,
                "trajectory_type": trajectory_type,
                "judge_model": judge_model,
                "save_to_db": save_to_db
            }
        )
    
    def evaluate_pairwise(
        self,
        question: str,
        response_a: str,
        response_b: str,
        model_a: Optional[str] = None,
        model_b: Optional[str] = None,
        judge_model: str = "llama3",
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """Compare two responses pairwise."""
        return self._request(
            "POST",
            "/api/v1/evaluations/pairwise",
            json={
                "question": question,
                "response_a": response_a,
                "response_b": response_b,
                "model_a": model_a,
                "model_b": model_b,
                "judge_model": judge_model,
                "save_to_db": save_to_db
            }
        )
    
    def get_evaluations(
        self,
        evaluation_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get evaluations from database."""
        params = {"limit": limit}
        if evaluation_type:
            params["evaluation_type"] = evaluation_type
        return self._request("GET", "/api/v1/evaluations", params=params)
    
    def get_analytics_overview(self) -> Dict[str, Any]:
        """Get analytics overview."""
        return self._request("GET", "/api/v1/analytics/overview")
    
    def create_webhook(
        self,
        url: str,
        events: List[str] = ["evaluation.completed"],
        secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a webhook."""
        return self._request(
            "POST",
            "/api/v1/webhooks",
            json={
                "url": url,
                "events": events,
                "secret": secret
            }
        )
    
    def list_webhooks(self) -> Dict[str, Any]:
        """List all webhooks."""
        return self._request("GET", "/api/v1/webhooks")
    
    def delete_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """Delete a webhook."""
        return self._request("DELETE", f"/api/v1/webhooks/{webhook_id}")
    
    # A/B Testing methods
    def create_ab_test(
        self,
        test_name: str,
        variant_a_name: str,
        variant_b_name: str,
        variant_a_config: Dict[str, Any],
        variant_b_config: Dict[str, Any],
        evaluation_type: str,
        test_cases: List[Dict[str, Any]],
        test_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new A/B test."""
        return self._request(
            "POST",
            "/api/v1/ab-tests",
            json={
                "test_name": test_name,
                "variant_a_name": variant_a_name,
                "variant_b_name": variant_b_name,
                "variant_a_config": variant_a_config,
                "variant_b_config": variant_b_config,
                "evaluation_type": evaluation_type,
                "test_cases": test_cases,
                "test_description": test_description
            }
        )
    
    def list_ab_tests(self, limit: int = 50) -> Dict[str, Any]:
        """List all A/B tests."""
        return self._request("GET", "/api/v1/ab-tests", params={"limit": limit})
    
    def get_ab_test(self, test_id: str) -> Dict[str, Any]:
        """Get a specific A/B test by ID."""
        return self._request("GET", f"/api/v1/ab-tests/{test_id}")
    
    def run_ab_test(
        self,
        test_id: str,
        judge_model: str = "llama3"
    ) -> Dict[str, Any]:
        """Run an A/B test."""
        return self._request(
            "POST",
            f"/api/v1/ab-tests/{test_id}/run",
            json={
                "test_id": test_id,
                "judge_model": judge_model
            }
        )
    
    # Evaluation Templates methods
    def create_template(
        self,
        template_name: str,
        evaluation_type: str,
        template_config: Dict[str, Any],
        template_description: Optional[str] = None,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new evaluation template."""
        return self._request(
            "POST",
            "/api/v1/templates",
            json={
                "template_name": template_name,
                "evaluation_type": evaluation_type,
                "template_config": template_config,
                "template_description": template_description,
                "industry": industry
            }
        )
    
    def list_templates(
        self,
        evaluation_type: Optional[str] = None,
        industry: Optional[str] = None,
        include_predefined: bool = True,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List all evaluation templates."""
        params = {"include_predefined": include_predefined, "limit": limit}
        if evaluation_type:
            params["evaluation_type"] = evaluation_type
        if industry:
            params["industry"] = industry
        return self._request("GET", "/api/v1/templates", params=params)
    
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """Get a specific template by ID."""
        return self._request("GET", f"/api/v1/templates/{template_id}")
    
    def delete_template(self, template_id: str) -> Dict[str, Any]:
        """Delete an evaluation template (only custom templates)."""
        return self._request("DELETE", f"/api/v1/templates/{template_id}")
    
    def apply_template(
        self,
        template_id: str,
        evaluation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply a template to evaluation data."""
        return self._request(
            "POST",
            f"/api/v1/templates/{template_id}/apply",
            json={
                "template_id": template_id,
                "evaluation_data": evaluation_data
            }
        )
    
    # Custom Metrics methods
    def create_custom_metric(
        self,
        metric_name: str,
        evaluation_type: str,
        metric_definition: str,
        metric_description: Optional[str] = None,
        domain: Optional[str] = None,
        scoring_function: Optional[str] = None,
        criteria_json: Optional[Dict[str, Any]] = None,
        weight: float = 1.0,
        scale_min: float = 0.0,
        scale_max: float = 10.0
    ) -> Dict[str, Any]:
        """Create a new custom metric."""
        return self._request(
            "POST",
            "/api/v1/custom-metrics",
            json={
                "metric_name": metric_name,
                "evaluation_type": evaluation_type,
                "metric_definition": metric_definition,
                "metric_description": metric_description,
                "domain": domain,
                "scoring_function": scoring_function,
                "criteria_json": criteria_json,
                "weight": weight,
                "scale_min": scale_min,
                "scale_max": scale_max
            }
        )
    
    def list_custom_metrics(
        self,
        evaluation_type: Optional[str] = None,
        domain: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List all custom metrics."""
        params = {"limit": limit}
        if evaluation_type:
            params["evaluation_type"] = evaluation_type
        if domain:
            params["domain"] = domain
        if is_active is not None:
            params["is_active"] = is_active
        return self._request("GET", "/api/v1/custom-metrics", params=params)
    
    def get_custom_metric(self, metric_id: str) -> Dict[str, Any]:
        """Get a specific custom metric by ID."""
        return self._request("GET", f"/api/v1/custom-metrics/{metric_id}")
    
    def delete_custom_metric(self, metric_id: str) -> Dict[str, Any]:
        """Deactivate a custom metric (soft delete)."""
        return self._request("DELETE", f"/api/v1/custom-metrics/{metric_id}")
    
    def evaluate_with_custom_metric(
        self,
        metric_id: str,
        question: str,
        response: str,
        reference: Optional[str] = None,
        judge_model: str = "llama3"
    ) -> Dict[str, Any]:
        """Evaluate a response using a custom metric."""
        return self._request(
            "POST",
            f"/api/v1/custom-metrics/{metric_id}/evaluate",
            json={
                "metric_id": metric_id,
                "question": question,
                "response": response,
                "reference": reference,
                "judge_model": judge_model
            }
        )


# Convenience function to create API key
def create_api_key(base_url: str = "http://localhost:8000", description: Optional[str] = None) -> Dict[str, Any]:
    """Create a new API key (no authentication required)."""
    url = f"{base_url.rstrip('/')}/api/v1/keys"
    with httpx.Client() as client:
        response = client.post(url, json={"description": description} if description else {})
        response.raise_for_status()
        return response.json()

