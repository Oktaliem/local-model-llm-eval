"""Skills evaluation strategy"""
from core.domain.strategies.base import EvaluationStrategy
from core.domain.models import EvaluationRequest, EvaluationResult


class SkillsStrategy(EvaluationStrategy):
    @property
    def name(self) -> str:
        return "skills"

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        # Use the new service layer for skills evaluation
        from backend.services.skills_evaluation_service import evaluate_skill
        opts = request.options
        try:
            result = evaluate_skill(
                skill_type=opts.get("skill_type", "general"),
                question=request.question,
                response=request.response or "",
                reference_answer=opts.get("reference_answer"),
                domain=opts.get("domain"),
                judge_model=request.judge_model,
            )
            if not result.get("success"):
                return EvaluationResult(
                    success=False,
                    evaluation_type="skills",
                    error=result.get("error", "Unknown error"),
                    execution_time=result.get("execution_time", 0)
                )
            return EvaluationResult(
                success=True,
                evaluation_type="skills",
                judgment=result.get("judgment_text"),
                scores=result.get("metrics"),
                execution_time=result.get("execution_time", 0)
            )
        except Exception as e:
            return EvaluationResult(success=False, evaluation_type="skills", error=str(e))


