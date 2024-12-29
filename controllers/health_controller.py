import os
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    message: str


@router.get("/check", response_model=HealthResponse, operation_id="check", status_code=200)
async def health_check():
    """Health check endpoint that returns the status of the service and a message"""
    return {"status": "healthy", "message": "Service is running"}


@router.get("/check2", response_model=HealthResponse, operation_id="check2", status_code=200)
async def health_check2():
    """Health check endpoint that returns the status of the service and a message"""
    return {"status": "healthy", "message": "Service is running"}


@router.get("/check3", response_model=HealthResponse, operation_id="check3", status_code=200)
async def health_check3():
    """Third health check endpoint to verify deployment process"""
    return {"status": "healthy", "message": "Deployment verification endpoint!!"}
