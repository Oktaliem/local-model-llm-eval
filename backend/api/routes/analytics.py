"""Analytics API routes"""
from fastapi import APIRouter, HTTPException, Depends
from backend.api.middleware.auth import verify_api_key
from backend.services.data_service import get_all_evaluation_data
from backend.services.analytics_service import calculate_aggregate_statistics

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/overview")
async def get_analytics_overview(
    api_key: str = Depends(verify_api_key)
):
    """Get analytics overview."""
    try:
        data = get_all_evaluation_data(limit=5000)
        stats = calculate_aggregate_statistics(data)
        return {
            "overview": {
                "total_evaluations": (
                    len(data["judgments"]) + 
                    len(data["router_evaluations"]) + 
                    len(data["skills_evaluations"]) + 
                    len(data["trajectory_evaluations"])
                ),
                "comprehensive_evaluations": len(data["comprehensive"]),
                "code_evaluations": len(data["code_evaluations"]),
                "router_evaluations": len(data["router_evaluations"]),
                "skills_evaluations": len(data["skills_evaluations"]),
                "trajectory_evaluations": len(data["trajectory_evaluations"]),
                "human_annotations": len(data["human_annotations"])
            },
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

