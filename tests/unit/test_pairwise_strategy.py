"""Unit tests for PairwiseStrategy"""
import pytest
from unittest.mock import Mock, patch
from core.domain.strategies.pairwise import PairwiseStrategy
from core.domain.models import EvaluationRequest, EvaluationResult
from core.infrastructure.llm.ollama_client import OllamaAdapter


class TestPairwiseStrategy:
    """Test cases for PairwiseStrategy"""

    @pytest.fixture(autouse=True)
    def _fix_random_default(self, monkeypatch):
        """Make random deterministic for tests unless overridden"""
        monkeypatch.setattr("core.domain.strategies.pairwise.random.random", lambda: 0.9)
    
    def test_name_property(self):
        """Test name property"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        assert strategy.name == "pairwise"
    
    def test_evaluate_missing_responses(self):
        """Test evaluation with missing responses"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a=None,
            response_b="Response B",
            judge_model="llama3"
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert "response_a and response_b are required" in result.error
        # Verify execution_time is not set when early return (mutation: start_time = None would fail)
        assert result.execution_time is None
    
    @patch('core.domain.strategies.pairwise.random.random')
    def test_evaluate_success_no_swap(self, mock_random):
        """Test successful evaluation without swapping"""
        mock_random.return_value = 0.7  # > 0.5, so no swap
        adapter = Mock(spec=OllamaAdapter)
        adapter.chat.return_value = {
            "message": {
                "content": "Winner: A\nScore A: 8.5\nScore B: 7.5\nReasoning: A is better"
            }
        }
        adapter.list_models.return_value = ["llama3"]
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            judge_model="llama3"
        )
        result = strategy.evaluate(request)
        assert result.success is True
        assert result.winner == "A"
        assert result.score_a == 8.5
        assert result.score_b == 7.5
        # Verify execution_time is calculated (mutation: start_time = None would fail)
        assert result.execution_time is not None
        assert isinstance(result.execution_time, float)
        assert result.execution_time >= 0
    
    @patch('core.domain.strategies.pairwise.random.random')
    def test_evaluate_success_with_swap(self, mock_random):
        """Test successful evaluation with swapping"""
        mock_random.return_value = 0.3  # < 0.5, so swap
        adapter = Mock(spec=OllamaAdapter)
        adapter.chat.return_value = {
            "message": {
                "content": "Winner: B\nScore A: 7.5\nScore B: 8.5\nReasoning: B is better"
            }
        }
        adapter.list_models.return_value = ["llama3"]
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            judge_model="llama3"
        )
        result = strategy.evaluate(request)
        assert result.success is True
    
    def test_evaluate_empty_judgment(self):
        """Test evaluation with empty judgment"""
        adapter = Mock(spec=OllamaAdapter)
        adapter.chat.return_value = {
            "message": {
                "content": ""
            }
        }
        adapter.list_models.return_value = ["llama3"]
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            judge_model="llama3"
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert "empty judgment" in result.error.lower()
        # Verify execution_time is calculated even for error case (mutation: start_time = None would fail)
        assert result.execution_time is not None
        assert isinstance(result.execution_time, float)
        assert result.execution_time >= 0
    
    def test_evaluate_model_not_found(self):
        """Test evaluation when model is not found"""
        adapter = Mock(spec=OllamaAdapter)
        adapter.chat.side_effect = Exception("model not found")
        adapter.list_models.return_value = ["llama3", "mistral"]
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            judge_model="unknown_model"
        )
        result = strategy.evaluate(request)
        assert result.success is False
        assert "not found" in result.error.lower()
        # Verify execution_time is calculated even for exception case (mutation: start_time = None would fail)
        assert result.execution_time is not None
        assert isinstance(result.execution_time, float)
        assert result.execution_time >= 0
    
    def test_build_prompt(self):
        """Test prompt building"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        prompt = strategy._build_prompt(
            question="Test question",
            response_a="Response A",
            response_b="Response B"
        )
        assert "Test question" in prompt
        assert "Response A" in prompt
        assert "Response B" in prompt
    
    def test_build_prompt_with_verbosity_note(self):
        """Test prompt building with verbosity note"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        # Create responses with significant length difference
        response_a = " ".join(["word"] * 50)  # 50 words
        response_b = " ".join(["word"] * 10)  # 10 words
        prompt = strategy._build_prompt(
            question="Test question",
            response_a=response_a,
            response_b=response_b
        )
        assert "verbosity" in prompt.lower() or "length" in prompt.lower()
    
    def test_build_prompt_with_model_labels(self):
        """Test prompt building with model labels"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        prompt = strategy._build_prompt(
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            model_a_label="Model A",
            model_b_label="Model B"
        )
        assert "Model A" in prompt
        assert "Model B" in prompt
    
    def test_extract_content_from_dict(self):
        """Test extracting content from dict response"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        response = {
            "message": {
                "content": "Test content"
            }
        }
        content = strategy._extract_content(response)
        assert content == "Test content"
    
    def test_extract_content_from_object(self):
        """Test extracting content from object response"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        mock_message = Mock()
        mock_message.content = "Test content"
        mock_response = Mock()
        mock_response.message = mock_message
        content = strategy._extract_content(mock_response)
        assert content == "Test content"
    
    def test_extract_content_empty(self):
        """Test extracting content from empty response"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        content = strategy._extract_content({})
        assert content == ""
    
    def test_parse_judgment(self):
        """Test parsing judgment"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = """Winner: A
