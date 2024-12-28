import os
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    message: str
    version: str
    dockerfile_hash: str
    build_timestamp: str


@router.get("/check", response_model=HealthResponse, operation_id="check")
async def health_check():
    """Health check endpoint that returns the status of the service and version"""
    return {"status": "healthy", "message": "Service is running", "version": os.environ.get("GIT_HASH", "unknown"), "dockerfile_hash": os.environ.get("DOCKERFILE_HASH", "unknown"), "build_timestamp": os.environ.get("BUILD_TIMESTAMP", "unknown")}  # We'll add this to manifest
