"""Comprehensive evaluation strategy"""
from core.domain.strategies.base import EvaluationStrategy
from core.domain.models import EvaluationRequest, EvaluationResult


class ComprehensiveStrategy(EvaluationStrategy):
    @property
    def name(self) -> str:
        return "comprehensive"

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        # TODO: Refactor to use EvaluationService directly instead of app.py wrapper
        # Local import to avoid circular dependency with app.py
        from backend.services.evaluation_functions import evaluate_comprehensive  # type: ignore
        response = request.response or request.response_a or ""
        if not response:
            return EvaluationResult(success=False, evaluation_type="comprehensive", error="response is required for comprehensive evaluation")
        result = evaluate_comprehensive(
            question=request.question,
            response=response,
            reference=request.options.get("reference"),
            model=request.judge_model,
            task_type=request.options.get("task_type", "general"),
            include_additional_properties=request.options.get("include_additional_properties", True),
        )
        if not result.get("success"):
            return EvaluationResult(success=False, evaluation_type="comprehensive", error=result.get("error"))
        return EvaluationResult(success=True, evaluation_type="comprehensive", judgment=result.get("judgment_text"), scores=result.get("metrics"))