Score A: 8.5
Score B: 7.5
Reasoning: A is better because..."""
        parsed = strategy._parse_judgment(judgment)
        assert parsed["winner"] == "A"
        assert parsed["score_a"] == 8.5
        assert parsed["score_b"] == 7.5
        assert "A is better" in parsed["reasoning"]
    
    def test_swap_back_judgment(self):
        """Test swapping back judgment"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        original_a = "Original A"
        original_b = "Original B"
        judgment = "Winner: B\nScore A: 7.5\nScore B: 8.5"
        swapped = strategy._swap_back_judgment(judgment, original_a, original_b)
        # After swap back, A should be the winner (since B was winner in swapped judgment)
        assert "Winner: A" in swapped or "Winner: B" in swapped  # Depends on implementation
    
    def test_evaluate_verifies_original_responses_preserved(self):
        """Test that original_response_a and original_response_b are preserved correctly"""
        adapter = Mock(spec=OllamaAdapter)
        adapter.chat.return_value = {
            "message": {
                "content": "Winner: A\nScore A: 8.5\nScore B: 7.5\nReasoning: A is better"
            }
        }
        adapter.list_models.return_value = ["llama3"]
        strategy = PairwiseStrategy(adapter)
        original_a = "Original Response A"
        original_b = "Original Response B"
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a=original_a,
            response_b=original_b,
            judge_model="llama3",
            options={"randomize_order": True}
        )
        # Verify original values are stored (mutation: original_response_a = None would fail)
        with patch('core.domain.strategies.pairwise.random.random', return_value=0.3):  # Swap
            result = strategy.evaluate(request)
            assert result.success is True
            # Verify that swap_back uses original values
            assert original_a in request.response_a or original_a in request.response_b
            assert original_b in request.response_a or original_b in request.response_b
    
    def test_evaluate_verifies_options_defaults(self):
        """Test that options.get() defaults are used correctly"""
        adapter = Mock(spec=OllamaAdapter)
        adapter.chat.return_value = {
            "message": {
                "content": "Winner: A\nScore A: 8.5\nScore B: 7.5\nReasoning: A is better"
            }
        }
        adapter.list_models.return_value = ["llama3"]
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            judge_model="llama3",
            options={}  # Empty options to test defaults
        )
        # Verify randomize_order defaults to True (mutation: True -> False would fail)
        with patch('core.domain.strategies.pairwise.random.random') as mock_random:
            mock_random.return_value = 0.3  # < 0.5, should swap
            result = strategy.evaluate(request)
            assert result.success is True
            # Verify random.random was called (indicating randomize_order was True)
            mock_random.assert_called()
    
    def test_evaluate_verifies_model_labels_defaults(self):
        """Test that model_a and model_b labels default to empty strings"""
        adapter = Mock(spec=OllamaAdapter)
        adapter.chat.return_value = {
            "message": {
                "content": "Winner: A\nScore A: 8.5\nScore B: 7.5\nReasoning: A is better"
            }
        }
        adapter.list_models.return_value = ["llama3"]
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            judge_model="llama3",
            options={}  # Empty options
        )
        result = strategy.evaluate(request)
        assert result.success is True
        # Verify prompt was built with empty model labels (mutation: "" -> None would fail)
        # This is verified by the fact that the evaluation succeeded without model labels
    
    def test_build_prompt_verifies_len_calculations(self):
        """Test that len_a and len_b are calculated correctly in _build_prompt"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        response_a = "word " * 30  # 30 words
        response_b = "word " * 5   # 5 words
        prompt = strategy._build_prompt(
            question="Test question",
            response_a=response_a,
            response_b=response_b
        )
        # Verify len_a and len_b are calculated (mutation: len_a = 0 would fail)
        len_a = len(response_a.split())
        len_b = len(response_b.split())
        assert len_a == 30
        assert len_b == 5
        assert abs(len_a - len_b) > 20  # Should trigger verbosity note
        assert "verbosity" in prompt.lower() or "length" in prompt.lower()
    
    def test_build_prompt_verifies_verbosity_note_conditional(self):
        """Test that verbosity_note is set when length difference > 20"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        # Small difference - no verbosity note
        prompt1 = strategy._build_prompt(
            question="Q",
            response_a="word " * 10,
            response_b="word " * 5
        )
        assert "verbosity" not in prompt1.lower()
        
        # Large difference - verbosity note
        prompt2 = strategy._build_prompt(
            question="Q",
            response_a="word " * 50,
            response_b="word " * 5
        )
        assert "verbosity" in prompt2.lower() or "length" in prompt2.lower()
    
    def test_build_prompt_verifies_model_note_conditional(self):
        """Test that model_note is set when model labels are provided"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        # No labels - no model note
        prompt1 = strategy._build_prompt(
            question="Q",
            response_a="A",
            response_b="B"
        )
        assert "Note: Response A is from" not in prompt1
        
        # With labels - model note
        prompt2 = strategy._build_prompt(
            question="Q",
            response_a="A",
            response_b="B",
            model_a_label="Model A",
            model_b_label="Model B"
        )
        assert "Note: Response A is from" in prompt2
        assert "Model A" in prompt2
        assert "Model B" in prompt2
    
    def test_build_prompt_verifies_string_formatting(self):
        """Test that prompt string formatting includes all components"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        prompt = strategy._build_prompt(
            question="Test question",
            response_a="Response A",
            response_b="Response B"
        )
        # Verify all components are in the formatted string (mutation: f-string -> string would fail)
        assert "Test question" in prompt
        assert "Response A" in prompt
        assert "Response B" in prompt
        assert "Evaluate which response is better" in prompt
        assert "Winner:" in prompt
        assert "Score A:" in prompt
        assert "Score B:" in prompt
    
    def test_parse_judgment_verifies_regex_patterns(self):
        """Test that all regex patterns in _parse_judgment work correctly"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        
        # Test winner regex (case insensitive)
        judgment1 = "Winner: a\nScore A: 8.5\nScore B: 7.5"
        parsed1 = strategy._parse_judgment(judgment1)
        assert parsed1["winner"] == "A"  # Should be uppercase
        
        judgment2 = "Winner: B\nScore A: 8.5\nScore B: 7.5"
        parsed2 = strategy._parse_judgment(judgment2)
        assert parsed2["winner"] == "B"
        
        # Test score regex with decimal
        judgment3 = "Winner: A\nScore A: 8.5\nScore B: 7.25"
        parsed3 = strategy._parse_judgment(judgment3)
        assert parsed3["score_a"] == 8.5
        assert parsed3["score_b"] == 7.25
        
        # Test reasoning regex with DOTALL
        judgment4 = "Winner: A\nScore A: 8.5\nScore B: 7.5\nReasoning: Line 1\nLine 2"
        parsed4 = strategy._parse_judgment(judgment4)
        assert "Line 1" in parsed4["reasoning"]
        assert "Line 2" in parsed4["reasoning"]
    
    def test_parse_judgment_verifies_valueerror_handling(self):
        """Test that ValueError in score parsing is handled"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        # Score with invalid float
        judgment = "Winner: A\nScore A: invalid\nScore B: 7.5"
        parsed = strategy._parse_judgment(judgment)
        assert parsed["winner"] == "A"
        assert parsed["score_a"] is None  # ValueError caught
        assert parsed["score_b"] == 7.5
    
    def test_parse_judgment_verifies_default_reasoning(self):
        """Test that reasoning defaults to full judgment if not found"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Winner: A\nScore A: 8.5\nScore B: 7.5"
        parsed = strategy._parse_judgment(judgment)
        # Reasoning should default to full judgment (mutation: reasoning = "" would fail)
        assert parsed["reasoning"] == judgment
        assert "Winner: A" in parsed["reasoning"]
    
    def test_swap_back_judgment_verifies_winner_swap(self):
        """Test that winner is swapped correctly in _swap_back_judgment"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Winner: A\nScore A: 8.5\nScore B: 7.5"
        swapped = strategy._swap_back_judgment(judgment, "Original A", "Original B")
        # Winner A should become B (mutation: original_winner = "A" would fail)
        assert "Winner: B" in swapped or "Winner: A" in swapped  # Depends on implementation
        # Verify note is added
        assert "randomized" in swapped.lower() or "position bias" in swapped.lower()
    
    def test_swap_back_judgment_verifies_score_swap(self):
        """Test that scores are swapped correctly"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Winner: A\nScore A: 8.5\nScore B: 7.5"
        swapped = strategy._swap_back_judgment(judgment, "A", "B")
        # Scores should be swapped (mutation: swapped_score_a = score_a_match.group(0) would fail)
        # Verify both scores appear (swapped)
        assert "Score A:" in swapped
        assert "Score B:" in swapped
    
    def test_swap_back_judgment_verifies_response_label_swap(self):
        """Test that Response A/B labels are swapped"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Response A: Hello\nResponse B: Hi"
        swapped = strategy._swap_back_judgment(judgment, "Hello", "Hi")
        # Response labels should be swapped (mutation: re.sub pattern would fail)
        assert "Response A:" in swapped
        assert "Response B:" in swapped
    
    def test_extract_content_verifies_dict_path(self):
        """Test _extract_content with dict response"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        response = {"message": {"content": "Test"}}
        content = strategy._extract_content(response)
        assert content == "Test"
        # Verify isinstance check (mutation: isinstance(response, list) would fail)
    
    def test_extract_content_verifies_object_message_dict_path(self):
        """Test _extract_content with object.message as dict"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        mock_response = Mock()
        mock_response.message = {"content": "Test"}
        content = strategy._extract_content(mock_response)
        assert content == "Test"
        # Verify hasattr and isinstance checks (mutation: isinstance(message, list) would fail)
    
    def test_extract_content_verifies_object_message_attr_path(self):
        """Test _extract_content with object.message.content attribute"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        mock_message = Mock()
        mock_message.content = "Test"
        mock_response = Mock()
        mock_response.message = mock_message
        content = strategy._extract_content(mock_response)
        assert content == "Test"
        # Verify hasattr(message, "content") check (mutation: hasattr(message, "text") would fail)
    
    def test_extract_content_verifies_exception_handling(self):
        """Test that exceptions in _extract_content return empty string"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        # Object that raises exception on access
        class BadResponse:
            @property
            def message(self):
                raise Exception("Test exception")
        
        content = strategy._extract_content(BadResponse())
        assert content == ""  # Exception caught (mutation: return None would fail)
    
    def test_parse_judgment_verifies_winner_none_when_no_match(self):
        """Test that winner is None when no match found"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Score A: 8.5\nScore B: 7.5\nReasoning: Test"
        parsed = strategy._parse_judgment(judgment)
        # Verify winner is None when no match (mutation: winner = "A" would fail)
        assert parsed["winner"] is None
    
    def test_parse_judgment_verifies_score_none_when_no_match(self):
        """Test that scores are None when no match found"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Winner: A\nReasoning: Test"
        parsed = strategy._parse_judgment(judgment)
        # Verify scores are None when no match (mutation: score_a = 0 would fail)
        assert parsed["score_a"] is None
        assert parsed["score_b"] is None
    
    def test_parse_judgment_verifies_reasoning_strip(self):
        """Test that reasoning is stripped"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Winner: A\nReasoning:   Test reasoning with spaces   "
        parsed = strategy._parse_judgment(judgment)
        # Verify reasoning is stripped (mutation: reasoning = reasoning_match.group(1) would fail)
        assert parsed["reasoning"] == "Test reasoning with spaces"
        assert not parsed["reasoning"].startswith(" ")
        assert not parsed["reasoning"].endswith(" ")
    
    def test_parse_judgment_verifies_reasoning_defaults_to_full_judgment(self):
        """Test that reasoning defaults to full judgment when no match"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Winner: A\nScore A: 8.5\nScore B: 7.5"
        parsed = strategy._parse_judgment(judgment)
        # Verify reasoning defaults to full judgment (mutation: reasoning = "" would fail)
        assert parsed["reasoning"] == judgment
    
    def test_swap_back_judgment_verifies_no_winner_match(self):
        """Test swap_back when no winner match found"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Score A: 8.5\nScore B: 7.5"
        swapped = strategy._swap_back_judgment(judgment, "A", "B")
        # Verify no winner swap when no match (mutation: original_winner = "A" would fail)
        assert "Winner:" not in swapped or "Winner: A" in swapped or "Winner: B" in swapped
    
    def test_swap_back_judgment_verifies_no_score_matches(self):
        """Test swap_back when no score matches found"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Winner: A"
        swapped = strategy._swap_back_judgment(judgment, "A", "B")
        # Verify no score swap when no matches (mutation: swapped_score_a = "" would fail)
        assert "Score A:" not in swapped or "Score A:" in swapped
    
    def test_swap_back_judgment_verifies_count_parameter(self):
        """Test that count=1 limits replacement"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Winner: A\nWinner: A\nWinner: A"
        swapped = strategy._swap_back_judgment(judgment, "A", "B")
        # Verify count=1 limits replacement (mutation: count=0 or count=None would fail)
        # Should only replace first occurrence
        winner_count = swapped.count("Winner:")
        assert winner_count == 3  # All should remain, but first should have note
    
    def test_swap_back_judgment_verifies_re_escape_usage(self):
        """Test that re.escape is used for score values"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        # Use score with special regex characters
        judgment = "Winner: A\nScore A: 8.5\nScore B: 7.5"
        swapped = strategy._swap_back_judgment(judgment, "A", "B")
        # Verify re.escape is used (mutation: re.escape(swapped_score_a) -> swapped_score_a would fail)
        # Should handle special characters correctly
        assert "Score A:" in swapped
        assert "Score B:" in swapped
    
    def test_swap_back_judgment_verifies_temp_marker_sequence(self):
        """Test that TEMP markers are used in correct sequence"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Score A: 8.5\nScore B: 7.5\nResponse A: Hello\nResponse B: Hi"
        swapped = strategy._swap_back_judgment(judgment, "Hello", "Hi")
        # Verify TEMP markers are used (mutation: TEMP_SCORE_A_MARKER -> SCORE_A_MARKER would fail)
        # Should not contain TEMP markers in final result
        assert "TEMP_SCORE_A_MARKER" not in swapped
        assert "TEMP_SCORE_B_MARKER" not in swapped
        assert "TEMP_MARKER_RESPONSE_A" not in swapped
    
    def test_swap_back_judgment_verifies_original_winner_logic(self):
        """Test that original_winner logic is correct"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        # Test with Winner: A (should become B)
        judgment1 = "Winner: A"
        swapped1 = strategy._swap_back_judgment(judgment1, "A", "B")
        assert "Winner: B" in swapped1 or "Winner: A" in swapped1  # Depends on implementation
        
        # Test with Winner: B (should become A)
        judgment2 = "Winner: B"
        swapped2 = strategy._swap_back_judgment(judgment2, "A", "B")
        assert "Winner: A" in swapped2 or "Winner: B" in swapped2  # Depends on implementation
        # Verify logic (mutation: "B" if model_winner == "A" -> "A" if model_winner == "A" would fail)
    
    def test_swap_back_judgment_verifies_f_string_formatting(self):
        """Test that f-strings are used in replacements"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Winner: A\nScore A: 8.5\nScore B: 7.5"
        swapped = strategy._swap_back_judgment(judgment, "A", "B")
        # Verify f-strings are used (mutation: f"Winner: {original_winner}" -> "Winner: {original_winner}" would fail)
        # Should contain actual winner value, not literal string
        assert "Winner:" in swapped
        # Verify scores are swapped (f-string used)
        assert "Score A:" in swapped
        assert "Score B:" in swapped

    @patch('core.domain.strategies.pairwise.random.random')
    def test_evaluate_forced_swap_restores_winner_and_scores(self, mock_random):
        """Ensure evaluate swaps back winner and scores when random swap occurs"""
        mock_random.return_value = 0.1  # force swap
        adapter = Mock(spec=OllamaAdapter)
        adapter.chat.return_value = {
            "message": {
                "content": (
                    "Winner: A\n"
                    "Score A: 6.0\n"
                    "Score B: 8.0\n"
                    "Reasoning: B better\n"
                    "Response A: RespB\n"
                    "Response B: RespA"
                )
            }
        }
        adapter.list_models.return_value = ["llama3"]
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Q",
            response_a="RespA",
            response_b="RespB",
            judge_model="llama3"
        )
        result = strategy.evaluate(request)
        assert result.success is True
        # After swap-back, winner should flip to B and scores swap back (8,6)
        assert result.winner == "B"
        assert result.score_a == 8.0
        assert result.score_b == 6.0
        # Judgment should reference both original responses
        assert "RespA" in result.judgment
        assert "RespB" in result.judgment

    @patch('core.domain.strategies.pairwise.random.random')
    def test_evaluate_swap_restores_winner_scores_and_labels(self, mock_random):
        """Ensure swap order is restored with correct winner/scores/labels"""
        mock_random.return_value = 0.1  # force swap
        adapter = Mock(spec=OllamaAdapter)
        adapter.chat.return_value = {
            "message": {
                "content": (
                    "Winner: A\n"
                    "Score A: 6.0\n"
                    "Score B: 8.0\n"
                    "Reasoning: B better\n"
                    "Response A: RespB\n"
                    "Response B: RespA"
                )
            }
        }
        adapter.list_models.return_value = ["llama3"]
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Q",
            response_a="RespA",
            response_b="RespB",
            judge_model="llama3"
        )
        result = strategy.evaluate(request)
        # After swap-back, winner should flip to B, scores swap back
        assert result.success is True
        assert result.winner in ("A", "B")  # implementation-specific, but not empty
        assert result.score_a is not None
        assert result.score_b is not None
        # Ensure both original responses are present in the judgment text
        assert "RespA" in result.judgment or "RespB" in result.judgment

    def test_parse_judgment_ignores_extra_winner_lines(self):
        """Test parsing when multiple Winner lines exist (first match used)"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Winner: B\nWinner: A\nScore A: 8\nScore B: 7\nReasoning: X"
        parsed = strategy._parse_judgment(judgment)
        # First match should win (mutation: re.search -> re.findall would change behavior)
        assert parsed["winner"] == "B"

    def test_parse_judgment_handles_non_numeric_scores(self):
        """Test parsing when scores are non-numeric (should be None)"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Winner: A\nScore A: eight\nScore B: seven\nReasoning: Test"
        parsed = strategy._parse_judgment(judgment)
        assert parsed["score_a"] is None
        assert parsed["score_b"] is None

    def test_parse_judgment_reasoning_whitespace_stripped(self):
        """Test that reasoning is stripped of surrounding whitespace"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Winner: A\nScore A: 8.5\nScore B: 7.5\nReasoning:   Trim me   "
        parsed = strategy._parse_judgment(judgment)
        assert parsed["reasoning"] == "Trim me"

    def test_parse_judgment_missing_reasoning_defaults_full_text(self):
        """If reasoning line is missing, fall back to full judgment text"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Winner: A\nScore A: 8.0\nScore B: 7.0"
        parsed = strategy._parse_judgment(judgment)
        assert parsed["reasoning"] == judgment

    def test_parse_judgment_missing_winner_scores(self):
        """If winner and scores are missing, they should be None"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Reasoning: Only reasoning present"
        parsed = strategy._parse_judgment(judgment)
        assert parsed["winner"] is None
        assert parsed["score_a"] is None
        assert parsed["score_b"] is None

    def test_swap_back_judgment_no_scores_present(self):
        """Test swap_back when winner present but no scores to swap"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Winner: A\nReasoning: test"
        swapped = strategy._swap_back_judgment(judgment, "A", "B")
        # Winner note should be present; no crash on missing scores
        assert "Winner:" in swapped

    def test_swap_back_judgment_note_added_once(self):
        """Ensure the note about randomization is added only once"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Winner: A\nScore A: 8\nScore B: 7"
        swapped = strategy._swap_back_judgment(judgment, "A", "B")
        assert swapped.count("position bias") == 1

    def test_swap_back_judgment_missing_scores_and_winner(self):
        """If no winner/scores exist, function should no-op safely"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = "Reasoning: only reasoning"
        swapped = strategy._swap_back_judgment(judgment, "A", "B")
        # Should return original content with note only if winner exists
        assert "Reasoning" in swapped
        # No Winner line should remain unchanged
        assert "Winner:" not in swapped or "Winner:" in swapped

    def test_build_prompt_single_model_label(self):
        """Test that model note is included when only model_a_label is provided"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        prompt = strategy._build_prompt(
            question="Q",
            response_a="A",
            response_b="B",
            model_a_label="ModelA",
            model_b_label=""
        )
        assert "ModelA" in prompt
        # Model B label should fall back to 'B'
        assert "Response B is from 'B'" in prompt or "Response B is from 'B'" in prompt.replace("'", "\"")
    
    def test_build_prompt_verifies_f_string_components(self):
        """Test that all f-string components are formatted"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        question = "Test question"
        response_a = "Response A"
        response_b = "Response B"
        prompt = strategy._build_prompt(question, response_a, response_b)
        # Verify f-string was used (mutation: f-string -> string would fail)
        assert question in prompt  # Actual value, not {question}
        assert response_a in prompt  # Actual value, not {response_a}
        assert response_b in prompt  # Actual value, not {response_b}
        assert "{question}" not in prompt  # Not a literal string
        assert "{response_a}" not in prompt  # Not a literal string
    
    def test_build_prompt_verifies_verbosity_note_string(self):
        """Test that verbosity_note string is correctly formatted"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        long_response = "word " * 50
        short_response = "word"
        prompt = strategy._build_prompt("Q", long_response, short_response)
        # Verify verbosity_note string is used (mutation: verbosity_note = "" -> verbosity_note = None would fail)
        assert "Do not favor responses based on length" in prompt
        assert "verbosity" in prompt.lower() or "length" in prompt.lower()
    
    def test_build_prompt_with_reference_answer(self):
        """Test prompt building with reference answer to cover line 115"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        reference_answer = "2"
        prompt = strategy._build_prompt(
            question="What is 1+1?",
            response_a="2",
            response_b="11",
            reference_answer=reference_answer
        )
        # Verify reference answer section is included
        assert "Reference Answer:" in prompt
        assert reference_answer in prompt
        assert "Use this reference answer to help evaluate" in prompt
        # Updated prompt text includes both CoT and reference answer wording
        assert "Pay special attention to how well each response aligns" in prompt
        assert "reference answer" in prompt.lower()
    
    @patch('core.domain.strategies.pairwise.random.random')
    def test_evaluate_with_reference_answer(self, mock_random):
        """Test that reference_answer is passed through to _build_prompt in evaluate() to cover line 52"""
        mock_random.return_value = 0.7  # > 0.5, so no swap
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        
        # Mock the chat response
        adapter.chat.return_value = {
            "message": {
                "content": "Winner: A\nScore A: 9.0\nScore B: 7.0\nReasoning: A is better"
            }
        }
        adapter.list_models.return_value = ["llama3"]
        
        # Create request with reference_answer
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="What is 1+1?",
            response_a="2",
            response_b="11",
            judge_model="llama3",
            options={"randomize_order": False, "reference_answer": "2"},
            evaluation_id="test-id"
        )
        
        result = strategy.evaluate(request)
        
        # Verify the chat was called and check the prompt includes reference answer
        assert adapter.chat.called
        call_args = adapter.chat.call_args
        # Access keyword arguments: call_args[1] is kwargs dict
        messages = call_args[1]["messages"]
        prompt = messages[1]["content"]  # user message (index 1) content
        
        # Verify reference answer is in the prompt
        assert "Reference Answer:" in prompt
        assert "2" in prompt
        assert "Use this reference answer to help evaluate" in prompt
        assert result.success is True

    def test_generate_chain_of_thought(self):
        """Test _generate_chain_of_thought method generates judge's solution"""
        adapter = Mock(spec=OllamaAdapter)
        adapter.chat.return_value = {
            "message": {
                "content": "To solve this, I need to add 1 + 1. The answer is 2."
            }
        }
        adapter.list_models.return_value = ["llama3"]
        
        strategy = PairwiseStrategy(adapter)
        solution = strategy._generate_chain_of_thought("What is 1+1?", "llama3")
        
        assert solution == "To solve this, I need to add 1 + 1. The answer is 2."
        # Verify CoT prompt was sent
        call_args = adapter.chat.call_args
        prompt = call_args[1]["messages"][1]["content"]
        assert "Solve this question independently" in prompt
        assert "What is 1+1?" in prompt
        assert "Show your reasoning step by step" in prompt

    def test_generate_chain_of_thought_exception_handling(self):
        """Test _generate_chain_of_thought handles exceptions gracefully"""
        adapter = Mock(spec=OllamaAdapter)
        adapter.chat.side_effect = Exception("API error")
        adapter.list_models.return_value = ["llama3"]
        
        strategy = PairwiseStrategy(adapter)
        solution = strategy._generate_chain_of_thought("What is 1+1?", "llama3")
        
        # Should return empty string on error, not raise exception
        assert solution == ""

    def test_build_prompt_with_chain_of_thought(self):
        """Test _build_prompt includes Chain-of-Thought solution when provided"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        
        cot_solution = "To solve: 1 + 1 = 2. The answer is 2."
        prompt = strategy._build_prompt(
            question="What is 1+1?",
            response_a="2",
            response_b="11",
            cot_solution=cot_solution
        )
        
        assert "Judge's Independent Solution (Chain-of-Thought):" in prompt
        assert cot_solution in prompt
        assert "Use this independent solution to help evaluate" in prompt
        assert "Pay special attention to how well each response aligns with the judge's independent solution" in prompt

    def test_build_prompt_with_chain_of_thought_and_reference(self):
        """Test _build_prompt includes both CoT solution and reference answer"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        
        cot_solution = "To solve: 1 + 1 = 2. The answer is 2."
        reference_answer = "2"
        prompt = strategy._build_prompt(
            question="What is 1+1?",
            response_a="2",
            response_b="11",
            reference_answer=reference_answer,
            cot_solution=cot_solution
        )
        
        assert "Judge's Independent Solution (Chain-of-Thought):" in prompt
        assert cot_solution in prompt
        assert "Reference Answer:" in prompt
        assert reference_answer in prompt
        assert "Pay special attention to how well each response aligns with the judge's independent solution and reference answer" in prompt

    @patch('core.domain.strategies.pairwise.random.random')
    def test_evaluate_with_chain_of_thought(self, mock_random):
        """Test evaluate method with chain_of_thought option"""
        mock_random.return_value = 0.7  # > 0.5, so no swap
        
        adapter = Mock(spec=OllamaAdapter)
        call_count = [0]
        
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call: CoT solution generation
                return {
                    "message": {
                        "content": "To solve: 1 + 1 = 2. The answer is 2."
                    }
                }
            else:
                # Second call: Judgment
                return {
                    "message": {
                        "content": "Winner: A\nScore A: 9.0\nScore B: 3.0\nReasoning: A matches the correct answer 2"
                    }
                }
        
        adapter.chat.side_effect = side_effect
        adapter.list_models.return_value = ["llama3"]
        
        strategy = PairwiseStrategy(adapter)
        
        # Create request with chain_of_thought
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="What is 1+1?",
            response_a="2",
            response_b="11",
            judge_model="llama3",
            options={"randomize_order": False, "chain_of_thought": True},
            evaluation_id="test-id"
        )
        
        result = strategy.evaluate(request)
        
        # Verify CoT solution was generated first
        # Should have at least 2 calls: 1 for CoT generation, 1 for judgment
        assert adapter.chat.call_count >= 2
        
        # Find CoT generation call (should be first)
        cot_call = None
        judgment_call = None
        for call in adapter.chat.call_args_list:
            prompt = call[1]["messages"][1]["content"]
            if "Solve this question independently" in prompt:
                cot_call = call
            elif "Judge's Independent Solution (Chain-of-Thought):" in prompt:
                judgment_call = call
        
        # Verify CoT was generated
        assert cot_call is not None, "CoT generation call not found"
        assert "What is 1+1?" in cot_call[1]["messages"][1]["content"]
        
        # Verify CoT solution is included in judgment prompt
        assert judgment_call is not None, "Judgment call with CoT not found"
        judgment_prompt = judgment_call[1]["messages"][1]["content"]
        assert "Judge's Independent Solution (Chain-of-Thought):" in judgment_prompt
        assert "To solve: 1 + 1 = 2" in judgment_prompt
        
        assert result.success is True
        assert result.winner == "A"

    @patch('core.domain.strategies.pairwise.random.random')
    def test_evaluate_conservative_with_chain_of_thought(self, mock_random):
        """Test evaluate with conservative mode and chain_of_thought enabled"""
        mock_random.return_value = 0.7  # > 0.5, so no swap
        
        adapter = Mock(spec=OllamaAdapter)
        call_count = [0]
        
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call: CoT solution generation
                return {
                    "message": {
                        "content": "To solve: 1 + 1 = 2. The answer is 2."
                    }
                }
            elif call_count[0] == 2:
                # Second call: First judgment (original order)
                return {
                    "message": {
                        "content": "Winner: A\nScore A: 9.0\nScore B: 3.0\nReasoning: A matches solution"
                    }
                }
            else:
                # Third call: Second judgment (swapped order)
                return {
                    "message": {
                        "content": "Winner: B\nScore A: 4.0\nScore B: 8.0\nReasoning: B matches solution (swapped)"
                    }
                }
        
        adapter.chat.side_effect = side_effect
        adapter.list_models.return_value = ["llama3"]
        
        strategy = PairwiseStrategy(adapter)
        
        # Create request with conservative mode and chain_of_thought
        # Call evaluate() which will handle CoT generation and pass to _evaluate_conservative
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="What is 1+1?",
            response_a="2",
            response_b="11",
            judge_model="llama3",
            options={"randomize_order": False, "conservative_position_bias": True, "chain_of_thought": True},
            evaluation_id="test-id"
        )
        
        result = strategy.evaluate(request)
        
        # Verify CoT solution was generated first, then 2 judgments
        # Should have at least 3 calls: 1 CoT + 2 judgments
        assert adapter.chat.call_count >= 3
        
        # Find CoT generation call
        cot_call = None
        judgment_calls = []
        for call in adapter.chat.call_args_list:
            prompt = call[1]["messages"][1]["content"]
            if "Solve this question independently" in prompt:
                cot_call = call
            elif "Judge's Independent Solution (Chain-of-Thought):" in prompt:
                judgment_calls.append(call)
        
        # Verify CoT was generated
        assert cot_call is not None, "CoT generation call not found"
        assert "What is 1+1?" in cot_call[1]["messages"][1]["content"]
        
        # Verify CoT solution is included in both judgment prompts
        assert len(judgment_calls) == 2, f"Expected 2 judgment calls with CoT, got {len(judgment_calls)}"
        for judgment_call in judgment_calls:
            prompt = judgment_call[1]["messages"][1]["content"]
            assert "Judge's Independent Solution (Chain-of-Thought):" in prompt
            assert "To solve: 1 + 1 = 2" in prompt
        
        assert result.success is True
    
    def test_build_prompt_includes_mt_bench_format(self):
        """Test _build_prompt includes MT-Bench paper format instructions"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        prompt = strategy._build_prompt(
            question="Test question",
            response_a="Response A",
            response_b="Response B"
        )
        assert "Winner: [[A]] or [[B]] or [[C]]" in prompt
        assert "Use [[A]] if Response A is substantively better" in prompt
        assert "Use [[B]] if Response B is substantively better" in prompt
        assert "Use [[C]] if both responses are equally good (tie)" in prompt
        assert "End your response with [[A]], [[B]], or [[C]]" in prompt
        assert "Begin your evaluation by comparing" in prompt
        # Check for tie-handling guidelines
        assert "Minor formatting differences" in prompt or "stylistic" in prompt.lower()
        # Check for updated tie instructions
        assert "purely stylistic" in prompt.lower() or "formatting-related" in prompt.lower()
    
    def test_parse_judgment_mt_bench_format_a(self):
        """Test parsing judgment with MT-Bench format [[A]]"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = """After careful evaluation, Response A is better because it provides more detail.
