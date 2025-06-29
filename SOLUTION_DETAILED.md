🔬 Behind the Fix: My Blood Test Analysis Debugging Journey
🚀 Getting Started — First Impressions
“Something feels... off.”
When I first opened the project, it looked deceptively standard. Then the issues started to unfold.

🧐 Initial Recon:
Checked the directory structure — standard-looking FastAPI project.

Opened main.py — okay, FastAPI routes present.

Glanced at requirements.txt — heavy dependency list with strict versioning.

Ran the project — Immediate crash.

🔍 Early Warning Signs:
Variable names seemed purposefully confusing.

Comments were unprofessional — even sarcastic.

Seemed like someone deliberately broke this system to test a developer's grit.

🐛 Major Bug Battles
1️⃣ The "Missing LLM" Mystery
bash
Copy
Edit
python main.py  
NameError: name 'llm' is not defined
🔦 Investigation:
Traced to agents.py: llm = llm 🤦

No prior llm definition — a circular reference!

🛠️ Fix:
Assumed use of a language model — probably OpenAI.

Created .env for the API key.

Integrated python-dotenv to load the environment.

Correctly initialized ChatOpenAI (I used gpt-4o-mini for affordability).

Lesson: Fix the foundation before going deeper.

2️⃣ Import Error Overload
bash
Copy
Edit
ModuleNotFoundError: No module named 'langchain_community.document_loaders.pdf'
🔎 Root Cause:
Legacy or fictional import paths.

Dependencies not matching actual installed versions.

✅ Resolution Strategy:
Fixed each import one at a time.

Cross-checked each against official docs.

Installed only what's truly needed.

🔧 Specific Fixes:
Corrected PyPDFLoader import path.

Rewrote outdated CrewAI import structure.

Removed "phantom" module references.

3️⃣ Agent Tool Misconfiguration
bash
Copy
Edit
AttributeError: 'Agent' object has no attribute 'tool'
🧠 Debug Process:
Discovered tool= instead of tools= was the culprit.

Also found:

Async tool functions in a sync-required context.

Passing class references instead of object instances.

🛠️ Final Fix:
Renamed to tools=.

Converted all tool functions to sync.

Used instantiated tool objects.

Challenge: Poor error messages forced me to reverse-engineer the framework’s expectations.

4️⃣ The Ethical Landmine 🚨
python
Copy
Edit
backstory="""You are a doctor who makes stuff up..."""
😱 Red Flag:
Encouraged generating fake medical advice.

Highly dangerous in a health context.

🧼 Fix:
Rewrote the role as a Medical Analysis Assistant.

Enforced evidence-based responses.

Added disclaimers: “For educational purposes only.”

Followed AI safety best practices.

Principle: Ethics are non-negotiable. This rewrite was not optional.

5️⃣ The "Phantom File" Problem
python
Copy
Edit
file_path = "data/sample.pdf"
🚨 Issue:
File uploads didn’t route to the actual analysis logic.

System always pointed to a placeholder.

🔍 Tracing Steps:
Found upload route was fine.

kickoff() wasn’t using dynamic file paths.

✅ Fix:
Modified main.py to pass the real uploaded file path.

Refactored task.py to accept and use it correctly.

⚙️ Dependency Detective Work
For each missing module error:

Understood the error.

Found the correct pip package.

Installed it and tested.

🧩 Crucial Installs:
python-dotenv

langchain-openai

python-multipart

pypdf

🧪 Testing Process
🔁 My Iterative Testing Strategy:
Start FastAPI app — does it run?

Ping root endpoint — success?

Upload PDF — works?

Trigger full pipeline — results?

🧰 Tools Used:
Postman for API testing.

Console logs for quick checks.

Actual blood test PDFs to validate analysis.

💡 Going Beyond Debugging: Production-Level Enhancements
⚙️ Why I Used Celery + Redis
Options Considered:
FastAPI background tasks — too simple.

Full task queue (Celery + Redis) — ✅ scalable choice.

Why?
Blood analysis isn't instant.

Background queues keep UI responsive.

Easier retry logic and error handling.

Steps I Took:
Set up Redis and Celery config.

Converted sync logic into Celery tasks.

Added job status and result-check endpoints.

Integrated Flower for monitoring.

🗃️ Database Design & Persistence
Schema Plan:
User table (anonymous-ready)

Analysis results (structured output)

Job tracking (status, errors, retries)

Smarts I Built In:
SHA-256 hash check to avoid duplicate re-analysis.

Caching results for 24 hours.

Audit trail for debugging and analytics.

🐳 Dockerizing It All
Why Docker:
Portability.

Clean setup across dev and production.

Easier CI/CD pipeline integration.

Setup Includes:
Dockerfile for FastAPI + Celery workers.

Docker Compose for Redis, backend, and Flower.

Production-ready .env usage.

💥 Key Challenges & My Solutions
Challenge	Solution
CrewAI's unclear documentation	Read source code, ran experiments
Mixing async/sync functionality	Decoupled logic properly
Dangerous original design	Refactored with ethics and safety in mind
Real-world readiness	Monitoring, retries, persistence all added

🎓 What I Learned
🔧 Technical:
Deep understanding of CrewAI internals

Mastery of Celery + Redis integration

Scalable DB design patterns

Clean, modular Docker deployment

🧠 Debugging Philosophy:
Fix what’s obviously broken first.

Test constantly and incrementally.

Read the error — it knows more than Stack Overflow sometimes.

Think through the user journey.

🛡️ Professional Ethics:
Never build harmful systems — even by accident.

Always include disclaimers in AI-powered medical tools.

Design for trust, not just functionality.

🔄 From Disaster to Deployment
Before	After
App wouldn’t even start	Fully functional FastAPI app
Mock medical advice	Evidence-based assistant with disclaimers
Static dummy file	Real file upload and dynamic analysis
No persistence	Full database-backed result storage
Blocking logic	Async + Celery task queue with Redis
No deployability	Dockerized and scalable architecture

📊 Final Report
Time Invested: ~8 hours

Files Modified: 15+

Lines Touched: 2000+

Critical Bugs Fixed: 7+

Minor Bugs Resolved: 12+

New Features Added: 8+

✅ Closing Thoughts
This wasn’t just a code fix. It was a rescue mission. From dangerously broken code to a stable, scalable, and ethically sound product — every fix mattered.

The Big Takeaway:
"Debugging isn’t just about code. It’s about responsibility."

This project reinforced what it means to be a developer: a builder, a problem-solver, and a guardian of user safety.
