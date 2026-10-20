"""Feedback (with AI sentiment/topic tagging) and in-app notifications."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.assistant import classify_feedback
from app.database import get_db
from app.models import Feedback, Notification, Query, Service, User
from app.schemas import FeedbackIn
from app.security import get_current_user

router = APIRouter(prefix="/api", tags=["feedback & notifications"])


@router.post("/feedback", status_code=201)
def give_feedback(body: FeedbackIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if body.query_id and not db.get(Query, body.query_id):
        raise HTTPException(422, "Unknown query")
    if body.service_id and not db.get(Service, body.service_id):
        raise HTTPException(422, "Unknown service")
    sentiment, topic = classify_feedback(body.comment, body.rating)
    fb = Feedback(user_id=user.id, query_id=body.query_id, service_id=body.service_id, rating=body.rating,
                  comment=body.comment.strip(), sentiment=sentiment, topic=topic)
    db.add(fb)
    db.commit()
    return {"id": fb.id, "sentiment": sentiment, "topic": topic}


@router.get("/notifications")
def notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.id.desc()).limit(50)
    items = [{"id": n.id, "title": n.title, "body": n.body, "read": n.read, "created_at": n.created_at} for n in rows]
    return {"unread": sum(not i["read"] for i in items), "items": items}


@router.post("/notifications/{nid}/read")
def mark_read(nid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    n = db.get(Notification, nid)
    if not n or n.user_id != user.id:
        raise HTTPException(404, "Notification not found")
    n.read = True
    db.commit()
    return {"ok": True}