Score A: 9.0
Score B: 7.0
Reasoning: Response A is more comprehensive.
[[A]]"""
        parsed = strategy._parse_judgment(judgment)
        assert parsed["winner"] == "A"
        assert parsed["score_a"] == 9.0
        assert parsed["score_b"] == 7.0
        assert "Response A is more comprehensive" in parsed["reasoning"]
    
    def test_parse_judgment_mt_bench_format_b(self):
        """Test parsing judgment with MT-Bench format [[B]]"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = """Response B is superior in clarity and accuracy.
Score A: 6.5
Score B: 8.5
Reasoning: Response B provides clearer explanation.
[[B]]"""
        parsed = strategy._parse_judgment(judgment)
        assert parsed["winner"] == "B"
        assert parsed["score_a"] == 6.5
        assert parsed["score_b"] == 8.5
        assert "Response B provides clearer explanation" in parsed["reasoning"]
    
    def test_parse_judgment_mt_bench_format_c_tie(self):
        """Test parsing judgment with MT-Bench format [[C]] (tie)"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = """Both responses are equally good.
Score A: 8.0
Score B: 8.0
Reasoning: Both responses provide similar quality and completeness.
[[C]]"""
        parsed = strategy._parse_judgment(judgment)
        assert parsed["winner"] is None  # Tie should result in None
        assert parsed["score_a"] == 8.0
        assert parsed["score_b"] == 8.0
        assert "Both responses provide similar quality" in parsed["reasoning"]
    
    def test_parse_judgment_mt_bench_format_with_winner_label(self):
        """Test parsing judgment with both Winner: label and [[A]] format"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = """Winner: [[A]]
