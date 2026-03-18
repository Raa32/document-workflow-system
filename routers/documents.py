from fastapi import APIRouter, UploadFile, File, Form, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
import models, shutil, uuid, os

router = APIRouter(prefix="/documents", tags=["documents"])
templates = Jinja2Templates(directory="templates")

@router.get("/upload")
def upload_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/upload")
async def upload_document(
    uploaded_by: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = f"uploads/{unique_name}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc = models.Document(
        filename=unique_name,
        original_name=file.filename,
        uploaded_by=uploaded_by,
        status="Submitted"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    event = models.WorkflowEvent(
        document_id=doc.id,
        action="Submitted",
        performed_by=uploaded_by,
        comment="Document uploaded and submitted for review."
    )
    db.add(event)
    db.commit()

    return RedirectResponse(url=f"/documents/{doc.id}", status_code=303)

@router.get("/{doc_id}")
def document_detail(doc_id: int, request: Request, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    events = db.query(models.WorkflowEvent).filter(
        models.WorkflowEvent.document_id == doc_id
    ).order_by(models.WorkflowEvent.timestamp).all()
    return templates.TemplateResponse("document_detail.html", {
        "request": request, "document": doc, "events": events
    })