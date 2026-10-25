from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.db.database import Base

class ProjectStatus(str, enum.Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    ON_HOLD = "On Hold"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    mobile = Column(String, nullable=False)
    email = Column(String, nullable=True)
    company = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    projects = relationship("Project", back_populates="client", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)

    req_start_date = Column(Date, nullable=True)
    req_end_date = Column(Date, nullable=True)
    actual_start_date = Column(Date, nullable=True)
    expected_end_date = Column(Date, nullable=True)

    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_team = Column(String, nullable=True)

    status = Column(Enum(ProjectStatus), default=ProjectStatus.NOT_STARTED, nullable=False)

    agreed_amount = Column(Numeric(12, 2), default=0.00)
    payment_terms = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    client = relationship("Client", back_populates="projects")
    manager = relationship("User")
    stages = relationship("ProjectStage", back_populates="project", cascade="all, delete-orphan", order_by="ProjectStage.id")
    payments = relationship("Payment", back_populates="project", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="project", cascade="all, delete-orphan")