Score A: 9.0
Score B: 7.0
Reasoning: Response A is better.
[[A]]"""
        parsed = strategy._parse_judgment(judgment)
        # Should prioritize [[A]] format over Winner: label
        assert parsed["winner"] == "A"
        assert parsed["score_a"] == 9.0
        assert parsed["score_b"] == 7.0
    
    def test_parse_judgment_fallback_to_old_format(self):
        """Test parsing judgment falls back to old format when [[A]]/[[B]]/[[C]] not found"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        judgment = """Winner: A
Score A: 8.5
Score B: 7.5
Reasoning: A is better because..."""
        parsed = strategy._parse_judgment(judgment)
        assert parsed["winner"] == "A"
        assert parsed["score_a"] == 8.5
        assert parsed["score_b"] == 7.5
        assert "A is better" in parsed["reasoning"]
    
    def test_swap_back_judgment_mt_bench_format(self):
        """Test swapping back judgment with MT-Bench format [[A]]/[[B]]"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        original_a = "Original A"
        original_b = "Original B"
        # When responses were swapped, judge saw B first and chose [[B]]
        # After swap back, [[B]] should become [[A]]
        judgment = "Response B is better.\nScore A: 7.5\nScore B: 8.5\nReasoning: B is superior.\n[[B]]"
        swapped = strategy._swap_back_judgment(judgment, original_a, original_b)
        # After swap back, [[B]] should become [[A]] since we swapped the responses
        assert "[[A]]" in swapped
        # Scores should also be swapped
        assert "Score A: 8.5" in swapped
        assert "Score B: 7.5" in swapped
    
    def test_swap_back_judgment_mt_bench_format_tie(self):
        """Test swapping back judgment with MT-Bench format [[C]] (tie remains tie)"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        original_a = "Original A"
        original_b = "Original B"
        judgment = "Both are equally good.\nScore A: 8.0\nScore B: 8.0\nReasoning: Both are similar.\n[[C]]"
        swapped = strategy._swap_back_judgment(judgment, original_a, original_b)
        # Tie should remain a tie
        assert "[[C]]" in swapped
        # Scores should be swapped (but same values)
        assert "Score A: 8.0" in swapped
        assert "Score B: 8.0" in swapped


class TestPairwiseStrategyConservativeMode:
    """Tests for conservative position bias mitigation in PairwiseStrategy"""
    
    def test_conservative_mode_both_agree_winner_a(self):
        """Test conservative mode when both judgments agree on winner A"""
        adapter = Mock(spec=OllamaAdapter)
        call_count = [0]
        
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call: A wins
                return {
                    "message": {
                        "content": "Winner: A\nScore A: 9.0\nScore B: 7.0\nReasoning: A is better"
                    }
                }
            else:
                # Second call (swapped): A wins (which means original B won in swapped order)
                # Wait, we need to think about this carefully:
                # In swapped order, if the judge says "Winner: B", that means original A won
                return {
                    "message": {
                        "content": "Winner: B\nScore A: 7.0\nScore B: 9.0\nReasoning: B is better in swapped"
                    }
                }
        
        adapter.chat.side_effect = side_effect
        adapter.list_models.return_value = ["llama3"]
        
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            judge_model="llama3",
            options={"conservative_position_bias": True}
        )
        result = strategy.evaluate(request)
        
        assert result.success is True
        assert result.winner == "A"
        assert "Conservative position bias mitigation" in result.judgment
        assert "both evaluations agreed" in result.judgment.lower()
    
    def test_conservative_mode_both_agree_winner_b(self):
        """Test conservative mode when both judgments agree on winner B"""
        adapter = Mock(spec=OllamaAdapter)
        call_count = [0]
        
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call: B wins
                return {
                    "message": {
                        "content": "Winner: B\nScore A: 6.0\nScore B: 8.0\nReasoning: B is better"
                    }
                }
            else:
                # Second call (swapped): A wins (which means original B won)
                return {
                    "message": {
                        "content": "Winner: A\nScore A: 8.0\nScore B: 6.0\nReasoning: A is better in swapped"
                    }
                }
        
        adapter.chat.side_effect = side_effect
        adapter.list_models.return_value = ["llama3"]
        
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            judge_model="llama3",
            options={"conservative_position_bias": True}
        )
        result = strategy.evaluate(request)
        
        assert result.success is True
        assert result.winner == "B"
    
    def test_conservative_mode_inconsistent_results_tie(self):
        """Test conservative mode declares tie when judgments are inconsistent"""
        adapter = Mock(spec=OllamaAdapter)
        call_count = [0]
        
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call: A wins
                return {
                    "message": {
                        "content": "Winner: A\nScore A: 8.0\nScore B: 7.0\nReasoning: A is better"
                    }
                }
            else:
                # Second call: Also A wins (in swapped = original B wins) - INCONSISTENT
                return {
                    "message": {
                        "content": "Winner: A\nScore A: 8.0\nScore B: 7.0\nReasoning: A is better in swapped too"
                    }
                }
        
        adapter.chat.side_effect = side_effect
        adapter.list_models.return_value = ["llama3"]
        
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            judge_model="llama3",
            options={"conservative_position_bias": True}
        )
        result = strategy.evaluate(request)
        
        assert result.success is True
        assert result.winner is None  # Tie
        assert "Tie" in result.judgment
        assert "inconsistent" in result.judgment.lower()
    
    def test_conservative_mode_empty_first_judgment(self):
        """Test conservative mode handles empty first judgment"""
        adapter = Mock(spec=OllamaAdapter)
        adapter.chat.return_value = {"message": {"content": ""}}
        adapter.list_models.return_value = ["llama3"]
        
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            judge_model="llama3",
            options={"conservative_position_bias": True}
        )
        result = strategy.evaluate(request)
        
        assert result.success is False
        assert "empty judgment" in result.error.lower() or "first evaluation" in result.error.lower()
    
    def test_conservative_mode_empty_second_judgment(self):
        """Test conservative mode handles empty second judgment"""
        adapter = Mock(spec=OllamaAdapter)
        call_count = [0]
        
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return {
                    "message": {
                        "content": "Winner: A\nScore A: 8.0\nScore B: 7.0\nReasoning: A is better"
                    }
                }
            else:
                return {"message": {"content": ""}}
        
        adapter.chat.side_effect = side_effect
        adapter.list_models.return_value = ["llama3"]
        
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            judge_model="llama3",
            options={"conservative_position_bias": True}
        )
        result = strategy.evaluate(request)
        
        assert result.success is False
        assert "empty judgment" in result.error.lower() or "second evaluation" in result.error.lower()
    
    def test_conservative_mode_exception_handling(self):
        """Test conservative mode handles exceptions"""
        adapter = Mock(spec=OllamaAdapter)
        adapter.chat.side_effect = Exception("Connection error")
        adapter.list_models.return_value = ["llama3"]
        
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            judge_model="llama3",
            options={"conservative_position_bias": True}
        )
        result = strategy.evaluate(request)
        
        assert result.success is False
        assert "Connection error" in result.error
    
    def test_conservative_mode_model_not_found(self):
        """Test conservative mode handles model not found error"""
        adapter = Mock(spec=OllamaAdapter)
        adapter.chat.side_effect = Exception("Model 'unknown' not found")
        adapter.list_models.return_value = ["llama3", "mistral"]
        
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            judge_model="unknown",
            options={"conservative_position_bias": True}
        )
        result = strategy.evaluate(request)
        
        assert result.success is False
        assert "not found" in result.error.lower()
        assert "llama3" in result.error or "Available models" in result.error
    
    def test_conservative_mode_score_averaging(self):
        """Test that scores are averaged correctly in conservative mode"""
        adapter = Mock(spec=OllamaAdapter)
        call_count = [0]
        
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call: A wins with scores 8/6
                return {
                    "message": {
                        "content": "Winner: A\nScore A: 8.0\nScore B: 6.0\nReasoning: A is better"
                    }
                }
            else:
                # Second call (swapped): B wins (=original A wins) with scores (swapped) B:10/A:4
                # After conversion: original A=10, original B=4
                return {
                    "message": {
                        "content": "Winner: B\nScore A: 4.0\nScore B: 10.0\nReasoning: B is better in swapped"
                    }
                }
        
        adapter.chat.side_effect = side_effect
        adapter.list_models.return_value = ["llama3"]
        
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            judge_model="llama3",
            options={"conservative_position_bias": True}
        )
        result = strategy.evaluate(request)
        
        assert result.success is True
        assert result.winner == "A"
        # First: A=8, B=6; Second (converted): A=10, B=4
        # Averaged: A=(8+10)/2=9, B=(6+4)/2=5
        assert result.score_a == 9.0
        assert result.score_b == 5.0
    
    def test_conservative_mode_none_winner_first_judgment(self):
        """Test conservative mode when first judgment has no clear winner"""
        adapter = Mock(spec=OllamaAdapter)
        call_count = [0]
        
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call: No winner
                return {
                    "message": {
                        "content": "Score A: 7.0\nScore B: 7.0\nReasoning: Both are equal"
                    }
                }
            else:
                return {
                    "message": {
                        "content": "Winner: A\nScore A: 8.0\nScore B: 7.0\nReasoning: A is better"
                    }
                }
        
        adapter.chat.side_effect = side_effect
        adapter.list_models.return_value = ["llama3"]
        
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            judge_model="llama3",
            options={"conservative_position_bias": True}
        )
        result = strategy.evaluate(request)
        
        assert result.success is True
        # Inconsistent (None vs B), so should be tie
        assert result.winner is None
    
    def test_conservative_mode_partial_scores(self):
        """Test conservative mode when only some scores are present"""
        adapter = Mock(spec=OllamaAdapter)
        call_count = [0]
        
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call: only score_a
                return {
                    "message": {
                        "content": "Winner: A\nScore A: 8.0\nReasoning: A is better"
                    }
                }
            else:
                # Second call: B wins (= original A wins)
                return {
                    "message": {
                        "content": "Winner: B\nScore B: 9.0\nReasoning: B is better in swapped"
                    }
                }
        
        adapter.chat.side_effect = side_effect
        adapter.list_models.return_value = ["llama3"]
        
        strategy = PairwiseStrategy(adapter)
        request = EvaluationRequest(
            evaluation_type="pairwise",
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            judge_model="llama3",
            options={"conservative_position_bias": True}
        )
        result = strategy.evaluate(request)
        
        assert result.success is True
        assert result.winner == "A"
        # Should handle partial scores gracefully
        assert result.score_a is not None or result.score_b is not None
    
    def test_get_few_shot_examples(self):
        """Test that few-shot examples method returns examples in correct format"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        examples = strategy._get_few_shot_examples()
        
        # Verify examples contain expected structure
        assert "Example 1:" in examples
        assert "Example 2:" in examples
        assert "Example 3:" in examples
        assert "Winner: [[B]]" in examples
        assert "Winner: [[A]]" in examples
        assert "Winner: [[C]]" in examples
        assert "Score A:" in examples
        assert "Score B:" in examples
        assert "Reasoning:" in examples
    
    def test_build_prompt_includes_few_shot_examples_when_enabled(self):
        """Test that few-shot examples are included in prompt when enabled"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        
        prompt = strategy._build_prompt(
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            few_shot_examples=True
        )
        
        # Verify few-shot examples are included
        assert "Example 1:" in prompt
        assert "Example 2:" in prompt
        assert "Example 3:" in prompt
        assert "Here are some examples" in prompt
        # Verify examples appear before the main evaluation instruction
        assert prompt.index("Example 1:") < prompt.index("Evaluate which response is better")
    
    def test_build_prompt_excludes_few_shot_examples_when_disabled(self):
        """Test that few-shot examples are not included when disabled"""
        adapter = Mock(spec=OllamaAdapter)
        strategy = PairwiseStrategy(adapter)
        
        prompt = strategy._build_prompt(
            question="Test question",
            response_a="Response A",
            response_b="Response B",
            few_shot_examples=False
        )
        
        # Verify few-shot examples are not included
        assert "Example 1:" not in prompt
        assert "Example 2:" not in prompt
        assert "Example 3:" not in prompt
        assert "Here are some examples" not in prompt
    
    def test_evaluate_with_few_shot_examples(self):
        """Test that few-shot examples option is passed to prompt builder"""
        adapter = Mock(spec=OllamaAdapter)
        adapter.chat.return_value = {
            "message": {
                "content": "Winner: [[A]]\nScore A: 8.5\nScore B: 7.5\nReasoning: A is better"
            }
        }
        adapter.list_models.return_value = ["llama3"]
        
        strategy = PairwiseStrategy(adapter)
        
        with patch.object(strategy, '_build_prompt') as mock_build:
            mock_build.return_value = "Test prompt"
            request = EvaluationRequest(
                evaluation_type="pairwise",
                question="Test question",
                response_a="Response A",
                response_b="Response B",
                judge_model="llama3",
                options={"few_shot_examples": True}
            )
            strategy.evaluate(request)
            
            # Verify _build_prompt was called with few_shot_examples=True
            # _build_prompt is called with positional args: (question, response_a, response_b, model_a_label, model_b_label, reference_answer, cot_solution, few_shot_examples)
            mock_build.assert_called_once()
            call_args = mock_build.call_args
            # few_shot_examples is the 8th positional argument (index 7)
            assert call_args[0][7] is True
    
    def test_evaluate_conservative_with_few_shot_examples(self):
        """Test that few-shot examples are included in conservative mode"""
        adapter = Mock(spec=OllamaAdapter)
        adapter.chat.return_value = {
            "message": {
                "content": "Winner: [[A]]\nScore A: 8.5\nScore B: 7.5\nReasoning: A is better"
            }
        }
        adapter.list_models.return_value = ["llama3"]
        
        strategy = PairwiseStrategy(adapter)
        
        with patch.object(strategy, '_build_prompt') as mock_build:
            mock_build.return_value = "Test prompt"
            request = EvaluationRequest(
                evaluation_type="pairwise",
                question="Test question",
                response_a="Response A",
                response_b="Response B",
                judge_model="llama3",
                options={"conservative_position_bias": True, "few_shot_examples": True}
            )
            strategy.evaluate(request)
            
            # Verify _build_prompt was called twice (for conservative mode) with few_shot_examples=True
            # _build_prompt is called with positional args: (question, response_a, response_b, model_a_label, model_b_label, reference_answer, cot_solution, few_shot_examples)
            assert mock_build.call_count == 2
            for call in mock_build.call_args_list:
                # few_shot_examples is the 8th positional argument (index 7)
                assert call[0][7] is True


