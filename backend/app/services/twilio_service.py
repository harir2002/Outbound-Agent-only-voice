"""
Twilio WhatsApp Service
WhatsApp Business API integration for customer messaging
"""

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from typing import Dict, Any, Optional
from datetime import datetime
import json

from app.core.config import settings
from app.core.logging import logger, audit_log
from app.core.security import ConsentManager, PIIMasker


class TwilioWhatsAppService:
    """Twilio WhatsApp Business API service"""
    
    def __init__(self):
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER
        self.sms_number = settings.TWILIO_PHONE_NUMBER
        
        # Session storage (use Redis in production)
        self.sessions = {}
    
    async def send_sms(
        self,
        to_number: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Send direct SMS message via Twilio
        
        Args:
            to_number: Recipient phone number (with country code)
            message: Message text
        
        Returns:
            Message details
        """
        try:
            logger.info(f"💬 Sending SMS message to {to_number}")
            logger.info(f"   From: {self.sms_number}")
            logger.info(f"   Message preview: {message[:100]}...")
            
            # Send SMS via Twilio
            twilio_message = self.client.messages.create(
                from_=self.sms_number,
                to=to_number,
                body=message
            )
            
            # Audit log
            audit_log(
                event="sms_message_sent",
                user_id=to_number,
                metadata={
                    "message_sid": twilio_message.sid,
                    "status": twilio_message.status,
                    "type": "sms"
                }
            )
            
            logger.info(f"✅ SMS message sent successfully!")
            logger.info(f"   Message SID: {twilio_message.sid}")
            
            return {
                "message_sid": twilio_message.sid,
                "status": twilio_message.status,
                "to": to_number,
                "type": "sms",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to send SMS message: {str(e)}")
            raise
    
    async def send_message(
        self,
        to_number: str,
        message: str,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send WhatsApp message via Twilio
        
        Args:
            to_number: Recipient phone number (with country code)
            message: Message text
            media_url: Optional media URL
        
        Returns:
            Message details
        """
        # Format number
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"
        
        # Check consent
        user_id = to_number.replace("whatsapp:", "")
        if not ConsentManager.check_consent(user_id, "whatsapp"):
            logger.warning(f"No WhatsApp consent for {user_id}")
            ConsentManager.record_consent(user_id, "whatsapp", False)
        
        logger.info(f"📱 Sending WhatsApp message to {user_id}")
        logger.info(f"   From: {self.whatsapp_number}")
        logger.info(f"   Message preview: {message[:100]}...")
        
        # Send message via Twilio
        message_params = {
            "from_": self.whatsapp_number,
            "to": to_number,
            "body": message
        }
        
        if media_url:
            message_params["media_url"] = [media_url]
        
        twilio_message = self.client.messages.create(**message_params)
        
        # Audit log
        audit_log(
            event="whatsapp_message_sent",
            user_id=user_id,
            metadata={
                "message_sid": twilio_message.sid,
                "status": twilio_message.status
            }
        )
        
        logger.info(f"✅ WhatsApp message sent successfully!")
        logger.info(f"   Message SID: {twilio_message.sid}")
        logger.info(f"   Status: {twilio_message.status}")
        logger.info(f"   To: {to_number}")
        
        return {
            "message_sid": twilio_message.sid,
            "status": twilio_message.status,
            "to": to_number,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def process_incoming_message(
        self,
        from_number: str,
        message_body: str,
        message_sid: str
    ) -> str:
        """
        Process incoming WhatsApp message
        
        Args:
            from_number: Sender phone number
            message_body: Message text
            message_sid: Twilio message SID
        
        Returns:
            Response message
        """
        try:
            user_id = from_number.replace("whatsapp:", "")
            
            # Audit log
            audit_log(
                event="whatsapp_message_received",
                user_id=user_id,
                metadata={
                    "message_sid": message_sid,
                    "message_preview": message_body[:100]
                }
            )
            
            # Get or create session
            session = self._get_session(user_id)
            
            # Update session
            session["messages"].append({
                "role": "user",
                "content": message_body,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Check for opt-in keywords
            if self._is_opt_in_message(message_body):
                ConsentManager.record_consent(user_id, "whatsapp", True)
                return "Thank you for opting in! How can I help you today?"
            
            # Check for opt-out keywords
            if self._is_opt_out_message(message_body):
                ConsentManager.record_consent(user_id, "whatsapp", False)
                return "You have been opted out. Reply START to opt back in."
            
            logger.info(f"📥 WhatsApp message from {user_id}: {message_body[:50]}...")
            
            # Return session for further processing
            return session
            
        except Exception as e:
            logger.error(f"❌ Failed to process incoming message: {str(e)}")
            raise
    
    def create_twiml_response(self, message: str) -> str:
        """
        Create TwiML response for webhook
        
        Args:
            message: Response message
        
        Returns:
            TwiML XML string
        """
        response = MessagingResponse()
        response.message(message)
        return str(response)
    
    def _get_session(self, user_id: str) -> Dict[str, Any]:
        """Get or create user session"""
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                "user_id": user_id,
                "messages": [],
                "context": {},
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat()
            }
        else:
            self.sessions[user_id]["last_activity"] = datetime.utcnow().isoformat()
        
        return self.sessions[user_id]
    
    def _is_opt_in_message(self, message: str) -> bool:
        """Check if message is opt-in"""
        opt_in_keywords = ["start", "yes", "subscribe", "join"]
        return message.lower().strip() in opt_in_keywords
    
    def _is_opt_out_message(self, message: str) -> bool:
        """Check if message is opt-out"""
        opt_out_keywords = ["stop", "unsubscribe", "quit", "cancel"]
        return message.lower().strip() in opt_out_keywords
    
    async def send_payment_link(
        self,
        to_number: str,
        amount: float,
        description: str,
        payment_url: str
    ) -> Dict[str, Any]:
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
        message = f"""
💳 Payment Request

Amount: ₹{amount:,.2f}
Description: {description}

Click here to pay: {payment_url}

This link is secure and expires in 24 hours.
"""
        
        return await self.send_message(to_number, message.strip())
    
    async def send_policy_details(
        self,
        to_number: str,
        policy_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send insurance policy details
        
        Args:
            to_number: Recipient phone number
            policy_data: Policy information
        
        Returns:
            Message details
        """
        message = f"""
📋 Policy Details

Policy Number: {policy_data.get('policy_number', 'N/A')}
Type: {policy_data.get('type', 'N/A')}
Premium: ₹{policy_data.get('premium', 0):,.2f}
Coverage: ₹{policy_data.get('coverage', 0):,.2f}
Status: {policy_data.get('status', 'N/A')}
Renewal Date: {policy_data.get('renewal_date', 'N/A')}

Need help? Reply with your question.
"""
        
        return await self.send_message(to_number, message.strip())
    
    async def send_loan_summary(
        self,
        to_number: str,
        loan_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send loan summary
        
        Args:
            to_number: Recipient phone number
            loan_data: Loan information
        
        Returns:
            Message details
        """
        message = f"""
🏦 Loan Summary

Loan Account: {loan_data.get('account_number', 'N/A')}
Type: {loan_data.get('type', 'N/A')}
Principal: ₹{loan_data.get('principal', 0):,.2f}
Outstanding: ₹{loan_data.get('outstanding', 0):,.2f}
EMI: ₹{loan_data.get('emi', 0):,.2f}
Next Due: {loan_data.get('next_due_date', 'N/A')}

Reply PAY to make payment.
"""
        
        return await self.send_message(to_number, message.strip())


# Create singleton instance
twilio_whatsapp_service = TwilioWhatsAppService()


# Export
__all__ = ["twilio_whatsapp_service", "TwilioWhatsAppService"]
