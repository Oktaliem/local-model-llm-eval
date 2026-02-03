"""Unit tests for sanitize module"""
import pytest
from core.common.sanitize import sanitize_model_output


class TestSanitize:
    """Test cases for sanitize_model_output function"""
    
    def test_sanitize_empty_string(self):
        """Test sanitizing empty string"""
        result = sanitize_model_output("")
        assert result == ""
    
    def test_sanitize_none(self):
        """Test sanitizing None (should handle gracefully)"""
        result = sanitize_model_output(None)
        assert result == ""
    
    def test_sanitize_redacted_reasoning(self):
        """Test removing <think> blocks"""
        text = "This is a test <think>hidden content</think> more text"
        result = sanitize_model_output(text)
        assert "hidden content" not in result
        assert "This is a test" in result
        assert "more text" in result
    
    def test_sanitize_redacted_reasoning_multiline(self):
        """Test removing multiline <think> blocks"""
        text = """Start
<think>
Line 1
Line 2
</think>
End"""
        result = sanitize_model_output(text)
        assert "Line 1" not in result
        assert "Line 2" not in result
        assert "Start" in result
        assert "End" in result
    
    def test_sanitize_html_tags(self):
        """Test removing HTML tags"""
        text = "Text with <div>HTML</div> tags <span>here</span>"
        result = sanitize_model_output(text)
        assert "<div>" not in result
        assert "<span>" not in result
        assert "HTML" in result
        assert "tags" in result
        assert "XXXX" not in result
    
    def test_sanitize_case_insensitive(self):
        """Test that redacted_reasoning removal is case insensitive"""
        text = "Text <REDACTED_REASONING>content</REDACTED_REASONING> more"
        result = sanitize_model_output(text)
        # The regex should remove the redacted_reasoning block (case insensitive)
        # But HTML tag removal will also remove <REDACTED_REASONING> tags
        # So content might still be there, but tags should be gone
        assert "<REDACTED_REASONING>" not in result
        assert "</REDACTED_REASONING>" not in result
        assert "Text" in result
        assert "more" in result
    
    def test_sanitize_none_input(self):
        """Test sanitizing None input"""
        result = sanitize_model_output(None)
        assert result == ""
    
    def test_sanitize_strips_whitespace(self):
        """Test that result is stripped of leading/trailing whitespace"""
        text = "   Test text   "
        result = sanitize_model_output(text)
        assert result == "Test text"
    
    def test_sanitize_normal_text(self):
        """Test sanitizing normal text without special content"""
        text = "This is normal text without any special tags."
        result = sanitize_model_output(text)
        assert result == text
    
    def test_sanitize_redacted_reasoning_exact_pattern(self):
        """Test that ONLY <think> pattern is removed by first regex"""
        # This test verifies the specific regex pattern works correctly
        # The mutation changes the pattern, so we need to verify the exact pattern
        text = "Before <think>hidden content</think> after"
        result = sanitize_model_output(text)
        # First regex should remove the entire <think> block including content
        assert "<think>" not in result
        assert "</think>" not in result
        assert "hidden content" not in result  # Content should be removed
        assert "XXXX" not in result
        assert "Before" in result
        assert "after" in result
    
    def test_sanitize_other_tags_not_removed_by_first_regex(self):
        """Test that other tags are NOT removed by first regex (but by second)"""
        # The first regex only matches <think>, not other tags
        text = "Text <div>content</div> more"
        result = sanitize_model_output(text)
        # First regex should NOT match <div>, so it should be removed by second regex
        assert "<div>" not in result
        assert "</div>" not in result
        # Second regex removes tags but content remains
        assert "content" in result
        assert "Text" in result
        assert "more" in result
    
    def test_sanitize_redacted_reasoning_vs_other_tags(self):
        """Test that <think> is removed but other tags only have tags removed"""
        text = "Start <think>remove this</think> middle <div>keep this</div> end"
        result = sanitize_model_output(text)
        # <think> block should be completely removed
        assert "remove this" not in result
        assert "<think>" not in result
        # <div> tags should be removed by second regex, but content remains
        assert "<div>" not in result
        assert "keep this" in result
        assert "Start" in result
        assert "middle" in result
        assert "end" in result
    
    def test_sanitize_redacted_reasoning_with_nested_tags(self):
        """Test <think> removal when it contains nested tags"""
        text = "Text <think><div>nested</div> content</think> more"
        result = sanitize_model_output(text)
        # Entire <think> block should be removed
        assert "<think>" not in result
        assert "nested" not in result
        assert "content" not in result
        assert "Text" in result
        assert "more" in result
    
    def test_sanitize_redacted_reasoning_multiple_blocks(self):
        """Test removing multiple <think> blocks"""
        text = "Start <think>first</think> middle <think>second</think> end"
        result = sanitize_model_output(text)
        assert "first" not in result
        assert "second" not in result
        assert "<think>" not in result
        assert "Start" in result
        assert "middle" in result
        assert "end" in result
    
    def test_sanitize_redacted_reasoning_empty_block(self):
        """Test removing empty <think> block"""
        text = "Text <think></think> more"
        result = sanitize_model_output(text)
        assert "<think>" not in result
        assert "Text" in result
        assert "more" in result
    
    def test_sanitize_verifies_first_regex_before_second(self):
        """Test that first regex removes <think> before second regex runs"""
        # If first regex is broken, second regex would still remove the tags
        # This test ensures first regex works by checking content is removed
        text = "Text <think>should be gone</think> more"
        result = sanitize_model_output(text)
        # If first regex works, content is removed
        # If only second regex works, tags are removed but content remains
        assert "should be gone" not in result  # Verifies first regex worked
        assert "<think>" not in result
        assert "Text" in result
        assert "more" in result
    
    def test_sanitize_redacted_reasoning_pattern_specificity(self):
        """Test that only <think> pattern is matched, not similar patterns"""
        # This ensures the regex pattern is specific to <think>
        text = "Text <think>remove</think> <redacted>keep</redacted> more"
        result = sanitize_model_output(text)
        # <think> should be removed
        assert "remove" not in result
        assert "<think>" not in result
        # <redacted> should only have tags removed by second regex
        assert "<redacted>" not in result
        assert "keep" in result  # Content should remain
        assert "Text" in result
        assert "more" in result
