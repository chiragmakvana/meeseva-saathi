"""Login with mobile number + one-time password, and the citizen's profile."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import config
from app.database import get_db
from app.models import District, User
from app.schemas import OtpRequest, OtpVerify, ProfileUpdate, UserOut
from app.security import check_otp, get_current_user, issue_otp, make_token, valid_mobile

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _user_out(u: User) -> UserOut:
    return UserOut(id=u.id, mobile=u.mobile, name=u.name, preferred_lang=u.preferred_lang,
                   district_id=u.district_id, role=u.role)


@router.post("/request-otp")
def request_otp(body: OtpRequest, db: Session = Depends(get_db)):
    """Send a 6-digit OTP. In demo mode (no SMS gateway) the OTP is returned in the response."""
    if not valid_mobile(body.mobile):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Enter a valid 10-digit mobile number")
    code = issue_otp(db, body.mobile)
    out = {"sent": True, "expires_in_seconds": config.OTP_TTL_SECONDS}
    if config.DEMO_OTP_MODE:
        out["demo_otp"] = code
    return out


@router.post("/verify-otp")
def verify_otp(body: OtpVerify, db: Session = Depends(get_db)):
    """Check the OTP; create the citizen account on first login; return a session token."""
    if not valid_mobile(body.mobile):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Enter a valid 10-digit mobile number")
    if not check_otp(db, body.mobile, body.otp):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong or expired OTP")
    user = db.query(User).filter(User.mobile == body.mobile).first()
    if not user:
        user = User(mobile=body.mobile, name=body.name.strip(), preferred_lang=body.preferred_lang)
        db.add(user)
        db.commit()
    return {"token": make_token(user), "user": _user_out(user)}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return _user_out(user)


@router.patch("/me", response_model=UserOut)
def update_me(body: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if body.district_id is not None and not db.get(District, body.district_id):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Unknown district")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(user, field, value.strip() if isinstance(value, str) else value)
    db.commit()
    return _user_out(user)
