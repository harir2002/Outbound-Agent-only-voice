"""
Voice AI API Endpoints
Outbound voice calls using Twilio Voice API
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from app.services.sarvam_service import sarvam_service
from app.services.groq_service import groq_service

from app.core.logging import logger, audit_log
from app.core.security import ConsentManager, get_call_recording_disclosure

router = APIRouter()


# ==================== REQUEST MODELS ====================

class OutboundCallRequest(BaseModel):
    """Outbound call request"""
    phone_number: str
    purpose: str  # sip_debit_reminder, kyc_update_reminder, sip_failure_notification
    sector: str = "banking"
    language: str = "en"
    customer_data: dict = {}
    public_url: Optional[str] = None


class VoiceQueryRequest(BaseModel):
    """Voice query request"""
    text: str
    sector: str = "banking"
    language: str = "en"
    session_id: Optional[str] = None


# ==================== CALL SESSIONS ====================

call_sessions = {}


# ==================== ENDPOINTS ====================

@router.post("/outbound")
async def initiate_outbound_call(request: OutboundCallRequest):
    """
    Initiate outbound voice call using Twilio Voice API
    
    Args:
        request: Outbound call request
    
    Returns:
        Call details
    """
    try:
        logger.info(f"🔵 Initiating REAL voice call to {request.phone_number}")
        
        # Check consent
        if not ConsentManager.check_consent(request.phone_number, "outbound_call"):
            logger.warning(f"No outbound call consent for {request.phone_number}")
            ConsentManager.record_consent(
                user_id=request.phone_number,
                consent_type="outbound_call",
                granted=False
            )
        
        # Create call session
        call_id = str(uuid.uuid4())
        call_sessions[call_id] = {
            "call_id": call_id,
            "phone_number": request.phone_number,
            "purpose": request.purpose,
            "sector": request.sector,
            "language": request.language,
            "customer_data": request.customer_data,
            "status": "initiated",
            "created_at": datetime.utcnow().isoformat(),
            "messages": [],
            "public_url": request.public_url
        }
        
        # Generate initial greeting
        greeting = await _generate_call_greeting(request)
        logger.info(f"📝 Generated greeting: {greeting[:100]}...")

        # Get language config for appropriate speaker
        lang_config = sarvam_service.get_language_config(request.language)
        speaker = lang_config.get("speaker", "meera")
        
        # Convert to speech using SARVAM AI (High Quality)
        logger.info(f"🎙️ Generating Sarvam AI high-quality audio with speaker {speaker}...")
        audio_bytes = await sarvam_service.text_to_speech(
            text=greeting,
            language=request.language,
            speaker=speaker
        )
        
        # Store audio and greeting in session
        call_sessions[call_id]["audio_bytes"] = audio_bytes
        call_sessions[call_id]["greeting"] = greeting
        
        # Make REAL Twilio Voice call
        from twilio.rest import Client
        from app.core.config import settings
        
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        
        # Create TwiML URL for the call
        # This will be the URL Twilio calls to get instructions
        if request.public_url:
            base_url = request.public_url.rstrip('/')
        elif settings.PUBLIC_URL:
            base_url = settings.PUBLIC_URL.rstrip('/')
        else:
            base_url = settings.FRONTEND_URL.replace('3000', '8000')
            
        twiml_url = f"{base_url}/api/voice/twiml/{call_id}"
        
        logger.info(f"📞 Making Twilio Voice call to {request.phone_number}")
        logger.info(f"🔗 TwiML URL: {twiml_url}")
        
        # Initiate the call via Twilio
        # Use PUBLIC_URL for status callback if available
        status_callback_url = f"{base_url}/api/voice/status/{call_id}"
        
        twilio_call = client.calls.create(
            to=request.phone_number,
            from_=settings.TWILIO_PHONE_NUMBER,
            url=twiml_url,
            method='POST',
            status_callback=status_callback_url,
            status_callback_event=['initiated', 'ringing', 'answered', 'completed']
        )
        
        # Update session with Twilio call SID
        call_sessions[call_id]["twilio_call_sid"] = twilio_call.sid
        call_sessions[call_id]["twilio_status"] = twilio_call.status
        
        # Audit log
        audit_log(
            event="outbound_call_initiated",
            user_id=request.phone_number,
            metadata={
                "call_id": call_id,
                "twilio_sid": twilio_call.sid,
                "purpose": request.purpose,
                "sector": request.sector,
                "audio_gen": "sarvam_ai"
            }
        )
        
        logger.info(f"✅ REAL Twilio call initiated with Sarvam AI audio!")
        logger.info(f"   Call ID: {call_id}")
        logger.info(f"   Twilio SID: {twilio_call.sid}")
        
        return {
            "success": True,
            "call_id": call_id,
            "twilio_sid": twilio_call.sid,
            "status": twilio_call.status,
            "greeting": greeting,
            "phone_number": request.phone_number,
            "real_call": True,
            "audio_provider": "sarvam_ai"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to initiate voice call: {str(e)}")
        logger.error(f"   Error type: {type(e).__name__}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to initiate call: {str(e)}")


@router.post("/tts")
async def text_to_speech(
    text: str,
    language: str = "en",
    speaker: str = "meera"
):
    """
    Convert text to speech
    
    Args:
        text: Text to convert
        language: Language code
        speaker: Voice speaker
    
    Returns:
        Audio bytes (base64 encoded)
    """
    try:
        audio_bytes = await sarvam_service.text_to_speech(
            text=text,
            language=language,
            speaker=speaker
        )
        
        import base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        return {
            "success": True,
            "audio": audio_base64,
            "language": language,
            "speaker": speaker
        }
        
    except Exception as e:
        logger.error(f"❌ TTS failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stt")
async def speech_to_text(
    audio: UploadFile = File(...),
    language: str = "en"
):
    """
    Convert speech to text
    
    Args:
        audio: Audio file
        language: Expected language
    
    Returns:
        Transcription result
    """
    try:
        # Read audio file
        audio_bytes = await audio.read()
        
        # Transcribe
        result = await sarvam_service.speech_to_text(
            audio_bytes=audio_bytes,
            language=language
        )
        
        return {
            "success": True,
            "transcript": result["transcript"],
            "confidence": result["confidence"],
            "language": result["language"]
        }
        
    except Exception as e:
        logger.error(f"❌ STT failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def process_voice_query(request: VoiceQueryRequest):
    """
    Process voice query with RAG
    
    Args:
        request: Voice query request
    
    Returns:
        AI response
    """
    try:
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        
        # Generate response (without RAG context)
        response_text = await groq_service.generate_bfsi_response(
            user_query=request.text,
            context="",
            sector=request.sector,
            language=request.language
        )
        
        # Convert to speech
        audio_bytes = await sarvam_service.text_to_speech(
            text=response_text,
            language=request.language
        )
        
        import base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        return {
            "success": True,
            "session_id": session_id,
            "text_response": response_text,
            "audio_response": audio_base64,
            "language": request.language
        }
        
    except Exception as e:
        logger.error(f"❌ Voice query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/call/{call_id}")
async def get_call_details(call_id: str):
    """
    Get call session details
    
    Args:
        call_id: Call ID
    
    Returns:
        Call details
    """
    if call_id not in call_sessions:
        raise HTTPException(status_code=404, detail="Call not found")
    
    return {
        "success": True,
        "data": call_sessions[call_id]
    }


@router.post("/call/{call_id}/complete")
async def complete_call(call_id: str, outcome: str):
    """
    Mark call as complete
    
    Args:
        call_id: Call ID
        outcome: Call outcome (completed, no_answer, busy, failed)
    
    Returns:
        Success status
    """
    if call_id not in call_sessions:
        raise HTTPException(status_code=404, detail="Call not found")
    
    call_sessions[call_id]["status"] = "completed"
    call_sessions[call_id]["outcome"] = outcome
    call_sessions[call_id]["completed_at"] = datetime.utcnow().isoformat()
    
    # Audit log
    audit_log(
        event="outbound_call_completed",
        user_id=call_sessions[call_id]["phone_number"],
        metadata={
            "call_id": call_id,
            "outcome": outcome
        }
    )
    
    return {
        "success": True,
        "message": "Call completed"
    }


@router.get("/voices")
async def get_available_voices(language: str = "en"):
    """
    Get available voice speakers
    
    Args:
        language: Language code
    
    Returns:
        List of voices
    """
    try:
        voices = await sarvam_service.get_available_voices(language)
        
        return {
            "success": True,
            "voices": voices
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get voices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/twiml/{call_id}")
async def get_twiml_for_call(call_id: str):
    """
    TwiML endpoint for Twilio Voice calls
    Returns instructions to <Play> the Sarvam AI audio
    """
    try:
        from fastapi.responses import Response
        from app.core.config import settings
        
        logger.info(f"📞 TwiML requested for call: {call_id}")
        
        if call_id not in call_sessions:
            logger.error(f"❌ Call session not found: {call_id}")
            twiml = '<?xml version="1.0" encoding="UTF-8"?><Response><Say>Meeting not found.</Say></Response>'
            return Response(content=twiml, media_type="application/xml")
        
        session = call_sessions[call_id]
        
        # Check if audio is likely the mock audio (Sarvam failed)
        # The mock audio header is very small (< 100 bytes usually)
        audio_bytes = session.get("audio_bytes", b"")
        use_fallback_tts = len(audio_bytes) < 100
        
        
        # Language-specific Twilio voices
        TWILIO_VOICES = {
            "en": ("alice", "en-IN"),  # English with Indian accent
            "hi": ("Polly.Aditi", "hi-IN"),  # Hindi (Amazon Polly via Twilio)
            "ta": ("Polly.Aditi", "ta-IN"),  # Tamil
            "te": ("Polly.Aditi", "te-IN"),  # Telugu  
            "mr": ("Polly.Aditi", "mr-IN"),  # Marathi
            "bn": ("Polly.Aditi", "bn-IN"),  # Bengali
        }
        
        # Get language from session
        language = session.get("language", "en")
        voice, lang_code = TWILIO_VOICES.get(language, ("alice", "en-IN"))
        
        if use_fallback_tts:
            logger.warning(f"⚠️ Sarvam TTS failed (size {len(audio_bytes)}), using Twilio TTS with {voice}")
            greeting = session.get("greeting", "Hello, this is a call from your bank.")
            # Escape XML special characters
            greeting = greeting.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="{voice}" language="{lang_code}">{greeting}</Say>
    <Pause length="1"/>
    <Say voice="{voice}" language="{lang_code}">Thank you for your time. Goodbye.</Say>
</Response>'''
        else:
            # Use public URL for high quality audio
            if session.get("public_url"):
                base_url = session["public_url"].rstrip('/')
            elif settings.PUBLIC_URL:
                base_url = settings.PUBLIC_URL.rstrip('/')
            else:
                base_url = settings.FRONTEND_URL.replace('3000', '8000')
                
            audio_url = f"{base_url}/api/voice/audio/{call_id}.wav"
            
            logger.info(f"🔗 Sending TwiML with <Play> URL: {audio_url}")
            
            twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{audio_url}</Play>
    <Pause length="1"/>
    <Say voice="alice" language="en-IN">Thank you for your time. Goodbye.</Say>
</Response>'''
        
        return Response(content=twiml, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"❌ TwiML generation failed: {str(e)}")
        twiml = '<?xml version="1.0" encoding="UTF-8"?><Response><Say>System error.</Say></Response>'
        return Response(content=twiml, media_type="application/xml")


@router.get("/audio/{call_id}.wav")
async def get_call_audio(call_id: str):
    """Serve the Sarvam AI audio file for a specific call session"""
    from fastapi.responses import Response
    import io
    
    if call_id not in call_sessions or "audio_bytes" not in call_sessions[call_id]:
        logger.error(f"❌ Audio not found for call: {call_id}")
        raise HTTPException(status_code=404, detail="Audio not found")
    
    logger.info(f"🔊 Serving audio bytes for call: {call_id}")
    audio_bytes = call_sessions[call_id]["audio_bytes"]
    
    return Response(
        content=audio_bytes,
        media_type="audio/wav",
        headers={"Content-Length": str(len(audio_bytes))}
    )


@router.post("/status/{call_id}")
async def handle_call_status(
    call_id: str,
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    From: Optional[str] = Form(None),
    To: Optional[str] = Form(None)
):
    """
    Twilio status callback endpoint
    Receives updates about call status
    
    Args:
        call_id: Call session ID
        CallSid: Twilio call SID
        CallStatus: Current call status
        From: Caller number
        To: Recipient number
    
    Returns:
        Success response
    """
    try:
        logger.info(f"📊 Call status update for {call_id}:")
        logger.info(f"   Twilio SID: {CallSid}")
        logger.info(f"   Status: {CallStatus}")
        logger.info(f"   From: {From}")
        logger.info(f"   To: {To}")
        
        if call_id in call_sessions:
            call_sessions[call_id]["twilio_status"] = CallStatus
            call_sessions[call_id]["last_status_update"] = datetime.utcnow().isoformat()
            
            # Audit log
            audit_log(
                event=f"call_status_{CallStatus}",
                user_id=To or "unknown",
                metadata={
                    "call_id": call_id,
                    "twilio_sid": CallSid,
                    "status": CallStatus
                }
            )
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"❌ Status callback failed: {str(e)}")
        return {"success": False, "error": str(e)}


# ==================== HELPER FUNCTIONS ====================

async def _generate_call_greeting(request: OutboundCallRequest) -> str:
    """Generate personalized call greeting"""
    
    # Extract variables
    name = request.customer_data.get("name") if request.customer_data else "sir or madam"
    amount = request.customer_data.get("amount") if request.customer_data and request.customer_data.get("amount") else "5000"
    due_date = request.customer_data.get("due_date") if request.customer_data and request.customer_data.get("due_date") else "the 5th of this month"
    
    debit_date = due_date
    deadline_date = due_date
    
    campaign_type = request.purpose
    language = request.language
    
    # Mapping exact scripts provided by user
    scripts = {
        "personal_loan_reminder": {
            "en": f"Hello {name}, this is a reminder that your Personal Loan EMI of ₹{amount} is due on {due_date}. Please ensure timely payment to avoid late charges. Thank you!",
            "hi": f"नमस्ते {name}, यह याद दिलाना है कि आपके पर्सनल लोन की EMI ₹{amount} की देय तिथि {due_date} है। देरी से बचने के लिए समय पर भुगतान करें। धन्यवाद!",
            "ta": f"வணக்கம் {name}, உங்கள் தனிநபர் கடன் EMI தொகை ₹{amount}, {due_date} அன்று செலுத்த வேண்டும். தாமதக் கட்டணங்களை தவிர்க்க சரியான நேரத்தில் செலுத்தவும். நன்றி!"
        },
        "credit_card_reminder": {
            "en": f"Hello {name}, your Credit Card minimum due amount of ₹{amount} must be paid by {due_date}. Avoid late fees by paying at the earliest. Thank you!",
            "hi": f"नमस्ते {name}, आपके क्रेडिट कार्ड की न्यूनतम देय राशि ₹{amount} {due_date} तक जमा करनी है। विलंब शुल्क से बचने के लिए जल्द भुगतान करें। धन्यवाद!",
            "ta": f"வணக்கம் {name}, உங்கள் கிரெடிட் கார்டு குறைந்தபட்ச தொகை ₹{amount}, {due_date} க்குள் செலுத்த வேண்டும். தாமதக் கட்டணங்களை தவிர்க்கவும். நன்றி!"
        },
        "home_loan_reminder": {
            "en": f"Hello {name}, your Home Loan EMI of ₹{amount} is due on {due_date}. Please ensure sufficient balance in your account for auto-debit. Thank you!",
            "hi": f"नमस्ते {name}, आपके होम लोन की EMI ₹{amount} की कटौती {due_date} को होगी। ऑटो-डेबिट के लिए पर्याप्त बैलेंस सुनिश्चित करें। धन्यवाद!",
            "ta": f"வணக்கம் {name}, உங்கள் வீட்டு கடன் EMI ₹{amount}, {due_date} அன்று கழிக்கப்படும். தானியங்கி பற்று வசதிக்கு போதுமான இருப்பு வைத்திருக்கவும். நன்றி!"
        },
        "auto_loan_reminder": {
            "en": f"Hello {name}, your Auto Loan EMI of ₹{amount} is scheduled on {due_date}. Please maintain adequate funds in your account. Thank you!",
            "hi": f"नमस्ते {name}, आपके ऑटो लोन की EMI ₹{amount} की तारीख {due_date} है। अपने खाते में पर्याप्त राशि बनाए रखें। धन्यवाद!",
            "ta": f"வணக்கம் {name}, உங்கள் வாகனக் கடன் EMI ₹{amount}, {due_date} அன்று நிர்ணயிக்கப்பட்டுள்ளது. உங்கள் கணக்கில் போதுமான தொகை வைத்திருக்கவும். நன்றி!"
        },
        "business_loan_reminder": {
            "en": f"Hello {name}, your Business Loan repayment of ₹{amount} is due on {due_date}. Timely payment helps maintain your business credit profile. Thank you!",
            "hi": f"नमस्ते {name}, आपके बिज़नेस लोन की किस्त ₹{amount} की देय तिथि {due_date} है। समय पर भुगतान आपकी क्रेडिट प्रोफ़ाइल को बनाए रखता है। धन्यवाद!",
            "ta": f"வணக்கம் {name}, உங்கள் வணிகக் கடன் தவணை ₹{amount}, {due_date} அன்று செலுத்த வேண்டும். சரியான நேரத்தில் செலுத்துவது உங்கள் கடன் மதிப்பை பாதுகாக்கும். நன்றி!"
        },
        "sip_debit_reminder": {
            "en": f"Hello {name}, your SIP installment of ₹{amount} will be auto-debited on {debit_date}. Please ensure sufficient balance to avoid SIP cancellation. Thank you!",
            "hi": f"नमस्ते {name}, आपकी SIP किस्त ₹{amount} की ऑटो-डेबिट {debit_date} को होगी। SIP रद्द होने से बचाने के लिए पर्याप्त बैलेंस रखें। धन्यवाद!",
            "ta": f"வணக்கம் {name}, உங்கள் SIP தவணை ₹{amount}, {debit_date} அன்று தானியங்கியாக கழிக்கப்படும். SIP ரத்தாவதை தவிர்க்க போதுமான இருப்பை உறுதி செய்யவும். நன்றி!"
        },
        "kyc_update_reminder": {
            "en": f"Hello {name}, your KYC documents are due for renewal by {deadline_date}. Please update your KYC to avoid interruption in your account services. Thank you!",
            "hi": f"नमस्ते {name}, आपके KYC दस्तावेज़ {deadline_date} तक नवीनीकृत करने हैं। अपनी सेवाओं में बाधा से बचने के लिए KYC अपडेट करें। धन्यवाद!",
            "ta": f"வணக்கம் {name}, உங்கள் KYC ஆவணங்கள் {deadline_date} க்குள் புதுப்பிக்கப்பட வேண்டும். உங்கள் சேவைகள் தடைபடாமல் இருக்க KYC புதுப்பிக்கவும். நன்றி!"
        },
        "sip_failure_notification": {
            "en": f"Hello {name}, your SIP installment of ₹{amount} scheduled on {debit_date} has failed due to insufficient funds. Please recharge your account immediately to avoid SIP discontinuation. Thank you!",
            "hi": f"नमस्ते {name}, {debit_date} को निर्धारित आपकी SIP किस्त ₹{amount} अपर्याप्त बैलेंस के कारण विफल हो गई है। SIP बंद होने से बचाने के लिए तुरंत अपना खाता रिचार्ज करें। धन्यवाद!",
            "ta": f"வணக்கம் {name}, {debit_date} அன்று நிர்ணயிக்கப்பட்ட உங்கள் SIP தவணை ₹{amount} போதுமான இருப்பு இல்லாததால் தோல்வியடைந்தது. SIP நிறுத்தப்படாமல் இருக்க உடனடியாக தொகையை நிரப்பவும். நன்றி!"
        }
    }
    
    # Fallback to default if unknown campaign
    if campaign_type not in scripts:
        campaign_type = "personal_loan_reminder"
        
    # Get localized script or default to English
    selected_script = scripts[campaign_type].get(language, scripts[campaign_type]["en"])
    
    # Add call recording disclosure
    disclosure = get_call_recording_disclosure(language)
    
    full_greeting = f"{selected_script} {disclosure}"
    
    return full_greeting
