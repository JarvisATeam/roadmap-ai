from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Mission(Base):
    __tablename__ = 'missions'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    target_date = Column(DateTime, nullable=True)
    
    milestones = relationship('Milestone', back_populates='mission', cascade='all, delete-orphan')
    decisions = relationship('Decision', back_populates='mission', cascade='all, delete-orphan')
    checkins = relationship('CheckIn', back_populates='mission', cascade='all, delete-orphan')

class Milestone(Base):
    __tablename__ = 'milestones'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mission_id = Column(String, ForeignKey('missions.id'), nullable=False)
    title = Column(String, nullable=False)
    success_criteria = Column(Text)
    status = Column(String, default='planned')
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    
    mission = relationship('Mission', back_populates='milestones')
    steps = relationship('Step', back_populates='milestone', cascade='all, delete-orphan')
    blockers = relationship('Blocker', back_populates='milestone', cascade='all, delete-orphan')

class Step(Base):
    __tablename__ = 'steps'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    milestone_id = Column(String, ForeignKey('milestones.id'), nullable=False)
    action = Column(String, nullable=False)
    status = Column(String, default='todo')
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    milestone = relationship('Milestone', back_populates='steps')

class Blocker(Base):
    __tablename__ = 'blockers'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    milestone_id = Column(String, ForeignKey('milestones.id'), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    milestone = relationship('Milestone', back_populates='blockers')

class Decision(Base):
    __tablename__ = 'decisions'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mission_id = Column(String, ForeignKey('missions.id'), nullable=False)
    choice = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    alternatives_considered = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    mission = relationship('Mission', back_populates='decisions')

class CheckIn(Base):
    __tablename__ = 'checkins'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mission_id = Column(String, ForeignKey('missions.id'), nullable=False)
    progress_summary = Column(Text, nullable=False)
    blockers_text = Column(Text)
    mood = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    mission = relationship('Mission', back_populates='checkins')

class Recovery(Base):
    __tablename__ = 'recoveries'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mission_id = Column(String, ForeignKey('missions.id'), nullable=False)
    last_session_date = Column(DateTime, nullable=False)
    completed_since_last = Column(Text)
    plan_drift = Column(Text)
    today_focus = Column(Text)
    key_context = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
