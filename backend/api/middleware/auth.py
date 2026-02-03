"""Authentication middleware"""
import os
import json
from typing import Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.api.middleware.rate_limit import enforce_rate_limit

# Configuration
API_KEYS_FILE = os.getenv("API_KEYS_FILE", "data/api_keys.json")

# Security
security = HTTPBearer()


def load_api_keys() -> Dict[str, Dict[str, Any]]:
    """Load API keys from file."""
    if os.path.exists(API_KEYS_FILE):
        try:
            with open(API_KEYS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_api_keys(keys: Dict[str, Dict[str, Any]]):
    """Save API keys to file."""
    os.makedirs(os.path.dirname(API_KEYS_FILE), exist_ok=True)
    with open(API_KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)


def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify API key from Authorization header."""
    api_key = credentials.credentials
    keys = load_api_keys()
    
    if api_key not in keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Enforce rate limiting
    enforce_rate_limit(api_key)
    
    return api_key

