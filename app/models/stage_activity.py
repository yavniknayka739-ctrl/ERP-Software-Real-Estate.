from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.db.database import Base

class StageStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class ActivityStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class ActivityTemplate(Base):
    __tablename__ = "activity_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

class ProjectStage(Base):
    __tablename__ = "project_stages"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(Enum(StageStatus), default=StageStatus.PENDING, nullable=False)
    start_date = Column(Date, nullable=True)
    completion_date = Column(Date, nullable=True)

    project = relationship("Project", back_populates="stages")
    activities = relationship("Activity", back_populates="stage", cascade="all, delete-orphan")

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    stage_id = Column(Integer, ForeignKey("project_stages.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(ActivityStatus), default=ActivityStatus.PENDING, nullable=False)
    completion_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    stage = relationship("ProjectStage", back_populates="activities")
    assignee = relationship("User")
    history = relationship("ActivityHistory", back_populates="activity", cascade="all, delete-orphan")

class ActivityHistory(Base):
    __tablename__ = "activity_history"
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    changed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    old_status = Column(String, nullable=True)
    new_status = Column(String, nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    activity = relationship("Activity", back_populates="history")
    user = relationship("User")
