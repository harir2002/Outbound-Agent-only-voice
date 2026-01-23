from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from datetime import datetime
from app.core.database import Base

class Call(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    call_sid = Column(String, unique=True, index=True)
    to_number = Column(String)
    from_number = Column(String)
    status = Column(String)
    duration = Column(Integer, default=0)
    direction = Column(String)  # inbound, outbound
    recording_url = Column(String, nullable=True)
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    sentiment = Column(String, nullable=True)
    sector = Column(String, default="banking")
    language = Column(String, default="en")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    message_sid = Column(String, unique=True, index=True)
    to_number = Column(String)
    from_number = Column(String)
    content = Column(Text)
    role = Column(String)  # user, assistant
    channel = Column(String, default="whatsapp")
    sector = Column(String, default="banking")
    
    timestamp = Column(DateTime, default=datetime.utcnow)

class Intent(Base):
    __tablename__ = "intents"

    id = Column(Integer, primary_key=True, index=True)
    intent = Column(String, index=True)
    text = Column(Text)
    confidence = Column(Float)
    sector = Column(String)
    user_id = Column(String, nullable=True)
    
    recorded_at = Column(DateTime, default=datetime.utcnow)

class UserConsent(Base):
    __tablename__ = "user_consents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # phone number
    channel = Column(String)  # whatsapp, voice
    granted = Column(Boolean, default=False)
    
    updated_at = Column(DateTime, default=datetime.utcnow)
