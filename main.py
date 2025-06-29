"""
FastAPI Blood Test Analysis System with Queue Worker Model and Database Integration
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import uuid
import hashlib
from datetime import datetime
from typing import Optional, List

# Database and queue imports
from database import (
    get_db, create_tables, create_analysis_record, get_analysis_by_id, 
    get_user_analyses, AnalysisResult as DBAnalysisResult
)
from worker_tasks import process_blood_test_analysis, get_analysis_status, calculate_file_hash
from celery_app import celery_app

# Pydantic models for API responses
from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    """Model for analysis request response"""
    analysis_id: str
    task_id: str
    status: str
    message: str
    estimated_completion_time: Optional[str] = None

class AnalysisStatus(BaseModel):
    """Model for analysis status response"""
    analysis_id: str
    status: str
    created_at: str
    query: str
    original_filename: str
    completed_at: Optional[str] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None

class AnalysisResult(BaseModel):
    """Model for analysis result response"""
    analysis_id: str
    status: str
    query: str
    original_filename: str
    summary: Optional[str] = None
    doctor_analysis: Optional[str] = None
    nutrition_analysis: Optional[str] = None
    exercise_analysis: Optional[str] = None
    verification_analysis: Optional[str] = None
    processing_time: Optional[float] = None
    completed_at: Optional[str] = None
    report_file_path: Optional[str] = None
    disclaimer: str

# Initialize FastAPI app
app = FastAPI(
    title="Blood Test Report Analyser - Queue System", 
    description="Advanced blood test analysis system with concurrent processing and database storage",
    version="2.0.0"
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables"""
    create_tables()
    print("Database tables initialized")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Blood Test Report Analyser API v2.0 is running",
        "features": ["Queue Worker Model", "Database Integration", "Concurrent Processing"],
        "endpoints": {
            "submit_analysis": "/analyze",
            "check_status": "/status/{analysis_id}",
            "get_results": "/results/{analysis_id}",
            "list_analyses": "/analyses",
            "queue_status": "/queue/status"
        }
    }

@app.post("/analyze", response_model=AnalysisRequest)
async def queue_blood_test_analysis(
    file: UploadFile = File(...),
    query: str = Form(default="Summarise my Blood Test Report"),
    user_id: Optional[str] = Form(default=None),
    db: Session = Depends(get_db)
):
    """
    Queue blood test analysis for background processing
    
    Returns analysis_id and task_id for tracking progress
    """
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Read file content
    content = await file.read()
    
    # Check file size (10MB limit)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")
    
    # Check if file is empty
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    
    # Calculate file hash for duplicate detection
    file_hash = calculate_file_hash(content)
    
    # Check for recent duplicate analysis (within last 24 hours)
    from datetime import timedelta
    recent_cutoff = datetime.utcnow() - timedelta(hours=24)
    existing_analysis = db.query(DBAnalysisResult).filter(
        DBAnalysisResult.file_hash == file_hash,
        DBAnalysisResult.created_at > recent_cutoff,
        DBAnalysisResult.status == "completed"
    ).first()
    
    if existing_analysis:
        return AnalysisRequest(
            analysis_id=existing_analysis.id,
            task_id="cached",
            status="completed",
            message="Analysis already exists for this file. Returning cached results.",
            estimated_completion_time=None
        )
    
    # Generate unique file ID and path
    file_id = str(uuid.uuid4())
    file_path = f"data/blood_test_report_{file_id}.pdf"
    
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save uploaded file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Validate query
        if not query or query.strip() == "":
            query = "Summarise my Blood Test Report"
        
        # Create analysis record in database
        analysis = create_analysis_record(
            db=db,
            user_id=user_id,
            original_filename=file.filename,
            file_size=len(content),
            file_hash=file_hash,
            query=query.strip()
        )
        
        # Queue the analysis task
        task = process_blood_test_analysis.delay(
            analysis_id=analysis.id,
            file_path=file_path,
            query=query.strip()
        )
        
        return AnalysisRequest(
            analysis_id=analysis.id,
            task_id=task.id,
            status="queued",
            message="Analysis has been queued for processing. Use the analysis_id to check status.",
            estimated_completion_time="2-5 minutes"
        )
        
    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Error queuing analysis: {str(e)}")

@app.get("/status/{analysis_id}", response_model=AnalysisStatus)
async def get_analysis_status(analysis_id: str, db: Session = Depends(get_db)):
    """
    Get the current status of an analysis
    """
    analysis = get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    status_data = {
        "analysis_id": analysis.id,
        "status": analysis.status,
        "created_at": analysis.created_at.isoformat(),
        "query": analysis.query,
        "original_filename": analysis.original_filename
    }
    
    if analysis.completed_at:
        status_data["completed_at"] = analysis.completed_at.isoformat()
    
    if analysis.processing_time:
        status_data["processing_time"] = analysis.processing_time
    
    if analysis.error_message:
        status_data["error_message"] = analysis.error_message
    
    return AnalysisStatus(**status_data)

