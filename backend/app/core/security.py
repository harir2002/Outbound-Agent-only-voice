"""
Security & Compliance Module
JWT authentication, PII masking, consent tracking
"""

import re
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings, get_pii_patterns
from app.core.logging import logger, audit_log


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==================== JWT AUTHENTICATION ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {str(e)}")
        return None


# ==================== PII MASKING ====================

class PIIMasker:
    """PII masking for compliance"""
    
    # Regex patterns for Indian PII
    PATTERNS = {
        "phone": r'\b(\+91[\-\s]?)?[6-9]\d{9}\b',
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "aadhaar": r'\b\d{4}\s?\d{4}\s?\d{4}\b',
        "pan": r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
        "account": r'\b\d{9,18}\b',
        "ifsc": r'\b[A-Z]{4}0[A-Z0-9]{6}\b',
        "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
    }
    
    @classmethod
    def mask_text(cls, text: str, patterns: list = None) -> str:
        """
        Mask PII in text
        
        Args:
            text: Input text
            patterns: List of PII patterns to mask (default: all)
        
        Returns:
            Masked text
        """
        if not settings.ENABLE_PII_MASKING:
            return text
        
        masked_text = text
        patterns_to_mask = patterns or get_pii_patterns()
        
        for pattern_name in patterns_to_mask:
            if pattern_name in cls.PATTERNS:
                pattern = cls.PATTERNS[pattern_name]
                masked_text = re.sub(pattern, f"[{pattern_name.upper()}_REDACTED]", masked_text)
        
        return masked_text
    
    @classmethod
    def hash_pii(cls, value: str) -> str:
        """Hash PII for storage"""
        return hashlib.sha256(value.encode()).hexdigest()


# ==================== CONSENT TRACKING ====================

class ConsentManager:
    """Manage user consent for calls and messages"""
    
    # In-memory storage (use Redis/DB in production)
    consent_records = {}
    
    @classmethod
    def record_consent(
        cls,
        user_id: str,
        consent_type: str,
        granted: bool,
        metadata: dict = None
    ):
        """
        Record user consent
        
        Args:
            user_id: User identifier
            consent_type: Type of consent (whatsapp, call_recording, etc.)
            granted: Whether consent was granted
            metadata: Additional metadata
        """
        consent_id = f"{user_id}:{consent_type}"
        
        cls.consent_records[consent_id] = {
            "user_id": user_id,
            "consent_type": consent_type,
            "granted": granted,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        # Audit log
        audit_log(
            event=f"consent_{consent_type}",
            user_id=user_id,
            metadata={"granted": granted, **(metadata if metadata else {})}
        )
        
        logger.info(f"Consent recorded: {user_id} - {consent_type} - {granted}")
    
    @classmethod
    def check_consent(cls, user_id: str, consent_type: str) -> bool:
        """
        Check if user has granted consent
        
        Args:
            user_id: User identifier
            consent_type: Type of consent
        
        Returns:
            True if consent granted, False otherwise
        """
        consent_id = f"{user_id}:{consent_type}"
        record = cls.consent_records.get(consent_id)
        
        if not record:
            return False
        
        return record.get("granted", False)
    
    @classmethod
    def get_consent_history(cls, user_id: str) -> list:
        """Get consent history for user"""
        return [
            record for record in cls.consent_records.values()
            if record["user_id"] == user_id
        ]


# ==================== CALL RECORDING COMPLIANCE ====================

def get_call_recording_disclosure(language: str = "en") -> str:
    """
    Get call recording disclosure message
    
    Args:
        language: Language code (en, hi, ta, etc.)
    
    Returns:
        Disclosure message
    """
    disclosures = {
        "en": "This call may be recorded for quality and training purposes. By continuing, you consent to this recording.",
        "hi": "यह कॉल गुणवत्ता और प्रशिक्षण उद्देश्यों के लिए रिकॉर्ड की जा सकती है। जारी रखकर, आप इस रिकॉर्डिंग के लिए सहमति देते हैं।",
        "ta": "இந்த அழைப்பு தரம் மற்றும் பயிற்சி நோக்கங்களுக்காக பதிவு செய்யப்படலாம். தொடர்வதன் மூலம், இந்த பதிவுக்கு நீங்கள் ஒப்புக்கொள்கிறீர்கள்.",
        "te": "ఈ కాల్ నాణ్యత మరియు శిక్షణ ప్రయోజనాల కోసం రికార్డ్ చేయబడవచ్చని దయచేసి గమనించండి. కొనసాగడం ద్వారా, మీరు ఈ రికార్డింగ్‌కు అంగీకరిస్తున్నారు."
    }
    
    return disclosures.get(language, disclosures["en"])


# ==================== DATA SANITIZATION ====================

def sanitize_for_embedding(text: str) -> str:
    """
    Sanitize text before creating embeddings
    Removes PII to ensure compliance
    
    Args:
        text: Input text
    
    Returns:
        Sanitized text
    """
    # Mask PII
    sanitized = PIIMasker.mask_text(text)
    
    # Log sanitization
    logger.debug("Text sanitized for embedding")
    
    return sanitized


# Export
__all__ = [
    "create_access_token",
    "verify_token",
    "PIIMasker",
    "ConsentManager",
    "get_call_recording_disclosure",
    "sanitize_for_embedding"
]
