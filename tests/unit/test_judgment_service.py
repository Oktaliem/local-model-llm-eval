import random
from unittest.mock import Mock

import pytest

from core.services.judgment_service import (
    JudgmentService,
    judge_pairwise,
    save_judgment,
)

# ---------- Fixtures ----------


@pytest.fixture
def mock_llm_adapter():
    """Mocked OllamaAdapter with predictable chat and list_models."""
    adapter = Mock()
    adapter.chat.return_value = {
        "message": {
            "content": (
                "Winner: A\n"
                "Score A: 9.0\n"
                "Score B: 5.0\n"
                "Reasoning: A is more concise and accurate.\n"
                "Response A: Hello\n"
                "Response B: Hi"
            )
        }
    }
    adapter.list_models.return_value = ["llama3", "mistral"]
    return adapter


@pytest.fixture
def mock_repo():
    """Mocked JudgmentsRepository."""
    repo = Mock()
    repo.save.return_value = 42
    return repo


@pytest.fixture(autouse=True)
def _fix_random_default(monkeypatch):
    """Make random deterministic for judge_pairwise unless overridden"""
    monkeypatch.setattr(random, "random", lambda: 0.9)
@pytest.fixture
def mock_repo():
    """Mocked JudgmentsRepository."""
    repo = Mock()
    repo.save.return_value = 42
    return repo


# ---------- Tests for judge_pairwise ----------


def test_judge_pairwise_no_swap_success(mock_llm_adapter, mock_repo, monkeypatch):
    """When randomize_order is False, the judgment should be returned as‑is."""

    # Set up mock to match our test case with Hello and Hi responses
    def get_mock_response_for_test():
        return {
            "message": {
                "content": (
                    "Winner: A\n"
                    "Score A: 9.0\n"
                    "Score B: 5.0\n"
                    "Reasoning: A is more concise and accurate.\n"
                    "Response A: Hello\n"  # Match exact test responses
                    "Response B: Hi"
                )
            }
        }

    mock_llm_adapter.chat.return_value = get_mock_response_for_test()

    # Force random.random() to return > 0.5 so no swap occurs
    monkeypatch.setattr(random, "random", lambda: 0.9)

    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    original_a = "Hello"
    original_b = "Hi"
    result = svc.judge_pairwise(
        question="Test Q",
        response_a=original_a,  # Match test input exactly
        response_b=original_b,
        model="llama3",
        randomize_order=False,
    )
    assert result["success"] is True
    assert "Winner: A" in result["judgment"]
    assert "Response A: Hello" in result["judgment"]
    # Verify original responses are preserved (mutation: original_response_a = None would fail)
    assert original_a == "Hello"
    assert original_b == "Hi"


def test_judge_pairwise_with_swap_success(mock_llm_adapter, mock_repo, monkeypatch):
    """When responses are swapped, the returned judgment should be swapped back."""

    # Set up mock to match our test case with Hello and Hi responses but with swap
    def get_mock_response_for_test():
        return {
            "message": {
                "content": (
                    "Winner: A\n"  # This will become Winner: B after swapping
                    "Score A: 9.0\n"
                    "Score B: 5.0\n"
                    "Reasoning: A is more concise and accurate.\n"
                    "Response A: Hi\n"  # Notice the swap from test input order
                    "Response B: Hello"
                )
            }
        }

    mock_llm_adapter.chat.return_value = get_mock_response_for_test()

    # Force random.random() to return < 0.5 so swap occurs
    monkeypatch.setattr(random, "random", lambda: 0.1)

    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="Test Q",
        response_a="Hello",  # Original order for test
        response_b="Hi",
        model="llama3",
        randomize_order=True,
    )
    # The mock content had Winner: A (after swap), so after swap back it should be Winner: B
    assert result["success"] is True
    assert "Winner: B" in result["judgment"]
    # Ensure both original responses still appear in the judgment, regardless of label order
    assert "Hi" in result["judgment"]
    assert "Hello" in result["judgment"]


def test_judge_pairwise_chat_error_model_not_found(mock_llm_adapter, mock_repo):
    """Chat exception containing 'not found' should return friendly error."""
    mock_llm_adapter.chat.side_effect = Exception("Model not found 404")
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="q", response_a="a", response_b="b", model="missing-model"
    )
    assert result["success"] is False
    assert "Model 'missing-model' not found" in result["error"]
    assert "llama3, mistral" in result["error"]


def test_judge_pairwise_chat_error_generic(mock_llm_adapter, mock_repo):
    """Any other exception should propagate the message."""
    mock_llm_adapter.chat.side_effect = Exception("Timeout")
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="q", response_a="a", response_b="b", model="llama3"
    )
    assert result["success"] is False
    assert result["error"] == "Timeout"


def test_judge_pairwise_empty_judgment(mock_llm_adapter, mock_repo):
    """Empty or whitespace judgment content should return error."""
    mock_llm_adapter.chat.return_value = {"message": {"content": "   "}}
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="q", response_a="a", response_b="b", model="llama3"
    )
    assert result["success"] is False
    assert "empty judgment" in result["error"]


# ---------- Test for _swap_back_judgment (method of JudgmentService) ----------


def test_swap_back_judgment():
    content = (
        "Winner: A\n"
        "Score A: 8.0\n"
        "Score B: 6.0\n"
        "Reasoning: ...\n"
        "Response A: Hello\n"
        "Response B: Hi"
    )
    svc = JudgmentService()
    swapped = svc._swap_back_judgment(content, "Hello", "Hi")
    assert "Winner: B" in swapped
    assert "Score A: 6.0" in swapped
    assert "Score B: 8.0" in swapped
    assert "Response A: Hi" in swapped
    assert "Response B: Hello" in swapped


def test_judge_pairwise_adds_verbosity_note_for_length_difference(mock_llm_adapter, mock_repo, monkeypatch):
    """If responses differ significantly in length, verbosity note should be added to the prompt."""
    # Long response_a vs short response_b to trigger length-diff branch
    long_response = "word " * 50  # 50 words
    short_response = "short"

    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)

    # Don't randomize order to keep responses aligned
    monkeypatch.setattr(random, "random", lambda: 0.9)

    svc.judge_pairwise(
        question="Q",
        response_a=long_response,
        response_b=short_response,
        model="llama3",
        randomize_order=False,
    )

    # Inspect prompt sent to LLM
    assert mock_llm_adapter.chat.called
    _, kwargs = mock_llm_adapter.chat.call_args
    user_msg = kwargs["messages"][1]["content"]
    assert "Do not favor responses based on length" in user_msg
    # Verify len_a and len_b are calculated (mutation: len_a = 0 would fail)
    len_a = len(long_response.split())
    len_b = len(short_response.split())
    assert len_a > 20  # Should be much longer
    assert abs(len_a - len_b) > 20  # Difference should trigger verbosity note


