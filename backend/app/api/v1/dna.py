from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict, Any, List

from app.services.dna_engine import DNAEngine
from app.api.deps import CurrentUser

router = APIRouter()
dna_engine = DNAEngine()


@router.get(
    "/",
    summary="Get current Financial DNA profile",
    response_description="The user's complete Financial DNA scores and personality type",
)
async def get_current_dna(current_user: CurrentUser) -> Dict[str, Any]:
    """
    Retrieve the current Financial DNA profile for the authenticated user.
    Returns 128-dimension financial personality scores and the computed DNA version.
    """
    dna = await dna_engine.compute_dna(
        customer_id=str(current_user.id),
        historical_transactions=[],  # In production: fetched from DB
    )
    return {"status": "success", "data": dna}


@router.post(
    "/recompute",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger async Financial DNA recomputation",
)
async def recompute_dna(
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
) -> Dict[str, Any]:
    """
    Trigger an asynchronous recomputation of the Financial DNA.
    Returns 202 Accepted immediately — computation runs in the background.
    The result will be available via GET /dna/ after processing.
    """
    async def _recompute():
        await dna_engine.compute_dna(
            customer_id=str(current_user.id),
            historical_transactions=[],  # In production: fetched from DB
        )

    background_tasks.add_task(_recompute)

    return {
        "status": "accepted",
        "message": "DNA recomputation has been scheduled.",
        "customer_id": str(current_user.id),
    }


@router.get(
    "/evolution",
    summary="Get historical DNA score evolution",
)
async def get_dna_evolution(current_user: CurrentUser) -> Dict[str, Any]:
    """
    Retrieve the historical evolution of Financial DNA scores over time.
    Shows how saving_dna, investment_dna, risk_dna etc. have changed month-by-month.
    """
    # Simulated evolution data (production: query MongoDB time-series collection)
    evolution: List[Dict[str, Any]] = [
        {
            "month": "2026-01",
            "overall_score": 68,
            "saving_dna": 72,
            "investment_dna": 60,
            "risk_dna": 50,
            "discipline_score": 74,
        },
        {
            "month": "2026-02",
            "overall_score": 71,
            "saving_dna": 76,
            "investment_dna": 63,
            "risk_dna": 52,
            "discipline_score": 78,
        },
        {
            "month": "2026-03",
            "overall_score": 74,
            "saving_dna": 80,
            "investment_dna": 68,
            "risk_dna": 54,
            "discipline_score": 82,
        },
        {
            "month": "2026-04",
            "overall_score": 77,
            "saving_dna": 84,
            "investment_dna": 72,
            "risk_dna": 55,
            "discipline_score": 85,
        },
        {
            "month": "2026-05",
            "overall_score": 80,
            "saving_dna": 88,
            "investment_dna": 75,
            "risk_dna": 56,
            "discipline_score": 87,
        },
        {
            "month": "2026-06",
            "overall_score": 82,
            "saving_dna": 90,
            "investment_dna": 77,
            "risk_dna": 55,
            "discipline_score": 88,
        },
        {
            "month": "2026-07",
            "overall_score": 84,
            "saving_dna": 92,
            "investment_dna": 78,
            "risk_dna": 55,
            "discipline_score": 88,
        },
    ]

    return {
        "status": "success",
        "customer_id": str(current_user.id),
        "evolution": evolution,
        "trend": "improving",
        "improvement_pct": 23.5,
    }
