"""Single response grading strategy"""
from core.domain.strategies.base import EvaluationStrategy
from core.domain.models import EvaluationRequest, EvaluationResult


class SingleStrategy(EvaluationStrategy):
    @property
    def name(self) -> str:
        return "single"

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        # TODO: Refactor to use EvaluationService directly instead of app.py wrapper
        # Local import to avoid circular import with app.py
        from backend.services.evaluation_functions import judge_single  # type: ignore
        if not request.response:
            return EvaluationResult(success=False, evaluation_type="single", error="response is required for single evaluation")
        criteria = request.options.get("criteria", "Accuracy, relevance, clarity, completeness, helpfulness")
        result = judge_single(question=request.question, response=request.response, criteria=criteria, model=request.judge_model)
        if not result.get("success"):
            return EvaluationResult(success=False, evaluation_type="single", error=result.get("error"))
        return EvaluationResult(success=True, evaluation_type="single", judgment=result.get("judgment", result.get("judgment_text")), scores=result.get("metrics"))


