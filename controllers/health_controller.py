import subprocess
import os
from fastapi import APIRouter
from pydantic import BaseModel
import asyncio


router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    message: str
    version: str


@router.get("/check", response_model=HealthResponse, operation_id="check")
async def health_check():
    """Health check endpoint that returns the status of the service and version"""
    try:
        # Use asyncio.create_subprocess_exec instead of subprocess.check_output
        process = await asyncio.create_subprocess_exec("git", "rev-parse", "--short", "HEAD", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        git_hash = stdout.decode().strip() if process.returncode == 0 else "unknown"
    except Exception:
        git_hash = "unknown"

    return {"status": "healthy", "message": "Service is running", "version": git_hash}
