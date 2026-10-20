"""Ask Saathi: the multilingual AI assistant endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.assistant import answer
from app.database import get_db
from app.models import Query, User
from app.schemas import AskIn
from app.security import get_optional_user

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.post("/ask")
def ask(body: AskIn, user: User | None = Depends(get_optional_user), db: Session = Depends(get_db)):
    """Answer a question in English, Telugu, Hindi or Urdu. Logged (anonymously if not signed in) for insights."""
    result = answer(db, body.text, body.lang)
    q = Query(user_id=user.id if user else None, text=body.text.strip(), lang=result["lang"],
              matched_service_id=result["service"]["id"] if result["service"] else None,
              confidence=result["confidence"], source=result["source"])
    db.add(q)
    db.commit()
    return result | {"query_id": q.id}