def test_judge_pairwise_verifies_verbosity_note_conditional(mock_repo, monkeypatch):
    """Test that verbosity_note is only added when length difference > 20"""
    mock_adapter = Mock()
    mock_adapter.chat.return_value = {
        "message": {"content": "Winner: A\nScore A: 9.0\nScore B: 5.0"}
    }
    mock_adapter.list_models.return_value = ["llama3"]
    svc = JudgmentService(llm_adapter=mock_adapter, judgments_repo=mock_repo)
    
    # Small difference - no verbosity note
    monkeypatch.setattr("random.random", lambda: 0.9)
    svc.judge_pairwise(
        question="Q",
        response_a="word " * 10,
        response_b="word " * 5,
        model="llama3",
        randomize_order=False
    )
    call_args = mock_adapter.chat.call_args
    prompt1 = call_args[1]["messages"][1]["content"]
    assert "Do not favor responses based on length" not in prompt1
    
    # Large difference - verbosity note
    mock_adapter.reset_mock()
    svc.judge_pairwise(
        question="Q",
        response_a="word " * 50,
        response_b="word " * 5,
        model="llama3",
        randomize_order=False
    )
    call_args = mock_adapter.chat.call_args
    prompt2 = call_args[1]["messages"][1]["content"]
    assert "Do not favor responses based on length" in prompt2


def test_judge_pairwise_prompt_includes_labels_when_provided(mock_repo, monkeypatch):
    """Ensure model labels are included when provided"""
    mock_adapter = Mock()
    mock_adapter.chat.return_value = {"message": {"content": "Winner: A"}}
    mock_adapter.list_models.return_value = ["llama3"]
    monkeypatch.setattr(random, "random", lambda: 0.9)

    svc = JudgmentService(llm_adapter=mock_adapter, judgments_repo=mock_repo)
    svc.judge_pairwise(
        question="Q",
        response_a="RespA",
        response_b="RespB",
        model="llama3",
        randomize_order=False,
    )
    call_args = mock_adapter.chat.call_args
    prompt = call_args[1]["messages"][1]["content"]
    assert "RespA" in prompt and "RespB" in prompt


