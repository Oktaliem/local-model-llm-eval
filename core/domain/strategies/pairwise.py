"""Pairwise comparison evaluation strategy"""
import random
import re
import sys
import time
from typing import Dict, Any
from core.domain.strategies.base import EvaluationStrategy
from core.domain.models import EvaluationRequest, EvaluationResult
from core.infrastructure.llm.ollama_client import OllamaAdapter


class PairwiseStrategy(EvaluationStrategy):
    """Strategy for pairwise comparison of two responses"""

    def __init__(self, llm_adapter: OllamaAdapter):
        self.llm_adapter = llm_adapter

    @property
    def name(self) -> str:
        return "pairwise"

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        start_time = time.time()

        if not request.response_a or not request.response_b:
            return EvaluationResult(
                success=False,
                evaluation_type="pairwise",
                error="Both response_a and response_b are required for pairwise comparison",
            )

        original_response_a = request.response_a
        original_response_b = request.response_b

        # Check for conservative position bias mitigation (MT-Bench paper recommendation)
        conservative_mode = request.options.get("conservative_position_bias", False)
        
        # Check for Chain-of-Thought option
        chain_of_thought = request.options.get("chain_of_thought", False)
        cot_solution = ""
        if chain_of_thought:
            cot_solution = self._generate_chain_of_thought(request.question, request.judge_model)
        
        if conservative_mode:
            # Conservative approach: Call judge twice with swapped positions
            # Only declare win if both agree, else tie (as per MT-Bench paper)
            return self._evaluate_conservative(request, original_response_a, original_response_b, start_time, cot_solution)
        
        # Aggressive approach: Random swap once (default behavior)
        randomize_order = request.options.get("randomize_order", True)
        swapped = False
        if randomize_order and random.random() < 0.5:
            request.response_a, request.response_b = request.response_b, request.response_a
            swapped = True

        model_a_label = request.options.get("model_a", "")
        model_b_label = request.options.get("model_b", "")
        reference_answer = request.options.get("reference_answer")
        few_shot_examples = request.options.get("few_shot_examples", False)
        
        # Use cot_solution generated earlier (before conservative check)
        prompt = self._build_prompt(request.question, request.response_a, request.response_b, model_a_label, model_b_label, reference_answer, cot_solution, few_shot_examples)

        try:
            response = self.llm_adapter.chat(
                model=request.judge_model,
                messages=[
                    {"role": "system", "content": "You are an expert evaluator. Provide detailed, specific comparative analysis with concrete examples."},
                    {"role": "user", "content": prompt},
                ],
                # Use temperature 0.0 for maximally deterministic judgments
                # Set num_predict to 65536 to allow very detailed, comprehensive judgments
                options={"temperature": 0.0, "num_predict": 65536, "timeout": 300},
            )
            judgment_content = self._extract_content(response)

            if not judgment_content or not judgment_content.strip():
                return EvaluationResult(
                    success=False,
                    evaluation_type="pairwise",
                    error="Received empty judgment from model. The model may not have generated a response.",
                    execution_time=time.time() - start_time,
                )

            if swapped:
                judgment_content = self._swap_back_judgment(judgment_content, original_response_a, original_response_b)

            parsed = self._parse_judgment(judgment_content)
            execution_time = time.time() - start_time
            return EvaluationResult(
                success=True,
                evaluation_type="pairwise",
                judgment=judgment_content,
                winner=parsed.get("winner"),
                score_a=parsed.get("score_a"),
                score_b=parsed.get("score_b"),
                reasoning=parsed.get("reasoning"),
                execution_time=execution_time,
            )
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"[DEBUG] Exception in PairwiseStrategy: {str(e)}", flush=True)
            print(f"[DEBUG] Traceback: {error_trace}", flush=True)
            sys.stdout.flush()
            error_msg = str(e)
            if "not found" in error_msg.lower() or "404" in error_msg:
                available = self.llm_adapter.list_models()
                error_msg = f"Model '{request.judge_model}' not found. Available models: {', '.join(available) if available else 'None - please pull a model first'}"
            return EvaluationResult(success=False, evaluation_type="pairwise", error=error_msg, execution_time=time.time() - start_time)

    def _generate_chain_of_thought(self, question: str, model: str) -> str:
        """Generate judge's independent solution using Chain-of-Thought (CoT) approach.
        
        As per MT-Bench paper recommendation:
        - Prompt judge to answer the question independently first
        - This helps reduce being misled by incorrect answers in the responses
        - Improves failure rate from 70% to 30% for math/reasoning questions
        
        Args:
            question: The question or task
            model: Judge model to use
            
        Returns:
            Judge's independent solution, or empty string if generation fails
        """
        try:
            cot_prompt = f"""Solve this question independently. Show your reasoning step by step.

Question: {question}

Provide your solution with clear reasoning. Think through the problem step by step before giving your final answer."""
            
            response = self.llm_adapter.chat(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert problem solver. Solve problems step by step with clear reasoning."},
                    {"role": "user", "content": cot_prompt}
                ],
                options={
                    "temperature": 0.0,  # Deterministic solution
                    "num_predict": 4096,  # Enough for reasoning
                    "timeout": 300
                }
            )
            
            content = self._extract_content(response)
            return content.strip() if content else ""
        except Exception as e:
            # If CoT generation fails, continue without it
            return ""
    
    def _get_few_shot_examples(self) -> str:
        """Generate few-shot examples to improve judge consistency.
        
        As per MT-Bench paper, few-shot examples improve consistency from 65% to 77.5%,
        but increase cost 4×. These examples demonstrate the expected format and reasoning.
        
        Returns:
            String containing 3 example judgments in MT-Bench format
        """
        return """
Here are some examples of good evaluations:

Example 1:
Question: What is the capital of France?
Response A: Paris
Response B: The capital of France is Paris, a beautiful city known for its art, culture, and history.

Winner: [[B]]
Score A: 8
Score B: 9
Reasoning: Both responses are correct. Response A is accurate and concise, which is valuable for quick queries. However, Response B provides the same correct answer with additional context about Paris, making it more informative and helpful. The extra information adds value without being verbose, so Response B is slightly better.

Example 2:
Question: Explain what photosynthesis is.
Response A: Photosynthesis is the process by which plants convert sunlight into energy. They use carbon dioxide and water to produce glucose and oxygen.
Response B: Photosynthesis is when plants make food using light.

Winner: [[A]]
Score A: 9
Score B: 6
Reasoning: Response A provides a complete and accurate explanation of photosynthesis, including the key inputs (sunlight, carbon dioxide, water) and outputs (glucose, oxygen). Response B is oversimplified and uses vague language ("make food" instead of "produce glucose"), which could mislead readers. Response A demonstrates better understanding and clarity.

Example 3:
Question: What is 5 + 3?
Response A: 8
Response B: The answer is 8.

Winner: [[C]]
Score A: 9
Score B: 9
Reasoning: Both responses correctly answer the question. Response A is concise and direct, which is ideal for simple arithmetic. Response B provides the same correct answer with a brief explanatory phrase, which is also clear and appropriate. The difference is purely stylistic - neither response is substantively better than the other. Both are equally accurate, relevant, clear, complete, and helpful. Minor formatting or stylistic variations (like bold text, explanatory phrases, etc.) should not determine the winner when both responses are correct and essentially equivalent. Therefore, this is a tie.

---
"""
    
    def _build_prompt(self, question: str, response_a: str, response_b: str, model_a_label: str = "", model_b_label: str = "", reference_answer: str = None, cot_solution: str = "", few_shot_examples: bool = False) -> str:
        len_a = len(response_a.split())
        len_b = len(response_b.split())
        verbosity_note = ""
        if abs(len_a - len_b) > 20:
            verbosity_note = "\n\nIMPORTANT: Do not favor responses based on length. Evaluate based on quality, not verbosity. A concise, accurate response can be better than a verbose one."
        model_note = ""
        if model_a_label or model_b_label:
            model_note = f"\nNote: Response A is from '{model_a_label or 'A'}'; Response B is from '{model_b_label or 'B'}'. Keep labels exactly aligned with the blocks below."
        
        reference_section = ""
        if reference_answer:
            reference_section = f"""

Reference Answer:
{reference_answer}

Use this reference answer to help evaluate the accuracy and correctness of the responses. Compare each response against this reference to assess how well they align with the correct answer.
"""
        
        cot_section = ""
        if cot_solution:
            cot_section = f"""

Judge's Independent Solution (Chain-of-Thought):
{cot_solution}

Use this independent solution to help evaluate the responses. Compare each response against this solution to assess accuracy and correctness. This helps avoid being misled by incorrect answers in the responses.
"""
        
        few_shot_section = ""
        if few_shot_examples:
            few_shot_section = self._get_few_shot_examples()
        
        return f"""{few_shot_section}Evaluate which response is better.

Question: {question}
{cot_section}{reference_section}
Response A:
{response_a}

Response B:
{response_b}
{verbosity_note}{model_note}

Evaluate based on: accuracy, relevance, clarity, completeness, helpfulness.
Do not favor based on position or length. Focus on quality.
{f"Pay special attention to how well each response aligns with the judge's independent solution and reference answer (if provided) above." if (cot_solution or reference_answer) else ""}

IMPORTANT EVALUATION GUIDELINES:
- If both responses are correct and essentially equal in quality, choose [[C]] (tie)
- Minor formatting differences (bold, italics, etc.) should NOT determine the winner unless they significantly impact clarity or helpfulness
- Only declare a winner ([[A]] or [[B]]) if there is a meaningful, substantive difference in quality
- Stylistic differences alone (like "8" vs "The answer is 8") should result in a tie if both are correct
- Focus on substantive differences: accuracy, completeness of information, clarity of explanation, helpfulness to the user

Provide specific comparative reasoning that explains:
- If there's a winner: What makes it better than the other response (substantive differences only)
- If it's a tie: Why both responses are equally good and any minor differences are purely stylistic
- Specific strengths and weaknesses of each response
- Why the scores differ (if they do), or why they're the same (if it's a tie)
- Concrete examples from the responses to support your evaluation
{f"- How each response compares to the reference answer (if provided)" if reference_answer else ""}

Format:
Begin your evaluation by comparing the two responses. Then provide your judgment in the following format:

Winner: [[A]] or [[B]] or [[C]]
- Use [[A]] if Response A is substantively better
- Use [[B]] if Response B is substantively better  
- Use [[C]] if both responses are equally good (tie) - this includes cases where differences are purely stylistic or formatting-related

Score A: [0-10]
Score B: [0-10]
Reasoning: [Detailed comparative analysis. If it's a tie, explain why both are equally valid. If there's a winner, explain the substantive difference.]

IMPORTANT: End your response with [[A]], [[B]], or [[C]] to clearly indicate the winner.
"""

    def _extract_content(self, response: Any) -> str:
        try:
            if isinstance(response, dict):
                return response.get("message", {}).get("content", "")
            if hasattr(response, "message"):
                message = response.message
                if isinstance(message, dict):
                    return message.get("content", "")
                elif hasattr(message, "content"):
                    return message.content
            return ""
        except Exception:
            return ""

    def _parse_judgment(self, judgment: str) -> Dict[str, Any]:
        winner = None
        score_a = None
        score_b = None
        reasoning = judgment
        
        # First, try to parse MT-Bench paper format: [[A]], [[B]], or [[C]]
        paper_format_match = re.search(r'\[\[([ABC])\]\]', judgment)
        if paper_format_match:
            winner_letter = paper_format_match.group(1).upper()
            if winner_letter == 'C':
                winner = None  # Tie
            else:
                winner = winner_letter
        else:
            # Fallback to old format: Winner: A or Winner: B
            winner_match = re.search(r"Winner:\s*([AB])", judgment, re.IGNORECASE)
            if winner_match:
                winner = winner_match.group(1).upper()
        
        score_a_match = re.search(r"Score A:\s*([0-9.]+)", judgment, re.IGNORECASE)
        if score_a_match:
            try:
                score_a = float(score_a_match.group(1))
            except ValueError:
                pass
        score_b_match = re.search(r"Score B:\s*([0-9.]+)", judgment, re.IGNORECASE)
        if score_b_match:
            try:
                score_b = float(score_b_match.group(1))
            except ValueError:
                pass
        reasoning_match = re.search(r"Reasoning:\s*(.+)", judgment, re.IGNORECASE | re.DOTALL)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
        return {"winner": winner, "score_a": score_a, "score_b": score_b, "reasoning": reasoning}

    def _swap_back_judgment(self, judgment_content: str, original_response_a: str, original_response_b: str) -> str:
        print(f"[DEBUG] Responses were swapped. Swapping back judgment...", flush=True)
        sys.stdout.flush()
        
        # Handle MT-Bench paper format: [[A]], [[B]], or [[C]]
        paper_format_match = re.search(r'\[\[([ABC])\]\]', judgment_content)
        if paper_format_match:
            model_winner = paper_format_match.group(1).upper()
            if model_winner == 'C':
                # Tie remains a tie
                pass
            else:
                # Swap A <-> B
                original_winner = "B" if model_winner == "A" else "A"
                judgment_content = re.sub(r'\[\[([ABC])\]\]', f'[[{original_winner}]]', judgment_content)
        else:
            # Fallback to old format: Winner: A or Winner: B
            winner_match = re.search(r"Winner:\s*([AB])", judgment_content, re.IGNORECASE)
            if winner_match:
                model_winner = winner_match.group(1).upper()
                original_winner = "B" if model_winner == "A" else "A"
                judgment_content = re.sub(r"Winner:\s*" + model_winner + r"(\s|$|\(|:)", f"Winner: {original_winner}\\1", judgment_content, flags=re.IGNORECASE)
        score_a_match = re.search(r"Score A:\s*([0-9.]+)", judgment_content, re.IGNORECASE)
        score_b_match = re.search(r"Score B:\s*([0-9.]+)", judgment_content, re.IGNORECASE)
        if score_a_match and score_b_match:
            swapped_score_a = score_a_match.group(1)
            swapped_score_b = score_b_match.group(1)
            judgment_content = re.sub(r"Score A:\s*" + re.escape(swapped_score_a), "TEMP_SCORE_A_MARKER", judgment_content, flags=re.IGNORECASE)
            judgment_content = re.sub(r"Score B:\s*" + re.escape(swapped_score_b), "TEMP_SCORE_B_MARKER", judgment_content, flags=re.IGNORECASE)
            judgment_content = re.sub("TEMP_SCORE_A_MARKER", f"Score A: {swapped_score_b}", judgment_content, flags=re.IGNORECASE)
            judgment_content = re.sub("TEMP_SCORE_B_MARKER", f"Score B: {swapped_score_a}", judgment_content, flags=re.IGNORECASE)
        judgment_content = re.sub(r"\bResponse\s+A\b", "TEMP_MARKER_RESPONSE_A", judgment_content, flags=re.IGNORECASE)
        judgment_content = re.sub(r"\bResponse\s+B\b", "Response A", judgment_content, flags=re.IGNORECASE)
        judgment_content = re.sub("TEMP_MARKER_RESPONSE_A", "Response B", judgment_content, flags=re.IGNORECASE)
        judgment_content = re.sub(r"(Winner:\s*[AB])", r"\1 (Note: Responses were randomized to mitigate position bias)", judgment_content, flags=re.IGNORECASE, count=1)
        return judgment_content

    def _evaluate_conservative(self, request: EvaluationRequest, original_response_a: str, original_response_b: str, start_time: float, cot_solution: str = "") -> EvaluationResult:
        """Conservative position bias mitigation: Call judge twice with swapped positions.
        
        As per MT-Bench paper recommendation:
        - Call judge twice: once with original order, once with swapped order
        - Only declare a win if both agree on the winner
        - If results are inconsistent, declare a tie
        """
        model_a_label = request.options.get("model_a", "")
        model_b_label = request.options.get("model_b", "")
        reference_answer = request.options.get("reference_answer")
        few_shot_examples = request.options.get("few_shot_examples", False)
        
        # First judgment: Original order (A, B)
        prompt1 = self._build_prompt(request.question, original_response_a, original_response_b, model_a_label, model_b_label, reference_answer, cot_solution, few_shot_examples)
        
        try:
            response1 = self.llm_adapter.chat(
                model=request.judge_model,
                messages=[
                    {"role": "system", "content": "You are an expert evaluator. Provide detailed, specific comparative analysis with concrete examples."},
                    {"role": "user", "content": prompt1},
                ],
                options={"temperature": 0.0, "num_predict": 65536, "timeout": 300},
            )
            judgment1_content = self._extract_content(response1)
            
            if not judgment1_content or not judgment1_content.strip():
                return EvaluationResult(
                    success=False,
                    evaluation_type="pairwise",
                    error="Received empty judgment from model in first evaluation.",
                    execution_time=time.time() - start_time,
                )
            
            parsed1 = self._parse_judgment(judgment1_content)
            winner1 = parsed1.get("winner")
            
            # Second judgment: Swapped order (B, A)
            prompt2 = self._build_prompt(request.question, original_response_b, original_response_a, model_b_label, model_a_label, reference_answer, cot_solution, few_shot_examples)
            
            response2 = self.llm_adapter.chat(
                model=request.judge_model,
                messages=[
                    {"role": "system", "content": "You are an expert evaluator. Provide detailed, specific comparative analysis with concrete examples."},
                    {"role": "user", "content": prompt2},
                ],
                options={"temperature": 0.0, "num_predict": 65536, "timeout": 300},
            )
            judgment2_content = self._extract_content(response2)
            
            if not judgment2_content or not judgment2_content.strip():
                return EvaluationResult(
                    success=False,
                    evaluation_type="pairwise",
                    error="Received empty judgment from model in second evaluation.",
                    execution_time=time.time() - start_time,
                )
            
            parsed2 = self._parse_judgment(judgment2_content)
            winner2_swapped = parsed2.get("winner")  # This is in swapped order, need to convert back
            
            # Convert winner2 back to original order
            # If winner2_swapped is "A", it means the second response (original B) won in swapped order
            # So in original order, B won
            winner2 = "B" if winner2_swapped == "A" else ("A" if winner2_swapped == "B" else None)
            
            # Check consistency: Only declare win if both agree
            if winner1 and winner2 and winner1 == winner2:
                # Both agree - use the agreed winner
                final_winner = winner1
                # Average scores from both judgments (convert second back to original order)
                score_a1 = parsed1.get("score_a")
                score_b1 = parsed1.get("score_b")
                score_a2_swapped = parsed2.get("score_a")  # In swapped order
                score_b2_swapped = parsed2.get("score_b")  # In swapped order
                # Convert second scores back: swapped A = original B, swapped B = original A
                score_a2 = score_b2_swapped
                score_b2 = score_a2_swapped
                
                # Average the scores
                final_score_a = (score_a1 + score_a2) / 2 if (score_a1 is not None and score_a2 is not None) else (score_a1 or score_a2)
                final_score_b = (score_b1 + score_b2) / 2 if (score_b1 is not None and score_b2 is not None) else (score_b1 or score_b2)
                
                # Combine reasoning from both judgments
                reasoning1 = parsed1.get("reasoning", "")
                reasoning2 = parsed2.get("reasoning", "")
                
                # Add conversion explanation for clarity
                winner2_swapped = parsed2.get("winner")
                conversion_note = ""
                if winner2_swapped:
                    if winner2_swapped == "A":
                        conversion_note = f"\n\nNote: In swapped order, 'A' refers to original Response B, and 'B' refers to original Response A. The judge selected '{winner2_swapped}' in swapped order, which converts to '{final_winner}' in original order."
                    else:  # winner2_swapped == "B"
                        conversion_note = f"\n\nNote: In swapped order, 'A' refers to original Response B, and 'B' refers to original Response A. The judge selected '{winner2_swapped}' in swapped order, which converts to '{final_winner}' in original order."
                
                # Truncate response texts for display if too long
                response_a_display = original_response_a[:100] + "..." if len(original_response_a) > 100 else original_response_a
                response_b_display = original_response_b[:100] + "..." if len(original_response_b) > 100 else original_response_b
                
                combined_reasoning = f"""Conservative Position Bias Mitigation Applied:
Both evaluations agreed on the winner. Results from both orderings are combined below.

First Evaluation (Original Order):
Response A: "{response_a_display}"
Response B: "{response_b_display}"
{reasoning1}

Second Evaluation (Swapped Order):
⚠️ IMPORTANT: Positions are swapped to test for position bias
Response A (in swapped order) = Original Response B: "{response_b_display}"
Response B (in swapped order) = Original Response A: "{response_a_display}"
{reasoning2}{conversion_note}

Final Verdict: Both evaluations consistently identified {final_winner} as the winner (after converting the second evaluation back to original order)."""
                
                # Format scores properly (can't use conditional inside format specifier)
                score_a_str = f"{final_score_a:.1f}" if isinstance(final_score_a, (int, float)) else str(final_score_a)
                score_b_str = f"{final_score_b:.1f}" if isinstance(final_score_b, (int, float)) else str(final_score_b)
                
                final_judgment = f"""Winner: {final_winner}
Score A: {score_a_str}
Score B: {score_b_str}
Reasoning: {combined_reasoning}

Note: Conservative position bias mitigation was applied. Judge was called twice with swapped positions, and only declared a win because both evaluations agreed."""
            else:
                # Inconsistent results - declare tie
                final_winner = None  # Tie
                # Average scores
                score_a1 = parsed1.get("score_a")
                score_b1 = parsed1.get("score_b")
                score_a2_swapped = parsed2.get("score_a")
                score_b2_swapped = parsed2.get("score_b")
                score_a2 = score_b2_swapped
                score_b2 = score_a2_swapped
                
                final_score_a = (score_a1 + score_a2) / 2 if (score_a1 is not None and score_a2 is not None) else (score_a1 or score_a2)
                final_score_b = (score_b1 + score_b2) / 2 if (score_b1 is not None and score_b2 is not None) else (score_b1 or score_b2)
                
                reasoning1 = parsed1.get("reasoning", "")
                reasoning2 = parsed2.get("reasoning", "")
                
                # Truncate response texts for display if too long
                response_a_display = original_response_a[:100] + "..." if len(original_response_a) > 100 else original_response_a
                response_b_display = original_response_b[:100] + "..." if len(original_response_b) > 100 else original_response_b
                
                combined_reasoning = f"""Conservative Position Bias Mitigation Applied:
The two evaluations produced inconsistent results, so a tie is declared.

First Evaluation (Original Order) Winner: {winner1 or 'None'}
Response A: "{response_a_display}"
Response B: "{response_b_display}"
{reasoning1}

Second Evaluation (Swapped Order) Winner: {winner2 or 'None'} (converted to original order)
⚠️ IMPORTANT: Positions are swapped to test for position bias
Response A (in swapped order) = Original Response B: "{response_b_display}"
Response B (in swapped order) = Original Response A: "{response_a_display}"
{reasoning2}

Final Verdict: Tie - Results were inconsistent across position orderings, indicating potential position bias."""
                
                # Format scores properly (can't use conditional inside format specifier)
                score_a_str = f"{final_score_a:.1f}" if isinstance(final_score_a, (int, float)) else str(final_score_a)
                score_b_str = f"{final_score_b:.1f}" if isinstance(final_score_b, (int, float)) else str(final_score_b)
                
                final_judgment = f"""Winner: Tie
Score A: {score_a_str}
Score B: {score_b_str}
Reasoning: {combined_reasoning}

Note: Conservative position bias mitigation was applied. Judge was called twice with swapped positions, but results were inconsistent, so a tie was declared."""
            
            execution_time = time.time() - start_time
            return EvaluationResult(
                success=True,
                evaluation_type="pairwise",
                judgment=final_judgment,
                winner=final_winner,
                score_a=final_score_a,
                score_b=final_score_b,
                reasoning=combined_reasoning,
                execution_time=execution_time,
            )
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"[DEBUG] Exception in PairwiseStrategy._evaluate_conservative: {str(e)}", flush=True)
            print(f"[DEBUG] Traceback: {error_trace}", flush=True)
            sys.stdout.flush()
            error_msg = str(e)
            if "not found" in error_msg.lower() or "404" in error_msg:
                available = self.llm_adapter.list_models()
                error_msg = f"Model '{request.judge_model}' not found. Available models: {', '.join(available) if available else 'None - please pull a model first'}"
            return EvaluationResult(success=False, evaluation_type="pairwise", error=error_msg, execution_time=time.time() - start_time)


