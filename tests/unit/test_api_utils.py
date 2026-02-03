"""Unit tests for API utility functions"""
import pytest
import json
import os
import tempfile
from unittest.mock import patch, AsyncMock, Mock
from backend.api.utils import (
    load_webhooks,
    save_webhooks,
    trigger_webhook
)


class TestAPIUtils:
    """Test cases for API utility functions"""
    
    def test_load_webhooks_file_exists(self):
        """Test loading webhooks when file exists"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_webhooks = {
                "webhook1": {"url": "http://example.com/webhook1", "events": ["evaluation.completed"]},
                "webhook2": {"url": "http://example.com/webhook2", "events": ["evaluation.started"]}
            }
            json.dump(test_webhooks, f)
            temp_path = f.name
        
        try:
            with patch('backend.api.utils.WEBHOOKS_FILE', temp_path):
                webhooks = load_webhooks()
                assert webhooks == test_webhooks
        finally:
            os.unlink(temp_path)
    
    def test_load_webhooks_file_not_exists(self):
        """Test loading webhooks when file doesn't exist"""
        with patch('backend.api.utils.WEBHOOKS_FILE', '/nonexistent/path/webhooks.json'):
            webhooks = load_webhooks()
            assert webhooks == {}
    
    def test_load_webhooks_invalid_json(self):
        """Test loading webhooks with invalid JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json}')  # Invalid JSON
            temp_path = f.name
        
        try:
            with patch('backend.api.utils.WEBHOOKS_FILE', temp_path):
                webhooks = load_webhooks()
                assert webhooks == {}  # Should return empty dict on error
        finally:
            os.unlink(temp_path)
    
    def test_save_webhooks(self):
        """Test saving webhooks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = os.path.join(temp_dir, 'webhooks.json')
            
            with patch('backend.api.utils.WEBHOOKS_FILE', temp_path):
                test_webhooks = {
                    "webhook1": {"url": "http://example.com/webhook1", "events": ["event1"]}
                }
                save_webhooks(test_webhooks)
                
                # Verify file was created and contains correct data
                assert os.path.exists(temp_path)
                with open(temp_path, 'r') as f:
                    loaded_webhooks = json.load(f)
                    assert loaded_webhooks == test_webhooks
    
    def test_save_webhooks_creates_directory(self):
        """Test that save_webhooks creates directory if it doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = os.path.join(temp_dir, 'subdir', 'webhooks.json')
            
            with patch('backend.api.utils.WEBHOOKS_FILE', temp_path):
                test_webhooks = {"webhook1": {"url": "http://example.com"}}
                save_webhooks(test_webhooks)
                
                assert os.path.exists(temp_path)
    
    @pytest.mark.asyncio
    @patch('backend.api.utils.load_webhooks')
    @patch('backend.api.utils.httpx.AsyncClient')
    async def test_trigger_webhook_no_matching_events(self, mock_client_class, mock_load):
        """Test triggering webhook when no webhooks match the event"""
        mock_load.return_value = {
            "webhook1": {"url": "http://example.com", "events": ["other.event"]}
        }
        
        await trigger_webhook("evaluation.completed", {"data": "test"})
        
        # Should not make any HTTP requests
        mock_client_class.assert_not_called()
    
    @pytest.mark.asyncio
    @patch('backend.api.utils.load_webhooks')
    @patch('backend.api.utils.httpx.AsyncClient')
    async def test_trigger_webhook_with_matching_event(self, mock_client_class, mock_load):
        """Test triggering webhook with matching event"""
        mock_load.return_value = {
            "webhook1": {
                "url": "http://example.com/webhook",
                "events": ["evaluation.completed"]
            }
        }
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.post = AsyncMock()
        
        await trigger_webhook("evaluation.completed", {"data": "test"})
        
        # Verify webhook was called
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "http://example.com/webhook"
        assert call_args[1]["json"]["event"] == "evaluation.completed"
        assert call_args[1]["json"]["data"] == {"data": "test"}
    
    @pytest.mark.asyncio
    @patch('backend.api.utils.load_webhooks')
    @patch('backend.api.utils.httpx.AsyncClient')
    async def test_trigger_webhook_with_secret(self, mock_client_class, mock_load):
        """Test triggering webhook with secret signature"""
        mock_load.return_value = {
            "webhook1": {
                "url": "http://example.com/webhook",
                "events": ["evaluation.completed"],
                "secret": "test-secret"
            }
        }
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.post = AsyncMock()
        
        await trigger_webhook("evaluation.completed", {"data": "test"})
        
        # Verify signature header was added
        call_args = mock_client.post.call_args
        assert "X-Webhook-Signature" in call_args[1]["headers"]
        assert call_args[1]["headers"]["X-Webhook-Signature"] is not None
    
    @pytest.mark.asyncio
    @patch('backend.api.utils.load_webhooks')
    @patch('backend.api.utils.httpx.AsyncClient')
    async def test_trigger_webhook_without_secret(self, mock_client_class, mock_load):
        """Test triggering webhook without secret"""
        mock_load.return_value = {
            "webhook1": {
                "url": "http://example.com/webhook",
                "events": ["evaluation.completed"]
            }
        }
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.post = AsyncMock()
        
        await trigger_webhook("evaluation.completed", {"data": "test"})
        
        # Verify no signature header
        call_args = mock_client.post.call_args
        assert call_args[1]["headers"] == {}
    
    @pytest.mark.asyncio
    @patch('backend.api.utils.load_webhooks')
    @patch('backend.api.utils.httpx.AsyncClient')
    @patch('backend.api.utils.print')
    async def test_trigger_webhook_handles_exception(self, mock_print, mock_client_class, mock_load):
        """Test that webhook exceptions are handled gracefully"""
        mock_load.return_value = {
            "webhook1": {
                "url": "http://example.com/webhook",
                "events": ["evaluation.completed"]
            }
        }
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.post = AsyncMock(side_effect=Exception("Connection error"))
        
        # Should not raise exception
        await trigger_webhook("evaluation.completed", {"data": "test"})
        
        # Should print error message
        mock_print.assert_called_once()
        assert "Failed to trigger webhook" in str(mock_print.call_args)
    
    @pytest.mark.asyncio
    @patch('backend.api.utils.load_webhooks')
    @patch('backend.api.utils.httpx.AsyncClient')
    async def test_trigger_webhook_multiple_webhooks(self, mock_client_class, mock_load):
        """Test triggering multiple webhooks for same event"""
        mock_load.return_value = {
            "webhook1": {
                "url": "http://example.com/webhook1",
                "events": ["evaluation.completed"]
            },
            "webhook2": {
                "url": "http://example.com/webhook2",
                "events": ["evaluation.completed"]
            }
        }
        
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.post = AsyncMock()
        
        await trigger_webhook("evaluation.completed", {"data": "test"})
        
        # Should call both webhooks
        assert mock_client.post.call_count == 2

