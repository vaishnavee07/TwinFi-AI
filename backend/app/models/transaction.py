import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, Boolean, DateTime, ForeignKey, Index, Uuid, JSON
from sqlalchemy.orm import relationship
from app.database.postgres import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(Uuid(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=False)
    customer_id = Column(Uuid(as_uuid=True), ForeignKey("customer_profiles.id"), nullable=False)

    reference_number = Column(String(50), unique=True, nullable=False)
    transaction_type = Column(String(50), nullable=False)  # debit, credit, transfer, upi, emi
    payment_method = Column(String(50))

    amount = Column(Numeric(15, 2), nullable=False)
    balance_after = Column(Numeric(15, 2))
    currency = Column(String(3), default="INR")

    description = Column(String(500))
    merchant_name = Column(String(200))
    merchant_category = Column(String(100))
    category = Column(String(100))  # AI-classified category
    sub_category = Column(String(100))

    counterparty_account = Column(String(30))
    counterparty_name = Column(String(200))
    upi_id = Column(String(100))

    location_lat = Column(Numeric(10, 8))
    location_lng = Column(Numeric(11, 8))
    device_id = Column(String(255))
    ip_address = Column(String(45))

    status = Column(String(30), default="completed")

    fraud_score = Column(Numeric(5, 4), default=0)
    fraud_flagged = Column(Boolean, default=False)
    is_recurring = Column(Boolean, default=False)

    parent_txn_id = Column(Uuid(as_uuid=True), ForeignKey("transactions.id"))
    tags = Column(JSON, default=list)  # Stored as JSON list for SQLite compatibility
    metadata_json = Column(JSON, default=dict)

    transacted_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    customer = relationship("CustomerProfile", back_populates="transactions", foreign_keys=[customer_id])
    account = relationship("BankAccount", back_populates="transactions", foreign_keys=[account_id])

    __table_args__ = (
        Index("idx_txn_customer_date", customer_id, transacted_at.desc()),
        Index("idx_txn_category", customer_id, category),
    )
