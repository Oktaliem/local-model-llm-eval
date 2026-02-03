"""Custom Metrics API routes"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from backend.api.models import CreateCustomMetricRequest, EvaluateWithCustomMetricRequest
from backend.api.middleware.auth import verify_api_key
from backend.services.custom_metric_service import (
    create_custom_metric,
    get_custom_metric,
    get_all_custom_metrics,
    delete_custom_metric,
    evaluate_with_custom_metric
)

router = APIRouter(prefix="/api/v1/custom-metrics", tags=["custom-metrics"])


@router.post("")
async def create_custom_metric_api(request: CreateCustomMetricRequest, api_key: str = Depends(verify_api_key)):
    """Create a new custom metric."""
    try:
        metric_id = create_custom_metric(
            metric_name=request.metric_name,
            evaluation_type=request.evaluation_type,
            metric_definition=request.metric_definition,
            metric_description=request.metric_description,
            domain=request.domain,
            scoring_function=request.scoring_function,
            criteria_json=request.criteria_json,
            weight=request.weight,
            scale_min=request.scale_min,
            scale_max=request.scale_max,
            created_by="api_user"
        )
        return {
            "success": True,
            "metric_id": metric_id,
            "message": "Custom metric created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_custom_metrics_api(
    evaluation_type: Optional[str] = None,
    domain: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 100,
    api_key: str = Depends(verify_api_key)
):
    """List all custom metrics."""
    try:
        metrics = get_all_custom_metrics(
            evaluation_type=evaluation_type,
            domain=domain,
            is_active=is_active,
            limit=limit
        )
        return {
            "total": len(metrics),
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{metric_id}")
async def get_custom_metric_api(
    metric_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get a specific custom metric by ID."""
    try:
        metric = get_custom_metric(metric_id)
        if not metric:
            raise HTTPException(status_code=404, detail="Metric not found")
        return metric
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{metric_id}")
async def delete_custom_metric_api(
    metric_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Deactivate a custom metric (soft delete)."""
    try:
        success = delete_custom_metric(metric_id)
        if not success:
            raise HTTPException(status_code=404, detail="Metric not found")
        return {"success": True, "message": "Metric deactivated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{metric_id}/evaluate")
async def evaluate_with_metric_api(
    metric_id: str,
    request: EvaluateWithCustomMetricRequest,
    api_key: str = Depends(verify_api_key)
):
    """Evaluate a response using a custom metric."""
    try:
        if metric_id != request.metric_id:
            raise HTTPException(status_code=400, detail="Metric ID mismatch")
        
        result = evaluate_with_custom_metric(
            metric_id=metric_id,
            question=request.question,
            response=request.response,
            reference=request.reference,
            judge_model=request.judge_model
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Evaluation failed"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

