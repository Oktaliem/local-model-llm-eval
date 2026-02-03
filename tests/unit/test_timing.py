"""Unit tests for timing module"""
import pytest
from core.common.timing import track_execution_time


class TestTrackExecutionTime:
    """Test cases for track_execution_time decorator"""
    
    def test_track_execution_time_dict_result(self):
        """Test that execution_time is added to dict result"""
        @track_execution_time
        def sample_function():
            return {"status": "success"}
        
        result = sample_function()
        
        assert isinstance(result, dict)
        assert "execution_time" in result
        assert "status" in result
        assert result["status"] == "success"
        assert isinstance(result["execution_time"], float)
        assert result["execution_time"] >= 0
    
    def test_track_execution_time_non_dict_result(self):
        """Test that non-dict results are returned unchanged"""
        @track_execution_time
        def sample_function():
            return "string result"
        
        result = sample_function()
        
        assert result == "string result"
        assert isinstance(result, str)
    
    def test_track_execution_time_with_args(self):
        """Test decorator with function that takes arguments"""
        @track_execution_time
        def sample_function(a, b):
            return {"sum": a + b}
        
        result = sample_function(1, 2)
        
        assert result["sum"] == 3
        assert "execution_time" in result
    
    def test_track_execution_time_with_kwargs(self):
        """Test decorator with function that takes keyword arguments"""
        @track_execution_time
        def sample_function(name="default"):
            return {"name": name}
        
        result = sample_function(name="test")
        
        assert result["name"] == "test"
        assert "execution_time" in result
    
    def test_track_execution_time_measures_time(self):
        """Test that execution time is a positive float"""
        @track_execution_time
        def sample_function():
            # Simple computation instead of sleep for faster/more reliable testing
            total = sum(range(100))
            return {"status": "done", "total": total}
        
        result = sample_function()
        
        assert "execution_time" in result
        assert isinstance(result["execution_time"], float)
        assert result["execution_time"] >= 0  # Time should be non-negative
    
    def test_track_execution_time_none_result(self):
        """Test that None result is returned unchanged"""
        @track_execution_time
        def sample_function():
            return None
        
        result = sample_function()
        
        assert result is None
    
    def test_track_execution_time_list_result(self):
        """Test that list result is returned unchanged"""
        @track_execution_time
        def sample_function():
            return [1, 2, 3]
        
        result = sample_function()
        
        assert result == [1, 2, 3]
        assert isinstance(result, list)
    
    def test_track_execution_time_int_result(self):
        """Test that int result is returned unchanged"""
        @track_execution_time
        def sample_function():
            return 42
        
        result = sample_function()
        
        assert result == 42
        assert isinstance(result, int)
    
    def test_track_execution_time_preserves_function_name(self):
        """Test that decorator preserves function name (uses @wraps)"""
        @track_execution_time
        def my_named_function():
            return {"data": "test"}
        
        assert my_named_function.__name__ == "my_named_function"
    
    def test_track_execution_time_empty_dict_result(self):
        """Test that execution_time is added to empty dict result"""
        @track_execution_time
        def sample_function():
            return {}
        
        result = sample_function()
        
        assert isinstance(result, dict)
        assert "execution_time" in result
        assert len(result) == 1  # Only execution_time key