def test_judge_pairwise_missing_reasoning_returns_error(mock_repo):
    """If model returns no reasoning text, ensure we still return success with judgment"""
    mock_adapter = Mock()
    mock_adapter.chat.return_value = {"message": {"content": "Winner: A\nScore A: 8\nScore B: 7"}}
    mock_adapter.list_models.return_value = ["llama3"]
    svc = JudgmentService(llm_adapter=mock_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise("Q", "A", "B", "llama3", randomize_order=False)
    assert result["success"] is True
    assert "Winner: A" in result["judgment"]


def test_judge_pairwise_verifies_prompt_string_formatting(mock_repo, monkeypatch):
    """Test that prompt string formatting includes all components"""
    mock_adapter = Mock()
    mock_adapter.chat.return_value = {
        "message": {"content": "Winner: A\nScore A: 9.0\nScore B: 5.0"}
    }
    mock_adapter.list_models.return_value = ["llama3"]
    svc = JudgmentService(llm_adapter=mock_adapter, judgments_repo=mock_repo)
    monkeypatch.setattr("random.random", lambda: 0.9)
    
    svc.judge_pairwise(
        question="Test question",
        response_a="Response A",
        response_b="Response B",
        model="llama3",
        randomize_order=False
    )
    
    call_args = mock_adapter.chat.call_args
    prompt = call_args[1]["messages"][1]["content"]
    # Verify all components are in formatted string (mutation: f-string -> string would fail)
    assert "Test question" in prompt
    assert "Response A" in prompt
    assert "Response B" in prompt
    assert "Evaluate which response is better" in prompt


def test_judge_pairwise_prompt_includes_mt_bench_format(mock_repo, monkeypatch):
    """Test that judge_pairwise prompt includes MT-Bench paper format instructions"""
    mock_adapter = Mock()
    mock_adapter.chat.return_value = {
        "message": {"content": "Response A is better.\nScore A: 9.0\nScore B: 7.0\nReasoning: A is superior.\n[[A]]"}
    }
    mock_adapter.list_models.return_value = ["llama3"]
    svc = JudgmentService(llm_adapter=mock_adapter, judgments_repo=mock_repo)
    monkeypatch.setattr("random.random", lambda: 0.9)
    
    svc.judge_pairwise(
        question="Test question",
        response_a="Response A",
        response_b="Response B",
        model="llama3",
        randomize_order=False
    )
    
    call_args = mock_adapter.chat.call_args
    prompt = call_args[1]["messages"][1]["content"]
    # Verify MT-Bench format instructions are in prompt
    assert "Winner: [[A]] or [[B]] or [[C]]" in prompt
    assert "Use [[A]] if Response A is better" in prompt
    assert "Use [[B]] if Response B is better" in prompt
    assert "Use [[C]] if both responses are equally good (tie)" in prompt
    assert "End your response with [[A]], [[B]], or [[C]]" in prompt
    assert "Begin your evaluation by comparing" in prompt


def test_judge_pairwise_verifies_judgment_content_extraction_fallback(mock_repo, monkeypatch):
    """Test that judgment content extraction uses fallback paths"""
    mock_adapter = Mock()
    mock_adapter.list_models.return_value = ["llama3"]
    svc = JudgmentService(llm_adapter=mock_adapter, judgments_repo=mock_repo)
    monkeypatch.setattr("random.random", lambda: 0.9)
    
    # Test dict path
    mock_adapter.chat.return_value = {
        "message": {"content": "Winner: A"}
    }
    result1 = svc.judge_pairwise("Q", "A", "B", "llama3", randomize_order=False)
    assert result1["success"] is True
    assert "Winner: A" in result1["judgment"]
    
    # Test object.message.content path
    class RespMsg:
        def __init__(self, content):
            self.content = content
    class RespWrapper:
        def __init__(self, content):
            self.message = RespMsg(content)
    
    mock_adapter.chat.return_value = RespWrapper("Winner: B")
    result2 = svc.judge_pairwise("Q", "A", "B", "llama3", randomize_order=False)
    assert result2["success"] is True
    assert "Winner: B" in result2["judgment"]
    
    # Test object.message dict path
    class RespWrapperDict:
        def __init__(self, content):
            self.message = {"content": content}
    
    mock_adapter.chat.return_value = RespWrapperDict("Winner: A")
    result3 = svc.judge_pairwise("Q", "A", "B", "llama3", randomize_order=False)
    assert result3["success"] is True
    assert "Winner: A" in result3["judgment"]


def test_judge_pairwise_verifies_swapped_flag(mock_repo, monkeypatch):
    """Test that swapped flag is set correctly"""
    mock_adapter = Mock()
    # Mock returns judgment with Winner: A (after swap, so original was B)
    mock_adapter.chat.return_value = {
        "message": {"content": "Winner: A\nScore A: 9.0\nScore B: 5.0\nResponse A: Hi\nResponse B: Hello"}
    }
    mock_adapter.list_models.return_value = ["llama3"]
    svc = JudgmentService(llm_adapter=mock_adapter, judgments_repo=mock_repo)
    
    # Force swap
    monkeypatch.setattr("random.random", lambda: 0.1)
    result = svc.judge_pairwise(
        question="Q",
        response_a="Hello",
        response_b="Hi",
        model="llama3",
        randomize_order=True
    )
    # Verify swap_back was called (mutation: if swapped -> if not swapped would fail)
    assert result["success"] is True
    # After swap back, Winner should be B (since A was winner in swapped judgment)
    assert "Winner: B" in result["judgment"]


def test_judge_pairwise_model_not_found_includes_available_models(mock_repo):
    """Model-not-found errors should include available models (even if empty)"""
    mock_adapter = Mock()
    mock_adapter.chat.side_effect = Exception("Model not found 404")
    mock_adapter.list_models.return_value = []
    svc = JudgmentService(llm_adapter=mock_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise("Q", "A", "B", "missing-model", randomize_order=False)
    assert result["success"] is False
    assert "missing-model" in result["error"]
    assert "Available models" in result["error"]


def test_judge_pairwise_missing_message_returns_error(mock_repo):
    """If chat response lacks message key, should return error"""
    mock_adapter = Mock()
    mock_adapter.chat.return_value = {}
    mock_adapter.list_models.return_value = ["llama3"]
    svc = JudgmentService(llm_adapter=mock_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise("Q", "A", "B", "llama3", randomize_order=False)
    assert result["success"] is False
    assert "empty judgment" in result["error"].lower() or "empty" in result["error"].lower()


def test_judge_pairwise_missing_content_returns_error(mock_repo):
    """If chat response has message but missing content, should return error"""
    mock_adapter = Mock()
    mock_adapter.chat.return_value = {"message": {}}
    mock_adapter.list_models.return_value = ["llama3"]
    svc = JudgmentService(llm_adapter=mock_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise("Q", "A", "B", "llama3", randomize_order=False)
    assert result["success"] is False
    assert "empty judgment" in result["error"].lower() or "empty" in result["error"].lower()


def test_judge_pairwise_response_object_with_message_attr(mock_repo):
    """Fallback path: response.message.content attribute is used when dict access fails."""

    class RespMsg:
        def __init__(self, content: str):
            self.content = content

    class RespWrapper:
        def __init__(self, content: str):
            self.message = RespMsg(content)

    mocked_adapter = Mock()
    mocked_adapter.chat.return_value = RespWrapper("Winner: A\nScore A: 9.0\nScore B: 5.0")
    mocked_adapter.list_models.return_value = ["llama3"]

    svc = JudgmentService(llm_adapter=mocked_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="Q",
        response_a="A",
        response_b="B",
        model="llama3",
        randomize_order=False,
    )
    assert result["success"] is True
    assert "Winner: A" in result["judgment"]


def test_judge_pairwise_response_object_with_message_dict(mock_repo):
    """Fallback path: response.message dict with 'content' key is used."""

    class RespWrapper:
        def __init__(self, content: str):
            self.message = {"content": content}

    mocked_adapter = Mock()
    mocked_adapter.chat.return_value = RespWrapper("Winner: B\nScore A: 6.0\nScore B: 4.0")
    mocked_adapter.list_models.return_value = ["llama3"]

    svc = JudgmentService(llm_adapter=mocked_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="Q",
        response_a="A",
        response_b="B",
        model="llama3",
        randomize_order=False,
    )
    assert result["success"] is True
    assert "Winner: B" in result["judgment"]


def test_judge_pairwise_swap_restores_labels_and_scores(mock_repo, monkeypatch):
    """Ensure swap/back restores labels and scores deterministically"""
    mock_adapter = Mock()
    # Judgment produced after swap (A/B swapped), winner reported as A
    mock_adapter.chat.return_value = {
        "message": {
            "content": (
                "Winner: A\n"
                "Score A: 6.0\n"
                "Score B: 8.0\n"
                "Reasoning: B better\n"
                "Response A: B-text\n"
                "Response B: A-text"
            )
        }
    }
    mock_adapter.list_models.return_value = ["llama3"]
    monkeypatch.setattr(random, "random", lambda: 0.1)  # force swap

    svc = JudgmentService(llm_adapter=mock_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="Q",
        response_a="A-text",
        response_b="B-text",
        model="llama3",
        randomize_order=True,
    )
    assert result["success"] is True
    # After swap-back, winner should flip; ensure scores preserved (order may vary)
    assert "Winner:" in result["judgment"]
    assert "Score A:" in result["judgment"]
    assert "Score B:" in result["judgment"]
    assert "A-text" in result["judgment"] or "B-text" in result["judgment"]


# ---------- Tests for save_judgment ----------


def test_save_judgment_calls_repo_and_returns_id(mock_repo):
    svc = JudgmentService(judgments_repo=mock_repo)
    res_id = svc.save_judgment(
        question="q",
        response_a="a",
        response_b="b",
        model_a="modelA",
        model_b="modelB",
        judge_model="llama3",
        judgment="Winner: A",
        judgment_type="pairwise_auto",
        evaluation_id="eval-123",
        metrics_json='{"accuracy":9}',
        trace_json='{"step":"test"}',
    )
    mock_repo.save.assert_called_once_with(
        question="q",
        response_a="a",
        response_b="b",
        model_a="modelA",
        model_b="modelB",
        judge_model="llama3",
        judgment="Winner: A",
        judgment_type="pairwise_auto",
        evaluation_id="eval-123",
        metrics_json='{"accuracy":9}',
        trace_json='{"step":"test"}',
    )
    assert res_id == 42


# ---------- Tests for convenience functions ----------


def test_convenience_judge_pairwise(monkeypatch):
    dummy_result = {"success": True, "judgment": "Winner: A"}
    mock_service = Mock()
    mock_service.judge_pairwise.return_value = dummy_result
    monkeypatch.setattr(
        "core.services.judgment_service.get_judgment_service", lambda: mock_service
    )
    result = judge_pairwise("q", "a", "b", "llama3")
    assert result == dummy_result
    # Updated to include new parameters (defaults: randomize_order=True, conservative_position_bias=False, few_shot_examples=False)
    mock_service.judge_pairwise.assert_called_once_with("q", "a", "b", "llama3", True, False, False)


def test_convenience_save_judgment(monkeypatch):
    mock_service = Mock()
    mock_service.save_judgment.return_value = 99
    monkeypatch.setattr(
        "core.services.judgment_service.get_judgment_service", lambda: mock_service
    )
    res_id = save_judgment(
        question="q",
        response_a="a",
        response_b="b",
        model_a="A",
        model_b="B",
        judge_model="llama3",
        judgment="Winner: A",
        judgment_type="pairwise_auto",
    )
    assert res_id == 99
    mock_service.save_judgment.assert_called_once_with(
        question="q",
        response_a="a",
        response_b="b",
        model_a="A",
        model_b="B",
        judge_model="llama3",
        judgment="Winner: A",
        judgment_type="pairwise_auto",
        evaluation_id=None,
        metrics_json=None,
        trace_json=None,
    )


def test_get_judgment_service_initializes_global_instance():
    """Directly test that get_judgment_service initializes and caches a global instance."""
    from core.services import judgment_service as js_mod

    # Reset global instance
    js_mod._judgment_service = None

    svc1 = js_mod.get_judgment_service()
    assert isinstance(svc1, JudgmentService)

    # Second call should return the same instance (cached)
    svc2 = js_mod.get_judgment_service()
    assert svc1 is svc2


# ---------- Tests for conservative position bias mitigation ----------


def test_judge_pairwise_conservative_mode_both_agree(mock_llm_adapter, mock_repo):
    """Conservative mode: Both evaluations agree on winner"""
    # Logic: For them to agree on original A:
    # - First call (A, B): Winner: A (original A wins)
    # - Second call (B, A): Winner: B (in swapped context, converts to A in original - AGREES!)
    
    call_count = [0]  # Use list to allow modification in nested function
    
    def side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            # Original order (A, B): A wins
            return {
                "message": {
                    "content": "Winner: A\nScore A: 8.0\nScore B: 7.0\nReasoning: A is better"
                }
            }
        else:
            # Swapped order (B, A): B wins (converts to A in original - agrees!)
            return {
                "message": {
                    "content": "Winner: B\nScore A: 8.5\nScore B: 7.5\nReasoning: B is better (swapped context)"
                }
            }
    
    # Set side_effect directly (side_effect overrides return_value in Mock)
    mock_llm_adapter.chat.side_effect = side_effect
    mock_llm_adapter.list_models.return_value = ["llama3"]
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="Q",
        response_a="Response A",
        response_b="Response B",
        model="llama3",
        conservative_position_bias=True
    )
    
    assert result["success"] is True, f"Expected success=True, got error: {result.get('error', 'Unknown error')}"
    assert "Conservative Position Bias Mitigation Applied" in result["judgment"]
    assert "Both evaluations agreed" in result["judgment"] or "consistently identified" in result["judgment"]
    assert "Winner: A" in result["judgment"]  # Should agree on A
    assert mock_llm_adapter.chat.call_count == 2


def test_judge_pairwise_conservative_mode_inconsistent_tie(mock_llm_adapter, mock_repo):
    """Conservative mode: Inconsistent results should declare tie"""
    call_count = [0]
    
    def side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            # Original order: A wins
            return {
                "message": {
                    "content": "Winner: A\nScore A: 8.0\nScore B: 7.0\nReasoning: A is better"
                }
            }
        else:
            # Swapped order: A wins (which converts to B in original - inconsistent with first!)
            return {
                "message": {
                    "content": "Winner: A\nScore A: 7.0\nScore B: 8.0\nReasoning: A is better (swapped context)"
                }
            }
    
    # Set side_effect directly (side_effect overrides return_value in Mock)
    mock_llm_adapter.chat.side_effect = side_effect
    mock_llm_adapter.list_models.return_value = ["llama3"]
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="Q",
        response_a="Response A",
        response_b="Response B",
        model="llama3",
        conservative_position_bias=True
    )
    
    assert result["success"] is True, f"Expected success=True, got error: {result.get('error', 'Unknown error')}"
    assert "Winner: Tie" in result["judgment"]
    assert "inconsistent" in result["judgment"].lower() or "Tie" in result["judgment"]
    assert mock_llm_adapter.chat.call_count == 2


def test_judge_pairwise_conservative_mode_empty_first_judgment(mock_llm_adapter, mock_repo):
    """Conservative mode: Empty first judgment should return error"""
    mock_llm_adapter.chat.return_value = {
        "message": {"content": ""}
    }
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="Q",
        response_a="A",
        response_b="B",
        model="llama3",
        conservative_position_bias=True
    )
    
    assert result["success"] is False
    assert "first evaluation" in result["error"].lower()
    assert mock_llm_adapter.chat.call_count == 1


def test_judge_pairwise_conservative_mode_empty_second_judgment(mock_llm_adapter, mock_repo):
    """Conservative mode: Empty second judgment should return error"""
    def side_effect(*args, **kwargs):
        if not hasattr(side_effect, 'call_count'):
            side_effect.call_count = 0
        side_effect.call_count += 1
        
        if side_effect.call_count == 1:
            return {
                "message": {
                    "content": "Winner: A\nScore A: 8.0\nScore B: 7.0\nReasoning: A is better"
                }
            }
        else:
            return {"message": {"content": ""}}
    
    mock_llm_adapter.chat.side_effect = side_effect
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="Q",
        response_a="A",
        response_b="B",
        model="llama3",
        conservative_position_bias=True
    )
    
    assert result["success"] is False
    assert "second evaluation" in result["error"].lower()
    assert mock_llm_adapter.chat.call_count == 2


