"""Unit tests for custom metrics API routes"""
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from backend.api_server import app
from backend.api.middleware.auth import verify_api_key


class TestCustomMetricsRoutes:
    """Test cases for custom metrics routes"""
    
    @patch('backend.api.routes.custom_metrics.create_custom_metric')
    def test_create_custom_metric_api_success(self, mock_create):
        """Test creating a custom metric via API"""
        mock_create.return_value = "metric-123"
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/custom-metrics",
                json={
                    "metric_name": "Test Metric",
                    "evaluation_type": "general",
                    "metric_definition": "Test definition",
                    "scale_min": 0.0,
                    "scale_max": 10.0
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["metric_id"] == "metric-123"
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.custom_metrics.create_custom_metric')
    def test_create_custom_metric_api_exception(self, mock_create):
        """Test custom metric creation with exception"""
        mock_create.side_effect = Exception("Database error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/custom-metrics",
                json={
                    "metric_name": "Test",
                    "evaluation_type": "general",
                    "metric_definition": "Test"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.custom_metrics.get_all_custom_metrics')
    def test_list_custom_metrics_api(self, mock_get_all):
        """Test listing custom metrics"""
        mock_get_all.return_value = [
            {"metric_id": "m1", "metric_name": "Metric 1"},
            {"metric_id": "m2", "metric_name": "Metric 2"}
        ]
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/custom-metrics?evaluation_type=general&limit=10",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            assert len(data["metrics"]) == 2
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.custom_metrics.get_all_custom_metrics')
    def test_list_custom_metrics_api_exception(self, mock_get_all):
        """Test listing custom metrics with exception"""
        mock_get_all.side_effect = Exception("Database error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/custom-metrics",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.custom_metrics.get_custom_metric')
    def test_get_custom_metric_api_success(self, mock_get):
        """Test getting a custom metric"""
        mock_get.return_value = {"metric_id": "m1", "metric_name": "Test"}
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/custom-metrics/m1",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["metric_id"] == "m1"
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.custom_metrics.get_custom_metric')
    def test_get_custom_metric_api_not_found(self, mock_get):
        """Test getting non-existent metric"""
        mock_get.return_value = None
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/custom-metrics/nonexistent",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.custom_metrics.get_custom_metric')
    def test_get_custom_metric_api_exception(self, mock_get):
        """Test getting metric with exception"""
        mock_get.side_effect = Exception("Database error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/custom-metrics/m1",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.custom_metrics.delete_custom_metric')
    def test_delete_custom_metric_api_success(self, mock_delete):
        """Test deleting a custom metric"""
        mock_delete.return_value = True
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.delete(
                "/api/v1/custom-metrics/m1",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            assert response.json()["success"] is True
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.custom_metrics.delete_custom_metric')
    def test_delete_custom_metric_api_not_found(self, mock_delete):
        """Test deleting non-existent metric"""
        mock_delete.return_value = False
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.delete(
                "/api/v1/custom-metrics/nonexistent",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.custom_metrics.delete_custom_metric')
    def test_delete_custom_metric_api_exception(self, mock_delete):
        """Test deleting metric with exception"""
        mock_delete.side_effect = Exception("Database error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.delete(
                "/api/v1/custom-metrics/m1",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.custom_metrics.evaluate_with_custom_metric')
    def test_evaluate_with_metric_api_success(self, mock_evaluate):
        """Test evaluating with custom metric"""
        mock_evaluate.return_value = {
            "success": True,
            "score": 8.5,
            "explanation": "Good response"
        }
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/custom-metrics/m1/evaluate",
                json={
                    "metric_id": "m1",
                    "question": "Test question",
                    "response": "Test response"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["score"] == 8.5
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.custom_metrics.evaluate_with_custom_metric')
    def test_evaluate_with_metric_api_id_mismatch(self, mock_evaluate):
        """Test evaluating with metric ID mismatch"""
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/custom-metrics/m1/evaluate",
                json={
                    "metric_id": "m2",  # Mismatch
                    "question": "Test",
                    "response": "Test"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.custom_metrics.evaluate_with_custom_metric')
    def test_evaluate_with_metric_api_failure(self, mock_evaluate):
        """Test evaluating with metric that fails"""
        mock_evaluate.return_value = {
            "success": False,
            "error": "Metric not found"
        }
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/custom-metrics/m1/evaluate",
                json={
                    "metric_id": "m1",
                    "question": "Test",
                    "response": "Test"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.custom_metrics.evaluate_with_custom_metric')
    def test_evaluate_with_metric_api_exception(self, mock_evaluate):
        """Test evaluating with metric with exception"""
        mock_evaluate.side_effect = Exception("Database error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/custom-metrics/m1/evaluate",
                json={
                    "metric_id": "m1",
                    "question": "Test",
                    "response": "Test"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()

