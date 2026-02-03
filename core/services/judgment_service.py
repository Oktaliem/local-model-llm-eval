"""Judgment service for pairwise comparisons and saving judgments"""
import random
import re
from typing import Dict, Any
from core.infrastructure.llm.ollama_client import OllamaAdapter
from core.infrastructure.db.repositories.judgments_repo import JudgmentsRepository


class JudgmentService:
    """Service for judgment operations"""
    
    def __init__(self, llm_adapter: OllamaAdapter = None, judgments_repo: JudgmentsRepository = None):
        self.llm_adapter = llm_adapter or OllamaAdapter()
        self.judgments_repo = judgments_repo or JudgmentsRepository()
    
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
    
    def judge_pairwise(
        self, 
        question: str, 
        response_a: str, 
        response_b: str, 
        model: str, 
        randomize_order: bool = True,
        conservative_position_bias: bool = False,
        reference_answer: str = None,
        chain_of_thought: bool = False,
        few_shot_examples: bool = False
    ) -> Dict[str, Any]:
        """Judge which of two responses is better.
        
        Args:
            question: The question or task
            response_a: First response to compare
            response_b: Second response to compare
            model: Judge model to use
            randomize_order: If True, randomly swap A/B to mitigate position bias (aggressive approach)
            conservative_position_bias: If True, use conservative approach: call judge twice with swapped positions,
                                       only declare win if both agree, else tie (MT-Bench paper recommendation)
            reference_answer: Optional reference answer to help judge evaluate responses more accurately
                             (MT-Bench paper recommendation for math/reasoning questions)
            chain_of_thought: If True, generate judge's independent solution first using CoT approach
                            (MT-Bench paper recommendation for math/reasoning questions)
            few_shot_examples: If True, include 3 example judgments in prompt (improves consistency 
                             from 65% to 77.5% but increases cost 4×, MT-Bench paper recommendation)
            
        Returns:
            Dict with 'success' (bool) and either 'judgment' (str) or 'error' (str)
        """
        # Store original responses for later reference
        original_response_a = response_a
        original_response_b = response_b
        
        # Generate Chain-of-Thought solution if requested (MT-Bench paper recommendation)
        cot_solution = ""
        if chain_of_thought:
            cot_solution = self._generate_chain_of_thought(question, model)
        
        # Conservative position bias mitigation (MT-Bench paper recommendation)
        if conservative_position_bias:
            return self._judge_pairwise_conservative(question, response_a, response_b, model, reference_answer, cot_solution, few_shot_examples)
        
        # Aggressive approach: Randomize response order to prevent position bias
        swapped = False
        if randomize_order and random.random() < 0.5:
            response_a, response_b = response_b, response_a
            swapped = True
        
        # Calculate response lengths for verbosity bias mitigation
        len_a = len(response_a.split())
        len_b = len(response_b.split())
        
        # Verbosity bias mitigation: Add instruction to not favor longer responses
        verbosity_note = ""
        if abs(len_a - len_b) > 20:  # Significant length difference
            verbosity_note = "\n\nIMPORTANT: Do not favor responses based on length. Evaluate based on quality, not verbosity. A concise, accurate response can be better than a verbose one."
        
        # Build prompt with optional reference answer and Chain-of-Thought
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
        
        # Build few-shot examples section if enabled
        few_shot_section = ""
        if few_shot_examples:
            few_shot_section = self._get_few_shot_examples()
        
        # Build prompt
        prompt = f"""{few_shot_section}Evaluate which response is better.

Question: {question}
{cot_section}{reference_section}
Response A:
{response_a}

Response B:
{response_b}
{verbosity_note}

Evaluate based on: accuracy, relevance, clarity, completeness, helpfulness.
Do not favor based on position or length. Focus on quality.
{f"Pay special attention to how well each response aligns with the judge's independent solution and reference answer (if provided) above." if (cot_solution or reference_answer) else ""}

IMPORTANT: Provide specific comparative reasoning that explains:
- What makes the winner better than the other response
- Specific strengths and weaknesses of each response
- Why the scores differ (if they do)
- Concrete examples from the responses to support your evaluation
{f"- How each response compares to the reference answer (if provided)" if reference_answer else ""}

Format:
Begin your evaluation by comparing the two responses. Then provide your judgment in the following format:

Winner: [[A]] or [[B]] or [[C]]
- Use [[A]] if Response A is better
- Use [[B]] if Response B is better  
- Use [[C]] if both responses are equally good (tie)

Score A: [0-10]
Score B: [0-10]
Reasoning: [Detailed comparative analysis explaining why one response is better, with specific examples]

IMPORTANT: End your response with [[A]], [[B]], or [[C]] to clearly indicate the winner.
"""
        
        try:
            response = self.llm_adapter.chat(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert evaluator. Provide detailed, specific comparative analysis with concrete examples."},
                    {"role": "user", "content": prompt}
                ],
                options={
                    # Use temperature 0.0 for maximally deterministic judgments
                    "temperature": 0.0,
                    "num_predict": 65536,  # 65,536 tokens for very detailed, comprehensive judgments
                    "timeout": 300  # 5 minute timeout to handle large models
                }
            )
            
            # Extract judgment content
            judgment_content = self._extract_judgment_content(response)
            
            if not judgment_content or not judgment_content.strip():
                return {
                    "success": False,
                    "error": "Received empty judgment from model. The model may not have generated a response."
                }
            
            # If responses were swapped, swap back the judgment
            if swapped:
                judgment_content = self._swap_back_judgment(judgment_content, original_response_a, original_response_b)
            
            return {"success": True, "judgment": judgment_content}
            
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "404" in error_msg:
                available = self.llm_adapter.list_models()
                error_msg = f"Model '{model}' not found. Available models: {', '.join(available) if available else 'None - please pull a model first'}"
            return {"success": False, "error": error_msg}
    
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
            
            solution = self._extract_judgment_content(response)
            return solution.strip() if solution else ""
        except Exception as e:
            # If CoT generation fails, continue without it
            return ""
    
    def _swap_back_judgment(self, judgment_content: str, original_response_a: str, original_response_b: str) -> str:
        """Swap back judgment references if responses were randomized."""
        # Swap winner
        winner_match = re.search(r"Winner:\s*([AB])", judgment_content, re.IGNORECASE)
        if winner_match:
            model_winner = winner_match.group(1).upper()
            original_winner = "B" if model_winner == "A" else "A"
            judgment_content = re.sub(
                r"Winner:\s*" + model_winner + r"(\s|$|\(|:)",
                f"Winner: {original_winner}\\1",
                judgment_content,
                flags=re.IGNORECASE
            )
        
        # Swap scores
        score_a_match = re.search(r"Score A:\s*([0-9.]+)", judgment_content, re.IGNORECASE)
        score_b_match = re.search(r"Score B:\s*([0-9.]+)", judgment_content, re.IGNORECASE)
        if score_a_match and score_b_match:
            swapped_score_a = score_a_match.group(1)
            swapped_score_b = score_b_match.group(1)
            judgment_content = re.sub(r"Score A:\s*" + re.escape(swapped_score_a), "TEMP_SCORE_A_MARKER", judgment_content, flags=re.IGNORECASE)
            judgment_content = re.sub(r"Score B:\s*" + re.escape(swapped_score_b), "TEMP_SCORE_B_MARKER", judgment_content, flags=re.IGNORECASE)
            judgment_content = re.sub("TEMP_SCORE_A_MARKER", f"Score A: {swapped_score_b}", judgment_content, flags=re.IGNORECASE)
            judgment_content = re.sub("TEMP_SCORE_B_MARKER", f"Score B: {swapped_score_a}", judgment_content, flags=re.IGNORECASE)
        
        # Swap response references
        judgment_content = re.sub(r"\bResponse\s+A\b", "TEMP_MARKER_RESPONSE_A", judgment_content, flags=re.IGNORECASE)
        judgment_content = re.sub(r"\bResponse\s+B\b", "Response A", judgment_content, flags=re.IGNORECASE)
        judgment_content = re.sub("TEMP_MARKER_RESPONSE_A", "Response B", judgment_content, flags=re.IGNORECASE)
        
        return judgment_content
    
    def _judge_pairwise_conservative(self, question: str, response_a: str, response_b: str, model: str, reference_answer: str = None, cot_solution: str = "", few_shot_examples: bool = False) -> Dict[str, Any]:
        """Conservative position bias mitigation: Call judge twice with swapped positions.
        
        As per MT-Bench paper recommendation:
        - Call judge twice: once with original order, once with swapped order
        - Only declare a win if both agree on the winner
        - If results are inconsistent, declare a tie
        
        Args:
            question: The question or task
            response_a: First response to compare
            response_b: Second response to compare
            model: Judge model to use
            reference_answer: Optional reference answer
            cot_solution: Optional Chain-of-Thought solution from judge
        """
        # Calculate response lengths for verbosity bias mitigation
        len_a = len(response_a.split())
        len_b = len(response_b.split())
        verbosity_note = ""
        if abs(len_a - len_b) > 20:
            verbosity_note = "\n\nIMPORTANT: Do not favor responses based on length. Evaluate based on quality, not verbosity. A concise, accurate response can be better than a verbose one."
        
        # Build reference section if provided
        reference_section = ""
        if reference_answer:
            reference_section = f"""

Reference Answer:
{reference_answer}

Use this reference answer to help evaluate the accuracy and correctness of the responses. Compare each response against this reference to assess how well they align with the correct answer.
"""
        
        # Build Chain-of-Thought section if provided
        cot_section = ""
        if cot_solution:
            cot_section = f"""

Judge's Independent Solution (Chain-of-Thought):
{cot_solution}

Use this independent solution to help evaluate the responses. Compare each response against this solution to assess accuracy and correctness. This helps avoid being misled by incorrect answers in the responses.
"""
        
        # Build few-shot examples section if enabled
        few_shot_section = ""
        if few_shot_examples:
            few_shot_section = self._get_few_shot_examples()
        
        # First judgment: Original order (A, B)
        prompt1 = f"""{few_shot_section}Evaluate which response is better.

Question: {question}
{cot_section}{reference_section}
Response A:
{response_a}

Response B:
{response_b}
{verbosity_note}

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
        
        try:
            response1 = self.llm_adapter.chat(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert evaluator. Provide detailed, specific comparative analysis with concrete examples."},
                    {"role": "user", "content": prompt1}
                ],
                options={
                    "temperature": 0.0,
                    "num_predict": 65536,
                    "timeout": 300
                }
            )
            
            judgment1_content = self._extract_judgment_content(response1)
            if not judgment1_content or not judgment1_content.strip():
                return {
                    "success": False,
                    "error": "Received empty judgment from model in first evaluation."
                }
            
            parsed1 = self._parse_judgment_for_conservative(judgment1_content)
            winner1 = parsed1.get("winner")
            
            # Second judgment: Swapped order (B, A)
            prompt2 = f"""{few_shot_section}Evaluate which response is better.