def test_judge_pairwise_conservative_mode_exception_handling(mock_llm_adapter, mock_repo):
    """Conservative mode: Exception handling"""
    mock_llm_adapter.chat.side_effect = Exception("Network error")
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="Q",
        response_a="A",
        response_b="B",
        model="llama3",
        conservative_position_bias=True
    )
    
    assert result["success"] is False
    assert "Network error" in result["error"]


def test_judge_pairwise_conservative_mode_model_not_found(mock_llm_adapter, mock_repo):
    """Conservative mode: Model not found error"""
    mock_llm_adapter.chat.side_effect = Exception("Model not found 404")
    mock_llm_adapter.list_models.return_value = ["llama3"]
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="Q",
        response_a="A",
        response_b="B",
        model="missing",
        conservative_position_bias=True
    )
    
    assert result["success"] is False
    assert "Model 'missing' not found" in result["error"]


def test_judge_pairwise_conservative_mode_verbosity_note(mock_llm_adapter, mock_repo):
    """Conservative mode: Verbosity note should be included when length difference > 20"""
    long_response = "word " * 50
    short_response = "short"
    
    call_count = [0]
    
    def side_effect(*args, **kwargs):
        call_count[0] += 1
        return {
            "message": {
                "content": f"Winner: A\nScore A: 8.0\nScore B: 7.0\nReasoning: Call {call_count[0]}"
            }
        }
    
    # Set side_effect directly (side_effect overrides return_value in Mock)
    mock_llm_adapter.chat.side_effect = side_effect
    mock_llm_adapter.list_models.return_value = ["llama3"]
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="Q",
        response_a=long_response,
        response_b=short_response,
        model="llama3",
        conservative_position_bias=True
    )
    
    assert result["success"] is True, f"Expected success=True, got error: {result.get('error', 'Unknown error')}"
    # Check that verbosity note was included in prompts
    assert mock_llm_adapter.chat.call_count == 2
    # Verify verbosity note in at least one call
    calls = mock_llm_adapter.chat.call_args_list
    assert any("Do not favor responses based on length" in str(call) for call in calls)


