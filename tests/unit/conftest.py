"""Pytest configuration for unit tests"""
import sys
import os
import tempfile
import pytest
from unittest.mock import patch

# Set MUTANT_UNDER_TEST during stats collection to prevent KeyError
# This allows Settings to be imported without errors during mutation testing stats collection
_file_path = os.path.abspath(__file__) if '__file__' in globals() else ''
_is_mutation_stats = (
    'MUTANT_UNDER_TEST' not in os.environ and 
    ('mutants' in _file_path or os.path.basename(os.getcwd()) == 'mutants')
)

if _is_mutation_stats:
    # During stats collection, set MUTANT_UNDER_TEST to allow Settings import
    os.environ.setdefault('MUTANT_UNDER_TEST', 'stats_collection')

# Detect if we're running under mutation testing
_is_mutation_testing = (
    'MUTANT_UNDER_TEST' in os.environ or 
    'mutants' in _file_path or 
    os.path.basename(os.getcwd()) == 'mutants'
)

# Now import settings - it should work with MUTANT_UNDER_TEST set
try:
    from core.common.settings import settings
except (KeyError, Exception):
    # If import still fails, create a dummy settings object
    class DummySettings:
        db_path = None
    settings = DummySettings()

# When running from mutants/ directory (mutmut), prioritize mutants directory
# This ensures tests import the mutated code, not the original
if os.path.basename(os.getcwd()) == "mutants":
    # Add mutants directory first so mutated code is imported
    mutants_dir = os.getcwd()
    if mutants_dir not in sys.path:
        sys.path.insert(0, mutants_dir)
    # Remove parent directory from sys.path to prevent importing original code
    project_root = os.path.dirname(mutants_dir)
    while project_root in sys.path:
        sys.path.remove(project_root)
    # Re-add parent after mutants/ for dependencies like backend/
    if project_root not in sys.path:
        sys.path.insert(1, project_root)

# Global patch for time.sleep during mutation testing to prevent timeouts
# This makes all sleep calls instant, preventing timeouts from hanging operations
@pytest.fixture(autouse=True)
def patch_time_sleep_for_mutation_testing(monkeypatch):
    """Automatically patch time.sleep to be instant during mutation testing"""
    if _is_mutation_testing:
        import time
        def instant_sleep(seconds):
            """Instant sleep for mutation testing - prevents timeouts"""
            pass  # Do nothing - instant return
        monkeypatch.setattr(time, 'sleep', instant_sleep)


@pytest.fixture(autouse=True)
def setup_test_database(monkeypatch):
    """Automatically set up a temporary database for each test"""
    # Create a temporary database file in a temp directory
    # Use a temp directory to avoid path issues when running from mutants/
    tmp_dir = tempfile.mkdtemp()
    tmp_db = os.path.join(tmp_dir, 'test.db')
    
    # Override db_path for this test (only if settings is available)
    if hasattr(settings, 'db_path'):
        original_path = settings.db_path
        monkeypatch.setattr(settings, 'db_path', tmp_db)
    else:
        original_path = None
    
    # Also set DB_PATH environment variable for any code that reads it directly
    monkeypatch.setenv('DB_PATH', tmp_db)
    
    yield tmp_db
    
    # Cleanup: restore original path and remove temp directory
    if original_path is not None:
        monkeypatch.setattr(settings, 'db_path', original_path)
    monkeypatch.delenv('DB_PATH', raising=False)
    if os.path.exists(tmp_dir):
        try:
            import shutil
            shutil.rmtree(tmp_dir)
        except:
            pass  # Ignore cleanup errors
