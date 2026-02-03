"""Unit tests for rate limiting middleware"""
import pytest
import time
from unittest.mock import patch
from fastapi import HTTPException
from backend.api.middleware.rate_limit import (
    check_rate_limit,
    enforce_rate_limit,
    rate_limit_store
)


class TestRateLimitMiddleware:
    """Test cases for rate limiting middleware"""
    
    def setup_method(self):
        """Clear rate limit store before each test"""
        rate_limit_store.clear()
    
    @patch('backend.api.middleware.rate_limit.RATE_LIMIT_REQUESTS', 3)
    @patch('backend.api.middleware.rate_limit.RATE_LIMIT_WINDOW', 3600)
    def test_check_rate_limit_within_limit(self):
        """Test rate limit check when within limit"""
        api_key = "test-key"
        
        # First 3 requests should pass
        assert check_rate_limit(api_key) is True
        assert check_rate_limit(api_key) is True
        assert check_rate_limit(api_key) is True
        
        # 4th request should fail
        assert check_rate_limit(api_key) is False
    
    @patch('backend.api.middleware.rate_limit.RATE_LIMIT_REQUESTS', 2)
    @patch('backend.api.middleware.rate_limit.RATE_LIMIT_WINDOW', 1)  # 1 second window
    @patch('backend.api.middleware.rate_limit.time.time', side_effect=[0, 0, 0, 1.1])
    def test_check_rate_limit_removes_old_requests(self, mock_time):
        """Test that old requests outside window are removed"""
        api_key = "test-key"
        
        # Make 2 requests (at limit)
        assert check_rate_limit(api_key) is True
        assert check_rate_limit(api_key) is True
        
        # Should be at limit now
        assert check_rate_limit(api_key) is False
        
        # Advance time beyond the window (mock_time side effect returns 1.1)
        assert check_rate_limit(api_key) is True
    
    @patch('backend.api.middleware.rate_limit.RATE_LIMIT_REQUESTS', 2)
    @patch('backend.api.middleware.rate_limit.RATE_LIMIT_WINDOW', 3600)
    def test_check_rate_limit_different_keys(self):
        """Test that different API keys have separate rate limits"""
        key1 = "key1"
        key2 = "key2"
        
        # Both keys should be able to make requests
        assert check_rate_limit(key1) is True
        assert check_rate_limit(key2) is True
        assert check_rate_limit(key1) is True
        assert check_rate_limit(key2) is True
        
        # Both should be at limit
        assert check_rate_limit(key1) is False
        assert check_rate_limit(key2) is False
    
    @patch('backend.api.middleware.rate_limit.check_rate_limit')
    @patch('backend.api.middleware.rate_limit.RATE_LIMIT_REQUESTS', 100)
    @patch('backend.api.middleware.rate_limit.RATE_LIMIT_WINDOW', 3600)
    def test_enforce_rate_limit_within_limit(self, mock_check):
        """Test enforce_rate_limit when within limit"""
        mock_check.return_value = True
        
        # Should not raise exception
        enforce_rate_limit("test-key")
        mock_check.assert_called_once_with("test-key")
    
    @patch('backend.api.middleware.rate_limit.check_rate_limit')
    @patch('backend.api.middleware.rate_limit.RATE_LIMIT_REQUESTS', 100)
    @patch('backend.api.middleware.rate_limit.RATE_LIMIT_WINDOW', 3600)
    def test_enforce_rate_limit_exceeded(self, mock_check):
        """Test enforce_rate_limit when limit exceeded"""
        mock_check.return_value = False
        
        with pytest.raises(HTTPException) as exc_info:
            enforce_rate_limit("test-key")
        
        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in str(exc_info.value.detail)
        mock_check.assert_called_once_with("test-key")

