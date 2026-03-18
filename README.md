# Document Management & Workflow Automation System

A web-based document management system built with FastAPI and SQLite. 
Documents move through a configurable approval workflow: Submitted → 
Under Review → Approved / Rejected, with a full audit trail logged at 
each stage.

## Tech Stack
- Python / FastAPI
- SQLAlchemy / SQLite
- Jinja2 templating
- Uvicorn

## How to Run
1. Clone the repo
2. Create a virtual environment and activate it
3. Run `pip install -r requirements.txt`
4. Run `uvicorn main:app --reload`
5. Open http://127.0.0.1:8000
