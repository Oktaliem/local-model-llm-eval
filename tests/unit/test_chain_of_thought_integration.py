"""
Integration test for Chain-of-Thought feature
Tests the complete flow from EvaluationService through PairwiseStrategy
"""
import pytest
from unittest.mock import Mock, patch
from core.services.evaluation_service import EvaluationService
from core.domain.models import EvaluationRequest
from core.infrastructure.llm.ollama_client import OllamaAdapter


class TestChainOfThoughtIntegration:
    """Integration tests for Chain-of-Thought feature"""
    
    def test_chain_of_thought_through_evaluation_service(self):
        """Test Chain-of-Thought through EvaluationService (simulating Auto Pairwise Comparison)"""
        adapter = Mock(spec=OllamaAdapter)
        call_count = [0]
        
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call: CoT solution generation
                return {
                    "message": {
                        "content": "To solve: 15 + 27, I add 15 and 27 together. 15 + 27 = 42. The answer is 42."
                    }
                }
            else:
                # Second call: Judgment
                return {
                    "message": {
                        "content": "Winner: B\nScore A: 8.0\nScore B: 9.0\nReasoning: Both responses correctly match the independent solution (42). Response B is more explanatory and helpful."
                    }
                }
        
        adapter.chat.side_effect = side_effect
        adapter.list_models.return_value = ["llama3"]
        
        # Create evaluation service with mocked adapter
        service = EvaluationService()
        # We need to patch the strategy factory to use our mocked adapter
        with patch('core.domain.factory.StrategyFactory.get') as mock_get_strategy:
            from core.domain.strategies.pairwise import PairwiseStrategy
            strategy = PairwiseStrategy(adapter)
            mock_get_strategy.return_value = strategy
            
            # Simulate Auto Pairwise Comparison call
            result = service.evaluate(
                evaluation_type="pairwise",
                question="What is 15 + 27?",
                judge_model="llama3",
                response_a="42",
                response_b="The answer is 15 plus 27 equals 42.",
                options={
                    "randomize_order": False,
                    "chain_of_thought": True,
                    "model_a": "llama3",
                    "model_b": "mistral"
                },
                save_to_db=False
            )
        
        # Verify results
        assert result["success"] is True
        assert result["winner"] == "B"
        assert result["score_a"] == 8.0
        assert result["score_b"] == 9.0
        
        # Verify CoT was called
        assert adapter.chat.call_count >= 2
        
        # Verify CoT generation call exists
        cot_found = False
        judgment_with_cot_found = False
        for call in adapter.chat.call_args_list:
            prompt = call[1]["messages"][1]["content"]
            if "Solve this question independently" in prompt:
                cot_found = True
                assert "What is 15 + 27?" in prompt
            elif "Judge's Independent Solution (Chain-of-Thought):" in prompt:
                judgment_with_cot_found = True
                assert "15 + 27" in prompt or "42" in prompt
        
        assert cot_found, "CoT generation call not found"
        assert judgment_with_cot_found, "Judgment call with CoT not found"
    
    def test_chain_of_thought_with_conservative_mode(self):
        """Test Chain-of-Thought with Conservative Position Bias Mitigation"""
        adapter = Mock(spec=OllamaAdapter)
        call_count = [0]
        
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call: CoT solution generation
                return {
                    "message": {
                        "content": "To solve: 12 * 5, I multiply 12 by 5. 12 * 5 = 60. The answer is 60."
                    }
                }
            elif call_count[0] == 2:
                # Second call: First judgment (original order)
                return {
                    "message": {
                        "content": "Winner: B\nScore A: 8.0\nScore B: 9.0\nReasoning: Both match independent solution (60). B is more explanatory."
                    }
                }
            else:
                # Third call: Second judgment (swapped order)
                return {
                    "message": {
                        "content": "Winner: A\nScore A: 9.0\nScore B: 8.0\nReasoning: Both match independent solution (60). A is clearer (swapped)."
                    }
                }
        
        adapter.chat.side_effect = side_effect
        adapter.list_models.return_value = ["llama3"]
        
        service = EvaluationService()
        with patch('core.domain.factory.StrategyFactory.get') as mock_get_strategy:
            from core.domain.strategies.pairwise import PairwiseStrategy
            strategy = PairwiseStrategy(adapter)
            mock_get_strategy.return_value = strategy
            
            result = service.evaluate(
                evaluation_type="pairwise",
                question="What is 12 * 5?",
                judge_model="llama3",
                response_a="60",
                response_b="The answer is 12 multiplied by 5 equals 60.",
                options={
                    "randomize_order": False,
                    "conservative_position_bias": True,
                    "chain_of_thought": True,
                    "model_a": "llama3",
                    "model_b": "mistral"
                },
                save_to_db=False
            )
        
        # Verify results
        assert result["success"] is True
        
        # Verify CoT was called first, then 2 judgments
        assert adapter.chat.call_count >= 3
        
        # Verify CoT solution is in both judgment prompts
        judgment_calls_with_cot = 0
        for call in adapter.chat.call_args_list:
            prompt = call[1]["messages"][1]["content"]
            if "Judge's Independent Solution (Chain-of-Thought):" in prompt:
                judgment_calls_with_cot += 1
                assert "12 * 5" in prompt or "60" in prompt
        
        assert judgment_calls_with_cot == 2, f"Expected 2 judgment calls with CoT, got {judgment_calls_with_cot}"
    
    def test_chain_of_thought_with_reference_answer(self):
        """Test Chain-of-Thought combined with Reference Answer"""
        adapter = Mock(spec=OllamaAdapter)
        call_count = [0]
        
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call: CoT solution generation
                return {
                    "message": {
                        "content": "To solve: 8 * 7, I multiply 8 by 7. 8 * 7 = 56. The answer is 56."
                    }
                }
            else:
                # Second call: Judgment with both CoT and reference
                return {
                    "message": {
                        "content": "Winner: B\nScore A: 8.0\nScore B: 9.0\nReasoning: Both match the independent solution and reference answer (56). Response B is more complete."
                    }
                }
        
        adapter.chat.side_effect = side_effect
        adapter.list_models.return_value = ["llama3"]
        
        service = EvaluationService()
        with patch('core.domain.factory.StrategyFactory.get') as mock_get_strategy:
            from core.domain.strategies.pairwise import PairwiseStrategy
            strategy = PairwiseStrategy(adapter)
            mock_get_strategy.return_value = strategy
            
            result = service.evaluate(
                evaluation_type="pairwise",
                question="What is 8 * 7?",
                judge_model="llama3",
                response_a="56",
                response_b="The product of 8 and 7 is 56.",
                options={
                    "randomize_order": False,
                    "chain_of_thought": True,
                    "reference_answer": "56",
                    "model_a": "llama3",
                    "model_b": "mistral"
                },
                save_to_db=False
            )
        
        # Verify results
        assert result["success"] is True
        assert result["winner"] == "B"
        
        # Verify both CoT and reference answer are in the prompt
        judgment_call = None
        for call in adapter.chat.call_args_list:
            prompt = call[1]["messages"][1]["content"]
            if "Judge's Independent Solution (Chain-of-Thought):" in prompt:
                judgment_call = call
                break
        
        assert judgment_call is not None, "Judgment call with CoT not found"
        prompt = judgment_call[1]["messages"][1]["content"]
        assert "Judge's Independent Solution (Chain-of-Thought):" in prompt
        assert "reference answer" in prompt.lower() or "Reference Answer" in prompt
