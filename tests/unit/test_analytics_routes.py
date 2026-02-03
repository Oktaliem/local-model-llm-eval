"""Unit tests for analytics API routes"""
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from backend.api_server import app
from backend.api.middleware.auth import verify_api_key


class TestAnalyticsRoutes:
    """Test cases for analytics routes"""
    
    @patch('backend.api.routes.analytics.get_all_evaluation_data')
    @patch('backend.api.routes.analytics.calculate_aggregate_statistics')
    def test_get_analytics_overview_success(self, mock_stats, mock_get_data):
        """Test successful analytics overview"""
        mock_get_data.return_value = {
            "judgments": [{"id": 1}, {"id": 2}],
            "comprehensive": [{"id": 1}],
            "code_evaluations": [{"id": 1}],
            "router_evaluations": [{"id": 1}],
            "skills_evaluations": [{"id": 1}],
            "trajectory_evaluations": [{"id": 1}],
            "human_annotations": [{"id": 1}]
        }
        mock_stats.return_value = {"mean": 8.5, "std": 1.2}
        
        # Override the dependency
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/analytics/overview",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "overview" in data
            assert "statistics" in data
            assert data["overview"]["total_evaluations"] == 5
            assert data["overview"]["comprehensive_evaluations"] == 1
            assert data["overview"]["code_evaluations"] == 1
            assert data["overview"]["router_evaluations"] == 1
            assert data["overview"]["skills_evaluations"] == 1
            assert data["overview"]["trajectory_evaluations"] == 1
            assert data["overview"]["human_annotations"] == 1
            assert data["statistics"] == {"mean": 8.5, "std": 1.2}
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.analytics.get_all_evaluation_data')
    def test_get_analytics_overview_exception(self, mock_get_data):
        """Test analytics overview with exception"""
        mock_get_data.side_effect = Exception("Database error")
        
        # Override the dependency
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/analytics/overview",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
            assert "Database error" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()

