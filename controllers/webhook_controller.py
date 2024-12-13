from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.process_service import handle_incoming_sms
import logging

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class SMSWebhook(BaseModel):
    phone: str
    message: str
    message_id: str


@router.post("/sms", operation_id="sms")
async def sms_webhook(data: SMSWebhook):
    """Receives and processes incoming SMS webhooks"""
    try:
        handle_incoming_sms(data.message_id, data.phone, data.message, True)
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
