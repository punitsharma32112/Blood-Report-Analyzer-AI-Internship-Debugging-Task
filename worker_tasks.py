"""
Celery worker tasks for Blood Test Analysis System
"""
import os
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session

from celery import current_task
from celery_app import celery_app
from database import SessionLocal, get_analysis_by_id, update_analysis_result, mark_analysis_failed, AnalysisResult
from crewai import Crew, Process
from agents import doctor, verifier, nutritionist, exercise_specialist
from task import help_patients, nutrition_analysis, exercise_planning, verification
from tools import BloodTestReportTool

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_blood_test_analysis(self, analysis_id: str, file_path: str, query: str) -> Dict[str, Any]:
    """
    Background task to process blood test analysis using CrewAI
    
    Args:
        analysis_id: Database ID of the analysis record
        file_path: Path to the uploaded PDF file
        query: User's query for the analysis
    
    Returns:
        Dict containing the analysis results
    """
    db = SessionLocal()
    start_time = time.time()
    
    try:
        # Update task status
        current_task.update_state(
            state="PROCESSING",
            meta={"analysis_id": analysis_id, "started_at": datetime.utcnow().isoformat()}
        )
        
        # Get analysis record from database
        analysis = get_analysis_by_id(db, analysis_id)
        if not analysis:
            raise ValueError(f"Analysis record not found: {analysis_id}")
        
        # Update analysis status to processing
        analysis.status = "processing"
        db.commit()
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Analysis file not found: {file_path}")
        
        # Set the file path in the tool for fallback usage
        BloodTestReportTool.set_current_file_path(file_path)
        
        # Create medical crew for analysis
        medical_crew = Crew(
            agents=[verifier, doctor, nutritionist, exercise_specialist],
            tasks=[verification, help_patients, nutrition_analysis, exercise_planning],
            process=Process.sequential,
            verbose=True,
            max_rpm=25
        )
        
        # Run the analysis
        crew_result = medical_crew.kickoff({'query': query, 'file_path': file_path})
        
        # Parse individual results if available
        individual_results = {}
        if hasattr(crew_result, 'tasks_output') and crew_result.tasks_output:
            for i, task_output in enumerate(crew_result.tasks_output):
                task_names = ['verification', 'doctor_analysis', 'nutrition_analysis', 'exercise_analysis']
                if i < len(task_names):
                    individual_results[task_names[i]] = str(task_output)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Prepare results
        analysis_data = {
            "analysis_id": analysis_id,
            "query": query,
            "full_result": str(crew_result),
            "individual_results": individual_results,
            "processing_time": processing_time,
            "completed_at": datetime.utcnow().isoformat(),
            "status": "completed"
        }
        
        # Create summary
        summary = f"Blood test analysis completed in {processing_time:.2f} seconds. "
        if individual_results:
            summary += f"Analysis includes {len(individual_results)} specialist evaluations."
        
        # Update database with results
        update_analysis_result(
            db=db,
            analysis_id=analysis_id,
            analysis_json=json.dumps(analysis_data),
            summary=summary,
            doctor_analysis=individual_results.get('doctor_analysis'),
            nutrition_analysis=individual_results.get('nutrition_analysis'),
            exercise_analysis=individual_results.get('exercise_analysis'),
            verification_analysis=individual_results.get('verification'),
            processing_time=processing_time,
            status="completed"
        )
        
        # Generate and save formatted report to outputs directory
        try:
            report_content = generate_formatted_report(analysis_data, individual_results, analysis.original_filename if analysis else "unknown")
            report_filename = f"blood_test_analysis_report_{analysis_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
            report_path = os.path.join("outputs", report_filename)
            
            # Ensure outputs directory exists
            os.makedirs("outputs", exist_ok=True)
            
            # Save the formatted report
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"✅ Formatted report saved to: {report_path}")
            
        except Exception as report_error:
            print(f"Warning: Could not save formatted report: {report_error}")
        
        # Clean up file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as cleanup_error:
            print(f"Warning: Could not clean up file {file_path}: {cleanup_error}")
        
        return analysis_data
        
    except Exception as exc:
        # Handle errors
        error_message = f"Analysis failed: {str(exc)}"
        processing_time = time.time() - start_time
        
        # Update database with error
        mark_analysis_failed(db, analysis_id, error_message)
        
        # Clean up file on error
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        
        # Retry logic
        if self.request.retries < self.max_retries:
            print(f"Task failed, retrying... Attempt {self.request.retries + 1}")
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        # Update task state
        current_task.update_state(
            state="FAILURE",
            meta={
                "analysis_id": analysis_id,
                "error": error_message,
                "processing_time": processing_time
            }
        )
        
        raise exc
        
    finally:
        db.close()

