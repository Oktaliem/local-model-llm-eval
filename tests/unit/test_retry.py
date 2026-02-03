"""Unit tests for RetryPolicy"""
import pytest
import time
from unittest.mock import Mock, patch
from core.infrastructure.llm.retry import RetryPolicy


class TestRetryPolicy:
    """Test cases for RetryPolicy"""
    
    def test_retry_policy_initialization_default(self):
        """Test retry policy initialization with default values"""
        policy = RetryPolicy()
        assert policy.max_retries == 2
        assert policy.retry_delay == 2.0
        assert policy.initial_num_predict == 768
        assert policy.retry_num_predict == 512
    
    def test_retry_policy_initialization_custom(self):
        """Test retry policy initialization with custom values"""
        policy = RetryPolicy(
            max_retries=3,
            retry_delay=1.5,
            initial_num_predict=1024,
            retry_num_predict=256
        )
        assert policy.max_retries == 3
        assert policy.retry_delay == 1.5
        assert policy.initial_num_predict == 1024
        assert policy.retry_num_predict == 256
    
    def test_execute_success_first_attempt(self):
        """Test execute succeeds on first attempt"""
        policy = RetryPolicy(max_retries=2)
        mock_func = Mock(return_value="success")
        
        result = policy.execute(mock_func)
        
        assert result == "success"
        assert mock_func.call_count == 1
        # Check that num_predict was set correctly
        call_args = mock_func.call_args[0][0]  # First positional arg (options dict)
        assert call_args["num_predict"] == 768
    
    @patch('core.infrastructure.llm.retry.time.sleep')
    def test_execute_success_after_retry(self, mock_sleep):
        """Test execute succeeds after retry"""
        policy = RetryPolicy(max_retries=2, retry_delay=0.1)
        mock_func = Mock(side_effect=[Exception("First fail"), "success"])
        
        result = policy.execute(mock_func)
        
        assert result == "success"
        assert mock_func.call_count == 2
        mock_sleep.assert_called_once_with(0.1)
        
        # Check retry used reduced num_predict
        second_call_args = mock_func.call_args_list[1][0][0]
        assert second_call_args["num_predict"] == 512

    @patch('core.infrastructure.llm.retry.time.sleep')
    def test_execute_retry_logs_debug_message(self, mock_sleep, capsys):
        """Test that a retry emits the debug log line."""
        policy = RetryPolicy(max_retries=1, retry_delay=0.1)
        mock_func = Mock(side_effect=[Exception("First fail"), "success"])

        policy.execute(mock_func)

        out = capsys.readouterr().out
        assert "Retry attempt 1/1" in out
    
    @patch('core.infrastructure.llm.retry.time.sleep')
    def test_execute_fails_all_attempts(self, mock_sleep):
        """Test execute fails after all retries"""
        policy = RetryPolicy(max_retries=2, retry_delay=0.1)
        test_exception = Exception("All failed")
        mock_func = Mock(side_effect=test_exception)
        
        with pytest.raises(Exception, match="All failed"):
            policy.execute(mock_func)
        
        assert mock_func.call_count == 3  # Initial + 2 retries
        assert mock_sleep.call_count == 2
    
    def test_execute_with_base_options(self):
        """Test execute with base options"""
        policy = RetryPolicy()
        mock_func = Mock(return_value="success")
        base_options = {"temperature": 0.5}
        
        result = policy.execute(mock_func, base_options=base_options)
        
        assert result == "success"
        call_args = mock_func.call_args[0][0]
        assert call_args["temperature"] == 0.5
        assert call_args["num_predict"] == 768
    
    @patch('core.infrastructure.llm.retry.time.sleep')
    def test_execute_retry_merges_options(self, mock_sleep):
        """Test that retry merges options correctly"""
        policy = RetryPolicy(max_retries=1, retry_delay=0.1)
        mock_func = Mock(side_effect=[Exception("Fail"), "success"])
        base_options = {"temperature": 0.5}
        
        result = policy.execute(mock_func, base_options=base_options)
        
        assert result == "success"
        # Check second call has both temperature and reduced num_predict
        second_call_args = mock_func.call_args_list[1][0][0]
        assert second_call_args["temperature"] == 0.5
        assert second_call_args["num_predict"] == 512
    
    def test_execute_verifies_base_options_default(self):
        """Test that base_options defaults to empty dict"""
        policy = RetryPolicy()
        mock_func = Mock(return_value="success")
        
        result = policy.execute(mock_func)
        
        assert result == "success"
        # Verify base_options was None and handled correctly (mutation: base_options = {} would fail)
        call_args = mock_func.call_args[0][0]
        assert "num_predict" in call_args
        assert call_args["num_predict"] == 768
    
    def test_execute_verifies_base_options_copy(self):
        """Test that base_options is copied (not mutated)"""
        policy = RetryPolicy()
        mock_func = Mock(return_value="success")
        base_options = {"temperature": 0.5}
        original_base = base_options.copy()
        
        result = policy.execute(mock_func, base_options=base_options)
        
        assert result == "success"
        # Verify base_options was copied (mutation: options = base_options would fail)
        assert base_options == original_base  # Original not mutated
        call_args = mock_func.call_args[0][0]
        assert call_args["temperature"] == 0.5
    
    def test_execute_verifies_last_exception_initialization(self):
        """Test that last_exception is initialized correctly"""
        policy = RetryPolicy(max_retries=0)
        test_exception = Exception("Test exception")
        mock_func = Mock(side_effect=test_exception)
        
        with pytest.raises(Exception) as exc_info:
            policy.execute(mock_func)
        
        # Verify last_exception was set (mutation: last_exception = None would fail)
        assert exc_info.value == test_exception
    
    def test_execute_verifies_attempt_range(self):
        """Test that attempt range is correct (0 to max_retries inclusive)"""
        policy = RetryPolicy(max_retries=2)
        mock_func = Mock(side_effect=[Exception("Fail"), Exception("Fail"), "success"])
        
        with patch('core.infrastructure.llm.retry.time.sleep'):
            result = policy.execute(mock_func)
        
        assert result == "success"
        # Verify 3 attempts (0, 1, 2) (mutation: range(max_retries) would fail)
        assert mock_func.call_count == 3
    
    def test_execute_verifies_num_predict_initial_attempt(self):
        """Test that initial attempt uses initial_num_predict"""
        policy = RetryPolicy(initial_num_predict=1024, retry_num_predict=256)
        mock_func = Mock(return_value="success")
        
        result = policy.execute(mock_func)
        
        assert result == "success"
        # Verify initial_num_predict is used (mutation: options["num_predict"] = retry_num_predict would fail)
        call_args = mock_func.call_args[0][0]
        assert call_args["num_predict"] == 1024
    
    def test_execute_verifies_num_predict_retry_attempt(self):
        """Test that retry attempts use retry_num_predict"""
        policy = RetryPolicy(initial_num_predict=1024, retry_num_predict=256)
        mock_func = Mock(side_effect=[Exception("Fail"), "success"])
        
        with patch('core.infrastructure.llm.retry.time.sleep'):
            result = policy.execute(mock_func)
        
        assert result == "success"
        # Verify retry_num_predict is used on retry (mutation: options["num_predict"] = initial_num_predict would fail)
        second_call_args = mock_func.call_args_list[1][0][0]
        assert second_call_args["num_predict"] == 256
    
    def test_execute_verifies_retry_condition(self):
        """Test that retry only happens if attempt < max_retries"""
        policy = RetryPolicy(max_retries=1)
        mock_func = Mock(side_effect=Exception("Fail"))
        
        with patch('core.infrastructure.llm.retry.time.sleep') as mock_sleep:
            with pytest.raises(Exception):
                policy.execute(mock_func)
        
        # Verify retry condition (mutation: attempt <= max_retries would fail)
        assert mock_func.call_count == 2  # Initial + 1 retry
        assert mock_sleep.call_count == 1  # Only one retry delay
    
    def test_execute_verifies_sleep_delay(self):
        """Test that sleep uses retry_delay"""
        policy = RetryPolicy(retry_delay=1.5)
        mock_func = Mock(side_effect=[Exception("Fail"), "success"])
        
        with patch('core.infrastructure.llm.retry.time.sleep') as mock_sleep:
            result = policy.execute(mock_func)
        
        assert result == "success"
        # Verify retry_delay is used (mutation: time.sleep(0) would fail)
        mock_sleep.assert_called_once_with(1.5)

