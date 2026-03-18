from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import models, database

models.Base.metadata.create_all(bind=database.engine)

from routers import documents, workflow

app = FastAPI(title="Document Workflow System")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="templates")

app.include_router(documents.router)
app.include_router(workflow.router)

@app.get("/")
def root():
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard")
def dashboard(request: Request):
    from database import get_db
    from sqlalchemy.orm import Session
    import models as m
    db: Session = next(get_db())
    docs = db.query(m.Document).order_by(m.Document.created_at.desc()).all()
    counts = {
        "Submitted": sum(1 for d in docs if d.status == "Submitted"),
        "Under Review": sum(1 for d in docs if d.status == "Under Review"),
        "Approved": sum(1 for d in docs if d.status == "Approved"),
        "Rejected": sum(1 for d in docs if d.status == "Rejected"),
    }
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "documents": docs, "counts": counts
    })