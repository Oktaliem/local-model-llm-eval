"""Unit tests for API key management routes"""
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from backend.api_server import app
from backend.api.middleware.auth import verify_api_key


class TestKeysRoutes:
    """Test cases for API key routes"""
    
    @patch('backend.api.routes.keys.load_api_keys')
    @patch('backend.api.routes.keys.save_api_keys')
    def test_create_api_key(self, mock_save, mock_load):
        """Test creating a new API key"""
        mock_load.return_value = {}
        
        client = TestClient(app)
        response = client.post(
            "/api/v1/keys?description=Test key"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert data["description"] == "Test key"
        assert "created_at" in data
        mock_save.assert_called_once()
    
    @patch('backend.api.routes.keys.load_api_keys')
    @patch('backend.api.routes.keys.save_api_keys')
    def test_create_api_key_no_description(self, mock_save, mock_load):
        """Test creating API key without description"""
        mock_load.return_value = {}
        
        client = TestClient(app)
        response = client.post("/api/v1/keys")
        
        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert data["description"] is None
    
    @patch('backend.api.routes.keys.load_api_keys')
    def test_list_api_keys(self, mock_load):
        """Test listing API keys"""
        mock_load.return_value = {
            "key1": {
                "created_at": "2024-01-01T00:00:00",
                "description": "Key 1",
                "requests_count": 10
            },
            "key2": {
                "created_at": "2024-01-02T00:00:00",
                "description": "Key 2",
                "requests_count": 5
            }
        }
        
        # Override the dependency
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/keys",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_keys"] == 2
            assert len(data["keys"]) == 2
            assert all("key_prefix" in k for k in data["keys"])
            assert all("..." in k["key_prefix"] for k in data["keys"])
        finally:
            app.dependency_overrides.clear()

