"""Unit tests for authentication middleware"""
import pytest
import json
import os
import tempfile
from unittest.mock import patch, Mock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from backend.api.middleware.auth import (
    load_api_keys,
    save_api_keys,
    verify_api_key
)


class TestAuthMiddleware:
    """Test cases for authentication middleware"""
    
    def test_load_api_keys_file_exists(self):
        """Test loading API keys when file exists"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_keys = {
                "key1": {"name": "Test Key 1", "created_at": "2024-01-01"},
                "key2": {"name": "Test Key 2", "created_at": "2024-01-02"}
            }
            json.dump(test_keys, f)
            temp_path = f.name
        
        try:
            with patch('backend.api.middleware.auth.API_KEYS_FILE', temp_path):
                keys = load_api_keys()
                assert keys == test_keys
        finally:
            os.unlink(temp_path)
    
    def test_load_api_keys_file_not_exists(self):
        """Test loading API keys when file doesn't exist"""
        with patch('backend.api.middleware.auth.API_KEYS_FILE', '/nonexistent/path/keys.json'):
            keys = load_api_keys()
            assert keys == {}
    
    def test_load_api_keys_invalid_json(self):
        """Test loading API keys with invalid JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json}')  # Invalid JSON
            temp_path = f.name
        
        try:
            with patch('backend.api.middleware.auth.API_KEYS_FILE', temp_path):
                keys = load_api_keys()
                assert keys == {}  # Should return empty dict on error
        finally:
            os.unlink(temp_path)
    
    def test_save_api_keys(self):
        """Test saving API keys"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = os.path.join(temp_dir, 'api_keys.json')
            
            with patch('backend.api.middleware.auth.API_KEYS_FILE', temp_path):
                test_keys = {
                    "key1": {"name": "Test Key 1"},
                    "key2": {"name": "Test Key 2"}
                }
                save_api_keys(test_keys)
                
                # Verify file was created and contains correct data
                assert os.path.exists(temp_path)
                with open(temp_path, 'r') as f:
                    loaded_keys = json.load(f)
                    assert loaded_keys == test_keys
    
    def test_save_api_keys_creates_directory(self):
        """Test that save_api_keys creates directory if it doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = os.path.join(temp_dir, 'subdir', 'api_keys.json')
            
            with patch('backend.api.middleware.auth.API_KEYS_FILE', temp_path):
                test_keys = {"key1": {"name": "Test"}}
                save_api_keys(test_keys)
                
                assert os.path.exists(temp_path)
    
    @patch('backend.api.middleware.auth.load_api_keys')
    @patch('backend.api.middleware.auth.enforce_rate_limit')
    def test_verify_api_key_valid(self, mock_enforce, mock_load):
        """Test verifying a valid API key"""
        mock_load.return_value = {"test-key": {"name": "Test Key"}}
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "test-key"
        
        result = verify_api_key(mock_credentials)
        
        assert result == "test-key"
        mock_enforce.assert_called_once_with("test-key")
    
    @patch('backend.api.middleware.auth.load_api_keys')
    def test_verify_api_key_invalid(self, mock_load):
        """Test verifying an invalid API key"""
        mock_load.return_value = {"other-key": {"name": "Other Key"}}
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = "invalid-key"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_api_key(mock_credentials)
        
        assert exc_info.value.status_code == 401
        assert "Invalid API key" in str(exc_info.value.detail)

