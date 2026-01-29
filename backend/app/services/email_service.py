"""
Email Service
Send emails using SMTP (Gmail, etc.)
"""

import aiosmtplib
from email.message import EmailMessage
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.logging import logger

class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL or self.user
        
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            
        Returns:
            True if successful, False otherwise
        """
        try:
            message = EmailMessage()
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject
            message.set_content(body)
            
            if html_body:
                message.add_alternative(html_body, subtype="html")
                
            logger.info(f"📧 Sending email to {to_email}: {subject}")
            
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                use_tls=False,
                start_tls=True
            )
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {str(e)}")
            return False

# Create singleton instance
email_service = EmailService()

__all__ = ["email_service"]
