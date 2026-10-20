"""Officials' dashboard (role = official): service insights and application processing."""
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Application, Feedback, Notification, Query, Service, User
from app.schemas import StatusUpdate
from app.security import require_official
from app.texts import STATUS, STATUS_CHANGED_TITLE, pick

router = APIRouter(prefix="/api/admin", tags=["officials"])


@router.get("/insights")
def insights(_: User = Depends(require_official), db: Session = Depends(get_db)):
    """What citizens ask, what the catalogue cannot answer, how they feel, and where applications are."""
    total_q = db.query(func.count(Query.id)).scalar() or 0
    unmatched = db.query(Query).filter(Query.matched_service_id.is_(None)).order_by(Query.id.desc()).limit(10).all()
    unmatched_n = db.query(func.count(Query.id)).filter(Query.matched_service_id.is_(None)).scalar() or 0
    top = (db.query(Service.name_en, func.count(Query.id))
           .join(Query, Query.matched_service_id == Service.id)
           .group_by(Service.name_en).order_by(func.count(Query.id).desc()).limit(8).all())
    langs = dict(db.query(Query.lang, func.count(Query.id)).group_by(Query.lang).all())
    fb = db.query(Feedback).all()
    by_status = dict(db.query(Application.status, func.count(Application.id)).group_by(Application.status).all())
    return {
        "queries": {"total": total_q, "unmatched": unmatched_n,
                    "answered_pct": round(100 * (total_q - unmatched_n) / total_q, 1) if total_q else None,
                    "by_language": langs,
                    "top_services": [{"service": n, "count": c} for n, c in top],
                    "recent_unanswered": [{"text": q.text, "lang": q.lang, "at": q.created_at} for q in unmatched]},
        "feedback": {"count": len(fb),
                     "avg_rating": round(sum(f.rating for f in fb) / len(fb), 2) if fb else None,
                     "sentiment": dict(Counter(f.sentiment for f in fb)),
                     "topics": dict(Counter(f.topic for f in fb)),
                     "recent": [{"rating": f.rating, "comment": f.comment, "sentiment": f.sentiment, "topic": f.topic}
                                for f in sorted(fb, key=lambda f: f.id, reverse=True)[:10]]},
        "applications": {"by_status": by_status},
    }


@router.get("/applications")
def all_applications(status: str = "", _: User = Depends(require_official), db: Session = Depends(get_db)):
    qry = db.query(Application)
    if status:
        qry = qry.filter(Application.status == status)
    return [{"id": a.id, "reference_no": a.reference_no, "service": a.service.name_en, "applicant_name": a.applicant_name,
             "status": a.status, "remarks": a.remarks, "updated_at": a.updated_at,
             "documents_ready": all(d.provided for d in a.documents)}
            for a in qry.order_by(Application.id.desc()).limit(100)]


@router.post("/applications/{app_id}/status")
def set_status(app_id: int, body: StatusUpdate, _: User = Depends(require_official), db: Session = Depends(get_db)):
    """Move an application forward and notify the citizen in their own language."""
    a = db.get(Application, app_id)
    if not a:
        raise HTTPException(404, "Application not found")
    if a.status == "draft":
        raise HTTPException(409, "The citizen has not submitted this application yet")
    a.status, a.remarks = body.status, body.remarks.strip()
    lang = a.user.preferred_lang
    meaning, next_step = pick(STATUS[a.status], lang)
    db.add(Notification(user_id=a.user_id, title=pick(STATUS_CHANGED_TITLE, lang).format(ref=a.reference_no),
                        body=f"{meaning} {next_step}" + (f"\n{a.remarks}" if a.remarks else "")))
    db.commit()
    return {"id": a.id, "status": a.status}
