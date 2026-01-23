"""
Analytics API Endpoints
Call analytics and reporting
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

from app.core.logging import logger
from app.core.database import get_db
from app.models import Call, Message, Intent

router = APIRouter()


# ==================== REQUEST MODELS ====================

class AnalyticsFilter(BaseModel):
    """Analytics filter"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    sector: Optional[str] = None
    channel: Optional[str] = None  # whatsapp, voice


# ==================== ENDPOINTS ====================

@router.get("/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """
    Get analytics overview
    
    Returns:
        Analytics summary
    """
    try:
        # Total calls
        total_calls = db.query(Call).count()
        total_messages = db.query(Message).count()
        
        # Success rate
        successful_calls = db.query(Call).filter(Call.status == "completed").count()
        success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
        
        # Average duration
        avg_duration = db.query(func.avg(Call.duration)).scalar() or 0
        
        # Top intents
        top_intents_query = db.query(
            Intent.intent, func.count(Intent.intent).label('count')
        ).group_by(Intent.intent).order_by(func.count(Intent.intent).desc()).limit(5).all()
        
        return {
            "success": True,
            "data": {
                "total_calls": total_calls,
                "total_messages": total_messages,
                "success_rate": round(success_rate, 2),
                "avg_call_duration": round(avg_duration, 2),
                "top_intents": [{"intent": i.intent, "count": i.count} for i in top_intents_query]
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get analytics overview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calls")
async def get_call_analytics(filter: AnalyticsFilter, db: Session = Depends(get_db)):
    """
    Get call analytics with filters
    """
    try:
        query = db.query(Call)
        
        if filter.sector:
            query = query.filter(Call.sector == filter.sector)
        
        if filter.start_date:
            date = datetime.fromisoformat(filter.start_date)
            query = query.filter(Call.created_at >= date)
        
        if filter.end_date:
            date = datetime.fromisoformat(filter.end_date)
            query = query.filter(Call.created_at <= date)
            
        calls = query.all()
        
        return {
            "success": True,
            "count": len(calls),
            "data": calls
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get call analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages")
async def get_message_analytics(filter: AnalyticsFilter, db: Session = Depends(get_db)):
    """
    Get message analytics with filters
    """
    try:
        query = db.query(Message)
        
        if filter.sector:
            query = query.filter(Message.sector == filter.sector)
        
        if filter.start_date:
            date = datetime.fromisoformat(filter.start_date)
            query = query.filter(Message.timestamp >= date)
        
        if filter.end_date:
            date = datetime.fromisoformat(filter.end_date)
            query = query.filter(Message.timestamp <= date)
            
        messages = query.all()
        
        return {
            "success": True,
            "count": len(messages),
            "data": messages
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get message analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intents")
async def get_intent_distribution(db: Session = Depends(get_db)):
    """
    Get intent distribution
    """
    try:
        results = db.query(
            Intent.sector, Intent.intent, func.count(Intent.id).label('count')
        ).group_by(Intent.sector, Intent.intent).all()
        
        distribution = [
            {
                "sector": r.sector,
                "intent": r.intent,
                "count": r.count
            }
            for r in results
        ]
        
        return {
            "success": True,
            "data": distribution
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get intent distribution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/record-call")
async def record_call_analytics(call_data: dict, db: Session = Depends(get_db)):
    """
    Record call analytics
    """
    try:
        call = Call(**call_data)
        db.add(call)
        db.commit()
        db.refresh(call)
        
        return {
            "success": True,
            "message": "Call analytics recorded"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to record call analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/record-message")
async def record_message_analytics(message_data: dict, db: Session = Depends(get_db)):
    """
    Record message analytics
    """
    try:
        # Ensure timestamp is datetime if present
        if "timestamp" in message_data and isinstance(message_data["timestamp"], str):
             # Simple parsing, might need adjustment based on format
             try:
                 message_data["timestamp"] = datetime.fromisoformat(message_data["timestamp"])
             except:
                 del message_data["timestamp"]

        message = Message(**message_data)
        db.add(message)
        db.commit()
        db.refresh(message)
        
        return {
            "success": True,
            "message": "Message analytics recorded"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to record message analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/record-intent")
async def record_intent_analytics(intent_data: dict, db: Session = Depends(get_db)):
    """
    Record intent analytics
    """
    try:
        intent = Intent(**intent_data)
        db.add(intent)
        db.commit()
        db.refresh(intent)
        
        return {
            "success": True,
            "message": "Intent analytics recorded"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to record intent analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
