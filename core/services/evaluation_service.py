"""Evaluation service - facade over strategies"""
import uuid
from typing import Dict, Any, Optional
from core.domain.models import EvaluationRequest, EvaluationResult
from core.domain.factory import StrategyFactory
from core.infrastructure.db.repositories.judgments_repo import JudgmentsRepository
from core.common.timing import track_execution_time


class EvaluationService:
    """Service for executing evaluations"""

    def __init__(self, strategy_factory: Optional[StrategyFactory] = None, judgments_repo: Optional[JudgmentsRepository] = None):
        self.strategy_factory = strategy_factory or StrategyFactory()
        self.judgments_repo = judgments_repo or JudgmentsRepository()

    @track_execution_time
    def evaluate(
        self,
        evaluation_type: str,
        question: str,
        judge_model: str,
        response_a: Optional[str] = None,
        response_b: Optional[str] = None,
        response: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        save_to_db: bool = False,
    ) -> Dict[str, Any]:
        if options is None:
            options = {}
        request = EvaluationRequest(
            evaluation_type=evaluation_type,
            question=question,
            response_a=response_a,
            response_b=response_b,
            response=response,
            judge_model=judge_model,
            options=options,
            evaluation_id=str(uuid.uuid4()),
        )
        strategy = self.strategy_factory.get(evaluation_type)
        result: EvaluationResult = strategy.evaluate(request)
        if save_to_db and result.success:
            self._save_result(result, request)
        return self._result_to_dict(result)

    def _save_result(self, result: EvaluationResult, request: EvaluationRequest):
        try:
            judgment_text = result.judgment or result.reasoning or ""
            metrics = {}
            if result.score_a is not None:
                metrics["score_a"] = result.score_a
            if result.score_b is not None:
                metrics["score_b"] = result.score_b
            if result.scores:
                metrics.update(result.scores)
            metrics_json = None
            if metrics:
                import json
                metrics_json = json.dumps(metrics)
            trace_json = None
            if result.trace:
                import json
                trace_json = json.dumps(result.trace)
            self.judgments_repo.save(
                question=request.question,
                response_a=request.response_a or "",
                response_b=request.response_b or "",
                model_a=request.options.get("model_a", ""),
                model_b=request.options.get("model_b", ""),
                judge_model=request.judge_model,
                judgment=judgment_text,
                judgment_type=result.evaluation_type,
                evaluation_id=result.evaluation_id or request.evaluation_id,
                metrics_json=metrics_json,
                trace_json=trace_json,
            )
        except Exception as e:
            print(f"[WARNING] Failed to save judgment to database: {str(e)}", flush=True)

    def _result_to_dict(self, result: EvaluationResult) -> Dict[str, Any]:
        return {
            "success": result.success,
            "judgment": result.judgment,
            "winner": result.winner,
            "score_a": result.score_a,
            "score_b": result.score_b,
            "scores": result.scores,
            "reasoning": result.reasoning,
            "trace": result.trace,
            "execution_time": result.execution_time,
            "error": result.error,
            "evaluation_id": result.evaluation_id,
        }


