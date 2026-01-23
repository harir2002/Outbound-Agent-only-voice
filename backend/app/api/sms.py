"""
SMS API Endpoints
Direct SMS messaging using Twilio
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.twilio_service import twilio_whatsapp_service
from app.core.logging import logger

router = APIRouter()


class SendSMSRequest(BaseModel):
    """Send SMS message request"""
    to_number: str
    message: str


@router.post("/send")
async def send_sms_message(request: SendSMSRequest):
    """
    Send SMS message programmatically
    
    Args:
        request: Send SMS request with to_number and message
    
    Returns:
        Message details
    """
    try:
        # We reuse the twilio_whatsapp_service which now has send_sms
        result = await twilio_whatsapp_service.send_sms(
            to_number=request.to_number,
            message=request.message
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send SMS: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
