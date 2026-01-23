"""
Groq LLM Service
Open-source LLM integration for BFSI AI
"""

from groq import Groq
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.core.logging import logger


class GroqService:
    """Groq LLM service for natural language understanding"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        self.temperature = settings.GROQ_TEMPERATURE
        self.max_tokens = settings.GROQ_MAX_TOKENS
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False
    ) -> str:
        """
        Generate response from Groq LLM
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            json_mode: Enable JSON response mode
        
        Returns:
            Generated response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                response_format={"type": "json_object"} if json_mode else {"type": "text"}
            )
            
            content = response.choices[0].message.content
            logger.info(f"✅ Groq response generated ({len(content)} chars)")
            
            return content
            
        except Exception as e:
            logger.error(f"❌ Groq API error: {str(e)}")
            raise
    
    async def classify_intent(self, user_message: str, sector: str = "banking") -> Dict[str, Any]:
        """
        Classify user intent for BFSI queries
        
        Args:
            user_message: User's message
            sector: BFSI sector (banking, insurance, nbfc, mutual_funds)
        
        Returns:
            Intent classification with confidence
        """
        system_prompt = self._get_intent_classification_prompt(sector)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = await self.generate_response(messages, json_mode=True)
        
        import json
        return json.loads(response)
    
    async def generate_bfsi_response(
        self,
        user_query: str,
        context: str,
        sector: str = "banking",
        language: str = "en"
    ) -> str:
        """
        Generate BFSI-safe response using RAG context
        
        Args:
            user_query: User's question
            context: Retrieved context from RAG
            sector: BFSI sector
            language: Response language
        
        Returns:
            Generated response
        """
        system_prompt = self._get_bfsi_response_prompt(sector, language)
        
        if context:
            user_prompt = f"""
Context from knowledge base:
{context}

User question: {user_query}

Generate a helpful, accurate response based ONLY on the provided context.
If the context doesn't contain the answer, politely say you don't have that information.
"""
        else:
            user_prompt = f"""
User question: {user_query}

Generate a helpful, accurate response based on your general knowledge of {sector} services.
Be professional and concise.
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.generate_response(messages)
        return response
    
    def _get_intent_classification_prompt(self, sector: str) -> str:
        """Get system prompt for intent classification"""
        return f"""You are an intent classification system for {sector} customer service.

Classify the user's intent into one of these categories:
- account_inquiry: Questions about account balance, status, details
- transaction_query: Questions about transactions, payments, transfers
- loan_inquiry: Questions about loans, EMI, interest rates
- policy_inquiry: Questions about insurance policies, coverage
- claim_status: Questions about claim status, processing
- payment_reminder: User wants to make a payment or set reminder
- complaint: User has a complaint or issue
- general_query: General questions about products/services
- escalation: User wants to speak to human agent

Return JSON with:
{{
    "intent": "category_name",
    "confidence": 0.0-1.0,
    "entities": {{"key": "value"}},
    "requires_human": true/false
}}

Be accurate and conservative. If unsure, set requires_human to true."""
    
    def _get_bfsi_response_prompt(self, sector: str, language: str) -> str:
        """Get system prompt for BFSI response generation"""
        lang_instruction = ""
        if language != "en":
            lang_instruction = f"\nRespond in {language} language."
        
        return f"""You are a helpful AI assistant for {sector} customer service.

CRITICAL RULES:
1. Answer ONLY based on the provided context
2. Never make up information or hallucinate
3. Be professional, clear, and concise
4. Use simple language suitable for all customers
5. If you don't know, say "I don't have that information"
6. Never share sensitive information
7. Follow all regulatory compliance guidelines
8. Be empathetic and customer-focused{lang_instruction}

COMPLIANCE:
- Never ask for sensitive data (passwords, PINs, CVV)
- Always maintain customer privacy
- Provide accurate information only
- Escalate complex queries to human agents"""


# Create singleton instance
groq_service = GroqService()


# Export
__all__ = ["groq_service", "GroqService"]
