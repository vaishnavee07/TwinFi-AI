import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.database.postgres import get_db
from app.models.transaction import Transaction
from app.services.fraud_detector import FraudDetector

router = APIRouter()
fraud_detector = FraudDetector()


# ── Schemas ──────────────────────────────────────────────────────────────────
class TransactionCreate(BaseModel):
    account_id: str = Field(..., description="Bank account UUID")
    amount: float = Field(..., gt=0, description="Transaction amount in INR")
    transaction_type: str = Field(..., description="debit | credit | transfer | upi | emi")
    description: Optional[str] = Field(None, max_length=500)
    merchant_name: Optional[str] = Field(None, max_length=200)
    merchant_category: Optional[str] = None
    payment_method: Optional[str] = None
    upi_id: Optional[str] = None


class TransactionResponse(BaseModel):
    id: str
    reference_number: str
    amount: float
    transaction_type: str
    description: Optional[str]
    merchant_name: Optional[str]
    category: Optional[str]
    fraud_score: float
    fraud_flagged: bool
    transacted_at: str
    status: str

    class Config:
        from_attributes = True


class PaginatedTransactions(BaseModel):
    items: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int


# ── Endpoints ────────────────────────────────────────────────────────────────
@router.get(
    "/",
    response_model=PaginatedTransactions,
    summary="List transactions with filtering and pagination",
)
async def list_transactions(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by AI category"),
    transaction_type: Optional[str] = Query(None, description="Filter by type (debit/credit/upi)"),
    fraud_only: bool = Query(False, description="Show only flagged transactions"),
    sort_by: str = Query("transacted_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
) -> PaginatedTransactions:
    """
    List the authenticated user's transactions with full filtering, sorting, and pagination.
    """
    # Build base query
    query = select(Transaction).where(Transaction.customer_id == current_user.id)

    # Apply filters
    if category:
        query = query.where(Transaction.category == category)
    if transaction_type:
        query = query.where(Transaction.transaction_type == transaction_type)
    if fraud_only:
        query = query.where(Transaction.fraud_flagged == True)  # noqa: E712

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply sorting and pagination
    sort_col = getattr(Transaction, sort_by, Transaction.transacted_at)
    if sort_order == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    transactions = result.scalars().all()

    items = [
        {
            "id": str(t.id),
            "reference_number": t.reference_number,
            "amount": float(t.amount),
            "transaction_type": t.transaction_type,
            "description": t.description,
            "merchant_name": t.merchant_name,
            "category": t.category,
            "fraud_score": float(t.fraud_score or 0),
            "fraud_flagged": t.fraud_flagged,
            "transacted_at": t.transacted_at.isoformat() if t.transacted_at else None,
            "status": t.status,
        }
        for t in transactions
    ]

    return PaginatedTransactions(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, -(-total // page_size)),  # ceiling division
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new transaction (with real-time fraud assessment)",
)
async def create_transaction(
    txn_in: TransactionCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Record a new transaction and run real-time fraud assessment.
    The fraud score is computed in < 100ms using the ensemble fraud model.
    If fraud_score > 0.75, the transaction is flagged and blocked.
    """
    # Run fraud assessment
    fraud_result = await fraud_detector.assess_transaction(
        {
            "amount": txn_in.amount,
            "transaction_type": txn_in.transaction_type,
            "merchant_name": txn_in.merchant_name,
            "customer_id": str(current_user.id),
        }
    )

    if fraud_result["flagged"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Transaction blocked: High fraud risk detected.",
                "fraud_score": fraud_result["fraud_score"],
                "explanation": fraud_result["explanation"],
            },
        )

    # Create transaction record
    ref_number = f"TXN{uuid.uuid4().hex[:12].upper()}"
    txn = Transaction(
        id=uuid.uuid4(),
        account_id=uuid.UUID(txn_in.account_id),
        customer_id=current_user.id,
        reference_number=ref_number,
        transaction_type=txn_in.transaction_type,
        amount=txn_in.amount,
        description=txn_in.description,
        merchant_name=txn_in.merchant_name,
        merchant_category=txn_in.merchant_category,
        payment_method=txn_in.payment_method,
        upi_id=txn_in.upi_id,
        fraud_score=fraud_result["fraud_score"],
        fraud_flagged=False,
        transacted_at=datetime.now(timezone.utc),
        status="completed",
    )
    db.add(txn)
    await db.commit()
    await db.refresh(txn)

    return {
        "status": "success",
        "transaction_id": str(txn.id),
        "reference_number": txn.reference_number,
        "fraud_score": fraud_result["fraud_score"],
        "action": fraud_result["action"],
    }


@router.get(
    "/{transaction_id}",
    summary="Get a single transaction by ID",
)
async def get_transaction(
    transaction_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve a specific transaction. Ensures the transaction belongs to the current user."""
    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.id == uuid.UUID(transaction_id),
                Transaction.customer_id == current_user.id,
            )
        )
    )
    txn = result.scalar_one_or_none()

    if not txn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found.",
        )

    return {
        "id": str(txn.id),
        "reference_number": txn.reference_number,
        "amount": float(txn.amount),
        "transaction_type": txn.transaction_type,
        "description": txn.description,
        "merchant_name": txn.merchant_name,
        "category": txn.category,
        "fraud_score": float(txn.fraud_score or 0),
        "fraud_flagged": txn.fraud_flagged,
        "transacted_at": txn.transacted_at.isoformat() if txn.transacted_at else None,
        "status": txn.status,
        "location_lat": float(txn.location_lat) if txn.location_lat else None,
        "location_lng": float(txn.location_lng) if txn.location_lng else None,
    }
