"""
Logging Configuration
Enterprise-grade logging with audit trail
"""

import logging
import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings


def setup_logging():
    """Setup application logging"""
    
    # Remove default handler
    logger.remove()
    
    # Console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True
    )
    
    # File handler - General logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        compression="zip"
    )
    
    # File handler - Error logs
    logger.add(
        log_dir / "error_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="90 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        compression="zip"
    )
    
    # File handler - Audit logs (compliance)
    logger.add(
        log_dir / "audit_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention=f"{settings.AUDIT_LOG_RETENTION_DAYS} days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        compression="zip",
        filter=lambda record: "AUDIT" in record["extra"]
    )
    
    logger.info("✅ Logging configured successfully")


def audit_log(event: str, user_id: str = None, metadata: dict = None):
    """
    Create audit log entry for compliance
    
    Args:
        event: Event description
        user_id: User identifier
        metadata: Additional metadata
    """
    log_data = {
        "event": event,
        "user_id": user_id,
        "metadata": metadata or {}
    }
    
    logger.bind(AUDIT=True).info(f"AUDIT: {log_data}")


# Export logger
__all__ = ["logger", "setup_logging", "audit_log"]
