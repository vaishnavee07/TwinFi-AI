"""
Updated coach.py API — Groq-powered natural language responses
on top of backend-calculated financial data.
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from app.services.twin_engine import TwinEngine
from app.services.groq_service import groq_service
from app.api.deps import CurrentUser

router = APIRouter()
twin_engine = TwinEngine()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(..., description="Unique session ID for conversation continuity")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=[], description="Previous turns: [{'role': 'user'|'assistant', 'content': '...'}]"
    )


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    intent: str
    powered_by: str = "Groq AI"


@router.post(
    "/sessions/{session_id}/messages",
    response_model=ChatResponse,
    summary="Chat with AI Financial Coach (Groq-powered)",
)
async def send_message(
    session_id: str,
    request: ChatRequest,
    current_user: CurrentUser,
) -> ChatResponse:
    """
    Send a message to the TwinFi AI Financial Coach.
    Backend calculates all financial data first, then Groq generates
    a natural language response — no calculations in AI layer.
    """
    # 1. Get pre-calculated financial context from backend engines
    twin_state = await twin_engine.get_twin_state(str(current_user.id))
    dna_context = {
        "dna_score": 84,
        "personality_type": "The Strategic Planner",
    }

    financial_context = {
        "dna_score": dna_context["dna_score"],
        "personality_type": dna_context["personality_type"],
        "health_score": twin_state.get("health_score", 87),
        "net_worth": twin_state.get("net_worth", 1627500),
        "savings_rate": round(
            twin_state.get("monthly_savings", 56000)
            / twin_state.get("monthly_income", 120000)
            * 100,
            1,
        ),
        "risk_profile": "moderate",
        "top_insight": "Consolidate subscriptions to save ₹22,164/year",
    }

    # 2. Groq converts data to natural language response
    reply = await groq_service.coach_chat(
        user_message=request.message,
        financial_context=financial_context,
        conversation_history=request.conversation_history,
    )

    # Detect intent for analytics
    msg_lower = request.message.lower()
    if any(kw in msg_lower for kw in ["dna", "personality", "trait"]):
        intent = "dna_inquiry"
    elif any(kw in msg_lower for kw in ["invest", "sip", "mutual"]):
        intent = "investment_advice"
    elif any(kw in msg_lower for kw in ["retire", "future", "simulate"]):
        intent = "simulation_request"
    elif any(kw in msg_lower for kw in ["save", "budget", "spend"]):
        intent = "savings_advice"
    else:
        intent = "general_coaching"

    return ChatResponse(
        reply=reply,
        session_id=session_id,
        intent=intent,
    )


@router.get(
    "/insights",
    summary="Get proactive AI insights (backend-calculated + Groq-explained)",
)
async def get_proactive_insights(current_user: CurrentUser) -> Dict[str, Any]:
    """
    Proactive insights: backend detects patterns, Groq explains them.
    """
    # Backend calculates leakage
    twin_state = await twin_engine.get_twin_state(str(current_user.id))
    leakage = await twin_engine.calculate_money_leakage([])

    # Backend generates insight data
    raw_insights = [
        {
            "id": "ins_001",
            "type": "saving_opportunity",
            "icon": "💡",
            "priority": "high",
            "title": "Subscription Consolidation",
            "data": {"monthly_leakage": leakage["leakage_breakdown"][0]["monthly"]},
            "action_url": "/leakage",
        },
        {
            "id": "ins_002",
            "type": "investment_alert",
            "icon": "📈",
            "priority": "medium",
            "title": "SIP Increase Opportunity",
            "data": {"current_health": twin_state.get("health_score"), "suggested_sip_increase": 5000},
            "action_url": "/investments",
        },
        {
            "id": "ins_003",
            "type": "market_event",
            "icon": "🌐",
            "priority": "low",
            "title": "RBI Rate Hold Impact",
            "data": {"emi_unchanged": True, "home_loan_emi": 24500},
            "action_url": "/economy",
        },
    ]

    # Groq explains each insight in natural language
    explained_insights = []
    for insight in raw_insights:
        explanation = await groq_service.explain_financial_data(
            data=insight["data"],
            user_query=f"Explain this insight: {insight['title']}",
            context_type="general",
        )
        explained_insights.append({
            **insight,
            "message": explanation,
            "potential_saving": leakage["total_monthly_leakage"] * 12
            if insight["type"] == "saving_opportunity"
            else None,
        })

    return {
        "status": "success",
        "customer_id": str(current_user.id),
        "insight_count": len(explained_insights),
        "insights": explained_insights,
    }
