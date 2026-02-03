"""A/B Testing API routes"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from backend.api.models import CreateABTestRequest, RunABTestRequest
from backend.api.middleware.auth import verify_api_key
from backend.api.utils import trigger_webhook
from backend.services.ab_test_service import create_ab_test, get_ab_test, get_all_ab_tests, execute_ab_test

router = APIRouter(prefix="/api/v1/ab-tests", tags=["ab-tests"])


@router.post("")
async def create_ab_test_api(request: CreateABTestRequest, api_key: str = Depends(verify_api_key)):
    """Create a new A/B test."""
    try:
        test_id = create_ab_test(
            test_name=request.test_name,
            variant_a_name=request.variant_a_name,
            variant_b_name=request.variant_b_name,
            variant_a_config=request.variant_a_config,
            variant_b_config=request.variant_b_config,
            evaluation_type=request.evaluation_type,
            test_cases=request.test_cases,
            test_description=request.test_description
        )
        return {
            "success": True,
            "test_id": test_id,
            "message": "A/B test created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_ab_tests(
    limit: int = 50,
    api_key: str = Depends(verify_api_key)
):
    """List all A/B tests."""
    try:
        tests = get_all_ab_tests(limit=limit)
        return {
            "total": len(tests),
            "tests": tests
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{test_id}")
async def get_ab_test_api(
    test_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get a specific A/B test by ID."""
    try:
        test = get_ab_test(test_id)
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        return test
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{test_id}/run")
async def run_ab_test_api(
    test_id: str,
    request: RunABTestRequest,
    api_key: str = Depends(verify_api_key)
):
    """Run an A/B test."""
    try:
        if test_id != request.test_id:
            raise HTTPException(status_code=400, detail="Test ID mismatch")
        
        result = execute_ab_test(
            test_id=test_id,
            judge_model=request.judge_model
        )
        
        if result.get("success"):
            await trigger_webhook("ab_test.completed", {
                "test_id": test_id,
                "total_cases": result.get("summary", {}).get("total_cases", 0),
                "variant_a_wins": result.get("summary", {}).get("variant_a_wins", 0),
                "variant_b_wins": result.get("summary", {}).get("variant_b_wins", 0)
            })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

