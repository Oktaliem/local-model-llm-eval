"""CORS middleware configuration"""
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

# Allowed origins (can be configured via environment variable)
ALLOWED_ORIGINS = [
    "http://localhost:8501",
    "http://localhost:8000",
    "http://127.0.0.1:8501",
    "http://127.0.0.1:8000",
]


def setup_cors(app: FastAPI):
    """Setup CORS middleware for FastAPI app."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

