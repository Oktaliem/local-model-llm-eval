"""Unit tests for webhook management routes"""
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from backend.api_server import app
from backend.api.middleware.auth import verify_api_key


class TestWebhooksRoutes:
    """Test cases for webhook routes"""
    
    @patch('backend.api.routes.webhooks.load_webhooks')
    @patch('backend.api.routes.webhooks.save_webhooks')
    def test_create_webhook(self, mock_save, mock_load):
        """Test creating a new webhook"""
        mock_load.return_value = {}
        
        # Override the dependency
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/webhooks",
                json={
                    "url": "http://example.com/webhook",
                    "events": ["evaluation.completed"],
                    "secret": "test-secret"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "webhook_id" in data
            assert data["url"] == "http://example.com/webhook"
            assert data["events"] == ["evaluation.completed"]
            assert "created_at" in data
            mock_save.assert_called_once()
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.webhooks.load_webhooks')
    def test_list_webhooks(self, mock_load):
        """Test listing webhooks"""
        mock_load.return_value = {
            "webhook1": {
                "url": "http://example.com/webhook1",
                "events": ["evaluation.completed"],
                "created_at": "2024-01-01T00:00:00"
            },
            "webhook2": {
                "url": "http://example.com/webhook2",
                "events": ["evaluation.started"],
                "created_at": "2024-01-02T00:00:00"
            }
        }
        
        # Override the dependency
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/webhooks",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_webhooks"] == 2
            assert len(data["webhooks"]) == 2
            assert all("webhook_id" in w for w in data["webhooks"])
            assert all("url" in w for w in data["webhooks"])
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.webhooks.load_webhooks')
    @patch('backend.api.routes.webhooks.save_webhooks')
    def test_delete_webhook_success(self, mock_save, mock_load):
        """Test deleting a webhook successfully"""
        mock_load.return_value = {
            "webhook1": {
                "url": "http://example.com/webhook1",
                "events": ["evaluation.completed"]
            }
        }
        
        # Override the dependency
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.delete(
                "/api/v1/webhooks/webhook1",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            mock_save.assert_called_once()
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.webhooks.load_webhooks')
    def test_delete_webhook_not_found(self, mock_load):
        """Test deleting a non-existent webhook"""
        mock_load.return_value = {}
        
        # Override the dependency
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.delete(
                "/api/v1/webhooks/nonexistent",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.clear()