Question: {question}
{cot_section}{reference_section}
Response A:
{response_b}

Response B:
{response_a}
{verbosity_note}

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
            
            response2 = self.llm_adapter.chat(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert evaluator. Provide detailed, specific comparative analysis with concrete examples."},
                    {"role": "user", "content": prompt2}
                ],
                options={
                    "temperature": 0.0,
                    "num_predict": 65536,
                    "timeout": 300
                }
            )
            
            judgment2_content = self._extract_judgment_content(response2)
            if not judgment2_content or not judgment2_content.strip():
                return {
                    "success": False,
                    "error": "Received empty judgment from model in second evaluation."
                }
            
            parsed2 = self._parse_judgment_for_conservative(judgment2_content)
            winner2_swapped = parsed2.get("winner")  # This is in swapped order
            
            # Convert winner2 back to original order
            # If winner2_swapped is "A", it means the second response (original B) won in swapped order
            winner2 = "B" if winner2_swapped == "A" else ("A" if winner2_swapped == "B" else None)
            
            # Check consistency: Only declare win if both agree
            if winner1 and winner2 and winner1 == winner2:
                # Both agree - use the agreed winner
                final_winner = winner1
                # Average scores from both judgments
                score_a1 = parsed1.get("score_a")
                score_b1 = parsed1.get("score_b")
                score_a2_swapped = parsed2.get("score_a")  # In swapped order
                score_b2_swapped = parsed2.get("score_b")  # In swapped order
                # Convert: swapped A = original B, swapped B = original A
                score_a2 = score_b2_swapped
                score_b2 = score_a2_swapped
                
                final_score_a = (score_a1 + score_a2) / 2 if (score_a1 is not None and score_a2 is not None) else (score_a1 or score_a2)
                final_score_b = (score_b1 + score_b2) / 2 if (score_b1 is not None and score_b2 is not None) else (score_b1 or score_b2)
                
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
                response_a_display = response_a[:100] + "..." if len(response_a) > 100 else response_a
                response_b_display = response_b[:100] + "..." if len(response_b) > 100 else response_b
                
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
                final_winner = None
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
                response_a_display = response_a[:100] + "..." if len(response_a) > 100 else response_a
                response_b_display = response_b[:100] + "..." if len(response_b) > 100 else response_b
                
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
            
            return {"success": True, "judgment": final_judgment}
            
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "404" in error_msg:
                available = self.llm_adapter.list_models()
                error_msg = f"Model '{model}' not found. Available models: {', '.join(available) if available else 'None - please pull a model first'}"
            return {"success": False, "error": error_msg}
    
    def _extract_judgment_content(self, response: Any) -> str:
        """Extract judgment content from LLM response."""
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
    
    def _parse_judgment_for_conservative(self, judgment: str) -> Dict[str, Any]:
        """Parse judgment to extract winner, scores, and reasoning."""
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
    
    def save_judgment(
        self,
        question: str,
        response_a: str,
        response_b: str,
        model_a: str,
        model_b: str,
        judge_model: str,
        judgment: str,
        judgment_type: str,
        evaluation_id: str = None,
        metrics_json: str = None,
        trace_json: str = None,
    ) -> int:
        """Save a judgment to the database.
        
        Args:
            question: The question that was evaluated
            response_a: First response
            response_b: Second response
            model_a: Model that generated response A
            model_b: Model that generated response B
            judge_model: Model used for judging
            judgment: The judgment text
            judgment_type: Type of judgment (e.g., 'pairwise_auto', 'pairwise_manual')
            evaluation_id: Optional evaluation ID
            metrics_json: Optional metrics as JSON string
            trace_json: Optional trace as JSON string
            
        Returns:
            The ID of the saved judgment
        """
        return self.judgments_repo.save(
            question=question,
            response_a=response_a,
            response_b=response_b,
            model_a=model_a,
            model_b=model_b,
            judge_model=judge_model,
            judgment=judgment,
            judgment_type=judgment_type,
            evaluation_id=evaluation_id,
            metrics_json=metrics_json,
            trace_json=trace_json,
        )


