"""Unit tests for templates API routes"""
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from backend.api_server import app
from backend.api.middleware.auth import verify_api_key


class TestTemplatesRoutes:
    """Test cases for templates routes"""
    
    @patch('backend.api.routes.templates.create_evaluation_template')
    def test_create_template_api_success(self, mock_create):
        """Test creating a template via API"""
        mock_create.return_value = "template-123"
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/templates",
                json={
                    "template_name": "Test Template",
                    "evaluation_type": "comprehensive",
                    "template_config": {"metrics": {"accuracy": 0.5}}
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["template_id"] == "template-123"
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.templates.create_evaluation_template')
    def test_create_template_api_exception(self, mock_create):
        """Test template creation with exception"""
        mock_create.side_effect = Exception("Database error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/templates",
                json={
                    "template_name": "Test",
                    "evaluation_type": "comprehensive",
                    "template_config": {}
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.templates.get_all_evaluation_templates')
    def test_list_templates_api(self, mock_get_all):
        """Test listing templates"""
        mock_get_all.return_value = [
            {"template_id": "t1", "template_name": "Template 1"},
            {"template_id": "t2", "template_name": "Template 2"}
        ]
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/templates?evaluation_type=comprehensive&limit=10",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            assert len(data["templates"]) == 2
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.templates.get_all_evaluation_templates')
    def test_list_templates_api_exception(self, mock_get_all):
        """Test listing templates with exception"""
        mock_get_all.side_effect = Exception("Database error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/templates",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.templates.get_evaluation_template')
    def test_get_template_api_success(self, mock_get):
        """Test getting a template"""
        mock_get.return_value = {"template_id": "t1", "template_name": "Test"}
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/templates/t1",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["template_id"] == "t1"
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.templates.get_evaluation_template')
    def test_get_template_api_not_found(self, mock_get):
        """Test getting non-existent template"""
        mock_get.return_value = None
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/templates/nonexistent",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.templates.get_evaluation_template')
    def test_get_template_api_exception(self, mock_get):
        """Test getting template with exception"""
        mock_get.side_effect = Exception("Database error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/templates/t1",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.templates.delete_evaluation_template')
    def test_delete_template_api_success(self, mock_delete):
        """Test deleting a template"""
        mock_delete.return_value = True
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.delete(
                "/api/v1/templates/t1",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            assert response.json()["success"] is True
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.templates.delete_evaluation_template')
    def test_delete_template_api_failure(self, mock_delete):
        """Test deleting template that cannot be deleted"""
        mock_delete.return_value = False
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.delete(
                "/api/v1/templates/t1",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.templates.delete_evaluation_template')
    def test_delete_template_api_exception(self, mock_delete):
        """Test deleting template with exception"""
        mock_delete.side_effect = Exception("Database error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.delete(
                "/api/v1/templates/t1",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.templates.apply_template_to_evaluation')
    def test_apply_template_api_success(self, mock_apply):
        """Test applying a template"""
        mock_apply.return_value = {"modified": "data"}
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/templates/t1/apply",
                json={
                    "template_id": "t1",
                    "evaluation_data": {"original": "data"}
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["template_id"] == "t1"
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.templates.apply_template_to_evaluation')
    def test_apply_template_api_id_mismatch(self, mock_apply):
        """Test applying template with ID mismatch"""
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/templates/t1/apply",
                json={
                    "template_id": "t2",  # Mismatch
                    "evaluation_data": {}
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.templates.apply_template_to_evaluation')
    def test_apply_template_api_exception(self, mock_apply):
        """Test applying template with exception"""
        mock_apply.side_effect = Exception("Database error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/templates/t1/apply",
                json={
                    "template_id": "t1",
                    "evaluation_data": {}
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()

