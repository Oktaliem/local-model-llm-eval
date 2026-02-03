"""Router evaluation strategy"""
from core.domain.strategies.base import EvaluationStrategy
from core.domain.models import EvaluationRequest, EvaluationResult


class RouterStrategy(EvaluationStrategy):
    @property
    def name(self) -> str:
        return "router"

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        # TODO: Refactor to use EvaluationService directly instead of app.py wrapper
        # Local import to avoid circular dependency with app.py
        from backend.services.evaluation_functions import evaluate_router_decision  # type: ignore
        opts = request.options
        try:
            result = evaluate_router_decision(
                query=request.question,
                available_tools=opts.get("available_tools", []),
                selected_tool=opts.get("selected_tool", ""),
                context=opts.get("context"),
                expected_tool=opts.get("expected_tool"),
                routing_strategy=opts.get("routing_strategy"),
                judge_model=request.judge_model,
            )
            if not result.get("success"):
                return EvaluationResult(success=False, evaluation_type="router", error=result.get("error"))
            return EvaluationResult(success=True, evaluation_type="router", judgment=result.get("judgment_text"), scores=result.get("metrics"))
        except Exception as e:
            return EvaluationResult(success=False, evaluation_type="router", error=str(e))


