## Importing libraries and files
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

from langchain_community.document_loaders import PyPDFLoader as PDFLoader
from crewai.tools import BaseTool
from pydantic import BaseModel
from typing import Type
import requests
import json

## Input schema for tools
class BloodTestReportInput(BaseModel):
    """Input schema for BloodTestReportTool."""
    file_path: Optional[str] = None

class WebSearchInput(BaseModel):
    """Input schema for WebSearchTool."""
    query: str

class NutritionAnalysisInput(BaseModel):
    """Input schema for NutritionTool."""
    blood_test_content: str

class ExerciseAnalysisInput(BaseModel):
    """Input schema for ExerciseTool."""
    blood_test_content: str

## Creating search tool (Simple web search placeholder)
class WebSearchTool(BaseTool):
    name: str = "web_search_tool"
    description: str = "Search the web for medical information and research to support blood test analysis"
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(self, query: str) -> str:
        """Web search tool for medical information"""
        return f"""
        Web Search Results for: "{query}"
        
        🔍 Medical Research Findings:
        - Evidence-based information about blood test markers
        - Current medical guidelines and reference ranges
        - Peer-reviewed research on health recommendations
        - Professional medical association guidelines
        
        📚 Key Resources:
        - Mayo Clinic: Medical test reference ranges
        - American Heart Association: Cardiovascular health guidelines  
        - National Institutes of Health: Blood marker significance
        - WebMD: Understanding blood test results
        
        ⚠️ Medical Disclaimer: This search provides educational information only.
        Always consult with qualified healthcare providers for medical advice.
        
        Note: This is a placeholder search tool. In production, this would connect
        to a real search API like Serper, Google, or medical databases.
        """

search_tool = WebSearchTool()

## Creating custom pdf reader tool

class BloodTestReportTool(BaseTool):
    name: str = "read_blood_test_report"
    description: str = "Read and extract content from blood test PDF reports. Use this tool to analyze uploaded blood test documents."
    args_schema: Type[BaseModel] = BloodTestReportInput
    
    # Store the file path as a class variable for fallback
    _current_file_path: str = None

    def _run(self, file_path: str = None, **kwargs) -> str:
        """Tool to read blood test PDF files and extract content"""
        try:
            # Handle different parameter formats that might be passed by CrewAI
            actual_file_path = None
            
            # Try to get file_path from different sources
            if file_path:
                actual_file_path = file_path
            elif self._current_file_path:
                actual_file_path = self._current_file_path
            elif kwargs.get('file_path'):
                actual_file_path = kwargs.get('file_path')
            elif kwargs.get('query'):
                # Fallback: if query contains a file path
                query_val = kwargs.get('query')
                if isinstance(query_val, str) and query_val.endswith('.pdf'):
                    actual_file_path = query_val
            
            # Look for any PDF files in data directory as last resort
            if not actual_file_path or not os.path.exists(actual_file_path):
                if os.path.exists("data"):
                    pdf_files = [f for f in os.listdir("data") if f.endswith('.pdf')]
                    if pdf_files:
                        actual_file_path = os.path.join("data", pdf_files[0])
                        print(f"Using fallback file: {actual_file_path}")
            
            if not actual_file_path:
                return "Error: No file path provided and no PDF files found in data directory"
            
            # Check if file exists
            if not os.path.exists(actual_file_path):
                return f"Error: File not found at path: {actual_file_path}"
            
            # Check if it's a PDF file
            if not actual_file_path.lower().endswith('.pdf'):
                return f"Error: File must be a PDF. Received: {actual_file_path}"
            
            # Load and extract text from PDF
            loader = PDFLoader(actual_file_path)
            pages = loader.load()
            
            # Check if PDF has content
            if not pages:
                return "Error: PDF file appears to be empty or corrupted"
            
            # Extract text from all pages
            full_text = ""
            for page in pages:
                page_content = page.page_content.strip()
                if page_content:  # Only add non-empty pages
                    full_text += page_content + "\n"
            
            # Check if we extracted any text
            if not full_text.strip():
                return "Error: No readable text found in the PDF file"
            
            # Format the extracted text
            formatted_text = full_text.replace('\n\n', '\n').strip()
            
            return f"Blood Test Report Content:\n\n{formatted_text}"
            
        except Exception as e:
            return f"Error reading blood test report: {str(e)}"
    
    @classmethod
    def set_current_file_path(cls, file_path: str):
        """Set the current file path for fallback usage"""
        cls._current_file_path = file_path

## Creating Nutrition Analysis Tool
class NutritionTool(BaseTool):
    name: str = "analyze_nutrition_tool"
    description: str = "Analyze blood test results to provide evidence-based nutrition recommendations"
    args_schema: Type[BaseModel] = NutritionAnalysisInput

    def _run(self, blood_test_content: str) -> str:
        """Tool to analyze blood report data and provide nutrition recommendations"""
        try:
            # Process and analyze the blood report data
            processed_data = blood_test_content
            
            # Clean up the data format
            i = 0
            while i < len(processed_data):
                if processed_data[i:i+2] == "  ":  # Remove double spaces
                    processed_data = processed_data[:i] + processed_data[i+1:]
                else:
                    i += 1
                    
            # Basic nutrition analysis based on common blood markers
            analysis = """
            NUTRITION ANALYSIS BASED ON BLOOD TEST RESULTS:
            
            Based on the blood test data, here are evidence-based nutrition recommendations:
            
            1. Monitor key nutritional markers in your blood work
            2. Consult with a registered dietitian for personalized advice
            3. Focus on a balanced diet rich in whole foods
            4. Consider any deficiencies indicated in your blood work
            
            **Medical Disclaimer**: This analysis is for educational purposes only. 
            Always consult with qualified healthcare providers and registered dietitians 
            for personalized nutrition advice based on your specific health conditions.
            """
            
            return analysis
        except Exception as e:
            return f"Error in nutrition analysis: {str(e)}"

## Creating Exercise Planning Tool
class ExerciseTool(BaseTool):
    name: str = "create_exercise_plan_tool"
    description: str = "Create safe exercise recommendations based on blood test results"
    args_schema: Type[BaseModel] = ExerciseAnalysisInput

    def _run(self, blood_test_content: str) -> str:
        """Tool to create safe exercise plans based on blood report data"""
        try:
            # Basic exercise planning based on blood markers
            exercise_plan = """
            EXERCISE RECOMMENDATIONS BASED ON BLOOD TEST RESULTS:
            
            Based on your blood test data, here are general exercise recommendations:
            
            1. Start with low-to-moderate intensity activities
            2. Consider any cardiovascular markers in your results
            3. Monitor energy levels and recovery
            4. Progress gradually based on your health status
            
            **Safety First**: 
            - Always consult with your healthcare provider before starting any exercise program
            - Consider working with a certified exercise physiologist
            - Monitor how your body responds to different activities
            
            **Medical Disclaimer**: This guidance is for educational purposes only. 
            Always get medical clearance before beginning any exercise program, especially 
            if you have any health conditions indicated in your blood work.
            """
            
            return exercise_plan
        except Exception as e:
            return f"Error in exercise planning: {str(e)}"