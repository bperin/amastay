import subprocess
import os
from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    message: str
    version: str


@router.get("/check", response_model=HealthResponse, operation_id="check")
async def health_check():
    """Health check endpoint that returns the status of the service and version"""
    try:
        # Get the git hash of the current commit
        git_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode("ascii").strip()
    except:
        git_hash = "unknown"

    return {"status": "healthy", "message": "Service is running", "version": git_hash, "task_id": os.environ.get("ECS_TASK_ID", "unknown"), "container_id": os.environ.get("ECS_CONTAINER_ID", "unknown")}
