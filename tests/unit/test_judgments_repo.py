"""Unit tests for JudgmentsRepository"""
import pytest
import os
import tempfile
import json
import sqlite3
from core.infrastructure.db.repositories.judgments_repo import JudgmentsRepository
from core.infrastructure.db.connection import init_database, get_db_connection
from core.common.settings import settings


def _create_full_schema(conn):
    """Create full database schema for testing"""
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS judgments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluation_id TEXT,
            question TEXT NOT NULL,
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
    conn.commit()


class TestJudgmentsRepository:
    """Test cases for JudgmentsRepository"""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db = tmp.name
        
        # Override db_path temporarily
        original_path = settings.db_path
        settings.db_path = tmp_db
        
        # Create full schema
        conn = get_db_connection()
        _create_full_schema(conn)
        conn.close()
        
        yield tmp_db
        
        # Cleanup
        settings.db_path = original_path
        if os.path.exists(tmp_db):
            os.unlink(tmp_db)
    
    def test_save_judgment(self, temp_db):
        """Test saving a judgment"""
        repo = JudgmentsRepository()
        judgment_id = repo.save(
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            model_a="model_a",
            model_b="model_b",
            judge_model="llama3",
            judgment="Test judgment",
            judgment_type="pairwise"
        )
        assert judgment_id > 0
    
    def test_save_judgment_with_optional_fields(self, temp_db):
        """Test saving a judgment with optional fields"""
        repo = JudgmentsRepository()
        metrics = {"score_a": 8.5, "score_b": 7.5}
        trace = [{"step": "test"}]
        judgment_id = repo.save(
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            model_a="model_a",
            model_b="model_b",
            judge_model="llama3",
            judgment="Test judgment",
            judgment_type="pairwise",
            evaluation_id="test-eval-id",
            metrics_json=json.dumps(metrics),
            trace_json=json.dumps(trace)
        )
        assert judgment_id > 0
    
    def test_get_all_judgments(self, temp_db):
        """Test getting all judgments"""
        repo = JudgmentsRepository()
        
        # Save some judgments
        repo.save(
            question="Q1",
            response_a="A1",
            response_b="B1",
            model_a="m1",
            model_b="m2",
            judge_model="llama3",
            judgment="J1",
            judgment_type="pairwise"
        )
        repo.save(
            question="Q2",
            response_a="A2",
            response_b="B2",
            model_a="m1",
            model_b="m2",
            judge_model="llama3",
            judgment="J2",
            judgment_type="pairwise"
        )
        
        # Get all
        judgments = repo.get_all()
        assert len(judgments) == 2
        assert judgments[0]["question"] in ["Q1", "Q2"]
    
    def test_get_all_judgments_with_limit(self, temp_db):
        """Test getting judgments with limit"""
        repo = JudgmentsRepository()
        
        # Save multiple judgments
        for i in range(10):
            repo.save(
                question=f"Q{i}",
                response_a="A",
                response_b="B",
                model_a="m1",
                model_b="m2",
                judge_model="llama3",
                judgment=f"J{i}",
                judgment_type="pairwise"
            )
        
        # Get with limit
        judgments = repo.get_all(limit=5)
        assert len(judgments) == 5
    
    def test_get_all_judgments_empty(self, temp_db):
        """Test getting judgments from empty database"""
        repo = JudgmentsRepository()
        judgments = repo.get_all()
        assert judgments == []

