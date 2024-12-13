from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    status: str
    message: str


@router.get("/check", response_model=HealthResponse, operation_id="check")
async def health_check():
    """Health check endpoint that returns the status of the service"""
    return {"status": "healthy", "message": "Service is running"}
