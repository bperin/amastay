from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from auth_utils import get_current_user
from services.model_params_service import get_active_model_param
from services.process_service import handle_incoming_sms
import logging
import uuid
from uuid import UUID

# Create router
router = APIRouter(tags=["model"])


class SMSInput(BaseModel):
    message: str
    phone: str
    send_message: bool


class ModelResponse(BaseModel):
    response: str


@router.post("/query", response_model=ModelResponse, operation_id="query")
async def query_model(data: SMSInput, current_user: dict = Depends(get_current_user)):
    """Query the model with SMS input"""
    try:
        message_id = str(uuid.uuid4())
        response = handle_incoming_sms(message_id=message_id, origination_number=data.phone, message_body=data.message, send_message=data.send_message, current_user_id=current_user["id"])
        return {"response": response}
    except Exception as e:
        logging.error(f"Error in query_model for phone {data.phone}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/current", operation_id="current")
async def get_model_params(current_user: dict = Depends(get_current_user)):
    """Get current model parameters"""
    try:
        model_params = get_active_model_param()
        return model_params
    except Exception as e:
        logging.error(f"Error fetching model parameters: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching model parameters")
