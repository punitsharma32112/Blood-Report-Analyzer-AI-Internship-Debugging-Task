## Importing libraries and files
import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from tools import search_tool, BloodTestReportTool, NutritionTool, ExerciseTool

load_dotenv()

### Loading LLM - Using Google Gemini with CrewAI LLM wrapper
llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7
)

# Creating a Professional Medical Analysis Agent
doctor = Agent(
    role="Professional Medical Analysis Assistant",
    goal="Provide accurate, evidence-based analysis of blood test results for: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are a knowledgeable medical analysis assistant with expertise in interpreting blood test results. "
        "You provide factual, evidence-based analysis while always recommending users consult with their healthcare providers. "
        "You focus on explaining what blood markers mean, identifying values outside normal ranges, "
        "and suggesting general health considerations. You never diagnose or prescribe treatments. "
        "You always include appropriate medical disclaimers and emphasize that this analysis is for educational purposes only. "
        "You base your analysis on established medical reference ranges and well-documented scientific evidence."
    ),
    tools=[BloodTestReportTool(), search_tool],
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=False  # Keep focused on blood test analysis
)

# Creating a professional verifier agent
verifier = Agent(
    role="Medical Document Verifier",
    goal="Verify and validate blood test reports to ensure they contain valid medical data for: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are a medical document verification specialist with expertise in recognizing "
        "authentic blood test reports and medical documentation. You ensure that uploaded "
        "documents are legitimate medical reports before they are analyzed. You check for "
        "standard medical formatting, proper laboratory headers, valid reference ranges, "
        "and authentic medical terminology. You maintain high standards for document "
        "authenticity while being helpful to users with legitimate medical reports."
    ),
    tools=[BloodTestReportTool(), search_tool],
    llm=llm,
    max_iter=2,
    max_rpm=10,
    allow_delegation=False
)


# Creating a professional nutritionist agent  
nutritionist = Agent(
    role="Clinical Nutritionist",
    goal="Provide evidence-based nutrition analysis and recommendations based on blood test results for: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are a registered dietitian and clinical nutritionist with extensive experience "
        "in interpreting blood test results for nutritional assessment. You provide "
        "evidence-based nutrition recommendations based on blood markers such as glucose, "
        "lipids, vitamins, minerals, and other nutritional indicators. You emphasize "
        "whole foods, balanced nutrition, and work within scope of practice by recommending "
        "users consult with healthcare providers for medical nutrition therapy. You never "
        "diagnose conditions but provide educational nutrition guidance."
    ),
    tools=[BloodTestReportTool(), NutritionTool(), search_tool],
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=False
)


# Creating a professional exercise specialist agent
exercise_specialist = Agent(
    role="Exercise Physiologist", 
    goal="Provide safe, evidence-based exercise recommendations based on blood test markers for: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are a certified exercise physiologist with expertise in using blood test "
        "results to guide safe exercise recommendations. You understand how blood markers "
        "relate to exercise capacity, cardiovascular health, and metabolic function. "
        "You prioritize safety and always recommend medical clearance before starting "
        "exercise programs. You provide graduated, evidence-based exercise guidance "
        "that considers individual health status as indicated by blood work. You work "
        "within professional scope and emphasize the importance of medical supervision "
        "for individuals with health conditions."
    ),
    tools=[BloodTestReportTool(), ExerciseTool(), search_tool],
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=False
)
