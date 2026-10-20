"""Citizen applications: create from a service, keep a document checklist, submit, follow the status."""
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Application, ApplicationDocument, Service, User
from app.schemas import ApplicationCreate, ApplicationUpdate, ChecklistUpdate
from app.security import get_current_user
from app.texts import STATUS, pick

router = APIRouter(prefix="/api/applications", tags=["applications"])


def _out(a: Application, lang: str = "en") -> dict:
    meaning, next_step = pick(STATUS[a.status], lang)
    return {
        "id": a.id, "reference_no": a.reference_no, "status": a.status, "remarks": a.remarks,
        "applicant_name": a.applicant_name, "purpose": a.purpose,
        "service": {"id": a.service.id, "code": a.service.code, "name": a.service.name(lang)},
        "checklist": [{"id": d.id, "document": d.document.name(lang), "provided": d.provided} for d in a.documents],
        "ready": all(d.provided for d in a.documents),
        "status_explained": {"meaning": meaning, "next_step": next_step},
        "created_at": a.created_at, "updated_at": a.updated_at,
    }


def _own(db: Session, app_id: int, user: User) -> Application:
    a = db.get(Application, app_id)
    if not a or a.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")
    return a


@router.get("")
def list_applications(lang: str = "en", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    apps = db.query(Application).filter(Application.user_id == user.id).order_by(Application.id.desc()).all()
    return [_out(a, lang) for a in apps]


@router.post("", status_code=201)
def create_application(body: ApplicationCreate, lang: str = "en", user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    """Start an application as a draft; the checklist is filled from the service's required documents."""
    svc = db.get(Service, body.service_id)
    if not svc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Unknown service")
    ref = f"MS{datetime.now(timezone.utc):%y%m}{secrets.token_hex(3).upper()}"
    a = Application(reference_no=ref, user=user, service=svc, applicant_name=body.applicant_name.strip(),
                    purpose=body.purpose.strip())
    a.documents = [ApplicationDocument(document=sd.document) for sd in svc.documents]
    db.add(a)
    db.commit()
    return _out(a, lang)


@router.get("/{app_id}")
def get_application(app_id: int, lang: str = "en", user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    return _out(_own(db, app_id, user), lang)


@router.patch("/{app_id}")
def update_application(app_id: int, body: ApplicationUpdate, lang: str = "en",
                       user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = _own(db, app_id, user)
    if a.status != "draft":
        raise HTTPException(status.HTTP_409_CONFLICT, "Only draft applications can be edited")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(a, field, value.strip())
    db.commit()
    return _out(a, lang)


@router.put("/{app_id}/checklist/{item_id}")
def tick_document(app_id: int, item_id: int, body: ChecklistUpdate, lang: str = "en",
                  user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = _own(db, app_id, user)
    item = next((d for d in a.documents if d.id == item_id), None)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Checklist item not found")
    item.provided = body.provided
    db.commit()
    return _out(a, lang)


@router.post("/{app_id}/submit")
def submit_application(app_id: int, lang: str = "en", user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    """Submit only when every required document is ticked (validation the counter staff would otherwise do)."""
    a = _own(db, app_id, user)
    if a.status not in ("draft", "needs_documents"):
        raise HTTPException(status.HTTP_409_CONFLICT, "Already submitted")
    missing = [d.document.name(lang) for d in a.documents if not d.provided]
    if missing:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, {"message": "Documents missing", "missing": missing})
    a.status = "submitted"
    db.commit()
    return _out(a, lang)


@router.delete("/{app_id}", status_code=204)
def delete_application(app_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = _own(db, app_id, user)
    if a.status != "draft":
        raise HTTPException(status.HTTP_409_CONFLICT, "Only draft applications can be deleted")
    db.delete(a)
    db.commit()
