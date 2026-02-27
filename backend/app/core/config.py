"""
Configuration Management
Loads environment variables and application settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # ==================== ENVIRONMENT ====================
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # ==================== API SERVICES ====================
    # Groq LLM
    GROQ_API_KEY: str
    GROQ_MODEL: str = "mixtral-8x7b-32768"
    GROQ_TEMPERATURE: float = 0.3
    GROQ_MAX_TOKENS: int = 2048
    
    # Sarvam AI
    SARVAM_API_KEY: str
    SARVAM_TTS_MODEL: str = "bulbul:v1"
    SARVAM_STT_MODEL: str = "saaras:v1"
    SARVAM_API_URL: str = "https://api.sarvam.ai"
    
    # Twilio
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    

    
    # ==================== DATABASE ====================
    DATABASE_URL: str = "sqlite:///./data/bfsi_ai.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./data/chromadb"
    CHROMA_COLLECTION_NAME: str = "bfsi_documents"
    
    # ==================== EMBEDDINGS ====================
    EMBEDDING_MODEL: str = "BAAI/bge-base-en-v1.5"
    EMBEDDING_DIMENSION: int = 768
    
    # ==================== SECURITY ====================
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440
    
    ENCRYPTION_KEY: str = "your-32-byte-encryption-key-here"
    
    # ==================== APPLICATION ====================
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"
    PUBLIC_URL: str = "https://1db819452b10.ngrok-free.app"  # For external access (ngrok, production URL)
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # ==================== COMPLIANCE ====================
    ENABLE_PII_MASKING: bool = True
    PII_PATTERNS: str = "phone,email,aadhaar,pan,account"
    
    CALL_RECORDING_ENABLED: bool = True
    CALL_RECORDING_CONSENT_REQUIRED: bool = True
    
    DATA_RETENTION_DAYS: int = 90
    AUDIT_LOG_RETENTION_DAYS: int = 365
    
    # ==================== CELERY ====================
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # ==================== RATE LIMITING ====================
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # ==================== BFSI ====================
    SUPPORTED_SECTORS: str = "banking,insurance,nbfc,mutual_funds"
    DEFAULT_SECTOR: str = "banking"
    
    SUPPORTED_LANGUAGES: str = "en,hi,ta,te,mr,bn"
    DEFAULT_LANGUAGE: str = "en"
    
    # ==================== MONITORING ====================
    ENABLE_METRICS: bool = True
    SENTRY_DSN: str = ""
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


# Create settings instance
settings = Settings()


# Helper functions
def get_supported_sectors() -> List[str]:
    """Get list of supported BFSI sectors"""
    return settings.SUPPORTED_SECTORS.split(",")


def get_supported_languages() -> List[str]:
    """Get list of supported languages"""
    return settings.SUPPORTED_LANGUAGES.split(",")


def get_pii_patterns() -> List[str]:
    """Get list of PII patterns to mask"""
    return settings.PII_PATTERNS.split(",")
