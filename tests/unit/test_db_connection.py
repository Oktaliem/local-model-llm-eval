"""Unit tests for database connection"""
import pytest
import os
import tempfile
import sqlite3
from core.infrastructure.db.connection import get_db_connection, init_database
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


class TestDatabaseConnection:
    """Test cases for database connection"""
    
    def test_get_db_connection(self):
        """Test getting a database connection"""
        conn = get_db_connection()
        assert conn is not None
        # Test that it's a valid connection
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
        conn.close()
    
    def test_init_database_creates_table(self):
        """Test that init_database creates the judgments table"""
        # Use a temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db = tmp.name
        
        try:
            # Temporarily override db_path
            original_path = settings.db_path
            settings.db_path = tmp_db
            
            # Initialize database
            init_database()
            
            # Verify table exists
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='judgments'
            """)
            result = cursor.fetchone()
            assert result is not None
            assert result[0] == "judgments"
            conn.close()
            
            # Restore original path
            settings.db_path = original_path
        finally:
            # Cleanup
            if os.path.exists(tmp_db):
                os.unlink(tmp_db)
    
    def test_init_database_idempotent(self):
        """Test that init_database can be called multiple times safely"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_db = tmp.name
        
        try:
            original_path = settings.db_path
            settings.db_path = tmp_db
            
            # Call multiple times
            init_database()
            init_database()
            init_database()
            
            # Should still work
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM judgments")
            count = cursor.fetchone()[0]
            assert count == 0  # Table exists but empty
            conn.close()
            
            settings.db_path = original_path
        finally:
            if os.path.exists(tmp_db):
                os.unlink(tmp_db)

