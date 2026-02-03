"""Trajectory evaluation strategy"""
from core.domain.strategies.base import EvaluationStrategy
from core.domain.models import EvaluationRequest, EvaluationResult


class TrajectoryStrategy(EvaluationStrategy):
    @property
    def name(self) -> str:
        return "trajectory"

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        # TODO: Refactor to use EvaluationService directly instead of app.py wrapper
        # Local import to avoid circular dependency with app.py
        from backend.services.evaluation_functions import evaluate_trajectory  # type: ignore
        opts = request.options
        try:
            result = evaluate_trajectory(
                task_description=request.question,
                trajectory=opts.get("trajectory", []),
                expected_trajectory=opts.get("expected_trajectory"),
                trajectory_type=opts.get("trajectory_type"),
                judge_model=request.judge_model,
            )
            if not result.get("success"):
                return EvaluationResult(success=False, evaluation_type="trajectory", error=result.get("error"))
            return EvaluationResult(success=True, evaluation_type="trajectory", judgment=result.get("judgment_text"), scores=result.get("metrics"))
        except Exception as e:
            return EvaluationResult(success=False, evaluation_type="trajectory", error=str(e))