# Global instance for convenience
_judgment_service = None

def get_judgment_service() -> JudgmentService:
    """Get the global judgment service instance."""
    global _judgment_service
    if _judgment_service is None:
        _judgment_service = JudgmentService()
    return _judgment_service

def judge_pairwise(question: str, response_a: str, response_b: str, model: str, randomize_order: bool = True, conservative_position_bias: bool = False, few_shot_examples: bool = False) -> Dict[str, Any]:
    """Convenience function to judge two responses.
    
    Args:
        question: The question or task
        response_a: First response to compare
        response_b: Second response to compare
        model: Judge model to use
        randomize_order: If True, randomly swap A/B to mitigate position bias (aggressive approach)
        conservative_position_bias: If True, use conservative approach: call judge twice with swapped positions,
                                   only declare win if both agree, else tie (MT-Bench paper recommendation)
        few_shot_examples: If True, include 3 example judgments in prompt (improves consistency but increases cost 4×)
        
    Returns:
        Dict with 'success' (bool) and either 'judgment' (str) or 'error' (str)
    """
    return get_judgment_service().judge_pairwise(question, response_a, response_b, model, randomize_order, conservative_position_bias, few_shot_examples)

def save_judgment(
    question: str,
    response_a: str,
    response_b: str,
    model_a: str,
    model_b: str,
    judge_model: str,
    judgment: str,
    judgment_type: str,
    evaluation_id: str = None,
    metrics_json: str = None,
    trace_json: str = None,
) -> int:
    """Convenience function to save a judgment to the database.
    
    Args:
        question: The question that was evaluated
        response_a: First response
        response_b: Second response
        model_a: Model that generated response A
        model_b: Model that generated response B
        judge_model: Model used for judging
        judgment: The judgment text
        judgment_type: Type of judgment (e.g., 'pairwise_auto', 'pairwise_manual')
        evaluation_id: Optional evaluation ID
        metrics_json: Optional metrics as JSON string
        trace_json: Optional trace as JSON string
        
    Returns:
        The ID of the saved judgment
    """
    return get_judgment_service().save_judgment(
        question=question,
        response_a=response_a,
        response_b=response_b,
        model_a=model_a,
        model_b=model_b,
        judge_model=judge_model,
        judgment=judgment,
        judgment_type=judgment_type,
        evaluation_id=evaluation_id,
        metrics_json=metrics_json,
        trace_json=trace_json,
    )



