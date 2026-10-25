from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.db.database import Base

class PaymentStatus(str, enum.Enum):
    PENDING = "Pending"
    PARTIALLY_PAID = "Partially Paid"
    PAID = "Paid"
    OVERDUE = "Overdue"

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(String, nullable=False) # Advance, Milestone, etc.
    expected_date = Column(Date, nullable=False)
    actual_date = Column(Date, nullable=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    reference = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="payments")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    category = Column(String, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    expense_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="expenses")

# Add agreed amount to Project for financial tracking
# We'll need a migration for this
