"""Unit tests for template service"""
import pytest
import json
import sqlite3
import tempfile
import os
import importlib
from backend.services.template_service import (
    create_evaluation_template,
    get_evaluation_template,
    get_all_evaluation_templates,
    delete_evaluation_template,
    apply_template_to_evaluation
)


class TestTemplateService:
    """Test cases for template service functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        """Set up test database for each test"""
        fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        # Create schema
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS evaluation_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id TEXT UNIQUE,
                template_name TEXT,
                template_description TEXT,
                industry TEXT,
                evaluation_type TEXT,
                template_config TEXT,
                is_predefined INTEGER DEFAULT 0,
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
        import backend.services.template_service
        importlib.reload(backend.services.template_service)
        # Re-import functions after reload
        from backend.services.template_service import (
            create_evaluation_template,
            get_evaluation_template,
            get_all_evaluation_templates,
            delete_evaluation_template,
            apply_template_to_evaluation
        )
        # Update module-level references
        globals()['create_evaluation_template'] = create_evaluation_template
        globals()['get_evaluation_template'] = get_evaluation_template
        globals()['get_all_evaluation_templates'] = get_all_evaluation_templates
        globals()['delete_evaluation_template'] = delete_evaluation_template
        globals()['apply_template_to_evaluation'] = apply_template_to_evaluation
        
        self.test_db = db_path
        yield
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_create_evaluation_template_basic(self):
        """Test creating a basic evaluation template"""
        template_id = create_evaluation_template(
            template_name="Test Template",
            evaluation_type="comprehensive",
            template_config={"metrics": {"accuracy": 0.4}}
        )
        
        assert template_id is not None
        assert isinstance(template_id, str)
        assert len(template_id) > 0
    
    def test_create_evaluation_template_with_all_fields(self):
        """Test creating template with all optional fields"""
        template_id = create_evaluation_template(
            template_name="Full Template",
            evaluation_type="comprehensive",
            template_config={"metrics": {"accuracy": 0.5}},
            template_description="A full template",
            industry="healthcare",
            created_by="test_user",
            is_predefined=True
        )
        
        assert template_id is not None
        # Verify it was saved
        template = get_evaluation_template(template_id)
        assert template is not None
        assert template["template_name"] == "Full Template"
        assert template["template_description"] == "A full template"
        assert template["industry"] == "healthcare"
        assert template["created_by"] == "test_user"
        assert template["is_predefined"] is True
    
    def test_get_evaluation_template_existing(self):
        """Test getting an existing template"""
        template_id = create_evaluation_template(
            template_name="Get Test",
            evaluation_type="comprehensive",
            template_config={"test": "value"}
        )
        
        template = get_evaluation_template(template_id)
        
        assert template is not None
        assert template["template_id"] == template_id
        assert template["template_name"] == "Get Test"
        assert template["evaluation_type"] == "comprehensive"
        assert template["template_config"] == {"test": "value"}
        assert template["is_predefined"] is False
    
    def test_get_evaluation_template_nonexistent(self):
        """Test getting a non-existent template"""
        template = get_evaluation_template("nonexistent-id-12345")
        assert template is None
    
    def test_get_all_evaluation_templates_no_filters(self):
        """Test getting all templates without filters"""
        # Create a few templates
        create_evaluation_template(
            template_name="Template 1",
            evaluation_type="comprehensive",
            template_config={}
        )
        create_evaluation_template(
            template_name="Template 2",
            evaluation_type="code_evaluation",
            template_config={}
        )
        
        templates = get_all_evaluation_templates()
        
        assert isinstance(templates, list)
        assert len(templates) >= 2
    
    def test_get_all_evaluation_templates_filter_by_type(self):
        """Test filtering templates by evaluation type"""
        create_evaluation_template(
            template_name="Comprehensive Template",
            evaluation_type="comprehensive",
            template_config={}
        )
        create_evaluation_template(
            template_name="Code Template",
            evaluation_type="code_evaluation",
            template_config={}
        )
        
        comprehensive_templates = get_all_evaluation_templates(evaluation_type="comprehensive")
        code_templates = get_all_evaluation_templates(evaluation_type="code_evaluation")
        
        assert all(t["evaluation_type"] == "comprehensive" for t in comprehensive_templates)
        assert all(t["evaluation_type"] == "code_evaluation" for t in code_templates)
    
    def test_get_all_evaluation_templates_filter_by_industry(self):
        """Test filtering templates by industry"""
        create_evaluation_template(
            template_name="Healthcare Template",
            evaluation_type="comprehensive",
            template_config={},
            industry="healthcare"
        )
        create_evaluation_template(
            template_name="Finance Template",
            evaluation_type="comprehensive",
            template_config={},
            industry="finance"
        )
        
        healthcare_templates = get_all_evaluation_templates(industry="healthcare")
        finance_templates = get_all_evaluation_templates(industry="finance")
        
        assert all(t["industry"] == "healthcare" for t in healthcare_templates)
        assert all(t["industry"] == "finance" for t in finance_templates)
    
    def test_get_all_evaluation_templates_exclude_predefined(self):
        """Test excluding predefined templates"""
        # Create predefined template
        predefined_id = create_evaluation_template(
            template_name="Predefined",
            evaluation_type="comprehensive",
            template_config={},
            is_predefined=True
        )
        
        # Create user template
        user_id = create_evaluation_template(
            template_name="User Template",
            evaluation_type="comprehensive",
            template_config={},
            is_predefined=False
        )
        
        user_templates = get_all_evaluation_templates(include_predefined=False)
        
        assert all(not t["is_predefined"] for t in user_templates)
        assert predefined_id not in [t["template_id"] for t in user_templates]
    
    def test_get_all_evaluation_templates_with_limit(self):
        """Test limiting number of templates returned"""
        # Create multiple templates
        for i in range(5):
            create_evaluation_template(
                template_name=f"Template {i}",
                evaluation_type="comprehensive",
                template_config={}
            )
        
        limited = get_all_evaluation_templates(limit=3)
        assert len(limited) <= 3
    
    def test_get_all_evaluation_templates_combined_filters(self):
        """Test combining multiple filters"""
        create_evaluation_template(
            template_name="Healthcare Comprehensive",
            evaluation_type="comprehensive",
            template_config={},
            industry="healthcare"
        )
        create_evaluation_template(
            template_name="Finance Comprehensive",
            evaluation_type="comprehensive",
            template_config={},
            industry="finance"
        )
        
        filtered = get_all_evaluation_templates(
            evaluation_type="comprehensive",
            industry="healthcare"
        )
        
        assert all(t["evaluation_type"] == "comprehensive" for t in filtered)
        assert all(t["industry"] == "healthcare" for t in filtered)
    
    def test_delete_evaluation_template_user_template(self):
        """Test deleting a user-created template"""
        template_id = create_evaluation_template(
            template_name="To Delete",
            evaluation_type="comprehensive",
            template_config={},
            is_predefined=False
        )
        
        result = delete_evaluation_template(template_id)
        
        assert result is True
        # Verify it's deleted
        template = get_evaluation_template(template_id)
        assert template is None
    
    def test_delete_evaluation_template_predefined(self):
        """Test that predefined templates cannot be deleted"""
        template_id = create_evaluation_template(
            template_name="Predefined",
            evaluation_type="comprehensive",
            template_config={},
            is_predefined=True
        )
        
        result = delete_evaluation_template(template_id)
        
        assert result is False
        # Verify it still exists
        template = get_evaluation_template(template_id)
        assert template is not None
    
    def test_delete_evaluation_template_nonexistent(self):
        """Test deleting a non-existent template"""
        result = delete_evaluation_template("nonexistent-id-12345")
        assert result is False
    
    def test_apply_template_to_evaluation_comprehensive(self):
        """Test applying comprehensive template to evaluation"""
        template_id = create_evaluation_template(
            template_name="Comprehensive Template",
            evaluation_type="comprehensive",
            template_config={
                "metrics": {"accuracy": 0.4, "relevance": 0.3},
                "prompt_modifiers": {"temperature": 0.2},
                "task_type": "qa"
            }
        )
        
        evaluation_data = {}
        result = apply_template_to_evaluation(template_id, evaluation_data)
        
        assert result["metric_weights"] == {"accuracy": 0.4, "relevance": 0.3}
        assert result["prompt_modifiers"] == {"temperature": 0.2}
        assert result["task_type"] == "qa"
    
    def test_apply_template_to_evaluation_comprehensive_partial_config(self):
        """Test applying comprehensive template with partial config"""
        template_id = create_evaluation_template(
            template_name="Partial Template",
            evaluation_type="comprehensive",
            template_config={
                "metrics": {"accuracy": 0.5}
            }
        )
        
        evaluation_data = {}
        result = apply_template_to_evaluation(template_id, evaluation_data)
        
        assert result["metric_weights"] == {"accuracy": 0.5}
        assert "prompt_modifiers" not in result
        assert "task_type" not in result
    
    def test_apply_template_to_evaluation_code_evaluation(self):
        """Test applying code evaluation template"""
        template_id = create_evaluation_template(
            template_name="Code Template",
            evaluation_type="code_evaluation",
            template_config={
                "quality_weights": {"maintainability": 0.5},
                "strict_mode": True
            }
        )
        
        evaluation_data = {}
        result = apply_template_to_evaluation(template_id, evaluation_data)
        
        assert result["quality_weights"] == {"maintainability": 0.5}
        assert result["strict_mode"] is True
    
    def test_apply_template_to_evaluation_code_partial_config(self):
        """Test applying code template with partial config"""
        template_id = create_evaluation_template(
            template_name="Code Partial",
            evaluation_type="code_evaluation",
            template_config={
                "quality_weights": {"readability": 0.3}
            }
        )
        
        evaluation_data = {}
        result = apply_template_to_evaluation(template_id, evaluation_data)
        
        assert result["quality_weights"] == {"readability": 0.3}
        assert "strict_mode" not in result
    
    def test_apply_template_to_evaluation_nonexistent_template(self):
        """Test applying non-existent template returns original data"""
        evaluation_data = {"original": "data"}
        result = apply_template_to_evaluation("nonexistent-id", evaluation_data)
        
        assert result == evaluation_data
    
    def test_apply_template_to_evaluation_preserves_existing_data(self):
        """Test that applying template preserves existing evaluation data"""
        template_id = create_evaluation_template(
            template_name="Preserve Test",
            evaluation_type="comprehensive",
            template_config={
                "task_type": "qa"
            }
        )
        
        evaluation_data = {
            "question": "Test question",
            "response": "Test response",
            "existing_field": "preserved"
        }
        
        result = apply_template_to_evaluation(template_id, evaluation_data)
        
        assert result["question"] == "Test question"
        assert result["response"] == "Test response"
        assert result["existing_field"] == "preserved"
        assert result["task_type"] == "qa"
    
    def test_apply_template_to_evaluation_other_type(self):
        """Test applying template with other evaluation type (not comprehensive or code)"""
        template_id = create_evaluation_template(
            template_name="Other Type",
            evaluation_type="pairwise",
            template_config={
                "some_config": "value"
            }
        )
        
        evaluation_data = {"original": "data"}
        result = apply_template_to_evaluation(template_id, evaluation_data)
        
        # Should return original data unchanged for unsupported types
        assert result == evaluation_data