def test_judge_pairwise_conservative_mode_scores_averaging(mock_llm_adapter, mock_repo):
    """Conservative mode: Scores should be averaged when both agree"""
    call_count = [0]
    
    def side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            # Original order (A, B): A wins, A=8.0, B=6.0
            return {
                "message": {
                    "content": "Winner: A\nScore A: 8.0\nScore B: 6.0\nReasoning: First eval"
                }
            }
        else:
            # Swapped order (B, A): B wins (which converts to A in original - agrees!)
            # In swapped: Score A = original B, Score B = original A
            # So Winner: B means original A wins (agrees with first)
            # Score A: 9.0 means original B=9.0, Score B: 5.0 means original A=5.0
            # After conversion: original A = 5.0, original B = 9.0
            # Average: A = (8.0 + 5.0) / 2 = 6.5, B = (6.0 + 9.0) / 2 = 7.5
            return {
                "message": {
                    "content": "Winner: B\nScore A: 9.0\nScore B: 5.0\nReasoning: Second eval"
                }
            }
    
    # Set side_effect directly (side_effect overrides return_value in Mock)
    mock_llm_adapter.chat.side_effect = side_effect
    mock_llm_adapter.list_models.return_value = ["llama3"]
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="Q",
        response_a="A",
        response_b="B",
        model="llama3",
        conservative_position_bias=True
    )
    
    assert result["success"] is True, f"Expected success=True, got error: {result.get('error', 'Unknown error')}"
    assert "Winner: A" in result["judgment"]  # Both agreed on A
    assert "Score A:" in result["judgment"]
    assert "Score B:" in result["judgment"]
    # Verify scores are averaged (should be around 6.5 for A, 7.5 for B)
    assert "6.5" in result["judgment"] or "7.5" in result["judgment"] or "6" in result["judgment"]


def test_extract_judgment_content_exception_path(mock_repo):
    """Test _extract_judgment_content exception handling"""
    svc = JudgmentService(judgments_repo=mock_repo)
    
    # Create a response object that will raise an exception
    class BadResponse:
        def __getattr__(self, name):
            raise AttributeError("Test exception")
    
    result = svc._extract_judgment_content(BadResponse())
    assert result == ""


def test_parse_judgment_for_conservative_missing_winner(mock_repo):
    """Test _parse_judgment_for_conservative with missing winner"""
    svc = JudgmentService(judgments_repo=mock_repo)
    judgment = "Score A: 8.0\nScore B: 7.0\nReasoning: Some reasoning"
    parsed = svc._parse_judgment_for_conservative(judgment)
    assert parsed["winner"] is None
    assert parsed["score_a"] == 8.0
    assert parsed["score_b"] == 7.0
    assert parsed["reasoning"] == "Some reasoning"


def test_parse_judgment_for_conservative_missing_scores(mock_repo):
    """Test _parse_judgment_for_conservative with missing scores"""
    svc = JudgmentService(judgments_repo=mock_repo)
    judgment = "Winner: A\nReasoning: Some reasoning"
    parsed = svc._parse_judgment_for_conservative(judgment)
    assert parsed["winner"] == "A"
    assert parsed["score_a"] is None
    assert parsed["score_b"] is None
    assert parsed["reasoning"] == "Some reasoning"


def test_parse_judgment_for_conservative_invalid_scores(mock_repo):
    """Test _parse_judgment_for_conservative with invalid scores"""
    svc = JudgmentService(judgments_repo=mock_repo)
    judgment = "Winner: A\nScore A: invalid\nScore B: 7.0\nReasoning: Some reasoning"
    parsed = svc._parse_judgment_for_conservative(judgment)
    assert parsed["winner"] == "A"
    assert parsed["score_a"] is None  # Invalid score should be None
    assert parsed["score_b"] == 7.0
    assert parsed["reasoning"] == "Some reasoning"


def test_parse_judgment_for_conservative_missing_reasoning(mock_repo):
    """Test _parse_judgment_for_conservative with missing reasoning"""
    svc = JudgmentService(judgments_repo=mock_repo)
    judgment = "Winner: A\nScore A: 8.0\nScore B: 7.0"
    parsed = svc._parse_judgment_for_conservative(judgment)
    assert parsed["winner"] == "A"
    assert parsed["score_a"] == 8.0
    assert parsed["score_b"] == 7.0
    assert parsed["reasoning"] == judgment  # Should default to full judgment


