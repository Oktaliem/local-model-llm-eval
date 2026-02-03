"""Rate limiting middleware"""
import os
import time
from typing import Dict
from collections import defaultdict
from fastapi import HTTPException, status

# Configuration
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour

# Rate limiting store
rate_limit_store = defaultdict(list)


def check_rate_limit(api_key: str) -> bool:
    """Check if API key has exceeded rate limit."""
    now = time.time()
    key_requests = rate_limit_store[api_key]
    
    # Remove old requests outside the window
    key_requests[:] = [req_time for req_time in key_requests if now - req_time < RATE_LIMIT_WINDOW]
    
    if len(key_requests) >= RATE_LIMIT_REQUESTS:
        return False
    
    key_requests.append(now)
    return True


def enforce_rate_limit(api_key: str):
    """Enforce rate limit, raising exception if exceeded."""
    if not check_rate_limit(api_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds."
        )

