"""
WhatsApp API Endpoints
Twilio webhook handling and WhatsApp messaging
"""

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional

from app.services.twilio_service import twilio_whatsapp_service
from app.services.groq_service import groq_service
from app.core.logging import logger
from app.core.security import ConsentManager

router = APIRouter()


# ==================== REQUEST MODELS ====================

class SendMessageRequest(BaseModel):
    """Send WhatsApp message request"""
    to_number: str
    message: str
    media_url: Optional[str] = None


# ==================== ENDPOINTS ====================

@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...),
    ProfileName: Optional[str] = Form(None)
):
    """
    Twilio WhatsApp webhook endpoint
    Receives incoming WhatsApp messages
    
    Args:
        From: Sender phone number (whatsapp:+1234567890)
        Body: Message text
        MessageSid: Twilio message SID
        ProfileName: Sender's WhatsApp profile name
    
    Returns:
        TwiML response
    """
    try:
        logger.info(f"📥 WhatsApp webhook: {From} - {Body[:50]}...")
        
        # Process incoming message
        session = await twilio_whatsapp_service.process_incoming_message(
            from_number=From,
            message_body=Body,
            message_sid=MessageSid
        )
        
        # If it's an opt-in/opt-out response, return it directly
        if isinstance(session, str):
            twiml = twilio_whatsapp_service.create_twiml_response(session)
            return Response(content=twiml, media_type="application/xml")
        
        # Extract user ID and sector from session
        user_id = session["user_id"]
        sector = session.get("context", {}).get("sector", "banking")
        
        # Check consent
        if not ConsentManager.check_consent(user_id, "whatsapp"):
            response_text = "Please reply START to opt-in to receive messages."
            twiml = twilio_whatsapp_service.create_twiml_response(response_text)
            return Response(content=twiml, media_type="application/xml")
        
        # Classify intent
        intent_result = await groq_service.classify_intent(Body, sector)
        logger.info(f"Intent: {intent_result.get('intent')} (confidence: {intent_result.get('confidence')})")
        
        # Check if human escalation needed
        if intent_result.get("requires_human", False):
            response_text = "I'll connect you with a human agent. Please wait..."
            twiml = twilio_whatsapp_service.create_twiml_response(response_text)
            return Response(content=twiml, media_type="application/xml")
        
        # Get RAG context
        # Generate response (without RAG context)
        response_text = await groq_service.generate_bfsi_response(
            user_query=Body,
            context="",  # No RAG context
            sector=sector,
            language="en"  # TODO: Detect language
        )
        
        # Update session
        session["messages"].append({
            "role": "assistant",
            "content": response_text
        })
        
        # Create TwiML response
        twiml = twilio_whatsapp_service.create_twiml_response(response_text)
        
        logger.info(f"📤 WhatsApp response sent to {From}")
        
        return Response(content=twiml, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"❌ WhatsApp webhook error: {str(e)}")
        error_response = "Sorry, I encountered an error. Please try again later."
        twiml = twilio_whatsapp_service.create_twiml_response(error_response)
        return Response(content=twiml, media_type="application/xml")


@router.post("/send")
async def send_whatsapp_message(request: SendMessageRequest):
    """
    Send WhatsApp message programmatically
    
    Args:
        request: Send message request with to_number, message, and optional media_url
    
    Returns:
        Message details
    """
    try:
        result = await twilio_whatsapp_service.send_message(
            to_number=request.to_number,
            message=request.message,
            media_url=request.media_url
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-payment-link")
async def send_payment_link(
    to_number: str,
    amount: float,
    description: str,
    payment_url: str
):
    """
    Send payment link via WhatsApp
    
    Args:
        to_number: Recipient phone number
        amount: Payment amount
        description: Payment description
        payment_url: Payment link URL
    
    Returns:
        Message details
    """
    try:
        result = await twilio_whatsapp_service.send_sms(
            to_number=to_number,
            message=f"Payment Request: {description}. Amount: {amount}. Link: {payment_url}"
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send payment link: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-policy-details")
async def send_policy_details(
    to_number: str,
    policy_data: dict
):
    """
    Send insurance policy details
    
    Args:
        to_number: Recipient phone number
        policy_data: Policy information
    
    Returns:
        Message details
    """
    try:
        # Construct basic specific message for SMS
        msg = f"Policy Details for {policy_data.get('policy_number')}. Status: {policy_data.get('status')}. Premium: {policy_data.get('premium')}"
        result = await twilio_whatsapp_service.send_sms(
            to_number=to_number,
            message=msg
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send policy details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-loan-summary")
async def send_loan_summary(
    to_number: str,
    loan_data: dict
):
    """
    Send loan summary
    
    Args:
        to_number: Recipient phone number
        loan_data: Loan information
    
    Returns:
        Message details
    """
    try:
        msg = f"Loan Summary for {loan_data.get('account_number')}. Outstanding: {loan_data.get('outstanding')}. Please pay EMI: {loan_data.get('emi')}"
        result = await twilio_whatsapp_service.send_sms(
            to_number=to_number,
            message=msg
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send loan summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/opt-in")
async def record_opt_in(phone_number: str):
    """
    Record WhatsApp opt-in consent
    
    Args:
        phone_number: User phone number
    
    Returns:
        Success status
    """
    try:
        ConsentManager.record_consent(
            user_id=phone_number,
            consent_type="whatsapp",
            granted=True
        )
        
        return {
            "success": True,
            "message": "Opt-in recorded successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to record opt-in: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/opt-out")
async def record_opt_out(phone_number: str):
    """
    Record WhatsApp opt-out
    
    Args:
        phone_number: User phone number
    
    Returns:
        Success status
    """
    try:
        ConsentManager.record_consent(
            user_id=phone_number,
            consent_type="whatsapp",
            granted=False
        )
        
        return {
            "success": True,
            "message": "Opt-out recorded successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to record opt-out: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
