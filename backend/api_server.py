"""
REST API Server for LLM & AI Agent Evaluation Framework

This API provides programmatic access to all evaluation features.
Run with: uvicorn backend.api_server:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI
from backend.api.middleware.cors import setup_cors
from datetime import datetime
import os

# Import routers
from backend.api.routes import evaluations, keys, ab_tests, templates, custom_metrics, webhooks, analytics
from backend.api.middleware.rate_limit import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW

# Initialize FastAPI app
app = FastAPI(
    title="LLM & AI Agent Evaluation Framework API",
    description="REST API for programmatic access to evaluation features",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup CORS middleware
setup_cors(app)

# Include routers
app.include_router(evaluations.router)
app.include_router(analytics.router)
app.include_router(keys.router)
app.include_router(ab_tests.router)
app.include_router(templates.router)
app.include_router(custom_metrics.router)
app.include_router(webhooks.router)

# Root endpoint (no auth required)
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "LLM & AI Agent Evaluation Framework API",
        "version": "1.0.0",
        "description": "REST API for programmatic access to evaluation features",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "endpoints": {
            "health": "/health",
            "api_base": "/api/v1/",
            "evaluations": "/api/v1/evaluations",
            "analytics": "/api/v1/analytics/overview",
            "ab_tests": "/api/v1/ab-tests",
            "templates": "/api/v1/templates",
            "custom_metrics": "/api/v1/custom-metrics",
            "webhooks": "/api/v1/webhooks",
            "api_keys": "/api/v1/keys"
        },
        "authentication": {
            "type": "Bearer Token (API Key)",
            "header": "Authorization: Bearer <your_api_key>",
            "create_key": "POST /api/v1/keys"
        },
        "rate_limiting": {
            "requests_per_window": RATE_LIMIT_REQUESTS,
            "window_seconds": RATE_LIMIT_WINDOW
        }
    }

# Base API endpoint (no auth required)
@app.get("/api/v1/")
async def api_base():
    """Base API endpoint with version information and available resources."""
    return {
        "api_version": "v1",
        "name": "LLM & AI Agent Evaluation Framework API",
        "version": "1.0.0",
        "resources": {
            "evaluations": {
                "description": "Run various types of evaluations",
                "endpoints": {
                    "comprehensive": "POST /api/v1/evaluations/comprehensive",
                    "code": "POST /api/v1/evaluations/code",
                    "router": "POST /api/v1/evaluations/router",
                    "skills": "POST /api/v1/evaluations/skills",
                    "trajectory": "POST /api/v1/evaluations/trajectory",
                    "pairwise": "POST /api/v1/evaluations/pairwise",
                    "list": "GET /api/v1/evaluations"
                }
            },
            "analytics": {
                "description": "Get analytics and insights",
                "endpoints": {
                    "overview": "GET /api/v1/analytics/overview"
                }
            },
            "ab_tests": {
                "description": "A/B testing framework",
                "endpoints": {
                    "create": "POST /api/v1/ab-tests",
                    "list": "GET /api/v1/ab-tests",
                    "get": "GET /api/v1/ab-tests/{test_id}",
                    "run": "POST /api/v1/ab-tests/{test_id}/run"
                }
            },
            "templates": {
                "description": "Evaluation templates management",
                "endpoints": {
                    "create": "POST /api/v1/templates",
                    "list": "GET /api/v1/templates",
                    "get": "GET /api/v1/templates/{template_id}",
                    "delete": "DELETE /api/v1/templates/{template_id}",
                    "apply": "POST /api/v1/templates/{template_id}/apply"
                }
            },
            "custom_metrics": {
                "description": "Custom metrics management",
                "endpoints": {
                    "create": "POST /api/v1/custom-metrics",
                    "list": "GET /api/v1/custom-metrics",
                    "get": "GET /api/v1/custom-metrics/{metric_id}",
                    "delete": "DELETE /api/v1/custom-metrics/{metric_id}",
                    "evaluate": "POST /api/v1/custom-metrics/{metric_id}/evaluate"
                }
            },
            "webhooks": {
                "description": "Webhook management",
                "endpoints": {
                    "create": "POST /api/v1/webhooks",
                    "list": "GET /api/v1/webhooks",
                    "get": "GET /api/v1/webhooks/{webhook_id}",
                    "delete": "DELETE /api/v1/webhooks/{webhook_id}"
                }
            },
            "api_keys": {
                "description": "API key management",
                "endpoints": {
                    "create": "POST /api/v1/keys",
                    "list": "GET /api/v1/keys"
                }
            }
        },
        "links": {
            "documentation": "/docs",
            "health": "/health",
            "root": "/"
        }
    }

# Health check endpoint (no auth required)
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