@celery_app.task
def cleanup_old_results():
    """
    Periodic task to clean up old analysis results and files
    """
    db = SessionLocal()
    try:
        # Clean up results older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        old_analyses = db.query(AnalysisResult).filter(
            AnalysisResult.created_at < cutoff_date
        ).all()
        
        for analysis in old_analyses:
            # Remove any associated files
            potential_file_paths = [
                f"data/blood_test_report_{analysis.id}.pdf",
                f"uploads/blood_test_report_{analysis.id}.pdf"
            ]
            
            for file_path in potential_file_paths:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
            
            # Delete from database
            db.delete(analysis)
        
        db.commit()
        
        return {
            "cleaned_up": len(old_analyses),
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()

@celery_app.task
def get_analysis_status(analysis_id: str) -> Dict[str, Any]:
    """
    Get the current status of an analysis
    
    Args:
        analysis_id: Database ID of the analysis record
    
    Returns:
        Dict containing the analysis status and results if available
    """
    db = SessionLocal()
    try:
        analysis = get_analysis_by_id(db, analysis_id)
        if not analysis:
            return {"error": "Analysis not found"}
        
        result = {
            "analysis_id": analysis.id,
            "status": analysis.status,
            "created_at": analysis.created_at.isoformat(),
            "query": analysis.query,
            "original_filename": analysis.original_filename
        }
        
        if analysis.completed_at:
            result["completed_at"] = analysis.completed_at.isoformat()
        
        if analysis.processing_time:
            result["processing_time"] = analysis.processing_time
        
        if analysis.status == "completed" and analysis.analysis_json:
            try:
                analysis_data = json.loads(analysis.analysis_json)
                result["results"] = analysis_data
            except json.JSONDecodeError:
                result["results"] = {"raw": analysis.analysis_json}
        
        if analysis.error_message:
            result["error_message"] = analysis.error_message
        
        return result
        
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        db.close()

def calculate_file_hash(file_content: bytes) -> str:
    """Calculate SHA-256 hash of file content for duplicate detection"""
    return hashlib.sha256(file_content).hexdigest()

def generate_formatted_report(analysis_data: Dict[str, Any], individual_results: Dict[str, str], original_filename: str) -> str:
    """
    Generate a beautifully formatted report for the blood test analysis
    
    Args:
        analysis_data: Complete analysis data
        individual_results: Individual specialist analyses
        original_filename: Name of the original uploaded file
    
    Returns:
        Formatted report as a string
    """
    report_lines = []
    
    # Header
    report_lines.extend([
        "=" * 80,
        "🩸 COMPREHENSIVE BLOOD TEST ANALYSIS REPORT 🩸",
        "=" * 80,
        "",
        f"📋 Analysis ID: {analysis_data.get('analysis_id', 'N/A')}",
        f"📄 Original File: {original_filename}",
        f"🕐 Completed: {analysis_data.get('completed_at', 'N/A')}",
        f"⏱️  Processing Time: {analysis_data.get('processing_time', 0):.2f} seconds",
        f"❓ Query: {analysis_data.get('query', 'N/A')}",
        "",
        "🏥 MEDICAL DISCLAIMER:",
        "-" * 40,
        "This analysis is for educational purposes only and does not constitute",
        "medical advice, diagnosis, or treatment. Always consult with qualified",
        "healthcare providers for medical decisions based on your specific health",
        "conditions and circumstances.",
        "",
        "=" * 80,
        ""
    ])
    
    # Document Verification Section
    if 'verification' in individual_results:
        report_lines.extend([
            "🔍 DOCUMENT VERIFICATION ANALYSIS",
            "=" * 50,
            "",
            individual_results['verification'],
            "",
            "=" * 80,
            ""
        ])
    
    # Doctor Analysis Section
    if 'doctor_analysis' in individual_results:
        report_lines.extend([
            "👨‍⚕️ MEDICAL ANALYSIS",
            "=" * 50,
            "",
            individual_results['doctor_analysis'],
            "",
            "=" * 80,
            ""
        ])
    
    # Nutrition Analysis Section
    if 'nutrition_analysis' in individual_results:
        report_lines.extend([
            "🥗 NUTRITION ANALYSIS & RECOMMENDATIONS",
            "=" * 50,
            "",
            individual_results['nutrition_analysis'],
            "",
            "=" * 80,
            ""
        ])
    
    # Exercise Analysis Section
    if 'exercise_analysis' in individual_results:
        report_lines.extend([
            "🏃‍♂️ EXERCISE RECOMMENDATIONS",
            "=" * 50,
            "",
            individual_results['exercise_analysis'],
            "",
            "=" * 80,
            ""
        ])
    
    # Summary Section
    report_lines.extend([
        "📊 ANALYSIS SUMMARY",
        "=" * 50,
        "",
        f"✅ Status: Analysis Completed Successfully",
        f"📈 Specialist Evaluations: {len(individual_results)} reports generated",
        f"🔬 Analysis Quality: Comprehensive multi-specialist review",
        f"⚡ Performance: Processed in {analysis_data.get('processing_time', 0):.2f} seconds",
        "",
        "🎯 KEY RECOMMENDATIONS:",
        "• Consult with your healthcare provider to discuss these results",
        "• Follow up on any values outside normal reference ranges",
        "• Consider lifestyle modifications as recommended by specialists",
        "• Schedule regular health check-ups for monitoring",
        "",
        "=" * 80,
        "",
        "📞 NEXT STEPS:",
        "1. Share this report with your healthcare provider",
        "2. Discuss any concerning values or recommendations",
        "3. Follow medical advice for any required follow-up tests",
        "4. Implement lifestyle changes as appropriate",
        "",
        "=" * 80,
        "",
        f"🤖 Generated by Blood Test Analysis System v1.0",
        f"📅 Report Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        "",
        "Thank you for using our Blood Test Analysis System! 🙏",
        "=" * 80
    ])
    
    return "\n".join(report_lines)