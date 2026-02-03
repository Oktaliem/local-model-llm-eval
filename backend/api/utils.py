"""Utility functions for API routes"""
import os
import json
import hashlib
import hmac
from datetime import datetime
from typing import Dict, Any
import httpx


WEBHOOKS_FILE = os.getenv("WEBHOOKS_FILE", "data/webhooks.json")


def load_webhooks() -> Dict[str, Dict[str, Any]]:
    """Load webhooks from file."""
    if os.path.exists(WEBHOOKS_FILE):
        try:
            with open(WEBHOOKS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_webhooks(webhooks: Dict[str, Dict[str, Any]]):
    """Save webhooks to file."""
    os.makedirs(os.path.dirname(WEBHOOKS_FILE), exist_ok=True)
    with open(WEBHOOKS_FILE, 'w') as f:
        json.dump(webhooks, f, indent=2)


async def trigger_webhook(event: str, data: Dict[str, Any]):
    """Trigger webhook for an event."""
    webhooks = load_webhooks()
    
    for webhook_id, webhook_info in webhooks.items():
        if event in webhook_info.get("events", []):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    payload = {
                        "event": event,
                        "timestamp": datetime.now().isoformat(),
                        "data": data
                    }
                    # Add signature if secret is set
                    if webhook_info.get("secret"):
                        signature = hmac.new(
                            webhook_info["secret"].encode(),
                            json.dumps(payload).encode(),
                            hashlib.sha256
                        ).hexdigest()
                        headers = {"X-Webhook-Signature": signature}
                    else:
                        headers = {}
                    
                    await client.post(webhook_info["url"], json=payload, headers=headers)
            except Exception as e:
                print(f"Failed to trigger webhook {webhook_id}: {e}")