@app.get("/results/{analysis_id}", response_model=AnalysisResult)
async def get_analysis_results(analysis_id: str, db: Session = Depends(get_db)):
    """
    Get the complete results of an analysis
    """
    analysis = get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.status != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Analysis not completed yet. Current status: {analysis.status}"
        )
    
    # Check if a formatted report file exists
    report_file_path = None
    if analysis.completed_at:
        # Look for the report file in outputs directory
        import glob
        pattern = f"outputs/blood_test_analysis_report_{analysis.id}_*.txt"
        matching_files = glob.glob(pattern)
        if matching_files:
            # Get the most recent file if multiple exist
            report_file_path = max(matching_files, key=os.path.getctime)
    
    result_data = {
        "analysis_id": analysis.id,
        "status": analysis.status,
        "query": analysis.query,
        "original_filename": analysis.original_filename,
        "summary": analysis.summary,
        "doctor_analysis": analysis.doctor_analysis,
        "nutrition_analysis": analysis.nutrition_analysis,
        "exercise_analysis": analysis.exercise_analysis,
        "verification_analysis": analysis.verification_analysis,
        "processing_time": analysis.processing_time,
        "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
        "report_file_path": report_file_path,
        "disclaimer": "🏥 MEDICAL DISCLAIMER: This analysis is for educational purposes only and does not constitute medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers for medical decisions based on your specific health conditions and circumstances."
    }
    
    return AnalysisResult(**result_data)

@app.get("/analyses")
async def list_analyses(
    user_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    List analyses (optionally filtered by user_id)
    """
    if user_id:
        analyses = get_user_analyses(db, user_id, skip, limit)
    else:
        # Get all analyses (for admin or anonymous users)
        analyses = db.query(DBAnalysisResult).offset(skip).limit(limit).all()
    
    return {
        "analyses": [
            {
                "analysis_id": analysis.id,
                "status": analysis.status,
                "original_filename": analysis.original_filename,
                "query": analysis.query,
                "created_at": analysis.created_at.isoformat(),
                "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
                "processing_time": analysis.processing_time
            }
            for analysis in analyses
        ],
        "total": len(analyses),
        "skip": skip,
        "limit": limit
    }

@app.get("/queue/status")
async def get_queue_status():
    """
    Get current queue status and worker information
    """
    try:
        # Get active tasks
        active_tasks = celery_app.control.inspect().active()
        
        # Get queue lengths
        queue_info = celery_app.control.inspect().reserved()
        
        # Get worker stats
        worker_stats = celery_app.control.inspect().stats()
        
        return {
            "active_tasks": active_tasks,
            "queue_info": queue_info,
            "worker_stats": worker_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "error": f"Could not retrieve queue status: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/download/{analysis_id}")
async def download_report(analysis_id: str, db: Session = Depends(get_db)):
    """
    Download the formatted report file for an analysis
    """
    analysis = get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.status != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Analysis not completed yet. Current status: {analysis.status}"
        )
    
    # Look for the report file
    import glob
    pattern = f"outputs/blood_test_analysis_report_{analysis_id}_*.txt"
    matching_files = glob.glob(pattern)
    
    if not matching_files:
        raise HTTPException(status_code=404, detail="Report file not found")
    
    # Get the most recent file if multiple exist
    report_file_path = max(matching_files, key=os.path.getctime)
    
    if not os.path.exists(report_file_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    from fastapi.responses import FileResponse
    filename = f"blood_test_analysis_{analysis_id}.txt"
    
    return FileResponse(
        path=report_file_path,
        filename=filename,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.delete("/analysis/{analysis_id}")
async def delete_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """
    Delete an analysis record and its associated data
    """
    analysis = get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Clean up any associated files
    potential_file_paths = [
        f"data/blood_test_report_{analysis_id}.pdf",
        f"uploads/blood_test_report_{analysis_id}.pdf"
    ]
    
    # Also clean up report files
    import glob
    report_pattern = f"outputs/blood_test_analysis_report_{analysis_id}_*.txt"
    report_files = glob.glob(report_pattern)
    potential_file_paths.extend(report_files)
    
    for file_path in potential_file_paths:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
    
    # Delete from database
    db.delete(analysis)
    db.commit()
    
    return {"message": f"Analysis {analysis_id} deleted successfully"}

# Legacy endpoint for backward compatibility
@app.post("/analyze_sync")
async def analyze_blood_report_sync(
    file: UploadFile = File(...),
    query: str = Form(default="Summarise my Blood Test Report"),
    db: Session = Depends(get_db)
):
    """
    Legacy synchronous analysis endpoint (for backward compatibility)
    
    This endpoint processes the analysis immediately and returns results.
    For production use, prefer the queued /analyze endpoint.
    """
    # Queue the analysis
    analysis_request = await queue_blood_test_analysis(file, query, None, db)
    
    # If it's a cached result, return immediately
    if analysis_request.task_id == "cached":
        analysis = get_analysis_by_id(db, analysis_request.analysis_id)
        return {
            "status": "success",
            "query": query,
            "analysis": analysis.analysis_json,
            "file_processed": file.filename,
            "disclaimer": "🏥 MEDICAL DISCLAIMER: This analysis is for educational purposes only and does not constitute medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers for medical decisions based on your specific health conditions and circumstances."
        }
    
    # For new analyses, return the queue information
    return {
        "status": "queued",
        "message": "Analysis queued for processing",
        "analysis_id": analysis_request.analysis_id,
        "task_id": analysis_request.task_id,
        "check_status_url": f"/status/{analysis_request.analysis_id}",
        "get_results_url": f"/results/{analysis_request.analysis_id}",
        "disclaimer": "🏥 MEDICAL DISCLAIMER: This analysis is for educational purposes only and does not constitute medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers for medical decisions based on your specific health conditions and circumstances."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)