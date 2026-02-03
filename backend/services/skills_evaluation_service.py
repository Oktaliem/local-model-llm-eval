"""
Skills Evaluation service for domain-specific skill evaluations.
Extracted from app.py to separate backend concerns.
"""
import re
import time
import logging
import uuid
from typing import Dict, Any, Optional
from core.infrastructure.llm.ollama_client import OllamaAdapter

logger = logging.getLogger(__name__)


def evaluate_skill(
    skill_type: str,
    question: str,
    response: str,
    reference_answer: Optional[str] = None,
    domain: Optional[str] = None,
    judge_model: str = "llama3"
) -> Dict[str, Any]:
    """Evaluate a skill-specific response using LLM.
    
    Args:
        skill_type: Type of skill (mathematics, coding, reasoning, general)
        question: The question or task
        response: The response to evaluate
        reference_answer: Optional reference answer for comparison
        domain: Optional domain specification (e.g., algebra, python)
        judge_model: Model to use for judging
        
    Returns:
        Dict with 'success' (bool), scores, judgment_text, metrics, trace, and execution_time
    """
    start_time = time.time()
    llm_adapter = OllamaAdapter()
    evaluation_id = str(uuid.uuid4())
    
    # Skill-specific evaluation prompts
    skill_prompts = {
        "mathematics": """Evaluate this mathematical problem-solving response.

Question: {question}
Response: {response}
{reference}

Rate the response on these criteria (0-10 scale):

1. **Correctness**: Is the answer mathematically correct?
   - 9-10: Completely correct, all steps accurate
   - 7-8: Mostly correct, minor errors
   - 5-6: Partially correct, some errors
   - 3-4: Mostly incorrect
   - 0-2: Completely wrong

2. **Completeness**: Is the solution complete and well-explained?
   - 9-10: Fully complete with clear steps
   - 7-8: Complete but could be clearer
   - 5-6: Partially complete
   - 3-4: Incomplete solution
   - 0-2: Very incomplete

3. **Clarity**: Is the explanation clear and easy to follow?
   - 9-10: Extremely clear and well-structured
   - 7-8: Clear with minor issues
   - 5-6: Somewhat clear
   - 3-4: Unclear
   - 0-2: Very unclear

4. **Proficiency**: Overall mathematical skill level demonstrated?
   - 9-10: Expert level, advanced techniques
   - 7-8: Strong proficiency
   - 5-6: Moderate proficiency
   - 3-4: Basic proficiency
   - 0-2: Poor proficiency

Provide scores and brief explanations for each metric. Format your response as:
Correctness: [0-10]
Completeness: [0-10]
Clarity: [0-10]
Proficiency: [0-10]
[Your detailed explanation here]""",
        
        "coding": """Evaluate this coding/programming response.

Question: {question}
Response: {response}
{reference}

Rate the response on these criteria (0-10 scale):

1. **Correctness**: Does the code work correctly?
   - 9-10: Perfect, handles all edge cases
   - 7-8: Works correctly for most cases
   - 5-6: Works but has bugs
   - 3-4: Mostly incorrect
   - 0-2: Doesn't work

2. **Completeness**: Is the solution complete?
   - 9-10: Fully complete with error handling
   - 7-8: Complete but missing some features
   - 5-6: Partially complete
   - 3-4: Incomplete
   - 0-2: Very incomplete

3. **Clarity**: Is the code readable and well-structured?
   - 9-10: Excellent code quality, well-documented
   - 7-8: Good code quality
   - 5-6: Acceptable but could be better
   - 3-4: Poor code quality
   - 0-2: Very poor code quality

4. **Proficiency**: Overall coding skill level?
   - 9-10: Expert level, best practices
   - 7-8: Strong coding skills
   - 5-6: Moderate skills
   - 3-4: Basic skills
   - 0-2: Poor skills

Provide scores and brief explanations for each metric. Format your response as:
Correctness: [0-10]
Completeness: [0-10]
Clarity: [0-10]
Proficiency: [0-10]
[Your detailed explanation here]""",
        
        "reasoning": """Evaluate this logical reasoning response.

Question: {question}
Response: {response}
{reference}

Rate the response on these criteria (0-10 scale):

1. **Correctness**: Is the reasoning logically sound?
   - 9-10: Perfect logical reasoning
   - 7-8: Mostly sound reasoning
   - 5-6: Some logical flaws
   - 3-4: Major logical errors
   - 0-2: Fundamentally flawed

2. **Completeness**: Is the reasoning complete?
   - 9-10: Fully complete, all aspects covered
   - 7-8: Mostly complete
   - 5-6: Partially complete
   - 3-4: Incomplete
   - 0-2: Very incomplete

3. **Clarity**: Is the reasoning clearly explained?
   - 9-10: Extremely clear and well-structured
   - 7-8: Clear reasoning
   - 5-6: Somewhat clear
   - 3-4: Unclear
   - 0-2: Very unclear

4. **Proficiency**: Overall reasoning skill level?
   - 9-10: Expert level reasoning
   - 7-8: Strong reasoning skills
   - 5-6: Moderate reasoning
   - 3-4: Basic reasoning
   - 0-2: Poor reasoning

Provide scores and brief explanations for each metric. Format your response as:
Correctness: [0-10]
Completeness: [0-10]
Clarity: [0-10]
Proficiency: [0-10]
[Your detailed explanation here]""",
        
        "general": """Evaluate this response for general skills.

Question: {question}
Response: {response}
{reference}

Rate the response on these criteria (0-10 scale):

1. **Correctness**: Is the information accurate?
2. **Completeness**: Is the response complete?
3. **Clarity**: Is the response clear and well-structured?
4. **Proficiency**: Overall skill level demonstrated?

Provide scores and brief explanations for each metric. Format your response as:
Correctness: [0-10]
Completeness: [0-10]
Clarity: [0-10]
Proficiency: [0-10]
[Your detailed explanation here]"""
    }
    
    # Get skill-specific prompt
    prompt_template = skill_prompts.get(skill_type.lower(), skill_prompts["general"])
    reference_text = f"Reference Answer: {reference_answer}" if reference_answer else "No reference answer provided."
    domain_text = f"Domain: {domain}" if domain else ""
    
    prompt = prompt_template.format(
        question=question,
        response=response,
        reference=reference_text
    )
    
    if domain_text:
        prompt = f"{domain_text}\n\n{prompt}"
    
    trace = {
        "evaluation_id": evaluation_id,
        "type": "skills_evaluation",
        "skill_type": skill_type,
        "question": question,
        "domain": domain,
        "steps": []
    }
    
    try:
        trace["steps"].append({"step": "llm_evaluation", "status": "running"})
        logger.info(f"Starting skills evaluation for {skill_type} with model {judge_model}")
        
        response_obj = llm_adapter.chat(
            model=judge_model,
            messages=[
                {"role": "system", "content": f"You are an expert evaluator for {skill_type} skills."},
                {"role": "user", "content": prompt}
            ],
            options={
                "temperature": 0.2,
                "num_predict": 65536,  # Increased to 65536 for comprehensive evaluations
                "timeout": 300  # 5 minute timeout for safety
            }
        )
        
        judgment_text = response_obj.get("message", {}).get("content", "")
        if not judgment_text:
            # Try alternative response structure
            if hasattr(response_obj, "message") and hasattr(response_obj.message, "content"):
                judgment_text = response_obj.message.content
            elif hasattr(response_obj, "message") and isinstance(response_obj.message, dict):
                judgment_text = response_obj.message.get("content", "")
        
        if not judgment_text or not judgment_text.strip():
            logger.error("Received empty judgment from model")
            return {
                "success": False,
                "error": "Received empty judgment from model. The model may not have generated a response.",
                "evaluation_id": evaluation_id,
                "execution_time": time.time() - start_time
            }
        
        trace["steps"][-1]["status"] = "completed"
        logger.info(f"Received judgment text (length: {len(judgment_text)} chars)")
        
        # Improved score parsing with multiple regex patterns and validation
        scores = _parse_scores(judgment_text)
        
        if not scores["parsed_successfully"]:
            logger.warning(f"Failed to parse scores from judgment. Found: {scores}")
            return {
                "success": False,
                "error": f"Failed to parse scores from judgment. Expected format: 'Correctness: [0-10]', etc. Received: {judgment_text[:200]}...",
                "evaluation_id": evaluation_id,
                "judgment_text": judgment_text,
                "trace": trace,
                "execution_time": time.time() - start_time
            }
        
        correctness_score = scores["correctness"]
        completeness_score = scores["completeness"]
        clarity_score = scores["clarity"]
        proficiency_score = scores["proficiency"]
        
        # Validate scores are in range
        for score_name, score_value in [
            ("correctness", correctness_score),
            ("completeness", completeness_score),
            ("clarity", clarity_score),
            ("proficiency", proficiency_score)
        ]:
            if not (0.0 <= score_value <= 10.0):
                logger.warning(f"{score_name} score {score_value} is out of range [0-10], clamping")
                if score_value < 0:
                    scores[score_name] = 0.0
                elif score_value > 10:
                    scores[score_name] = 10.0
        
        overall_score = (correctness_score + completeness_score + clarity_score + proficiency_score) / 4
        
        metrics = {
            "correctness": {
                "score": correctness_score,
                "explanation": judgment_text
            },
            "completeness": {
                "score": completeness_score,
                "explanation": judgment_text
            },
            "clarity": {
                "score": clarity_score,
                "explanation": judgment_text
            },
            "proficiency": {
                "score": proficiency_score,
                "explanation": judgment_text
            },
            "overall_score": overall_score
        }
        
        trace["metrics"] = metrics
        trace["steps"].append({"step": "completed", "status": "completed"})
        
        execution_time = time.time() - start_time
        logger.info(f"Skills evaluation completed in {execution_time:.2f}s")
        
        return {
            "success": True,
            "evaluation_id": evaluation_id,
            "correctness_score": correctness_score,
            "completeness_score": completeness_score,
            "clarity_score": clarity_score,
            "proficiency_score": proficiency_score,
            "overall_score": overall_score,
            "judgment_text": judgment_text,
            "metrics": metrics,
            "trace": trace,
            "execution_time": execution_time
        }
        
    except Exception as e:
        logger.error(f"Error during skills evaluation: {str(e)}", exc_info=True)
        trace["steps"][-1]["status"] = "error"
        trace["error"] = str(e)
        return {
            "success": False,
            "error": f"Error during evaluation: {str(e)}",
            "evaluation_id": evaluation_id,
            "trace": trace,
            "execution_time": time.time() - start_time
        }


