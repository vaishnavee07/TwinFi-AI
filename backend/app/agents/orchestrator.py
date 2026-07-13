"""
LangGraph Multi-Agent Orchestrator with Groq AI Integration
============================================================
Groq handles ONLY natural language — all calculations come from backend engines.
Makes LangGraph/LangChain optional to ensure zero startup dependency failures.
"""
import logging
from typing import TypedDict, List, Dict, Any

try:
    from langgraph.graph import StateGraph, END
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False

from app.services.groq_service import groq_service

logger = logging.getLogger(__name__)


# Pydantic state schema
class AgentState(TypedDict):
    messages: List[Any]
    next_agent: str
    context: Dict[str, Any]
    current_intent: str
    financial_data: Dict[str, Any]
    user_id: str


class AgentOrchestrator:
    def __init__(self):
        logger.info("Initializing Financial Agent Orchestrator...")
        self.graph = None
        self._build_graph()

    def _build_graph(self):
        if not HAS_LANGGRAPH:
            logger.warning("⚠️ langgraph / langchain packages not installed. Running in direct Groq fallback mode.")
            return

        try:
            workflow = StateGraph(AgentState)

            workflow.add_node("supervisor", self._supervisor_node)
            workflow.add_node("dna_agent", self._dna_agent_node)
            workflow.add_node("fraud_agent", self._fraud_agent_node)
            workflow.add_node("investment_agent", self._investment_agent_node)
            workflow.add_node("simulation_agent", self._simulation_agent_node)
            workflow.add_node("coach_agent", self._coach_agent_node)

            workflow.add_conditional_edges(
                "supervisor",
                self._route_to_specialist,
                {
                    "dna_agent": "dna_agent",
                    "fraud_agent": "fraud_agent",
                    "investment_agent": "investment_agent",
                    "simulation_agent": "simulation_agent",
                    "coach_agent": "coach_agent",
                    "FINISH": END,
                },
            )

            for agent in ["dna_agent", "fraud_agent", "investment_agent", "simulation_agent", "coach_agent"]:
                workflow.add_edge(agent, "supervisor")

            workflow.set_entry_point("supervisor")
            self.graph = workflow.compile()
            logger.info("✅ LangGraph compiled successfully.")
        except Exception as e:
            logger.error(f"Failed to build LangGraph: {e}. Falling back to direct mode.")
            self.graph = None

    def _supervisor_node(self, state: AgentState) -> AgentState:
        messages = state.get("messages", [])
        last_message = messages[-1].get("content", "").lower() if messages else ""

        if any(kw in last_message for kw in ["dna", "personality", "trait", "score"]):
            state["next_agent"] = "dna_agent"
        elif any(kw in last_message for kw in ["fraud", "suspicious", "alert", "block"]):
            state["next_agent"] = "fraud_agent"
        elif any(kw in last_message for kw in ["invest", "sip", "mutual fund", "stock", "portfolio"]):
            state["next_agent"] = "investment_agent"
        elif any(kw in last_message for kw in ["simulate", "what if", "scenario", "future", "retire"]):
            state["next_agent"] = "simulation_agent"
        else:
            state["next_agent"] = "coach_agent"

        return state

    def _route_to_specialist(self, state: AgentState) -> str:
        return state.get("next_agent", "FINISH")

    def _dna_agent_node(self, state: AgentState) -> AgentState:
        state["next_agent"] = "FINISH"
        return state

    def _fraud_agent_node(self, state: AgentState) -> AgentState:
        state["next_agent"] = "FINISH"
        return state

    def _investment_agent_node(self, state: AgentState) -> AgentState:
        state["next_agent"] = "FINISH"
        return state

    def _simulation_agent_node(self, state: AgentState) -> AgentState:
        state["next_agent"] = "FINISH"
        return state

    def _coach_agent_node(self, state: AgentState) -> AgentState:
        state["next_agent"] = "FINISH"
        return state

    async def run_query(
        self,
        user_id: str,
        query: str,
        context: Dict[str, Any] = None,
        financial_data: Dict[str, Any] = None,
    ) -> str:
        """
        Run a user query. Calls Groq for explaining the pre-calculated financial data.
        """
        coach_context = financial_data or {
            "dna_score": 84,
            "personality_type": "The Strategic Planner",
            "health_score": 87,
            "net_worth": 1627500,
            "savings_rate": 46.7,
            "risk_profile": "moderate",
            "top_insight": "Consolidate OTT subscriptions to save ₹22,164/year",
        }

        # If LangGraph is compiled, try invoking it first
        if self.graph:
            try:
                initial_state = {
                    "messages": [{"role": "user", "content": query}],
                    "next_agent": "supervisor",
                    "context": context or {},
                    "current_intent": "unknown",
                    "financial_data": coach_context,
                    "user_id": user_id,
                }
                result = await self.graph.ainvoke(initial_state)
                last_msg = result.get("messages", [])
                if last_msg and isinstance(last_msg[-1], dict) and last_msg[-1].get("role") == "assistant":
                    return last_msg[-1]["content"]
            except Exception as e:
                logger.error(f"LangGraph execution error: {e}")

        # Fallback to direct Groq chat
        return await groq_service.coach_chat(
            user_message=query,
            financial_context=coach_context,
        )
