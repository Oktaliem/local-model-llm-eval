"""Unit tests for API server"""
import pytest
from fastapi.testclient import TestClient
from backend.api_server import app
from datetime import datetime


class TestAPIServer:
    """Test cases for API server endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "LLM & AI Agent Evaluation Framework API"
        assert data["version"] == "1.0.0"
        assert "documentation" in data
        assert "endpoints" in data
        assert "authentication" in data
        assert "rate_limiting" in data
    
    def test_root_endpoint_documentation_links(self, client):
        """Test root endpoint documentation links"""
        response = client.get("/")
        data = response.json()
        
        doc = data["documentation"]
        assert doc["swagger_ui"] == "/docs"
        assert doc["redoc"] == "/redoc"
        assert doc["openapi_json"] == "/openapi.json"
    
    def test_root_endpoint_endpoints_list(self, client):
        """Test root endpoint lists all endpoints"""
        response = client.get("/")
        data = response.json()
        
        endpoints = data["endpoints"]
        assert "health" in endpoints
        assert "api_base" in endpoints
        assert "evaluations" in endpoints
        assert "analytics" in endpoints
        assert "ab_tests" in endpoints
        assert "templates" in endpoints
        assert "custom_metrics" in endpoints
        assert "webhooks" in endpoints
        assert "api_keys" in endpoints
    
    def test_root_endpoint_authentication_info(self, client):
        """Test root endpoint authentication information"""
        response = client.get("/")
        data = response.json()
        
        auth = data["authentication"]
        assert auth["type"] == "Bearer Token (API Key)"
        assert "header" in auth
        assert "create_key" in auth
    
    def test_root_endpoint_rate_limiting_info(self, client):
        """Test root endpoint rate limiting information"""
        response = client.get("/")
        data = response.json()
        
        rate_limit = data["rate_limiting"]
        assert "requests_per_window" in rate_limit
        assert "window_seconds" in rate_limit
        assert isinstance(rate_limit["requests_per_window"], int)
        assert isinstance(rate_limit["window_seconds"], int)
    
    def test_api_base_endpoint(self, client):
        """Test /api/v1/ endpoint"""
        response = client.get("/api/v1/")
        assert response.status_code == 200
        data = response.json()
        
        assert data["api_version"] == "v1"
        assert data["name"] == "LLM & AI Agent Evaluation Framework API"
        assert data["version"] == "1.0.0"
        assert "resources" in data
        assert "links" in data
    
    def test_api_base_resources(self, client):
        """Test /api/v1/ endpoint resources"""
        response = client.get("/api/v1/")
        data = response.json()
        
        resources = data["resources"]
        assert "evaluations" in resources
        assert "analytics" in resources
        assert "ab_tests" in resources
        assert "templates" in resources
        assert "custom_metrics" in resources
        assert "webhooks" in resources
        assert "api_keys" in resources
    
    def test_api_base_evaluations_resource(self, client):
        """Test evaluations resource in /api/v1/"""
        response = client.get("/api/v1/")
        data = response.json()
        
        evaluations = data["resources"]["evaluations"]
        assert "description" in evaluations
        assert "endpoints" in evaluations
        
        endpoints = evaluations["endpoints"]
        assert "comprehensive" in endpoints
        assert "code" in endpoints
        assert "router" in endpoints
        assert "skills" in endpoints
        assert "trajectory" in endpoints
        assert "pairwise" in endpoints
        assert "list" in endpoints
    
    def test_api_base_analytics_resource(self, client):
        """Test analytics resource in /api/v1/"""
        response = client.get("/api/v1/")
        data = response.json()
        
        analytics = data["resources"]["analytics"]
        assert "description" in analytics
        assert "endpoints" in analytics
        assert "overview" in analytics["endpoints"]
    
    def test_api_base_ab_tests_resource(self, client):
        """Test ab_tests resource in /api/v1/"""
        response = client.get("/api/v1/")
        data = response.json()
        
        ab_tests = data["resources"]["ab_tests"]
        assert "description" in ab_tests
        assert "endpoints" in ab_tests
        
        endpoints = ab_tests["endpoints"]
        assert "create" in endpoints
        assert "list" in endpoints
        assert "get" in endpoints
        assert "run" in endpoints
    
    def test_api_base_templates_resource(self, client):
        """Test templates resource in /api/v1/"""
        response = client.get("/api/v1/")
        data = response.json()
        
        templates = data["resources"]["templates"]
        assert "description" in templates
        assert "endpoints" in templates
        
        endpoints = templates["endpoints"]
        assert "create" in endpoints
        assert "list" in endpoints
        assert "get" in endpoints
        assert "delete" in endpoints
        assert "apply" in endpoints
    
    def test_api_base_custom_metrics_resource(self, client):
        """Test custom_metrics resource in /api/v1/"""
        response = client.get("/api/v1/")
        data = response.json()
        
        custom_metrics = data["resources"]["custom_metrics"]
        assert "description" in custom_metrics
        assert "endpoints" in custom_metrics
        
        endpoints = custom_metrics["endpoints"]
        assert "create" in endpoints
        assert "list" in endpoints
        assert "get" in endpoints
        assert "delete" in endpoints
        assert "evaluate" in endpoints
    
    def test_api_base_webhooks_resource(self, client):
        """Test webhooks resource in /api/v1/"""
        response = client.get("/api/v1/")
        data = response.json()
        
        webhooks = data["resources"]["webhooks"]
        assert "description" in webhooks
        assert "endpoints" in webhooks
        
        endpoints = webhooks["endpoints"]
        assert "create" in endpoints
        assert "list" in endpoints
        assert "get" in endpoints
        assert "delete" in endpoints
    
    def test_api_base_api_keys_resource(self, client):
        """Test api_keys resource in /api/v1/"""
        response = client.get("/api/v1/")
        data = response.json()
        
        api_keys = data["resources"]["api_keys"]
        assert "description" in api_keys
        assert "endpoints" in api_keys
        
        endpoints = api_keys["endpoints"]
        assert "create" in endpoints
        assert "list" in endpoints
    
    def test_api_base_links(self, client):
        """Test /api/v1/ endpoint links"""
        response = client.get("/api/v1/")
        data = response.json()
        
        links = data["links"]
        assert "documentation" in links
        assert "health" in links
        assert "root" in links
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "timestamp" in data
        
        # Verify timestamp is valid ISO format
        timestamp = data["timestamp"]
        datetime.fromisoformat(timestamp)  # Should not raise
    
    def test_health_endpoint_timestamp_format(self, client):
        """Test health endpoint timestamp is valid ISO format"""
        response = client.get("/health")
        data = response.json()
        
        timestamp = data["timestamp"]
        # Should be parseable as ISO format
        parsed = datetime.fromisoformat(timestamp)
        assert isinstance(parsed, datetime)

