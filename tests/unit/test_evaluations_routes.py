"""Unit tests for evaluations API routes"""
import pytest
from unittest.mock import patch, Mock, AsyncMock
from fastapi.testclient import TestClient
from backend.api_server import app
from backend.api.middleware.auth import verify_api_key


class TestEvaluationsRoutes:
    """Test cases for evaluations routes"""
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    @patch('backend.api.routes.evaluations.trigger_webhook')
    def test_evaluate_comprehensive_api_success(self, mock_webhook, mock_service):
        """Test comprehensive evaluation via API"""
        mock_service.evaluate.return_value = {
            "success": True,
            "evaluation_id": "eval-123",
            "scores": {"overall_score": 8.5, "accuracy": 9.0},
            "judgment": "Good response"
        }
        mock_webhook.return_value = AsyncMock()
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/comprehensive",
                json={
                    "question": "Test question",
                    "response": "Test response",
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["evaluation_id"] == "eval-123"
            assert data["overall_score"] == 8.5
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    def test_evaluate_comprehensive_api_failure(self, mock_service):
        """Test comprehensive evaluation that fails"""
        mock_service.evaluate.return_value = {
            "success": False,
            "error": "Evaluation failed"
        }
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/comprehensive",
                json={
                    "question": "Test",
                    "response": "Test",
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    def test_evaluate_comprehensive_api_exception(self, mock_service):
        """Test comprehensive evaluation with exception"""
        mock_service.evaluate.side_effect = Exception("Database error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/comprehensive",
                json={
                    "question": "Test",
                    "response": "Test",
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    def test_evaluate_code_api_success(self, mock_service):
        """Test code evaluation via API"""
        mock_service.evaluate.return_value = {
            "success": True,
            "evaluation_id": "eval-123",
            "scores": {"overall_score": 9.0},
            "judgment": "Code is correct"
        }
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/code",
                json={
                    "code": "def func(): return 42",
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    def test_evaluate_code_api_failure(self, mock_service):
        """Test code evaluation that fails"""
        mock_service.evaluate.return_value = {"success": False, "error": "Failed"}
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/code",
                json={"code": "def func(): pass", "judge_model": "llama3"},
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    def test_evaluate_code_api_exception(self, mock_service):
        """Test code evaluation with exception"""
        mock_service.evaluate.side_effect = Exception("Error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/code",
                json={"code": "def func(): pass", "judge_model": "llama3"},
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    def test_evaluate_router_api_success(self, mock_service):
        """Test router evaluation via API"""
        mock_service.evaluate.return_value = {
            "success": True,
            "evaluation_id": "eval-123",
            "scores": {
                "tool_accuracy_score": 8.5,
                "routing_quality_score": 9.0,
                "reasoning_score": 8.0,
                "overall_score": 8.5
            },
            "judgment": "Good routing"
        }
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/router",
                json={
                    "query": "Test query",
                    "available_tools": [{"name": "tool1"}],
                    "selected_tool": "tool1",
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["overall_score"] == 8.5
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    def test_evaluate_router_api_failure(self, mock_service):
        """Test router evaluation that fails"""
        mock_service.evaluate.return_value = {"success": False, "error": "Failed"}
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/router",
                json={
                    "query": "Test",
                    "available_tools": [],
                    "selected_tool": "tool1",
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    def test_evaluate_router_api_exception(self, mock_service):
        """Test router evaluation with exception"""
        mock_service.evaluate.side_effect = Exception("Error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/router",
                json={
                    "query": "Test",
                    "available_tools": [],
                    "selected_tool": "tool1",
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    def test_evaluate_skills_api_success(self, mock_service):
        """Test skills evaluation via API"""
        mock_service.evaluate.return_value = {
            "success": True,
            "evaluation_id": "eval-123",
            "scores": {
                "correctness_score": 9.0,
                "completeness_score": 8.5,
                "clarity_score": 8.0,
                "proficiency_score": 9.0,
                "overall_score": 8.625
            },
            "judgment": "Good skills"
        }
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/skills",
                json={
                    "question": "Test question",
                    "response": "Test response",
                    "skill_type": "mathematics",
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["overall_score"] == 8.625
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    def test_evaluate_skills_api_failure(self, mock_service):
        """Test skills evaluation that fails"""
        mock_service.evaluate.return_value = {"success": False, "error": "Failed"}
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/skills",
                json={
                    "question": "Test",
                    "response": "Test",
                    "skill_type": "math",
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    def test_evaluate_skills_api_exception(self, mock_service):
        """Test skills evaluation with exception"""
        mock_service.evaluate.side_effect = Exception("Error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/skills",
                json={
                    "question": "Test",
                    "response": "Test",
                    "skill_type": "math",
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    def test_evaluate_trajectory_api_success(self, mock_service):
        """Test trajectory evaluation via API"""
        mock_service.evaluate.return_value = {
            "success": True,
            "evaluation_id": "eval-123",
            "scores": {
                "step_quality_score": 8.0,
                "path_efficiency_score": 9.0,
                "reasoning_chain_score": 8.5,
                "planning_quality_score": 9.0,
                "overall_score": 8.625
            },
            "judgment": "Good trajectory"
        }
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/trajectory",
                json={
                    "task_description": "Test task",
                    "trajectory": [{"step": "1", "action": "test"}],
                    "judge_model": "llama3",
                    "trajectory_type": "planning"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["overall_score"] == 8.625
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    def test_evaluate_trajectory_api_failure(self, mock_service):
        """Test trajectory evaluation that fails"""
        mock_service.evaluate.return_value = {"success": False, "error": "Failed"}
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/trajectory",
                json={
                    "task_description": "Test",
                    "trajectory": [],
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    def test_evaluate_trajectory_api_exception(self, mock_service):
        """Test trajectory evaluation with exception"""
        mock_service.evaluate.side_effect = Exception("Error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/trajectory",
                json={
                    "task_description": "Test",
                    "trajectory": [],
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    @patch('backend.api.routes.evaluations.trigger_webhook')
    def test_evaluate_pairwise_api_success(self, mock_webhook, mock_service):
        """Test pairwise evaluation via API"""
        mock_service.evaluate.return_value = {
            "success": True,
            "evaluation_id": "eval-123",
            "winner": "A",
            "judgment": "A is better"
        }
        mock_webhook.return_value = AsyncMock()
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/pairwise",
                json={
                    "question": "Test question",
                    "response_a": "Response A",
                    "response_b": "Response B",
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    def test_evaluate_pairwise_api_failure(self, mock_service):
        """Test pairwise evaluation that fails"""
        mock_service.evaluate.return_value = {"success": False, "error": "Failed"}
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/pairwise",
                json={
                    "question": "Test",
                    "response_a": "A",
                    "response_b": "B",
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    def test_evaluate_pairwise_api_exception(self, mock_service):
        """Test pairwise evaluation with exception"""
        mock_service.evaluate.side_effect = Exception("Error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/pairwise",
                json={
                    "question": "Test",
                    "response_a": "A",
                    "response_b": "B",
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.get_all_judgments')
    def test_get_evaluations_comprehensive(self, mock_get):
        """Test getting comprehensive evaluations"""
        mock_get.return_value = [
            {"id": 1, "judgment_type": "comprehensive"},
            {"id": 2, "judgment_type": "batch_comprehensive"}
        ]
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/evaluations?evaluation_type=comprehensive",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.get_router_evaluations')
    def test_get_evaluations_router(self, mock_get):
        """Test getting router evaluations"""
        mock_get.return_value = [{"id": 1, "query": "Test"}]
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/evaluations?evaluation_type=router",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.get_skills_evaluations')
    def test_get_evaluations_skills(self, mock_get):
        """Test getting skills evaluations"""
        mock_get.return_value = [{"id": 1, "skill_type": "math"}]
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/evaluations?evaluation_type=skills",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.get_trajectory_evaluations')
    def test_get_evaluations_trajectory(self, mock_get):
        """Test getting trajectory evaluations"""
        mock_get.return_value = [{"id": 1, "task_description": "Test"}]
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/evaluations?evaluation_type=trajectory",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.get_all_judgments')
    def test_get_evaluations_default(self, mock_get):
        """Test getting evaluations with no type filter"""
        mock_get.return_value = [{"id": 1}, {"id": 2}]
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/evaluations",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.get_all_judgments')
    def test_get_evaluations_exception(self, mock_get):
        """Test getting evaluations with exception"""
        mock_get.side_effect = Exception("Database error")
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.get(
                "/api/v1/evaluations",
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 500
        finally:
            app.dependency_overrides.clear()
    
    @patch('backend.api.routes.evaluations.evaluation_service')
    def test_evaluate_trajectory_api_with_none_scores(self, mock_service):
        """Test trajectory evaluation with None scores (line 194)"""
        mock_service.evaluate.return_value = {
            "success": True,
            "evaluation_id": "eval-123",
            "scores": None,  # This will trigger the .get() with None
            "judgment": "Test"
        }
        
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/evaluations/trajectory",
                json={
                    "task_description": "Test",
                    "trajectory": [],
                    "judge_model": "llama3"
                },
                headers={"Authorization": "Bearer test-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["overall_score"] == 0  # Should default to 0 when scores is None
        finally:
            app.dependency_overrides.clear()

