"""
Unit tests for backend.services.data_service
"""
import pytest
import sqlite3
import json
import os
import tempfile
import importlib
from unittest.mock import patch, MagicMock


def _create_test_db():
    """Create a temporary test database with schema."""
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create all necessary tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS judgments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluation_id TEXT,
            question TEXT,
            response_a TEXT,
            response_b TEXT,
            model_a TEXT,
            model_b TEXT,
            judge_model TEXT,
            judgment TEXT,
            judgment_type TEXT,
            metrics_json TEXT,
            trace_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS router_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluation_id TEXT,
            query TEXT,
            context TEXT,
            available_tools_json TEXT,
            selected_tool TEXT,
            expected_tool TEXT,
            routing_strategy TEXT,
            tool_accuracy_score REAL,
            routing_quality_score REAL,
            reasoning_score REAL,
            overall_score REAL,
            judgment_text TEXT,
            metrics_json TEXT,
            routing_path_json TEXT,
            trace_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS skills_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluation_id TEXT,
            skill_type TEXT,
            question TEXT,
            response TEXT,
            reference_answer TEXT,
            domain TEXT,
            skill_metrics_json TEXT,
            proficiency_score REAL,
            correctness_score REAL,
            completeness_score REAL,
            clarity_score REAL,
            overall_score REAL,
            judgment_text TEXT,
            trace_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS trajectory_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluation_id TEXT,
            task_description TEXT,
            trajectory_json TEXT,
            expected_trajectory_json TEXT,
            trajectory_type TEXT,
            step_quality_score REAL,
            path_efficiency_score REAL,
            reasoning_chain_score REAL,
            planning_quality_score REAL,
            overall_score REAL,
            judgment_text TEXT,
            metrics_json TEXT,
            trace_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS human_annotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            annotation_id TEXT UNIQUE,
            judgment_id INTEGER,
            evaluation_id TEXT,
            annotator_name TEXT,
            annotator_email TEXT,
            question TEXT,
            response TEXT,
            response_a TEXT,
            response_b TEXT,
            evaluation_type TEXT,
            accuracy_score REAL,
            relevance_score REAL,
            coherence_score REAL,
            hallucination_score REAL,
            toxicity_score REAL,
            overall_score REAL,
            feedback_text TEXT,
            ratings_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS evaluation_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT UNIQUE,
            run_name TEXT,
            dataset_name TEXT,
            total_cases INTEGER,
            completed_cases INTEGER DEFAULT 0,
            status TEXT,
            results_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    return db_path


