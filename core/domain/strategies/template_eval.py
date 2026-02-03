"""Template-driven evaluation strategy (delegates to comprehensive)"""
from core.domain.strategies.base import EvaluationStrategy
from core.domain.models import EvaluationRequest, EvaluationResult


class TemplateEvalStrategy(EvaluationStrategy):
    @property
    def name(self) -> str:
        return "template"

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        # TODO: Refactor to use EvaluationService directly instead of app.py wrapper
        # Local import to avoid circular dependency with app.py
        from backend.services.evaluation_functions import evaluate_comprehensive  # type: ignore
        opts = request.options
        response = request.response or request.response_a or ""
        if not response:
            return EvaluationResult(success=False, evaluation_type="template", error="response is required")
        result = evaluate_comprehensive(
            question=request.question,
            response=response,
            reference=opts.get("reference"),
            model=request.judge_model,
            task_type=opts.get("task_type", "general"),
            include_additional_properties=opts.get("include_additional_properties", True),
        )
        if not result.get("success"):
            return EvaluationResult(success=False, evaluation_type="template", error=result.get("error"))
        return EvaluationResult(success=True, evaluation_type="template", judgment=result.get("judgment_text"), scores=result.get("metrics"))