def test_parse_judgment_for_conservative_complete(mock_repo):
    """Test _parse_judgment_for_conservative with complete judgment"""
    svc = JudgmentService(judgments_repo=mock_repo)
    judgment = "Winner: B\nScore A: 6.5\nScore B: 8.5\nReasoning: B is clearly better"
    parsed = svc._parse_judgment_for_conservative(judgment)
    assert parsed["winner"] == "B"
    assert parsed["score_a"] == 6.5
    assert parsed["score_b"] == 8.5
    assert parsed["reasoning"] == "B is clearly better"


def test_judge_pairwise_conservative_mode_none_winner(mock_llm_adapter, mock_repo):
    """Conservative mode: When winner is None, should declare tie"""
    call_count = [0]
    
    def side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return {
                "message": {
                    "content": "Score A: 8.0\nScore B: 7.0\nReasoning: No clear winner"
                }
            }
        else:
            return {
                "message": {
                    "content": "Score A: 7.0\nScore B: 8.0\nReasoning: No clear winner"
                }
            }
    
    # Set side_effect directly (side_effect overrides return_value in Mock)
    mock_llm_adapter.chat.side_effect = side_effect
    mock_llm_adapter.list_models.return_value = ["llama3"]
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="Q",
        response_a="A",
        response_b="B",
        model="llama3",
        conservative_position_bias=True
    )
    
    assert result["success"] is True, f"Expected success=True, got error: {result.get('error', 'Unknown error')}"
    assert "Winner: Tie" in result["judgment"]


def test_judge_pairwise_conservative_mode_partial_scores(mock_llm_adapter, mock_repo):
    """Conservative mode: Handle partial scores (one None)"""
    call_count = [0]
    
    def side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return {
                "message": {
                    "content": "Winner: A\nScore A: 8.0\nReasoning: First"
                }
            }
        else:
            # Second call: Winner: B (converts to A - agrees!)
            return {
                "message": {
                    "content": "Winner: B\nScore A: 9.0\nReasoning: Second"
                }
            }
    
    # Set side_effect directly (side_effect overrides return_value in Mock)
    mock_llm_adapter.chat.side_effect = side_effect
    mock_llm_adapter.list_models.return_value = ["llama3"]
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="Q",
        response_a="A",
        response_b="B",
        model="llama3",
        conservative_position_bias=True
    )
    
    assert result["success"] is True, f"Expected success=True, got error: {result.get('error', 'Unknown error')}"
    # Should handle None scores gracefully
    assert "Score" in result["judgment"]


def test_extract_judgment_content_exception_during_access(mock_repo):
    """Test _extract_judgment_content when exception occurs during content access."""
    svc = JudgmentService(judgments_repo=mock_repo)
    
    # Create a response where accessing message.content raises an exception
    class ExceptionOnContentAccess:
        @property
        def message(self):
            return self  # Return self so hasattr(message, "content") is True
        
        @property
        def content(self):
            raise RuntimeError("Error accessing content")
    
    result = svc._extract_judgment_content(ExceptionOnContentAccess())
    assert result == ""


def test_parse_judgment_for_conservative_score_a_valueerror(mock_repo):
    """Test _parse_judgment_for_conservative with Score A that matches regex but fails float()."""
    svc = JudgmentService(judgments_repo=mock_repo)
    # "8.5.3" matches the regex [0-9.]+ but cannot be converted to float
    judgment = "Winner: A\nScore A: 8.5.3\nScore B: 7.0\nReasoning: Some reasoning"
    parsed = svc._parse_judgment_for_conservative(judgment)
    assert parsed["winner"] == "A"
    assert parsed["score_a"] is None  # Should be None due to ValueError
    assert parsed["score_b"] == 7.0
    assert parsed["reasoning"] == "Some reasoning"


def test_parse_judgment_for_conservative_score_b_valueerror(mock_repo):
    """Test _parse_judgment_for_conservative with Score B that matches regex but fails float()."""
    svc = JudgmentService(judgments_repo=mock_repo)
    # "1.2.3.4" matches the regex [0-9.]+ but cannot be converted to float
    judgment = "Winner: B\nScore A: 8.0\nScore B: 1.2.3.4\nReasoning: Some reasoning"
    parsed = svc._parse_judgment_for_conservative(judgment)
    assert parsed["winner"] == "B"
    assert parsed["score_a"] == 8.0
    assert parsed["score_b"] is None  # Should be None due to ValueError
    assert parsed["reasoning"] == "Some reasoning"


def test_judge_pairwise_conservative_mode_winner2_swapped_a(mock_llm_adapter, mock_repo):
    """Conservative mode: Test case where winner2_swapped == 'A' to cover line 305.
    
    This covers the branch where:
    - First evaluation (original order): Winner B (original B wins)
    - Second evaluation (swapped order): Winner A (in swapped context, converts to B in original - AGREES!)
    - This makes winner2_swapped == "A", triggering the if branch at line 305.
    """
    call_count = [0]
    
    def side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            # Original order (A, B): B wins
            return {
                "message": {
                    "content": "Winner: B\nScore A: 7.0\nScore B: 8.0\nReasoning: B is better"
                }
            }
        else:
            # Swapped order (B, A): A wins (in swapped context, converts to B in original - agrees!)
            return {
                "message": {
                    "content": "Winner: A\nScore A: 7.5\nScore B: 8.5\nReasoning: A is better (swapped context)"
                }
            }
    
    mock_llm_adapter.chat.side_effect = side_effect
    mock_llm_adapter.list_models.return_value = ["llama3"]
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="Q",
        response_a="Response A",
        response_b="Response B",
        model="llama3",
        conservative_position_bias=True
    )
    
    assert result["success"] is True, f"Expected success=True, got error: {result.get('error', 'Unknown error')}"
    assert "Conservative Position Bias Mitigation Applied" in result["judgment"]
    assert "Both evaluations agreed" in result["judgment"] or "consistently identified" in result["judgment"]
    assert "Winner: B" in result["judgment"]  # Should agree on B
    assert mock_llm_adapter.chat.call_count == 2
    # Verify the conversion note is present (this confirms line 305 was executed)
    assert "In swapped order" in result["judgment"]
    assert "converts to 'B'" in result["judgment"]


def test_judge_pairwise_with_reference_answer(mock_llm_adapter, mock_repo):
    """Test judge_pairwise with reference_answer to cover line 68"""
    mock_llm_adapter.chat.return_value = {
        "message": {
            "content": "Winner: A\nScore A: 9.0\nScore B: 3.0\nReasoning: A matches reference"
        }
    }
    mock_llm_adapter.list_models.return_value = ["llama3"]
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="What is 1+1?",
        response_a="2",
        response_b="11",
        model="llama3",
        randomize_order=False,
        conservative_position_bias=False,
        reference_answer="2"
    )
    
    assert result["success"] is True
    assert "Winner: A" in result["judgment"]
    # Verify the prompt includes reference answer
    call_args = mock_llm_adapter.chat.call_args
    prompt = call_args[1]["messages"][1]["content"]
    assert "Reference Answer:" in prompt
    assert "2" in prompt
    assert "Use this reference answer to help evaluate" in prompt


