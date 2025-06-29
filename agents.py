## Setting Up the Environment and Agents

```python
import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from tools import search_tool, BloodTestReportTool, NutritionTool, ExerciseTool

# Load environment variables
load_dotenv()

# Initialize LLM using Google Gemini model via CrewAI's LLM wrapper
llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7
)

# Agent: Medical Analysis Assistant
# Focus: Factual, ethical, and educational analysis of blood test reports

doctor = Agent(
    role="Professional Medical Analysis Assistant",
    goal="Provide accurate, evidence-based analysis of blood test results for: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "A professional assistant trained in interpreting blood test results using scientific evidence. "
        "Delivers responsible and clear health insights while avoiding diagnoses. Always suggests consulting licensed physicians. "
        "Focus is on explaining medical markers, identifying irregularities, and providing generalized health suggestions. "
        "The assistant never prescribes treatment and stresses educational intent with strong medical disclaimers."
    ),
    tools=[BloodTestReportTool(), search_tool],
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=False
)

# Agent: Medical Document Verifier
# Focus: Ensures legitimacy and format compliance of uploaded reports

verifier = Agent(
    role="Medical Document Verifier",
    goal="Verify and validate blood test reports to ensure they contain valid medical data for: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "Expert in authenticating medical reports. Checks for accurate formatting, terminology, and lab standards. "
        "Assures reports are credible before further processing, offering helpful validation for genuine submissions."
    ),
    tools=[BloodTestReportTool(), search_tool],
    llm=llm,
    max_iter=2,
    max_rpm=10,
    allow_delegation=False
)

# Agent: Clinical Nutritionist
# Focus: Provides nutritional advice from lab results without medical diagnosis

nutritionist = Agent(
    role="Clinical Nutritionist",
    goal="Provide evidence-based nutrition analysis and recommendations based on blood test results for: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "Registered dietitian experienced in lab-driven nutritional assessments. Interprets markers like vitamins, minerals, glucose, and lipids. "
        "Delivers practical dietary recommendations while promoting whole foods and balanced nutrition. "
        "Avoids diagnoses, emphasizes professional referral when needed."
    ),
    tools=[BloodTestReportTool(), NutritionTool(), search_tool],
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=False
)

# Agent: Exercise Physiologist
# Focus: Suggests exercise modifications based on blood data

exercise_specialist = Agent(
    role="Exercise Physiologist",
    goal="Provide safe, evidence-based exercise recommendations based on blood test markers for: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "Certified in clinical exercise science. Uses lab metrics to inform physical activity guidance. "
        "Considers cardiovascular and metabolic indicators, prioritizes patient safety. Recommends medical supervision for individuals with conditions."
    ),
    tools=[BloodTestReportTool(), ExerciseTool(), search_tool],
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=False
)
```
