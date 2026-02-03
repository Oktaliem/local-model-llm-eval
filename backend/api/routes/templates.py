"""Evaluation Templates API routes"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from backend.api.models import CreateTemplateRequest, ApplyTemplateRequest
from backend.api.middleware.auth import verify_api_key
from backend.services.template_service import (
    create_evaluation_template,
    get_evaluation_template,
    get_all_evaluation_templates,
    delete_evaluation_template,
    apply_template_to_evaluation
)

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])


@router.post("")
async def create_template_api(request: CreateTemplateRequest, api_key: str = Depends(verify_api_key)):
    """Create a new evaluation template."""
    try:
        template_id = create_evaluation_template(
            template_name=request.template_name,
            evaluation_type=request.evaluation_type,
            template_config=request.template_config,
            template_description=request.template_description,
            industry=request.industry,
            created_by="api_user"
        )
        return {
            "success": True,
            "template_id": template_id,
            "message": "Template created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_templates_api(
    evaluation_type: Optional[str] = None,
    industry: Optional[str] = None,
    include_predefined: bool = True,
    limit: int = 100,
    api_key: str = Depends(verify_api_key)
):
    """List all evaluation templates."""
    try:
        templates = get_all_evaluation_templates(
            evaluation_type=evaluation_type,
            industry=industry,
            include_predefined=include_predefined,
            limit=limit
        )
        return {
            "total": len(templates),
            "templates": templates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{template_id}")
async def get_template_api(
    template_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get a specific template by ID."""
    try:
        template = get_evaluation_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{template_id}")
async def delete_template_api(
    template_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Delete an evaluation template (only custom templates)."""
    try:
        success = delete_evaluation_template(template_id)
        if not success:
            raise HTTPException(status_code=400, detail="Cannot delete predefined template or template not found")
        return {"success": True, "message": "Template deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{template_id}/apply")
async def apply_template_api(
    template_id: str,
    request: ApplyTemplateRequest,
    api_key: str = Depends(verify_api_key)
):
    """Apply a template to evaluation data."""
    try:
        if template_id != request.template_id:
            raise HTTPException(status_code=400, detail="Template ID mismatch")
        
        modified_data = apply_template_to_evaluation(template_id, request.evaluation_data)
        return {
            "success": True,
            "template_id": template_id,
            "modified_data": modified_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

