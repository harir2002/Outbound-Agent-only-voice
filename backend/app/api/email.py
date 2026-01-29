"""
Email API Endpoints
Send email notifications
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.services.email_service import email_service
from app.core.logging import logger

router = APIRouter()

class SendEmailRequest(BaseModel):
    """Send email request"""
    to_email: EmailStr
    subject: str
    body: str

@router.post("/send")
async def send_email(request: SendEmailRequest):
    """
    Send an email
    
    Args:
        request: Email details
    
    Returns:
        Success message
    """
    try:
        success = await email_service.send_email(
            to_email=request.to_email,
            subject=request.subject,
            body=request.body
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send email")
            
        return {"success": True, "message": "Email sent successfully"}
        
    except Exception as e:
        logger.error(f"❌ Failed to send email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
