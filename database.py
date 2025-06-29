"""
Database configuration and models for Blood Test Analysis System
"""
import os
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blood_test_analysis.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    """User model for storing user information"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to analysis results
    analyses = relationship("AnalysisResult", back_populates="user")

class AnalysisResult(Base):
    """Model for storing blood test analysis results"""
    __tablename__ = "analysis_results"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Nullable for anonymous users
    
    # File information
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String, nullable=False)  # For duplicate detection
    
    # Analysis request
    query = Column(Text, nullable=False)
    
    # Analysis results
    analysis_json = Column(Text, nullable=False)  # JSON string of full analysis
    summary = Column(Text, nullable=False)
    
    # Individual specialist results
    doctor_analysis = Column(Text, nullable=True)
    nutrition_analysis = Column(Text, nullable=True)
    exercise_analysis = Column(Text, nullable=True)
    verification_analysis = Column(Text, nullable=True)
    
    # Processing information
    status = Column(String, default="pending")  # pending, processing, completed, failed
    processing_time = Column(Float, nullable=True)  # Processing time in seconds
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationship to user
    user = relationship("User", back_populates="analyses")

class JobQueue(Base):
    """Model for tracking background job status"""
    __tablename__ = "job_queue"
    
    id = Column(String, primary_key=True)  # Celery task ID
    analysis_id = Column(String, ForeignKey("analysis_results.id"), nullable=False)
    status = Column(String, default="pending")  # pending, processing, completed, failed, revoked
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

# Database utility functions
def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_analysis_by_id(db: Session, analysis_id: str) -> Optional[AnalysisResult]:
    """Get analysis result by ID"""
    return db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()

def get_user_analyses(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    """Get all analyses for a user"""
    return db.query(AnalysisResult).filter(AnalysisResult.user_id == user_id).offset(skip).limit(limit).all()

def create_analysis_record(
    db: Session,
    user_id: Optional[str],
    original_filename: str,
    file_size: int,
    file_hash: str,
    query: str
) -> AnalysisResult:
    """Create a new analysis record"""
    analysis = AnalysisResult(
        user_id=user_id,
        original_filename=original_filename,
        file_size=file_size,
        file_hash=file_hash,
        query=query,
        analysis_json="",
        summary="",
        status="pending"
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis

def update_analysis_result(
    db: Session,
    analysis_id: str,
    analysis_json: str,
    summary: str,
    doctor_analysis: str = None,
    nutrition_analysis: str = None,
    exercise_analysis: str = None,
    verification_analysis: str = None,
    processing_time: float = None,
    status: str = "completed"
) -> Optional[AnalysisResult]:
    """Update analysis result with completed data"""
    analysis = get_analysis_by_id(db, analysis_id)
    if analysis:
        analysis.analysis_json = analysis_json
        analysis.summary = summary
        analysis.doctor_analysis = doctor_analysis
        analysis.nutrition_analysis = nutrition_analysis
        analysis.exercise_analysis = exercise_analysis
        analysis.verification_analysis = verification_analysis
        analysis.processing_time = processing_time
        analysis.status = status
        analysis.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(analysis)
    return analysis

def mark_analysis_failed(db: Session, analysis_id: str, error_message: str) -> Optional[AnalysisResult]:
    """Mark analysis as failed with error message"""
    analysis = get_analysis_by_id(db, analysis_id)
    if analysis:
        analysis.status = "failed"
        analysis.error_message = error_message
        analysis.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(analysis)
    return analysis 