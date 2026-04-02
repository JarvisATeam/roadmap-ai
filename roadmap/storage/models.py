"""SQLAlchemy models for roadmap storage."""
import enum
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utc_now():
    """Return timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class MissionStatus(enum.Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"


class StepStatus(enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class Mission(Base):
    __tablename__ = "missions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(20), default=MissionStatus.PLANNED.value)

    created_at = Column(DateTime(timezone=True), default=utc_now)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    milestones = relationship("Milestone", back_populates="mission", cascade="all, delete-orphan")


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    mission_id = Column(String(36), ForeignKey("missions.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order = Column(Integer, nullable=False)
    status = Column(String(20), default=MissionStatus.PLANNED.value)

    created_at = Column(DateTime(timezone=True), default=utc_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    mission = relationship("Mission", back_populates="milestones")
    steps = relationship("Step", back_populates="milestone", cascade="all, delete-orphan")


class Step(Base):
    __tablename__ = "steps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    milestone_id = Column(String(36), ForeignKey("milestones.id"), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default=StepStatus.TODO.value)
    priority = Column(Integer, default=3)
    due_date = Column(DateTime(timezone=True), nullable=True)
    tags = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    milestone = relationship("Milestone", back_populates="steps")
    blockers = relationship("Blocker", back_populates="step", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="step", cascade="all, delete-orphan")
    check_ins = relationship("CheckIn", back_populates="step", cascade="all, delete-orphan")
    recovery = relationship("Recovery", back_populates="step", cascade="all, delete-orphan")


class Blocker(Base):
    __tablename__ = "blockers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    step_id = Column(String(36), ForeignKey("steps.id"), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default="active")
    resolution_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    step = relationship("Step", back_populates="blockers")


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    step_id = Column(String(36), ForeignKey("steps.id"), nullable=False)
    context = Column(Text, nullable=False)
    decision = Column(Text, nullable=False)
    alternatives = Column(Text, nullable=True)
    reasoning = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now)

    step = relationship("Step", back_populates="decisions")


class CheckIn(Base):
    __tablename__ = "check_ins"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    step_id = Column(String(36), ForeignKey("steps.id"), nullable=False)
    notes = Column(Text, nullable=False)
    progress_pct = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now)

    step = relationship("Step", back_populates="check_ins")


class Recovery(Base):
    __tablename__ = "recovery"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    step_id = Column(String(36), ForeignKey("steps.id"), nullable=False)
    incident = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=True)
    corrective_action = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    step = relationship("Step", back_populates="recovery")
