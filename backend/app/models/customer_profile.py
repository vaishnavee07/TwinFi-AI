import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, Boolean, DateTime, ForeignKey, Index, Uuid, JSON
from sqlalchemy.orm import relationship
from app.database.postgres import Base


class CustomerProfile(Base):
    """Extended profile for bank customers — stores financial metadata and Twin state."""

    __tablename__ = "customer_profiles"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Personal Details
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime(timezone=True), nullable=True)
    pan_number = Column(String(10), nullable=True)  # Encrypted in production
    aadhaar_hash = Column(String(255), nullable=True)  # Hashed, never stored plain

    # Financial Snapshot
    annual_income = Column(Numeric(15, 2), nullable=True)
    risk_profile = Column(String(30), default="moderate")  # conservative, moderate, aggressive
    credit_score = Column(Numeric(5, 0), nullable=True)

    # Financial DNA (stored as JSON for flexibility)
    dna_scores = Column(JSON, default=dict)
    dna_version = Column(Numeric(5, 0), default=0)
    dna_computed_at = Column(DateTime(timezone=True), nullable=True)
    dna_personality_type = Column(String(100), nullable=True)

    # Living Twin State
    twin_health_score = Column(Numeric(5, 2), nullable=True)
    twin_last_synced = Column(DateTime(timezone=True), nullable=True)
    twin_state_json = Column(JSON, default=dict)  # Full twin state snapshot

    # Relationships
    rm_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)
    customer_segment = Column(String(50), default="retail")  # retail, premium, hni

    # KYC & Compliance
    kyc_status = Column(String(30), default="pending")  # pending, verified, rejected
    onboarding_completed = Column(Boolean, default=False)

    # Preferences
    notification_preferences = Column(JSON, default=dict)
    language = Column(String(10), default="en")

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="customer_profile", foreign_keys=[user_id])
    bank_accounts = relationship("BankAccount", back_populates="customer", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="customer")

    __table_args__ = (
        Index("idx_customer_rm", rm_id),
        Index("idx_customer_segment", customer_segment),
        Index("idx_customer_kyc", kyc_status),
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