def _parse_scores(judgment_text: str) -> Dict[str, Any]:
    """Parse scores from judgment text using multiple regex patterns.
    
    Returns:
        Dict with scores and 'parsed_successfully' flag
    """
    # Multiple regex patterns to handle different formats
    patterns = [
        # Pattern 1: "Correctness: 8.5" or "Correctness: 8"
        (r'Correctness[:\s]+([0-9]+\.?[0-9]*)', 'correctness'),
        (r'Completeness[:\s]+([0-9]+\.?[0-9]*)', 'completeness'),
        (r'Clarity[:\s]+([0-9]+\.?[0-9]*)', 'clarity'),
        (r'Proficiency[:\s]+([0-9]+\.?[0-9]*)', 'proficiency'),
        
        # Pattern 2: "**Correctness**: 8.5" (markdown bold)
        (r'\*\*Correctness\*\*[:\s]+([0-9]+\.?[0-9]*)', 'correctness'),
        (r'\*\*Completeness\*\*[:\s]+([0-9]+\.?[0-9]*)', 'completeness'),
        (r'\*\*Clarity\*\*[:\s]+([0-9]+\.?[0-9]*)', 'clarity'),
        (r'\*\*Proficiency\*\*[:\s]+([0-9]+\.?[0-9]*)', 'proficiency'),
        
        # Pattern 3: "1. Correctness: 8.5" (numbered list)
        (r'1\.\s*Correctness[:\s]+([0-9]+\.?[0-9]*)', 'correctness'),
        (r'2\.\s*Completeness[:\s]+([0-9]+\.?[0-9]*)', 'completeness'),
        (r'3\.\s*Clarity[:\s]+([0-9]+\.?[0-9]*)', 'clarity'),
        (r'4\.\s*Proficiency[:\s]+([0-9]+\.?[0-9]*)', 'proficiency'),
    ]
    
    scores = {
        "correctness": None,
        "completeness": None,
        "clarity": None,
        "proficiency": None
    }
    
    # Try all patterns
    for pattern, score_key in patterns:
        match = re.search(pattern, judgment_text, re.IGNORECASE)
        if match and scores[score_key] is None:
            try:
                scores[score_key] = float(match.group(1))
                logger.debug(f"Parsed {score_key}: {scores[score_key]} using pattern: {pattern}")
            except (ValueError, IndexError):
                continue
    
    # Check if all scores were parsed
    parsed_successfully = all(score is not None for score in scores.values())
    
    if not parsed_successfully:
        logger.warning(f"Failed to parse all scores. Found: {scores}")
        logger.debug(f"Judgment text sample: {judgment_text[:500]}")
    
    # Default to 5.0 only if parsing failed (for backward compatibility, but we'll return success=False)
    if not parsed_successfully:
        scores["correctness"] = 5.0
        scores["completeness"] = 5.0
        scores["clarity"] = 5.0
        scores["proficiency"] = 5.0
    
    scores["parsed_successfully"] = parsed_successfully
    return scores