class TestDataService:
    """Test suite for data_service functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        """Set up test database for each test"""
        self.test_db = _create_test_db()
        monkeypatch.setenv("DB_PATH", self.test_db)
        # Reload module to pick up new DB_PATH
        import backend.services.data_service
        importlib.reload(backend.services.data_service)
        # Import functions after reload
        from backend.services.data_service import (
            get_all_judgments,
            delete_judgment,
            save_judgment,
            get_router_evaluations,
            save_router_evaluation,
            get_skills_evaluations,
            save_skills_evaluation,
            get_trajectory_evaluations,
            save_trajectory_evaluation,
            get_human_annotations,
            save_human_annotation,
            get_annotations_for_comparison,
            calculate_agreement_metrics,
            save_evaluation_run,
            update_evaluation_run,
            get_evaluation_run,
            get_all_evaluation_data
        )
        # Store in self for use in tests
        self.get_all_judgments = get_all_judgments
        self.delete_judgment = delete_judgment
        self.save_judgment = save_judgment
        self.get_router_evaluations = get_router_evaluations
        self.save_router_evaluation = save_router_evaluation
        self.get_skills_evaluations = get_skills_evaluations
        self.save_skills_evaluation = save_skills_evaluation
        self.get_trajectory_evaluations = get_trajectory_evaluations
        self.save_trajectory_evaluation = save_trajectory_evaluation
        self.get_human_annotations = get_human_annotations
        self.save_human_annotation = save_human_annotation
        self.get_annotations_for_comparison = get_annotations_for_comparison
        self.calculate_agreement_metrics = calculate_agreement_metrics
        self.save_evaluation_run = save_evaluation_run
        self.update_evaluation_run = update_evaluation_run
        self.get_evaluation_run = get_evaluation_run
        self.get_all_evaluation_data = get_all_evaluation_data
        yield
        # Cleanup
        if os.path.exists(self.test_db):
            os.unlink(self.test_db)
    
    def test_get_all_judgments_empty(self):
        """Test getting all judgments when database is empty"""
        result = self.get_all_judgments()
        assert result == []
    
    def test_save_judgment(self):
        """Test saving a judgment"""
        judgment_id = self.save_judgment(
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            model_a="Model A",
            model_b="Model B",
            judge_model="llama3",
            judgment="A is better",
            judgment_type="pairwise",
            evaluation_id="eval-123",
            metrics_json='{"score_a": 8.5}',
            trace_json='{"steps": []}'
        )
        
        assert judgment_id > 0
        
        judgments = self.get_all_judgments()
        assert len(judgments) == 1
        assert judgments[0]["question"] == "Test question"
        assert judgments[0]["judgment"] == "A is better"
        assert judgments[0]["evaluation_id"] == "eval-123"
    
    def test_delete_judgment(self):
        """Test deleting a judgment"""
        judgment_id = self.save_judgment(
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            model_a="Model A",
            model_b="Model B",
            judge_model="llama3",
            judgment="A is better",
            judgment_type="pairwise"
        )
        
        assert len(self.get_all_judgments()) == 1
        
        self.delete_judgment(judgment_id)
        
        assert len(self.get_all_judgments()) == 0
    
    def test_save_router_evaluation(self):
        """Test saving a router evaluation"""
        eval_id = self.save_router_evaluation(
            query="Test query",
            available_tools=[{"name": "tool1"}, {"name": "tool2"}],
            selected_tool="tool1",
            tool_accuracy_score=8.5,
            routing_quality_score=9.0,
            reasoning_score=8.0,
            overall_score=8.5,
            judgment_text="Good routing",
            metrics_json='{"accuracy": 8.5}',
            trace_json='{"steps": []}',
            evaluation_id="router-123"
        )
        
        assert eval_id > 0
        
        evaluations = self.get_router_evaluations()
        assert len(evaluations) == 1
        assert evaluations[0]["query"] == "Test query"
        assert evaluations[0]["selected_tool"] == "tool1"
        assert evaluations[0]["overall_score"] == 8.5
    
    def test_save_skills_evaluation(self):
        """Test saving a skills evaluation"""
        eval_id = self.save_skills_evaluation(
            skill_type="mathematics",
            question="What is 2+2?",
            response="4",
            correctness_score=10.0,
            completeness_score=9.0,
            clarity_score=8.5,
            proficiency_score=9.5,
            overall_score=9.25,
            judgment_text="Correct answer",
            skill_metrics_json='{"correctness": 10.0}',
            trace_json='{"steps": []}',
            evaluation_id="skills-123",
            domain="math"
        )
        
        assert eval_id > 0
        
        evaluations = self.get_skills_evaluations()
        assert len(evaluations) == 1
        assert evaluations[0]["skill_type"] == "mathematics"
        assert evaluations[0]["overall_score"] == 9.25
    
    def test_save_trajectory_evaluation(self):
        """Test saving a trajectory evaluation"""
        eval_id = self.save_trajectory_evaluation(
            task_description="Test task",
            trajectory=[{"step": 1, "action": "start"}],
            step_quality_score=8.0,
            path_efficiency_score=9.0,
            reasoning_chain_score=8.5,
            planning_quality_score=9.0,
            overall_score=8.625,
            judgment_text="Good trajectory",
            metrics_json='{"step_quality": 8.0}',
            trace_json='{"steps": []}',
            evaluation_id="traj-123",
            trajectory_type="planning"
        )
        
        assert eval_id > 0
        
        evaluations = self.get_trajectory_evaluations()
        assert len(evaluations) == 1
        assert evaluations[0]["task_description"] == "Test task"
        assert evaluations[0]["overall_score"] == 8.625
    
    def test_save_human_annotation(self):
        """Test saving a human annotation"""
        annotation_id = self.save_human_annotation(
            annotator_name="Test User",
            question="Test question",
            evaluation_type="comprehensive",
            accuracy_score=8.5,
            relevance_score=9.0,
            coherence_score=8.0,
            overall_score=8.5,
            response="Test response",
            annotator_email="test@example.com"
        )
        
        assert annotation_id > 0
        
        annotations = self.get_human_annotations()
        assert len(annotations) == 1
        assert annotations[0]["annotator_name"] == "Test User"
        assert annotations[0]["overall_score"] == 8.5
    
    def test_get_human_annotations_by_judgment_id(self):
        """Test getting human annotations filtered by judgment_id"""
        judgment_id = self.save_judgment(
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            model_a="Model A",
            model_b="Model B",
            judge_model="llama3",
            judgment="A is better",
            judgment_type="pairwise"
        )
        
        self.save_human_annotation(
            annotator_name="User 1",
            question="Test question",
            evaluation_type="pairwise",
            overall_score=8.5,
            judgment_id=judgment_id
        )
        
        self.save_human_annotation(
            annotator_name="User 2",
            question="Other question",
            evaluation_type="pairwise",
            overall_score=7.5
        )
        
        annotations = self.get_human_annotations(judgment_id=judgment_id)
        assert len(annotations) == 1
        assert annotations[0]["annotator_name"] == "User 1"
    
    def test_get_annotations_for_comparison(self):
        """Test getting annotations for comparison"""
        judgment_id = self.save_judgment(
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            model_a="Model A",
            model_b="Model B",
            judge_model="llama3",
            judgment="A is better",
            judgment_type="pairwise"
        )
        
        self.save_human_annotation(
            annotator_name="User 1",
            question="Test question",
            evaluation_type="pairwise",
            overall_score=8.5,
            judgment_id=judgment_id
        )
        
        result = self.get_annotations_for_comparison(judgment_id=judgment_id)
        assert "human_annotations" in result
        assert "llm_judgments" in result
        assert len(result["human_annotations"]) == 1
        assert len(result["llm_judgments"]) == 1
    
    def test_calculate_agreement_metrics_single_annotation(self):
        """Test calculating agreement metrics with single annotation"""
        annotations = [{
            "accuracy_score": 8.5,
            "relevance_score": 9.0,
            "overall_score": 8.75
        }]
        
        result = self.calculate_agreement_metrics(annotations)
        assert result["num_annotators"] == 1
        assert result["agreement_available"] == False
        assert "message" in result
    
    def test_calculate_agreement_metrics_multiple_annotations(self):
        """Test calculating agreement metrics with multiple annotations"""
        annotations = [
            {"accuracy_score": 8.5, "relevance_score": 9.0, "overall_score": 8.75},
            {"accuracy_score": 8.0, "relevance_score": 8.5, "overall_score": 8.25},
            {"accuracy_score": 9.0, "relevance_score": 9.5, "overall_score": 9.25}
        ]
        
        result = self.calculate_agreement_metrics(annotations)
        assert result["num_annotators"] == 3
        assert result["agreement_available"] == True
        assert "metrics" in result
        assert "accuracy_score" in result["metrics"]
        assert "mean" in result["metrics"]["accuracy_score"]
        assert "std_dev" in result["metrics"]["accuracy_score"]
    
    def test_save_evaluation_run(self):
        """Test saving an evaluation run"""
        run_id = "test-run-123"
        db_id = self.save_evaluation_run(
            run_id=run_id,
            run_name="Test Run",
            dataset_name="test_dataset",
            total_cases=100,
            status="running"
        )
        
        assert db_id > 0
        
        run = self.get_evaluation_run(run_id)
        assert run is not None
        assert run["run_name"] == "Test Run"
        assert run["total_cases"] == 100
        assert run["status"] == "running"
    
    def test_update_evaluation_run(self):
        """Test updating an evaluation run"""
        run_id = "test-run-123"
        self.save_evaluation_run(
            run_id=run_id,
            run_name="Test Run",
            dataset_name="test_dataset",
            total_cases=100,
            status="running"
        )
        
        self.update_evaluation_run(
            run_id=run_id,
            completed_cases=50,
            status="running"
        )
        
        run = self.get_evaluation_run(run_id)
        assert run["completed_cases"] == 50
        
        self.update_evaluation_run(
            run_id=run_id,
            completed_cases=100,
            status="completed",
            results_json='{"total": 100, "successful": 95}'
        )
        
        run = self.get_evaluation_run(run_id)
        assert run["status"] == "completed"
        assert run["completed_cases"] == 100
        assert run["results_json"]["total"] == 100
    
    def test_get_evaluation_run_nonexistent(self):
        """Test getting a non-existent evaluation run"""
        run = self.get_evaluation_run("nonexistent-run")
        assert run is None
    
    def test_get_human_annotations_by_evaluation_id(self):
        """Test getting human annotations filtered by evaluation_id"""
        eval_id = "eval-123"
        self.save_human_annotation(
            annotator_name="User 1",
            question="Test question",
            evaluation_type="comprehensive",
            overall_score=8.5,
            evaluation_id=eval_id
        )
        
        self.save_human_annotation(
            annotator_name="User 2",
            question="Other question",
            evaluation_type="comprehensive",
            overall_score=7.5,
            evaluation_id="other-eval"
        )
        
        annotations = self.get_human_annotations(evaluation_id=eval_id)
        assert len(annotations) == 1
        assert annotations[0]["annotator_name"] == "User 1"
        assert annotations[0]["evaluation_id"] == eval_id
    
    def test_get_annotations_for_comparison_by_evaluation_id(self):
        """Test getting annotations for comparison by evaluation_id"""
        eval_id = "eval-123"
        self.save_judgment(
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            model_a="Model A",
            model_b="Model B",
            judge_model="llama3",
            judgment="A is better",
            judgment_type="pairwise",
            evaluation_id=eval_id
        )
        
        self.save_human_annotation(
            annotator_name="User 1",
            question="Test question",
            evaluation_type="pairwise",
            overall_score=8.5,
            evaluation_id=eval_id
        )
        
        result = self.get_annotations_for_comparison(evaluation_id=eval_id)
        assert "human_annotations" in result
        assert "llm_judgments" in result
        assert len(result["human_annotations"]) == 1
        assert len(result["llm_judgments"]) == 1
        assert result["llm_judgments"][0]["evaluation_id"] == eval_id
    
    def test_get_skills_evaluations_with_filter(self):
        """Test getting skills evaluations filtered by skill_type"""
        self.save_skills_evaluation(
            skill_type="mathematics",
            question="Math question",
            response="4",
            correctness_score=10.0,
            completeness_score=9.0,
            clarity_score=8.5,
            proficiency_score=9.5,
            overall_score=9.25,
            judgment_text="Correct",
            skill_metrics_json='{}',
            trace_json='{}',
            evaluation_id="math-123"
        )
        
        self.save_skills_evaluation(
            skill_type="coding",
            question="Code question",
            response="def func(): pass",
            correctness_score=8.0,
            completeness_score=7.0,
            clarity_score=8.0,
            proficiency_score=7.5,
            overall_score=7.625,
            judgment_text="Good code",
            skill_metrics_json='{}',
            trace_json='{}',
            evaluation_id="code-123"
        )
        
        math_evals = self.get_skills_evaluations(skill_type="mathematics")
        coding_evals = self.get_skills_evaluations(skill_type="coding")
        
        assert all(e["skill_type"] == "mathematics" for e in math_evals)
        assert all(e["skill_type"] == "coding" for e in coding_evals)
    
    def test_get_trajectory_evaluations_with_filter(self):
        """Test getting trajectory evaluations filtered by trajectory_type"""
        self.save_trajectory_evaluation(
            task_description="Planning task",
            trajectory=[{"step": 1}],
            step_quality_score=8.0,
            path_efficiency_score=9.0,
            reasoning_chain_score=8.5,
            planning_quality_score=9.0,
            overall_score=8.625,
            judgment_text="Good planning",
            metrics_json='{}',
            trace_json='{}',
            evaluation_id="plan-123",
            trajectory_type="planning"
        )
        
        self.save_trajectory_evaluation(
            task_description="Execution task",
            trajectory=[{"step": 1}],
            step_quality_score=7.0,
            path_efficiency_score=8.0,
            reasoning_chain_score=7.5,
            planning_quality_score=8.0,
            overall_score=7.625,
            judgment_text="Good execution",
            metrics_json='{}',
            trace_json='{}',
            evaluation_id="exec-123",
            trajectory_type="execution"
        )
        
        planning_evals = self.get_trajectory_evaluations(trajectory_type="planning")
        execution_evals = self.get_trajectory_evaluations(trajectory_type="execution")
        
        assert all(e["trajectory_type"] == "planning" for e in planning_evals)
        assert all(e["trajectory_type"] == "execution" for e in execution_evals)
    
    def test_get_all_evaluation_data(self):
        """Test getting all evaluation data"""
        # Create some test data
        self.save_judgment(
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            model_a="Model A",
            model_b="Model B",
            judge_model="llama3",
            judgment="A is better",
            judgment_type="comprehensive",
            metrics_json='{"overall_score": 8.5, "accuracy": {"score": 8.0}}'
        )
        
        self.save_judgment(
            question="Code question",
            response_a="def func(): pass",
            response_b="def func(): return None",
            model_a="Model A",
            model_b="Model B",
            judge_model="llama3",
            judgment="B is better",
            judgment_type="code_evaluation",
            metrics_json='{"overall_score": 7.5, "syntax": {"valid": true}, "execution": {"success": true}, "quality": {"maintainability": 8.0, "readability": 7.0}}'
        )
        
        self.save_router_evaluation(
            query="Test query",
            available_tools=[],
            selected_tool="tool1",
            tool_accuracy_score=8.5,
            routing_quality_score=9.0,
            reasoning_score=8.0,
            overall_score=8.5,
            judgment_text="Good",
            metrics_json='{}',
            trace_json='{}',
            evaluation_id="router-123"
        )
        
        self.save_skills_evaluation(
            skill_type="mathematics",
            question="Math question",
            response="4",
            correctness_score=10.0,
            completeness_score=9.0,
            clarity_score=8.5,
            proficiency_score=9.5,
            overall_score=9.25,
            judgment_text="Correct",
            skill_metrics_json='{}',
            trace_json='{}',
            evaluation_id="skills-123",
            domain="math"
        )
        
        self.save_trajectory_evaluation(
            task_description="Test task",
            trajectory=[{"step": 1}],
            step_quality_score=8.0,
            path_efficiency_score=9.0,
            reasoning_chain_score=8.5,
            planning_quality_score=9.0,
            overall_score=8.625,
            judgment_text="Good",
            metrics_json='{}',
            trace_json='{}',
            evaluation_id="traj-123",
            trajectory_type="planning"
        )
        
        self.save_human_annotation(
            annotator_name="Test User",
            question="Test question",
            evaluation_type="comprehensive",
            accuracy_score=8.5,
            relevance_score=9.0,
            coherence_score=8.0,
            overall_score=8.5
        )
        
        data = self.get_all_evaluation_data(limit=100)
        assert "judgments" in data
        assert "comprehensive" in data
        assert "code_evaluations" in data
        assert "router_evaluations" in data
        assert "skills_evaluations" in data
        assert "trajectory_evaluations" in data
        assert "human_annotations" in data
        assert len(data["judgments"]) > 0
        assert len(data["comprehensive"]) > 0
        assert len(data["code_evaluations"]) > 0
        assert len(data["router_evaluations"]) > 0
        assert len(data["skills_evaluations"]) > 0
        assert len(data["trajectory_evaluations"]) > 0
        assert len(data["human_annotations"]) > 0
    
    def test_save_human_annotation_calculates_overall_score(self):
        """Test that overall_score is calculated when not provided"""
        annotation_id = self.save_human_annotation(
            annotator_name="Test User",
            question="Test question",
            evaluation_type="comprehensive",
            accuracy_score=8.0,
            relevance_score=9.0,
            coherence_score=8.5,
            # overall_score not provided - should be calculated
            hallucination_score=2.0,  # Lower is better, so will be inverted
            toxicity_score=1.0  # Lower is better, so will be inverted
        )
        
        annotations = self.get_human_annotations()
        assert len(annotations) == 1
        assert annotations[0]["overall_score"] is not None
        # Should be average of: 8.0, 9.0, 8.5, (10-2), (10-1) = 8.0, 9.0, 8.5, 8.0, 9.0
        # Average = 42.5 / 5 = 8.5
        assert annotations[0]["overall_score"] == pytest.approx(8.5, abs=0.1)
    
    def test_save_human_annotation_overall_score_with_only_some_scores(self):
        """Test overall_score calculation with only some scores provided"""
        annotation_id = self.save_human_annotation(
            annotator_name="Test User",
            question="Test question",
            evaluation_type="comprehensive",
            accuracy_score=8.0,
            relevance_score=9.0,
            # coherence_score not provided
            # hallucination_score not provided
            # toxicity_score not provided
            # overall_score not provided - should be calculated from available scores
        )
        
        annotations = self.get_human_annotations()
        assert len(annotations) == 1
        assert annotations[0]["overall_score"] is not None
        # Should be average of: 8.0, 9.0 = 8.5
        assert annotations[0]["overall_score"] == pytest.approx(8.5, abs=0.1)
    
    def test_get_all_evaluation_data_with_invalid_json(self):
        """Test get_all_evaluation_data handles invalid JSON gracefully"""
        # Create judgment with invalid JSON
        self.save_judgment(
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            model_a="Model A",
            model_b="Model B",
            judge_model="llama3",
            judgment="A is better",
            judgment_type="comprehensive",
            metrics_json='{"invalid": json}'  # Invalid JSON
        )
        
        # Should not raise exception, should handle gracefully
        data = self.get_all_evaluation_data(limit=100)
        assert "judgments" in data
        # May or may not include the invalid entry, but shouldn't crash
    
    def test_get_all_evaluation_data_code_evaluation_exception_handling(self):
        """Test exception handling in code_evaluations processing"""
        # Create judgment with code_evaluation type but potentially problematic JSON
        self.save_judgment(
            question="Code question",
            response_a="def func(): pass",
            response_b="def func(): return None",
            model_a="Model A",
            model_b="Model B",
            judge_model="llama3",
            judgment="B is better",
            judgment_type="code_evaluation",
            metrics_json='{"overall_score": 7.5}'  # Missing nested structure
        )
        
        # Should handle gracefully even if JSON structure is unexpected
        data = self.get_all_evaluation_data(limit=100)
        assert "code_evaluations" in data
        # Should not crash even if metrics_json doesn't have expected structure
    
    def test_get_all_evaluation_data_code_evaluation_with_exception(self):
        """Test exception handling path in code_evaluations (lines 523-524)"""
        # Create a judgment that will cause an exception when processing
        # We need to trigger the except block at line 523
        import sqlite3
        conn = sqlite3.connect(self.test_db)
        c = conn.cursor()
        # Insert directly with invalid JSON that will cause json.loads to fail
        c.execute('''
            INSERT INTO judgments 
            (question, response_a, response_b, model_a, model_b, judge_model, 
             judgment, judgment_type, metrics_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            "Code question",
            "def func(): pass",
            "def func(): return None",
            "Model A",
            "Model B",
            "llama3",
            "B is better",
            "code_evaluation",
            '{"invalid": json}'  # Invalid JSON syntax - missing quotes around json
        ))
        conn.commit()
        conn.close()
        
        # The function should handle the exception gracefully
        data = self.get_all_evaluation_data(limit=100)
        assert "code_evaluations" in data
        # Exception should be caught and passed, so function continues
        # The code_evaluation with invalid JSON should be skipped

