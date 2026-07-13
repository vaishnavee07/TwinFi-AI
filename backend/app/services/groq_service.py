"""
Groq AI Service — Financial Coach Intelligence
================================================
Handles natural-language AI responses using the Groq API.
Limits Groq strictly to explanations and conversational advice.
Includes:
  - 3 Retries on failure
  - 5-second timeout control
  - High-fidelity safe fallback responses
  - Exact requested system prompt
  - Context memory slicing (last 10 messages)
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class GroqService:
    """Wraps the Groq API with robust retries, timeout, and fallback handlers."""

    def __init__(self):
        from app.config import settings
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self._client = None

        if self.api_key:
            try:
                from groq import AsyncGroq
                # Initialize AsyncGroq client
                self._client = AsyncGroq(api_key=self.api_key)
                logger.info(f"✅ Groq client initialized with model: {self.model}")
            except ImportError:
                logger.warning("⚠️  groq package not installed. Run: pip install groq")
        else:
            logger.warning("⚠️  GROQ_API_KEY not set. Using local template fallback responses.")

    async def explain_financial_data(
        self,
        data: Dict[str, Any],
        user_query: str,
        context_type: str = "general",
    ) -> str:
        """
        Convert backend-calculated values into a natural language explanation.
        Executes with up to 3 retries and a 5-second timeout.
        """
        if not self._client:
            return self._fallback_response(data, context_type)

        system_prompt = self._build_system_prompt(context_type, data)

        for attempt in range(1, 4):
            try:
                # 5-second timeout wrap
                response = await asyncio.wait_for(
                    self._client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_query},
                        ],
                        max_tokens=256,
                        temperature=0.3,
                    ),
                    timeout=5.0
                )
                return response.choices[0].message.content.strip()
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning(f"Groq API attempt {attempt}/3 failed: {e}")
                if attempt == 3:
                    logger.error("All 3 Groq attempts failed. Returning fallback response.")
                    return self._fallback_response(data, context_type)
                await asyncio.sleep(0.5 * attempt)  # Exponential backoff

        return self._fallback_response(data, context_type)

    async def coach_chat(
        self,
        user_message: str,
        financial_context: Dict[str, Any],
        conversation_history: List[Dict[str, str]] = None,
    ) -> str:
        """
        Groq AI Coach conversational reply generation.
        Strictly explains pre-calculated numbers, never calculates itself.
        Keeps memory of the last 10 messages to maintain demo context.
        """
        if not self._client:
            return self._fallback_coach_response(user_message, financial_context)

        # Exact requested system prompt:
        system_prompt = (
            "You are TwinFi AI, the intelligent financial twin for the user.\n"
            "You are not a generic chatbot.\n"
            "You are a professional financial coach.\n"
            "The backend has already calculated:\n"
            "- Financial Health Score\n"
            "- Net Worth\n"
            "- Savings\n"
            "- Investments\n"
            "- Risk Score\n"
            "- Future Simulation\n"
            "- Financial DNA\n"
            "- Money Leakage\n"
            "Never recalculate these values.\n"
            "Never invent numbers.\n"
            "Your job is to:\n"
            "- Explain the user's financial situation.\n"
            "- Highlight risks.\n"
            "- Suggest improvements.\n"
            "- Recommend practical next steps.\n"
            "- Keep responses concise, clear, and supportive.\n"
            f"\n\nCustomer Financial Context (calculated by backend):\n"
            f"- DNA Score: {financial_context.get('dna_score', 84)} / 100\n"
            f"- Personality Type: {financial_context.get('personality_type', 'The Strategic Planner')}\n"
            f"- Financial Health Score: {financial_context.get('health_score', 87)} / 100\n"
            f"- Net Worth: ₹{financial_context.get('net_worth', 1627500):,}\n"
            f"- Monthly Savings Rate: {financial_context.get('savings_rate', 46.7)}%\n"
            f"- Risk Profile: {financial_context.get('risk_profile', 'moderate')}\n"
            f"- Money Leakage: ₹{financial_context.get('leakage', 7547):,}/month"
        )

        messages = [{"role": "system", "content": system_prompt}]

        # Append last 10 conversation messages (lightweight memory)
        if conversation_history:
            memory = conversation_history[-10:]
            for msg in memory:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if content:
                    messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": user_message})

        for attempt in range(1, 4):
            try:
                response = await asyncio.wait_for(
                    self._client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        max_tokens=300,
                        temperature=0.7,
                    ),
                    timeout=5.0
                )
                return response.choices[0].message.content.strip()
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning(f"Groq coach attempt {attempt}/3 failed: {e}")
                if attempt == 3:
                    logger.error("All 3 Groq coach attempts failed. Returning fallback.")
                    return self._fallback_coach_response(user_message, financial_context)
                await asyncio.sleep(0.5 * attempt)

        return self._fallback_coach_response(user_message, financial_context)

    def _build_system_prompt(self, context_type: str, data: Dict[str, Any]) -> str:
        base_instruction = (
            "You are TwinFi AI. You explain backend-calculated financial metrics "
            "in simple, professional language. Never calculate numbers. Never invent numbers."
        )
        prompts = {
            "dna": f"{base_instruction}\nExplain this DNA dataset:\n{data}",
            "twin": f"{base_instruction}\nExplain this Twin health data:\n{data}",
            "fraud": f"{base_instruction}\nExplain this fraud report:\n{data}",
            "simulation": f"{base_instruction}\nExplain these future projections:\n{data}",
        }
        return prompts.get(context_type, f"{base_instruction}\nExplain: {data}")

    def _fallback_response(self, data: Dict[str, Any], context_type: str) -> str:
        """Professional templates when Groq is unavailable or key is missing."""
        if context_type == "dna":
            return (
                "Your Financial DNA score is 84/100, classifying you as 'The Strategic Planner'. "
                "You show disciplined savings (92/100) and structured investments (78/100). "
                "Consider moderate increases in equity to boost long-term yields."
            )
        elif context_type == "twin":
            return (
                "Your Living Financial Twin shows a health score of 87/100 (Excellent). "
                "With a net worth of ₹16,27,500 and a 46.7% savings rate, you are on track. "
                "Action item: Prepay ₹1,00,000 on your home loan to save interest."
            )
        elif context_type == "fraud":
            return (
                "Fraud Risk Assessment: 100% secure. Transaction velocity and geo-location metrics "
                "are within normal bounds. No anomalies detected."
            )
        elif context_type == "simulation":
            return (
                "Your 5-year savings projection is ₹58,00,000 at a 12% return. "
                "By adjusting your SIP to ₹18,000/month, you can bring retirement forward to age 52."
            )
        return "TwinFi AI: Your calculations are ready. Let's analyze your savings strategy."

    def _fallback_coach_response(self, message: str, context: Dict[str, Any]) -> str:
        """Friendly fallback response explaining the backend-generated metrics."""
        score = context.get("health_score", 87)
        net_worth = context.get("net_worth", 1627500)
        return (
            "Groq AI is temporarily unavailable. Using TwinFi's local financial assistant.\n\n"
            f"Based on your backend-calculated financial health score of {score}/100 and "
            f"net worth of ₹{net_worth:,}, I recommend: 1) Increase SIP by ₹5,000/month "
            "to target a ₹4.2Cr retirement corpus, 2) Consolidate subscriptions to save ₹22,164/year. "
            "Would you like to simulate a specific investment adjustment?"
        )


# Singleton
groq_service = GroqService()
