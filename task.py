## Importing libraries and files
from crewai import Task

from agents import doctor, verifier, nutritionist, exercise_specialist
from tools import search_tool, BloodTestReportTool, NutritionTool, ExerciseTool

## Creating a professional blood test analysis task
help_patients = Task(
    description="""Analyze the uploaded blood test report and provide a professional medical analysis based on the user query: {query}

    STEP 1: Use the read_blood_test_report tool with file_path="{file_path}" to extract the blood test content.
    
    Your analysis should include:
    1. Summary of key blood markers and their values
    2. Identification of any values outside normal reference ranges
    3. General health insights based on the results
    4. Recommendations for lifestyle considerations
    5. Clear disclaimer about consulting healthcare providers

    Always maintain a professional, helpful tone and provide evidence-based information.
    Use established medical reference ranges and avoid speculation.
    Focus on educating the patient about what their results mean in clear, understandable language.""",

    expected_output="""A comprehensive blood test analysis report including:
    - Executive summary of results
    - Detailed breakdown of key blood markers with explanations
    - Normal vs abnormal value identification with reference ranges
    - General health recommendations based on evidence
    - Important medical disclaimer
    - Formatted in clear, easy-to-understand language
    - Professional tone throughout
    - No speculation or unsubstantiated claims""",

    agent=doctor,
    tools=[BloodTestReportTool()],
    async_execution=False,
)

## Creating a professional nutrition analysis task
nutrition_analysis = Task(
    description="""Analyze the blood test report to provide evidence-based nutrition recommendations for the user query: {query}

    STEP 1: Use the read_blood_test_report tool with file_path="{file_path}" to extract the blood test content.

    Your nutrition analysis should include:
    1. Review of nutrition-related blood markers (glucose, lipids, vitamins, minerals)
    2. Identification of any nutritional deficiencies or imbalances indicated by blood work
    3. Evidence-based dietary recommendations to support optimal blood marker values
    4. General nutrition guidance for maintaining good health
    5. Clear disclaimer about consulting with registered dietitians and healthcare providers

    Focus on whole foods, balanced nutrition, and established nutritional science.""",

    expected_output="""A comprehensive nutrition analysis report including:
    - Summary of nutrition-related blood markers and their significance
    - Evidence-based dietary recommendations
    - Foods that may help optimize blood marker values
    - General nutrition guidance for health maintenance
    - Important disclaimer about consulting with registered dietitians
    - Professional, educational tone throughout
    - No supplement sales or unsubstantiated claims""",

    agent=nutritionist,
    tools=[BloodTestReportTool(), NutritionTool(), search_tool],
    async_execution=False,
)

## Creating a professional exercise planning task
exercise_planning = Task(
    description="""Analyze the blood test report to provide safe, evidence-based exercise recommendations for the user query: {query}

    STEP 1: Use the read_blood_test_report tool with file_path="{file_path}" to extract the blood test content.

    Your exercise analysis should include:
    1. Review of cardiovascular and metabolic markers that relate to exercise capacity
    2. Assessment of any health indicators that might affect exercise recommendations
    3. Safe, graduated exercise suggestions based on blood marker values
    4. General fitness guidance for improving health markers
    5. Clear disclaimer about medical clearance before starting exercise programs

    Prioritize safety and emphasize the importance of healthcare provider approval.""",

    expected_output="""A comprehensive exercise guidance report including:
    - Assessment of exercise-related blood markers
    - Safe, evidence-based exercise recommendations
    - Graduated fitness progression suggestions
    - Important safety considerations and medical clearance requirements
    - Professional disclaimer about consulting healthcare providers
    - Emphasis on individual health status and capabilities
    - No dangerous or inappropriate exercise suggestions""",

    agent=exercise_specialist,
    tools=[BloodTestReportTool(), ExerciseTool(), search_tool],
    async_execution=False,
)

## Creating a professional verification task    
verification = Task(
    description="""Verify that the uploaded document is a legitimate blood test report for the user query: {query}

    STEP 1: Use the read_blood_test_report tool with file_path="{file_path}" to extract the document content.

    Your verification should include:
    1. Check for standard medical laboratory formatting and headers
    2. Verify presence of authentic blood test markers and reference ranges
    3. Confirm the document contains legitimate medical terminology
    4. Validate that the document appears to be from a recognized laboratory
    5. Provide clear feedback on document authenticity

    Only approve documents that appear to be genuine medical blood test reports.""",

    expected_output="""A professional document verification report including:
    - Confirmation of document type and authenticity
    - Assessment of medical formatting and laboratory standards
    - Verification of blood test markers and reference ranges
    - Clear approval or rejection of document for medical analysis
    - Professional recommendations for next steps
    - Emphasis on using only legitimate medical documents""",

    agent=verifier,
    tools=[BloodTestReportTool(), search_tool],
    async_execution=False
)