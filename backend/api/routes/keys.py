"""API key management routes"""
from fastapi import APIRouter, Depends
from datetime import datetime
import secrets
from typing import Optional
from backend.api.models import APIKeyResponse
from backend.api.middleware.auth import verify_api_key, load_api_keys, save_api_keys

router = APIRouter(prefix="/api/v1/keys", tags=["keys"])


@router.post("", response_model=APIKeyResponse)
async def create_api_key(description: Optional[str] = None):
    """Create a new API key."""
    api_key = secrets.token_urlsafe(32)
    keys = load_api_keys()
    keys[api_key] = {
        "created_at": datetime.now().isoformat(),
        "description": description,
        "requests_count": 0
    }
    save_api_keys(keys)
    return APIKeyResponse(
        api_key=api_key,
        created_at=keys[api_key]["created_at"],
        description=description
    )


@router.get("")
async def list_api_keys(api_key: str = Depends(verify_api_key)):
    """List all API keys (admin function)."""
    keys = load_api_keys()
    # Return keys without exposing full keys
    return {
        "total_keys": len(keys),
        "keys": [
            {
                "key_prefix": key[:8] + "...",
                "created_at": info["created_at"],
                "description": info.get("description"),
                "requests_count": info.get("requests_count", 0)
            }
            for key, info in keys.items()
        ]
    }

