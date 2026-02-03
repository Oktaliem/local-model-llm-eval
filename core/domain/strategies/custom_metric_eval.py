"""Custom metric evaluation strategy"""
from core.domain.strategies.base import EvaluationStrategy
from core.domain.models import EvaluationRequest, EvaluationResult


class CustomMetricStrategy(EvaluationStrategy):
    @property
    def name(self) -> str:
        return "custom_metric"

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        # TODO: Refactor to use backend.services.custom_metric_service.evaluate_with_custom_metric
        # Local import to avoid circular dependency with app.py
        from backend.services.evaluation_functions import evaluate_with_custom_metric  # type: ignore
        opts = request.options
        metric_id = opts.get("metric_id")
        response = request.response or request.response_a or ""
        if not metric_id:
            return EvaluationResult(success=False, evaluation_type="custom_metric", error="metric_id is required")
        if not response:
            return EvaluationResult(success=False, evaluation_type="custom_metric", error="response is required")
        result = evaluate_with_custom_metric(metric_id=metric_id, question=request.question, response=response, reference=opts.get("reference"), judge_model=request.judge_model)
        if not result.get("success"):
            return EvaluationResult(success=False, evaluation_type="custom_metric", error=result.get("error"))
        return EvaluationResult(success=True, evaluation_type="custom_metric", judgment=result.get("judgment_text"), scores=result.get("scores"))


