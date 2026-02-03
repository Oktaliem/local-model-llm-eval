"""Unit tests for custom metric service"""
import pytest
import json
import sqlite3
import tempfile
import os
import importlib
from unittest.mock import Mock, patch
from backend.services.custom_metric_service import (
    create_custom_metric,
    get_custom_metric,
    get_all_custom_metrics,
    delete_custom_metric,
    evaluate_with_custom_metric
)


class TestCustomMetricService:
    """Test cases for custom metric service functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        """Set up test database for each test"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        # Create schema
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS custom_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_id TEXT UNIQUE,
                metric_name TEXT,
                metric_description TEXT,
                domain TEXT,
                evaluation_type TEXT,
                metric_definition TEXT,
                scoring_function TEXT,
                criteria_json TEXT,
                weight REAL DEFAULT 1.0,
                scale_min REAL DEFAULT 0.0,
                scale_max REAL DEFAULT 10.0,
                is_active INTEGER DEFAULT 1,
                usage_count INTEGER DEFAULT 0,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        
        monkeypatch.setenv("DB_PATH", db_path)
        # Reload module to pick up new DB_PATH
        import backend.services.custom_metric_service
        importlib.reload(backend.services.custom_metric_service)
        # Re-import functions after reload
        from backend.services.custom_metric_service import (
            create_custom_metric,
            get_custom_metric,
            get_all_custom_metrics,
            delete_custom_metric,
            evaluate_with_custom_metric
        )
        # Update module-level references
        globals()['create_custom_metric'] = create_custom_metric
        globals()['get_custom_metric'] = get_custom_metric
        globals()['get_all_custom_metrics'] = get_all_custom_metrics
        globals()['delete_custom_metric'] = delete_custom_metric
        globals()['evaluate_with_custom_metric'] = evaluate_with_custom_metric
        
        self.test_db = db_path
        yield
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_create_custom_metric_basic(self):
        """Test creating a basic custom metric"""
        metric_id = create_custom_metric(
            metric_name="Test Metric",
            evaluation_type="general",
            metric_definition="Tests something"
        )
        
        assert metric_id is not None
        assert isinstance(metric_id, str)
        assert len(metric_id) > 0
    
    def test_create_custom_metric_with_all_fields(self):
        """Test creating metric with all optional fields"""
        criteria = {"criterion1": "value1", "criterion2": "value2"}
        metric_id = create_custom_metric(
            metric_name="Full Metric",
            evaluation_type="comprehensive",
            metric_definition="Full definition",
            metric_description="A full metric",
            domain="healthcare",
            scoring_function="score = value * 2",
            criteria_json=criteria,
            weight=1.5,
            scale_min=0.0,
            scale_max=100.0,
            created_by="test_user"
        )
        
        assert metric_id is not None
        # Verify it was saved
        metric = get_custom_metric(metric_id)
        assert metric is not None
        assert metric["metric_name"] == "Full Metric"
        assert metric["metric_description"] == "A full metric"
        assert metric["domain"] == "healthcare"
        assert metric["created_by"] == "test_user"
        assert metric["weight"] == 1.5
        assert metric["scale_min"] == 0.0
        assert metric["scale_max"] == 100.0
        assert metric["criteria_json"] == criteria
    
    def test_create_custom_metric_with_none_criteria(self):
        """Test creating metric with None criteria_json"""
        metric_id = create_custom_metric(
            metric_name="No Criteria",
            evaluation_type="general",
            metric_definition="No criteria",
            criteria_json=None
        )
        
        metric = get_custom_metric(metric_id)
        assert metric is not None
        assert metric.get("criteria_json") is None
    
    def test_get_custom_metric_existing(self):
        """Test getting an existing metric"""
        metric_id = create_custom_metric(
            metric_name="Get Test",
            evaluation_type="general",
            metric_definition="Test definition"
        )
        
        metric = get_custom_metric(metric_id)
        
        assert metric is not None
        assert metric["metric_id"] == metric_id
        assert metric["metric_name"] == "Get Test"
        assert metric["evaluation_type"] == "general"
        assert metric["is_active"] is True
    
    def test_get_custom_metric_with_criteria_json(self):
        """Test getting metric with criteria_json"""
        criteria = {"key": "value"}
        metric_id = create_custom_metric(
            metric_name="Criteria Test",
            evaluation_type="general",
            metric_definition="Test",
            criteria_json=criteria
        )
        
        metric = get_custom_metric(metric_id)
        
        assert metric is not None
        assert metric["criteria_json"] == criteria
        assert isinstance(metric["criteria_json"], dict)
    
    def test_get_custom_metric_nonexistent(self):
        """Test getting a non-existent metric"""
        metric = get_custom_metric("nonexistent-id-12345")
        assert metric is None
    
    def test_get_all_custom_metrics_no_filters(self):
        """Test getting all metrics without filters"""
        create_custom_metric(
            metric_name="Metric 1",
            evaluation_type="general",
            metric_definition="Test 1"
        )
        create_custom_metric(
            metric_name="Metric 2",
            evaluation_type="comprehensive",
            metric_definition="Test 2"
        )
        
        metrics = get_all_custom_metrics()
        
        assert isinstance(metrics, list)
        assert len(metrics) >= 2
    
    def test_get_all_custom_metrics_filter_by_type(self):
        """Test filtering metrics by evaluation type"""
        create_custom_metric(
            metric_name="General Metric",
            evaluation_type="general",
            metric_definition="General"
        )
        create_custom_metric(
            metric_name="Comprehensive Metric",
            evaluation_type="comprehensive",
            metric_definition="Comprehensive"
        )
        
        general_metrics = get_all_custom_metrics(evaluation_type="general")
        comprehensive_metrics = get_all_custom_metrics(evaluation_type="comprehensive")
        
        assert all(m["evaluation_type"] == "general" for m in general_metrics)
        assert all(m["evaluation_type"] == "comprehensive" for m in comprehensive_metrics)
    
    def test_get_all_custom_metrics_filter_by_domain(self):
        """Test filtering metrics by domain"""
        create_custom_metric(
            metric_name="Healthcare Metric",
            evaluation_type="general",
            metric_definition="Healthcare",
            domain="healthcare"
        )
        create_custom_metric(
            metric_name="Finance Metric",
            evaluation_type="general",
            metric_definition="Finance",
            domain="finance"
        )
        
        healthcare_metrics = get_all_custom_metrics(domain="healthcare")
        finance_metrics = get_all_custom_metrics(domain="finance")
        
        assert all(m["domain"] == "healthcare" for m in healthcare_metrics)
        assert all(m["domain"] == "finance" for m in finance_metrics)
    
    def test_get_all_custom_metrics_filter_active(self):
        """Test filtering by active status"""
        active_id = create_custom_metric(
            metric_name="Active Metric",
            evaluation_type="general",
            metric_definition="Active"
        )
        
        inactive_id = create_custom_metric(
            metric_name="Inactive Metric",
            evaluation_type="general",
            metric_definition="Inactive"
        )
        delete_custom_metric(inactive_id)  # Soft delete
        
        active_metrics = get_all_custom_metrics(is_active=True)
        inactive_metrics = get_all_custom_metrics(is_active=False)
        
        assert all(m["is_active"] is True for m in active_metrics)
        assert all(m["is_active"] is False for m in inactive_metrics)
        assert active_id in [m["metric_id"] for m in active_metrics]
        assert inactive_id in [m["metric_id"] for m in inactive_metrics]
    
    def test_get_all_custom_metrics_with_limit(self):
        """Test limiting number of metrics returned"""
        for i in range(5):
            create_custom_metric(
                metric_name=f"Metric {i}",
                evaluation_type="general",
                metric_definition=f"Test {i}"
            )
        
        limited = get_all_custom_metrics(limit=3)
        assert len(limited) <= 3
    
    def test_get_all_custom_metrics_combined_filters(self):
        """Test combining multiple filters"""
        create_custom_metric(
            metric_name="Healthcare General",
            evaluation_type="general",
            metric_definition="Test",
            domain="healthcare"
        )
        create_custom_metric(
            metric_name="Finance General",
            evaluation_type="general",
            metric_definition="Test",
            domain="finance"
        )
        
        filtered = get_all_custom_metrics(
            evaluation_type="general",
            domain="healthcare"
        )
        
        assert all(m["evaluation_type"] == "general" for m in filtered)
        assert all(m["domain"] == "healthcare" for m in filtered)
    
    def test_get_all_custom_metrics_with_criteria_json(self):
        """Test get_all_custom_metrics parses criteria_json (line 122)"""
        criteria = {"criterion1": "value1", "criterion2": "value2"}
        metric_id = create_custom_metric(
            metric_name="Criteria Metric",
            evaluation_type="general",
            metric_definition="Test",
            criteria_json=criteria
        )
        
        metrics = get_all_custom_metrics()
        
        # Find the metric we just created
        metric = next((m for m in metrics if m["metric_id"] == metric_id), None)
        assert metric is not None
        # Verify criteria_json was parsed from JSON string
        assert metric["criteria_json"] == criteria
        assert isinstance(metric["criteria_json"], dict)
    
    def test_delete_custom_metric_success(self):
        """Test soft deleting a metric"""
        metric_id = create_custom_metric(
            metric_name="To Delete",
            evaluation_type="general",
            metric_definition="Delete me"
        )
        
        result = delete_custom_metric(metric_id)
        
        assert result is True
        # Verify it's soft deleted (still exists but inactive)
        metric = get_custom_metric(metric_id)
        assert metric is not None
        assert metric["is_active"] is False
    
    def test_delete_custom_metric_nonexistent(self):
        """Test deleting a non-existent metric"""
        result = delete_custom_metric("nonexistent-id-12345")
        assert result is False
    
    @patch('core.infrastructure.llm.ollama_client.OllamaAdapter')
    def test_evaluate_with_custom_metric_success(self, mock_ollama_adapter_class):
        """Test evaluating with custom metric successfully"""
        # Create metric
        metric_id = create_custom_metric(
            metric_name="Test Metric",
            evaluation_type="general",
            metric_definition="Test definition",
            scale_min=0.0,
            scale_max=10.0
        )
        
        # Mock OllamaAdapter
        mock_adapter = Mock()
        mock_adapter.chat.return_value = {
            "message": {"content": "Score: 8.5. This is a good response."}
        }
        mock_adapter._extract_content.return_value = "Score: 8.5. This is a good response."
        mock_ollama_adapter_class.return_value = mock_adapter
        
        result = evaluate_with_custom_metric(
            metric_id=metric_id,
            question="Test question",
            response="Test response"
        )
        
        assert result["success"] is True
        assert result["metric_id"] == metric_id
        assert "score" in result
        assert "normalized_score" in result
        assert "explanation" in result
        assert "scale" in result
        assert "execution_time" in result
        mock_adapter.chat.assert_called_once()
    
    @patch('core.infrastructure.llm.ollama_client.OllamaAdapter')
    def test_evaluate_with_custom_metric_with_reference(self, mock_ollama_adapter_class):
        """Test evaluating with reference answer"""
        metric_id = create_custom_metric(
            metric_name="Reference Metric",
            evaluation_type="general",
            metric_definition="Test"
        )
        
        mock_adapter = Mock()
        mock_adapter.chat.return_value = {"message": {"content": "Score: 9.0"}}
        mock_adapter._extract_content.return_value = "Score: 9.0"
        mock_ollama_adapter_class.return_value = mock_adapter
        
        result = evaluate_with_custom_metric(
            metric_id=metric_id,
            question="Test question",
            response="Test response",
            reference="Reference answer"
        )
        
        assert result["success"] is True
        # Verify reference was included in prompt
        call_args = mock_adapter.chat.call_args
        assert "Reference answer" in call_args[1]["messages"][1]["content"]
    
    @patch('core.infrastructure.llm.ollama_client.OllamaAdapter')
    def test_evaluate_with_custom_metric_custom_scale(self, mock_ollama_adapter_class):
        """Test evaluating with custom scale (not 0-10)"""
        metric_id = create_custom_metric(
            metric_name="Custom Scale",
            evaluation_type="general",
            metric_definition="Test",
            scale_min=0.0,
            scale_max=100.0
        )
        
        mock_adapter = Mock()
        mock_adapter.chat.return_value = {"message": {"content": "Score: 85"}}
        mock_adapter._extract_content.return_value = "Score: 85"
        mock_ollama_adapter_class.return_value = mock_adapter
        
        result = evaluate_with_custom_metric(
            metric_id=metric_id,
            question="Test",
            response="Test"
        )
        
        assert result["success"] is True
        assert result["scale"]["min"] == 0.0
        assert result["scale"]["max"] == 100.0
        assert result["score"] == 85.0
        # Should normalize to 0-10
        assert result["normalized_score"] == pytest.approx(8.5, abs=0.1)
    
    @patch('core.infrastructure.llm.ollama_client.OllamaAdapter')
    def test_evaluate_with_custom_metric_score_clamping(self, mock_ollama_adapter_class):
        """Test that score is clamped to scale bounds"""
        metric_id = create_custom_metric(
            metric_name="Clamp Test",
            evaluation_type="general",
            metric_definition="Test",
            scale_min=0.0,
            scale_max=10.0
        )
        
        mock_adapter = Mock()
        mock_adapter.chat.return_value = {"message": {"content": "Score: 999"}}
        mock_adapter._extract_content.return_value = "Score: 999"
        mock_ollama_adapter_class.return_value = mock_adapter
        
        result = evaluate_with_custom_metric(
            metric_id=metric_id,
            question="Test",
            response="Test"
        )
        
        assert result["success"] is True
        assert result["score"] <= 10.0
        assert result["score"] >= 0.0
    
    @patch('core.infrastructure.llm.ollama_client.OllamaAdapter')
    def test_evaluate_with_custom_metric_no_score_match(self, mock_ollama_adapter_class):
        """Test when no score can be extracted from response"""
        metric_id = create_custom_metric(
            metric_name="No Score",
            evaluation_type="general",
            metric_definition="Test",
            scale_min=5.0,
            scale_max=10.0
        )
        
        mock_adapter = Mock()
        mock_adapter.chat.return_value = {"message": {"content": "No score here"}}
        mock_adapter._extract_content.return_value = "No score here"
        mock_ollama_adapter_class.return_value = mock_adapter
        
        result = evaluate_with_custom_metric(
            metric_id=metric_id,
            question="Test",
            response="Test"
        )
        
        assert result["success"] is True
        # Should default to scale_min when no score found
        assert result["score"] == 5.0
    
    def test_evaluate_with_custom_metric_nonexistent(self):
        """Test evaluating with non-existent metric"""
        result = evaluate_with_custom_metric(
            metric_id="nonexistent-id",
            question="Test",
            response="Test"
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower() or "inactive" in result["error"].lower()
    
    def test_evaluate_with_custom_metric_inactive(self):
        """Test evaluating with inactive metric"""
        metric_id = create_custom_metric(
            metric_name="Inactive",
            evaluation_type="general",
            metric_definition="Test"
        )
        delete_custom_metric(metric_id)  # Soft delete
        
        result = evaluate_with_custom_metric(
            metric_id=metric_id,
            question="Test",
            response="Test"
        )
        
        assert result["success"] is False
        assert "error" in result
    
    @patch('core.infrastructure.llm.ollama_client.OllamaAdapter')
    def test_evaluate_with_custom_metric_exception(self, mock_ollama_adapter_class):
        """Test handling exception during evaluation"""
        metric_id = create_custom_metric(
            metric_name="Exception Test",
            evaluation_type="general",
            metric_definition="Test"
        )
        
        mock_adapter = Mock()
        mock_adapter.chat.side_effect = Exception("Connection error")
        mock_ollama_adapter_class.return_value = mock_adapter
        
        result = evaluate_with_custom_metric(
            metric_id=metric_id,
            question="Test",
            response="Test"
        )
        
        assert result["success"] is False
        assert "error" in result
        assert result["metric_id"] == metric_id
    
    @patch('core.infrastructure.llm.ollama_client.OllamaAdapter')
    def test_evaluate_with_custom_metric_with_criteria(self, mock_ollama_adapter_class):
        """Test evaluating with criteria_json"""
        criteria = {"criterion1": "value1", "criterion2": "value2"}
        metric_id = create_custom_metric(
            metric_name="Criteria Metric",
            evaluation_type="general",
            metric_definition="Test",
            criteria_json=criteria
        )
        
        mock_adapter = Mock()
        mock_adapter.chat.return_value = {"message": {"content": "Score: 8.0"}}
        mock_adapter._extract_content.return_value = "Score: 8.0"
        mock_ollama_adapter_class.return_value = mock_adapter
        
        result = evaluate_with_custom_metric(
            metric_id=metric_id,
            question="Test",
            response="Test"
        )
        
        assert result["success"] is True
        # Verify criteria was included in prompt
        call_args = mock_adapter.chat.call_args
        assert "CRITERIA" in call_args[1]["messages"][1]["content"]
    
    @patch('core.infrastructure.llm.ollama_client.OllamaAdapter')
    def test_evaluate_with_custom_metric_custom_judge_model(self, mock_ollama_adapter_class):
        """Test evaluating with custom judge model"""
        metric_id = create_custom_metric(
            metric_name="Custom Model",
            evaluation_type="general",
            metric_definition="Test"
        )
        
        mock_adapter = Mock()
        mock_adapter.chat.return_value = {"message": {"content": "Score: 7.5"}}
        mock_adapter._extract_content.return_value = "Score: 7.5"
        mock_ollama_adapter_class.return_value = mock_adapter
        
        result = evaluate_with_custom_metric(
            metric_id=metric_id,
            question="Test",
            response="Test",
            judge_model="mistral"
        )
        
        assert result["success"] is True
        # Verify custom model was used
        call_args = mock_adapter.chat.call_args
        assert call_args[1]["model"] == "mistral"

