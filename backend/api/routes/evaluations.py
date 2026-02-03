"""Evaluation API routes"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from backend.api.models import (
    ComprehensiveEvaluationRequest,
    CodeEvaluationRequest,
    RouterEvaluationRequest,
    SkillsEvaluationRequest,
    TrajectoryEvaluationRequest,
    PairwiseComparisonRequest
)
from backend.api.middleware.auth import verify_api_key
from backend.api.dependencies import evaluation_service
from backend.api.utils import trigger_webhook
from backend.services.data_service import (
    get_all_judgments,
    get_router_evaluations,
    get_skills_evaluations,
    get_trajectory_evaluations,
    get_all_evaluation_data
)
from backend.services.analytics_service import calculate_aggregate_statistics

router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])


@router.post("/comprehensive")
async def evaluate_comprehensive_api(
    request: ComprehensiveEvaluationRequest,
    api_key: str = Depends(verify_api_key)
):
    """Evaluate a response using comprehensive metrics."""
    try:
        result = evaluation_service.evaluate(
            evaluation_type="comprehensive",
            question=request.question,
            judge_model=request.judge_model,
            response=request.response,
            options={
                "task_type": request.task_type,
                "reference": request.reference,
                "include_additional_properties": request.include_additional_properties,
            },
            save_to_db=request.save_to_db
        )
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Evaluation failed"))
        # Trigger webhook
        await trigger_webhook("evaluation.completed", {
            "type": "comprehensive",
            "evaluation_id": result.get("evaluation_id"),
        })
        return {
            "success": True,
            "evaluation_id": result.get("evaluation_id"),
            "metrics": result.get("scores", {}) or {},
            "overall_score": (result.get("scores", {}) or {}).get("overall_score", 0),
            "judgment_text": result.get("judgment", "")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code")
async def evaluate_code_api(
    request: CodeEvaluationRequest,
    api_key: str = Depends(verify_api_key)
):
    """Evaluate Python code."""
    try:
        result = evaluation_service.evaluate(
            evaluation_type="code",
            question="Code Evaluation",
            judge_model=request.judge_model,
            options={
                "code": request.code,
                "language": "python",
                "test_inputs": [request.test_input] if request.test_input else None,
                "expected_output": request.expected_output,
            },
            save_to_db=request.save_to_db
        )
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Evaluation failed"))
        return {
            "success": True,
            "evaluation_id": result.get("evaluation_id"),
            "results": result.get("scores", {}) or {},
            "overall_score": (result.get("scores", {}) or {}).get("overall_score", 0),
            "judgment_text": result.get("judgment", "")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/router")
async def evaluate_router_api(
    request: RouterEvaluationRequest,
    api_key: str = Depends(verify_api_key)
):
    """Evaluate router/tool selection decision."""
    try:
        result = evaluation_service.evaluate(
            evaluation_type="router",
            question=request.query,
            judge_model=request.judge_model,
            options={
                "available_tools": request.available_tools,
                "selected_tool": request.selected_tool,
                "context": request.context,
                "expected_tool": request.expected_tool,
                "routing_strategy": request.routing_strategy,
            },
            save_to_db=request.save_to_db
        )
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Evaluation failed"))
        return {
            "success": True,
            "evaluation_id": result.get("evaluation_id"),
            "tool_accuracy_score": (result.get("scores", {}) or {}).get("tool_accuracy_score", 0),
            "routing_quality_score": (result.get("scores", {}) or {}).get("routing_quality_score", 0),
            "reasoning_score": (result.get("scores", {}) or {}).get("reasoning_score", 0),
            "overall_score": (result.get("scores", {}) or {}).get("overall_score", 0),
            "judgment_text": result.get("judgment", "")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/skills")
async def evaluate_skills_api(
    request: SkillsEvaluationRequest,
    api_key: str = Depends(verify_api_key)
):
    """Evaluate domain-specific skills."""
    try:
        result = evaluation_service.evaluate(
            evaluation_type="skills",
            question=request.question,
            judge_model=request.judge_model,
            response=request.response,
            options={
                "skill_type": request.skill_type,
                "reference_answer": request.reference_answer,
                "domain": request.domain,
            },
            save_to_db=request.save_to_db
        )
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Evaluation failed"))
        return {
            "success": True,
            "evaluation_id": result.get("evaluation_id"),
            "correctness_score": (result.get("scores", {}) or {}).get("correctness_score", 0),
            "completeness_score": (result.get("scores", {}) or {}).get("completeness_score", 0),
            "clarity_score": (result.get("scores", {}) or {}).get("clarity_score", 0),
            "proficiency_score": (result.get("scores", {}) or {}).get("proficiency_score", 0),
            "overall_score": (result.get("scores", {}) or {}).get("overall_score", 0),
            "judgment_text": result.get("judgment", "")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trajectory")
async def evaluate_trajectory_api(
    request: TrajectoryEvaluationRequest,
    api_key: str = Depends(verify_api_key)
):
    """Evaluate multi-step trajectory/action sequence."""
    try:
        result = evaluation_service.evaluate(
            evaluation_type="trajectory",
            question=request.task_description,
            judge_model=request.judge_model,
            options={
                "trajectory": request.trajectory,
                "expected_trajectory": request.expected_trajectory,
                "trajectory_type": request.trajectory_type,
            },
            save_to_db=request.save_to_db
        )
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Evaluation failed"))
        return {
            "success": True,
            "evaluation_id": result.get("evaluation_id"),
            "step_quality_score": (result.get("scores", {}) or {}).get("step_quality_score", 0),
            "path_efficiency_score": (result.get("scores", {}) or {}).get("path_efficiency_score", 0),
            "reasoning_chain_score": (result.get("scores", {}) or {}).get("reasoning_chain_score", 0),
            "planning_quality_score": (result.get("scores", {}) or {}).get("planning_quality_score", 0),
            "overall_score": (result.get("scores", {}) or {}).get("overall_score", 0),
            "judgment_text": result.get("judgment", "")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pairwise")
async def evaluate_pairwise_api(
    request: PairwiseComparisonRequest,
    api_key: str = Depends(verify_api_key)
):
    """Compare two responses pairwise."""
    try:
        result = evaluation_service.evaluate(
            evaluation_type="pairwise",
            question=request.question,
            judge_model=request.judge_model,
            response_a=request.response_a,
            response_b=request.response_b,
            options={"randomize_order": True},
            save_to_db=request.save_to_db
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Evaluation failed"))
        
        # Trigger webhook
        await trigger_webhook("evaluation.completed", {
            "type": "pairwise",
            "winner": result.get("winner", "unknown"),
            "evaluation_id": result.get("evaluation_id")
        })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def get_evaluations(
    evaluation_type: Optional[str] = None,
    limit: int = 50,
    api_key: str = Depends(verify_api_key)
):
    """Get evaluations from database."""
    try:
        if evaluation_type == "comprehensive":
            judgments = get_all_judgments(limit=limit)
            return [j for j in judgments if j.get("judgment_type") in ["comprehensive", "batch_comprehensive"]]
        elif evaluation_type == "router":
            return get_router_evaluations(limit=limit)
        elif evaluation_type == "skills":
            return get_skills_evaluations(limit=limit)
        elif evaluation_type == "trajectory":
            return get_trajectory_evaluations(limit=limit)
        else:
            return get_all_judgments(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

