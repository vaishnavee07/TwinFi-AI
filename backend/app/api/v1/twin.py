from fastapi import APIRouter, Depends
from typing import Dict, Any, List

from app.services.twin_engine import TwinEngine
from app.api.deps import CurrentUser

router = APIRouter()
twin_engine = TwinEngine()


@router.get("/", summary="Get current Living Financial Twin state")
async def get_twin_state(current_user: CurrentUser) -> Dict[str, Any]:
    """
    Retrieve the complete current state of the Living Financial Twin.
    Includes net worth, cashflow, health score, asset breakdown, and 12-month predictions.
    """
    health_score = await twin_engine.calculate_health_score({})
    predictions = await twin_engine.generate_predictions({})

    return {
        "status": "success",
        "twin": {
            "customer_id": str(current_user.id),
            "version": 47,
            "last_synced": "2026-07-13T09:00:00+05:30",
            "health_score": health_score,
            "net_worth": 1627500,
            "monthly_income": 120000,
            "monthly_expenses": 64000,
            "monthly_savings": 56000,
            "savings_rate_pct": 46.7,
            "debt_to_income_ratio": 0.20,
            "emergency_fund_months": 4.8,
            "predictions": predictions,
            "emotional_state": "Financially Confident",
            "risk_tolerance": "moderate",
        },
    }


@router.get("/assets", summary="Get asset breakdown")
async def get_twin_assets(current_user: CurrentUser) -> Dict[str, Any]:
    """
    Retrieve the asset breakdown of the Living Financial Twin.
    Includes savings, investments, real estate, gold, and liabilities.
    """
    assets: List[Dict[str, Any]] = [
        {
            "category": "Mutual Funds",
            "icon": "📈",
            "value": 828000,
            "change_pct": 18.4,
            "color": "#00FF9D",
        },
        {
            "category": "Fixed Deposits",
            "icon": "🏦",
            "value": 400000,
            "change_pct": 7.1,
            "color": "#00F5FF",
        },
        {
            "category": "Savings Account",
            "icon": "💰",
            "value": 421500,
            "change_pct": 2.1,
            "color": "#8A2BE2",
        },
        {
            "category": "Stocks",
            "icon": "📊",
            "value": 315000,
            "change_pct": 22.8,
            "color": "#FFB800",
        },
        {
            "category": "Gold",
            "icon": "🥇",
            "value": 180000,
            "change_pct": 14.3,
            "color": "#C9A84C",
        },
        {
            "category": "EPF / PPF",
            "icon": "🏛️",
            "value": 283000,
            "change_pct": 8.1,
            "color": "#6366F1",
        },
    ]

    liabilities: List[Dict[str, Any]] = [
        {"category": "Home Loan", "value": 1500000, "emi": 24500, "remaining_months": 192},
        {"category": "Car Loan", "value": 350000, "emi": 9800, "remaining_months": 36},
    ]

    total_assets = sum(a["value"] for a in assets)
    total_liabilities = sum(l["value"] for l in liabilities)

    return {
        "status": "success",
        "customer_id": str(current_user.id),
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "net_worth": total_assets - total_liabilities,
        "assets": assets,
        "liabilities": liabilities,
    }


@router.get("/predictions", summary="Get AI-driven future predictions")
async def get_twin_predictions(current_user: CurrentUser) -> Dict[str, Any]:
    """
    Retrieve AI-driven future predictions for the Living Financial Twin.
    Includes net worth projections, retirement age prediction, and goal achievement probability.
    """
    predictions = await twin_engine.generate_predictions({})

    return {
        "status": "success",
        "customer_id": str(current_user.id),
        "predictions": {
            **predictions,
            "retirement_savings_gap": 14200000,
            "goal_achievement_probability": 0.82,
            "recommended_sip_increase": 5000,
            "scenarios": [
                {
                    "name": "Current Path",
                    "net_worth_5y": predictions["net_worth_5y"],
                    "retirement_age": predictions["retirement_age_current_path"],
                    "color": "#00F5FF",
                },
                {
                    "name": "Optimized Path",
                    "net_worth_5y": int(predictions["net_worth_5y"] * 1.35),
                    "retirement_age": 52,
                    "color": "#00FF9D",
                    "action": "Increase SIP by ₹5,000/month",
                },
                {
                    "name": "Conservative Path",
                    "net_worth_5y": int(predictions["net_worth_5y"] * 0.7),
                    "retirement_age": 64,
                    "color": "#FFB800",
                    "action": "Reduce spending by 20%",
                },
            ],
        },
    }
