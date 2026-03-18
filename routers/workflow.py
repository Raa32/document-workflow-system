from fastapi import APIRouter, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter(prefix="/workflow", tags=["workflow"])

TRANSITIONS = {
    "Submitted": ["Under Review"],
    "Under Review": ["Approved", "Rejected"],
    "Approved": [],
    "Rejected": []
}

@router.post("/update/{doc_id}")
def update_status(
    doc_id: int,
    new_status: str = Form(...),
    reviewed_by: str = Form(...),
    comment: str = Form(""),
    db: Session = Depends(get_db)
):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()

    if new_status not in TRANSITIONS.get(doc.status, []):
        return RedirectResponse(url=f"/documents/{doc_id}", status_code=303)

    doc.status = new_status
    db.commit()

    event = models.WorkflowEvent(
        document_id=doc_id,
        action=new_status,
        performed_by=reviewed_by,
        comment=comment
    )
    db.add(event)
    db.commit()

    return RedirectResponse(url=f"/documents/{doc_id}", status_code=303)