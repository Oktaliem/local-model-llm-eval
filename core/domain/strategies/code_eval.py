"""Code evaluation strategy"""
from typing import Optional, List
from core.domain.strategies.base import EvaluationStrategy
from core.domain.models import EvaluationRequest, EvaluationResult


class CodeEvalStrategy(EvaluationStrategy):
    @property
    def name(self) -> str:
        return "code"

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        # TODO: Refactor to use EvaluationService directly instead of app.py wrapper
        # Local import to avoid circular dependency with app.py
        from backend.services.evaluation_functions import evaluate_code_comprehensive  # type: ignore
        code = request.options.get("code") or request.response or request.response_a or ""
        language = request.options.get("language", "python")
        test_inputs: Optional[List[str]] = request.options.get("test_inputs")
        expected_output = request.options.get("expected_output")
        if not code:
            return EvaluationResult(success=False, evaluation_type="code", error="code is required for code evaluation")
        result = evaluate_code_comprehensive(code=code, language=language, test_inputs=test_inputs, expected_output=expected_output)
        if not result.get("success"):
            return EvaluationResult(success=False, evaluation_type="code", error=result.get("error"))
        return EvaluationResult(success=True, evaluation_type="code", judgment=result.get("judgment_text"), scores=result.get("results"))


