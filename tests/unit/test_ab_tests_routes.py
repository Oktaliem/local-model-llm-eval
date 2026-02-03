"""Unit tests for A/B tests API routes"""
import pytest
from unittest.mock import patch, Mock, AsyncMock
from fastapi.testclient import TestClient
from backend.api_server import app
from backend.api.middleware.auth import verify_api_key


class TestABTestsRoutes:
    """Test cases for A/B tests routes"""
    
    @patch('backend.api.routes.ab_tests.create_ab_test')
    def test_create_ab_test_api_success(self, mock_create):
        """Test creating an A/B test via API"""
        mock_create.return_value = "test-123"
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/ab-tests",
                json={
                    "test_name": "Test AB Test",
                    "variant_a_name": "Variant A",
                    "variant_b_name": "Variant B",
                    "variant_a_config": {"model": "model-a"},
                    "variant_b_config": {"model": "model-b"},
                    "evaluation_type": "pairwise",
                    "test_cases": [{"question": "Test"}]
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["test_id"] == "test-123"
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.ab_tests.create_ab_test')
    def test_create_ab_test_api_exception(self, mock_create):
        """Test A/B test creation with exception"""
        mock_create.side_effect = Exception("Database error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/ab-tests",
                json={
                    "test_name": "Test",
                    "variant_a_name": "A",
                    "variant_b_name": "B",
                    "variant_a_config": {},
                    "variant_b_config": {},
                    "evaluation_type": "pairwise",
                    "test_cases": []
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.ab_tests.get_all_ab_tests')
    def test_list_ab_tests_api(self, mock_get_all):
        """Test listing A/B tests"""
        mock_get_all.return_value = [
            {"test_id": "t1", "test_name": "Test 1"},
            {"test_id": "t2", "test_name": "Test 2"}
        ]
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/ab-tests?limit=10",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            assert len(data["tests"]) == 2
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.ab_tests.get_all_ab_tests')
    def test_list_ab_tests_api_exception(self, mock_get_all):
        """Test listing A/B tests with exception"""
        mock_get_all.side_effect = Exception("Database error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/ab-tests",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.ab_tests.get_ab_test')
    def test_get_ab_test_api_success(self, mock_get):
        """Test getting an A/B test"""
        mock_get.return_value = {"test_id": "t1", "test_name": "Test"}
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/ab-tests/t1",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["test_id"] == "t1"
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.ab_tests.get_ab_test')
    def test_get_ab_test_api_not_found(self, mock_get):
        """Test getting non-existent A/B test"""
        mock_get.return_value = None
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/ab-tests/nonexistent",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.ab_tests.get_ab_test')
    def test_get_ab_test_api_exception(self, mock_get):
        """Test getting A/B test with exception"""
        mock_get.side_effect = Exception("Database error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/ab-tests/t1",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.ab_tests.execute_ab_test')
    @patch('backend.api.routes.ab_tests.trigger_webhook')
    def test_run_ab_test_api_success(self, mock_webhook, mock_execute):
        """Test running an A/B test successfully"""
        mock_execute.return_value = {
            "success": True,
            "summary": {
                "total_cases": 10,
                "variant_a_wins": 6,
                "variant_b_wins": 4
            }
        }
        mock_webhook.return_value = AsyncMock()
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/ab-tests/t1/run",
                json={
                    "test_id": "t1",
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.ab_tests.execute_ab_test')
    def test_run_ab_test_api_id_mismatch(self, mock_execute):
        """Test running A/B test with ID mismatch"""
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/ab-tests/t1/run",
                json={
                    "test_id": "t2",  # Mismatch
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.ab_tests.execute_ab_test')
    def test_run_ab_test_api_failure(self, mock_execute):
        """Test running A/B test that fails"""
        mock_execute.return_value = {
            "success": False,
            "error": "Test execution failed"
        }
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/ab-tests/t1/run",
                json={
                    "test_id": "t1",
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.ab_tests.execute_ab_test')
    def test_run_ab_test_api_exception(self, mock_execute):
        """Test running A/B test with exception"""
        mock_execute.side_effect = Exception("Database error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/ab-tests/t1/run",
                json={
                    "test_id": "t1",
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()