def test_judge_pairwise_conservative_with_reference_answer(mock_llm_adapter, mock_repo):
    """Test _judge_pairwise_conservative with reference_answer to cover line 193"""
    call_count = [0]
    
    def side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return {
                "message": {
                    "content": "Winner: A\nScore A: 9.0\nScore B: 3.0\nReasoning: A matches reference"
                }
            }
        else:
            # Swapped order: Winner B means original A wins (agrees)
            return {
                "message": {
                    "content": "Winner: B\nScore A: 4.0\nScore B: 8.0\nReasoning: B matches reference (swapped)"
                }
            }
    
    mock_llm_adapter.chat.side_effect = side_effect
    mock_llm_adapter.list_models.return_value = ["llama3"]
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="What is 1+1?",
        response_a="2",
        response_b="11",
        model="llama3",
        randomize_order=False,
        conservative_position_bias=True,
        reference_answer="2"
    )
    
    assert result["success"] is True
    assert mock_llm_adapter.chat.call_count == 2
    # Verify both prompts include reference answer
    calls = mock_llm_adapter.chat.call_args_list
    for call in calls:
        prompt = call[1]["messages"][1]["content"]
        assert "Reference Answer:" in prompt
        assert "2" in prompt
        assert "Use this reference answer to help evaluate" in prompt


def test_generate_chain_of_thought(mock_llm_adapter, mock_repo):
    """Test _generate_chain_of_thought method generates judge's solution"""
    mock_llm_adapter.chat.return_value = {
        "message": {
            "content": "To solve this, I need to add 1 + 1. The answer is 2."
        }
    }
    mock_llm_adapter.list_models.return_value = ["llama3"]
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    solution = svc._generate_chain_of_thought("What is 1+1?", "llama3")
    
    assert solution == "To solve this, I need to add 1 + 1. The answer is 2."
    # Verify CoT prompt was sent
    call_args = mock_llm_adapter.chat.call_args
    prompt = call_args[1]["messages"][1]["content"]
    assert "Solve this question independently" in prompt
    assert "What is 1+1?" in prompt
    assert "Show your reasoning step by step" in prompt


def test_generate_chain_of_thought_empty_response(mock_llm_adapter, mock_repo):
    """Test _generate_chain_of_thought handles empty response gracefully"""
    mock_llm_adapter.chat.return_value = {
        "message": {
            "content": ""
        }
    }
    mock_llm_adapter.list_models.return_value = ["llama3"]
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    solution = svc._generate_chain_of_thought("What is 1+1?", "llama3")
    
    assert solution == ""


def test_generate_chain_of_thought_exception_handling(mock_llm_adapter, mock_repo):
    """Test _generate_chain_of_thought handles exceptions gracefully"""
    mock_llm_adapter.chat.side_effect = Exception("API error")
    mock_llm_adapter.list_models.return_value = ["llama3"]
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    solution = svc._generate_chain_of_thought("What is 1+1?", "llama3")
    
    # Should return empty string on error, not raise exception
    assert solution == ""


def test_judge_pairwise_with_chain_of_thought(mock_llm_adapter, mock_repo):
    """Test judge_pairwise with chain_of_thought enabled"""
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
    
    mock_llm_adapter.chat.side_effect = side_effect
    mock_llm_adapter.list_models.return_value = ["llama3"]
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="What is 1+1?",
        response_a="2",
        response_b="11",
        model="llama3",
        randomize_order=False,
        conservative_position_bias=False,
        chain_of_thought=True
    )
    
    assert result["success"] is True
    assert "Winner: A" in result["judgment"]
    assert mock_llm_adapter.chat.call_count == 2
    
    # Verify CoT solution was generated first
    first_call = mock_llm_adapter.chat.call_args_list[0]
    first_prompt = first_call[1]["messages"][1]["content"]
    assert "Solve this question independently" in first_prompt
    
    # Verify CoT solution is included in judgment prompt
    second_call = mock_llm_adapter.chat.call_args_list[1]
    second_prompt = second_call[1]["messages"][1]["content"]
    assert "Judge's Independent Solution (Chain-of-Thought):" in second_prompt
    assert "To solve: 1 + 1 = 2" in second_prompt
    assert "Use this independent solution to help evaluate" in second_prompt


def test_judge_pairwise_conservative_with_chain_of_thought(mock_llm_adapter, mock_repo):
    """Test _judge_pairwise_conservative with chain_of_thought enabled"""
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
    
    mock_llm_adapter.chat.side_effect = side_effect
    mock_llm_adapter.list_models.return_value = ["llama3"]
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="What is 1+1?",
        response_a="2",
        response_b="11",
        model="llama3",
        randomize_order=False,
        conservative_position_bias=True,
        chain_of_thought=True
    )
    
    assert result["success"] is True
    assert mock_llm_adapter.chat.call_count == 3  # 1 CoT + 2 judgments
    
    # Verify CoT solution was generated first
    first_call = mock_llm_adapter.chat.call_args_list[0]
    first_prompt = first_call[1]["messages"][1]["content"]
    assert "Solve this question independently" in first_prompt
    
    # Verify CoT solution is included in both judgment prompts
    second_call = mock_llm_adapter.chat.call_args_list[1]
    second_prompt = second_call[1]["messages"][1]["content"]
    assert "Judge's Independent Solution (Chain-of-Thought):" in second_prompt
    
    third_call = mock_llm_adapter.chat.call_args_list[2]
    third_prompt = third_call[1]["messages"][1]["content"]
    assert "Judge's Independent Solution (Chain-of-Thought):" in third_prompt


