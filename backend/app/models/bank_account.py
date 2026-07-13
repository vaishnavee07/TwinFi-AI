import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, Boolean, DateTime, ForeignKey, Index, Uuid, JSON
from sqlalchemy.orm import relationship
from app.database.postgres import Base


class BankAccount(Base):
    """Represents a customer's bank account (savings, current, FD, loan)."""

    __tablename__ = "bank_accounts"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("customer_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Account Details
    account_number = Column(String(30), unique=True, nullable=False)
    ifsc_code = Column(String(11), nullable=True)
    account_type = Column(String(30), nullable=False)  # savings, current, fd, loan, rd
    account_name = Column(String(200), nullable=True)  # "IDBI Bank Savings Account"

    # Balance
    current_balance = Column(Numeric(15, 2), default=0)
    available_balance = Column(Numeric(15, 2), default=0)
    currency = Column(String(3), default="INR")

    # Status & Metadata
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    linked_upi_ids = Column(JSON, default=list)  # ["arjun@idbi", "9876543210@idbi"]

    # For Loan / FD accounts
    interest_rate = Column(Numeric(5, 2), nullable=True)
    maturity_date = Column(DateTime(timezone=True), nullable=True)
    emi_amount = Column(Numeric(12, 2), nullable=True)

    opened_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    customer = relationship("CustomerProfile", back_populates="bank_accounts")
    transactions = relationship("Transaction", back_populates="account")

    __table_args__ = (
        Index("idx_account_customer", customer_id),
        Index("idx_account_type", account_type),
    )
