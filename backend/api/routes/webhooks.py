"""Webhook management API routes"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import secrets
from backend.api.models import WebhookRequest, WebhookResponse
from backend.api.middleware.auth import verify_api_key
from backend.api.utils import load_webhooks, save_webhooks

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


@router.post("", response_model=WebhookResponse)
async def create_webhook(
    request: WebhookRequest,
    api_key: str = Depends(verify_api_key)
):
    """Create a new webhook."""
    webhook_id = secrets.token_urlsafe(16)
    webhooks = load_webhooks()
    webhooks[webhook_id] = {
        "url": request.url,
        "events": request.events,
        "secret": request.secret,
        "created_at": datetime.now().isoformat()
    }
    save_webhooks(webhooks)
    return WebhookResponse(
        webhook_id=webhook_id,
        url=request.url,
        events=request.events,
        created_at=webhooks[webhook_id]["created_at"]
    )


@router.get("")
async def list_webhooks(api_key: str = Depends(verify_api_key)):
    """List all webhooks."""
    webhooks = load_webhooks()
    return {
        "total_webhooks": len(webhooks),
        "webhooks": [
            {
                "webhook_id": webhook_id,
                "url": info["url"],
                "events": info["events"],
                "created_at": info["created_at"]
            }
            for webhook_id, info in webhooks.items()
        ]
    }


@router.delete("/{webhook_id}")
async def delete_webhook(webhook_id: str, api_key: str = Depends(verify_api_key)):
    """Delete a webhook."""
    webhooks = load_webhooks()
    if webhook_id not in webhooks:
        raise HTTPException(status_code=404, detail="Webhook not found")
    del webhooks[webhook_id]
    save_webhooks(webhooks)
    return {"success": True, "message": "Webhook deleted"}