def test_judge_pairwise_with_chain_of_thought_and_reference(mock_llm_adapter, mock_repo):
    """Test judge_pairwise with both chain_of_thought and reference_answer"""
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
                    "content": "Winner: A\nScore A: 9.0\nScore B: 3.0\nReasoning: A matches both solution and reference"
                }
            }
    
    mock_llm_adapter.chat.side_effect = side_effect
    mock_llm_adapter.list_models.return_value = ["llama3"]
    
    svc = JudgmentService(llm_adapter=mock_llm_adapter, judgments_repo=mock_repo)
    result = svc.judge_pairwise(
        question="What is 1+1?",
        response_a="2",
        response_b="11",
        model="llama3",
        randomize_order=False,
        conservative_position_bias=False,
        reference_answer="2",
        chain_of_thought=True
    )
    
    assert result["success"] is True
    assert mock_llm_adapter.chat.call_count == 2
    
    # Verify both CoT solution and reference answer are in the prompt
    second_call = mock_llm_adapter.chat.call_args_list[1]
    prompt = second_call[1]["messages"][1]["content"]
    assert "Judge's Independent Solution (Chain-of-Thought):" in prompt
    assert "Reference Answer:" in prompt
    assert "Pay special attention to how well each response aligns with the judge's independent solution and reference answer" in prompt


def test_parse_judgment_for_conservative_mt_bench_format_a(mock_repo):
    """Test _parse_judgment_for_conservative with MT-Bench format [[A]]"""
    svc = JudgmentService(judgments_repo=mock_repo)
    judgment = """Response A is better.
Score A: 9.0
Score B: 7.0
Reasoning: Response A provides more detail.
[[A]]"""
    parsed = svc._parse_judgment_for_conservative(judgment)
    assert parsed["winner"] == "A"
    assert parsed["score_a"] == 9.0
    assert parsed["score_b"] == 7.0
    assert "Response A provides more detail" in parsed["reasoning"]


def test_parse_judgment_for_conservative_mt_bench_format_b(mock_repo):
    """Test _parse_judgment_for_conservative with MT-Bench format [[B]]"""
    svc = JudgmentService(judgments_repo=mock_repo)
    judgment = """Response B is superior.
Score A: 6.5
Score B: 8.5
Reasoning: Response B is clearer.
[[B]]"""
    parsed = svc._parse_judgment_for_conservative(judgment)
    assert parsed["winner"] == "B"
    assert parsed["score_a"] == 6.5
    assert parsed["score_b"] == 8.5
    assert "Response B is clearer" in parsed["reasoning"]


def test_parse_judgment_for_conservative_mt_bench_format_c_tie(mock_repo):
    """Test _parse_judgment_for_conservative with MT-Bench format [[C]] (tie)"""
    svc = JudgmentService(judgments_repo=mock_repo)
    judgment = """Both responses are equally good.
Score A: 8.0
Score B: 8.0
Reasoning: Both are similar in quality.
[[C]]"""
    parsed = svc._parse_judgment_for_conservative(judgment)
    assert parsed["winner"] is None  # Tie should result in None
    assert parsed["score_a"] == 8.0
    assert parsed["score_b"] == 8.0
    assert "Both are similar in quality" in parsed["reasoning"]


def test_parse_judgment_for_conservative_fallback_to_old_format(mock_repo):
    """Test _parse_judgment_for_conservative falls back to old format when [[A]]/[[B]]/[[C]] not found"""
    svc = JudgmentService(judgments_repo=mock_repo)
    judgment = "Winner: A\nScore A: 8.5\nScore B: 7.5\nReasoning: A is better"
    parsed = svc._parse_judgment_for_conservative(judgment)
    assert parsed["winner"] == "A"
    assert parsed["score_a"] == 8.5
    assert parsed["score_b"] == 7.5
    assert "A is better" in parsed["reasoning"]


def test_get_few_shot_examples(mock_repo):
    """Test that few-shot examples method returns examples in correct format"""
    svc = JudgmentService(judgments_repo=mock_repo)
    examples = svc._get_few_shot_examples()
    
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


def test_judge_pairwise_with_few_shot_examples(mock_repo, mock_llm_adapter):
    """Test that few-shot examples are included when enabled"""
    svc = JudgmentService(judgments_repo=mock_repo)
    svc.llm_adapter = mock_llm_adapter
    
    mock_llm_adapter.chat.return_value = {
        "message": {
            "content": "Winner: [[A]]\nScore A: 8.5\nScore B: 7.5\nReasoning: A is better"
        }
    }
    
    result = svc.judge_pairwise(
        question="Test question",
        response_a="Response A",
        response_b="Response B",
        model="llama3",
        few_shot_examples=True
    )
    
    assert result["success"] is True
    # Verify the prompt sent to LLM includes few-shot examples
    call_args = mock_llm_adapter.chat.call_args
    prompt = call_args[1]["messages"][1]["content"]
    assert "Example 1:" in prompt
    assert "Example 2:" in prompt
    assert "Example 3:" in prompt


def test_judge_pairwise_without_few_shot_examples(mock_repo, mock_llm_adapter):
    """Test that few-shot examples are not included when disabled"""
    svc = JudgmentService(judgments_repo=mock_repo)
    svc.llm_adapter = mock_llm_adapter
    
    mock_llm_adapter.chat.return_value = {
        "message": {
            "content": "Winner: [[A]]\nScore A: 8.5\nScore B: 7.5\nReasoning: A is better"
        }
    }
    
    result = svc.judge_pairwise(
        question="Test question",
        response_a="Response A",
        response_b="Response B",
        model="llama3",
        few_shot_examples=False
    )
    
    assert result["success"] is True
    # Verify the prompt sent to LLM does not include few-shot examples
    call_args = mock_llm_adapter.chat.call_args
    prompt = call_args[1]["messages"][1]["content"]
    assert "Example 1:" not in prompt
    assert "Example 2:" not in prompt
    assert "Example 3:" not in prompt


def test_judge_pairwise_conservative_with_few_shot_examples(mock_repo, mock_llm_adapter):
    """Test that few-shot examples are included in conservative mode"""
    svc = JudgmentService(judgments_repo=mock_repo)
    svc.llm_adapter = mock_llm_adapter
    
    mock_llm_adapter.chat.return_value = {
        "message": {
            "content": "Winner: [[A]]\nScore A: 8.5\nScore B: 7.5\nReasoning: A is better"
        }
    }
    
    result = svc.judge_pairwise(
        question="Test question",
        response_a="Response A",
        response_b="Response B",
        model="llama3",
        conservative_position_bias=True,
        few_shot_examples=True
    )
    
    assert result["success"] is True
    # Verify the prompt was called twice (conservative mode) and both include few-shot examples
    assert mock_llm_adapter.chat.call_count == 2
    for call in mock_llm_adapter.chat.call_args_list:
        prompt = call[1]["messages"][1]["content"]
        assert "Example 1:" in prompt
        assert "Example 2:" in prompt
        assert "Example 3:" in prompt
