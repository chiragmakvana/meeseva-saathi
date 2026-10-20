"""OTP login and session tokens.

- OTPs are stored only as an HMAC-SHA256 hash, expire after 5 minutes and allow 5 attempts.
- Sessions are signed, time-limited bearer tokens (itsdangerous); no passwords are stored.
"""
import hashlib
import hmac
import re
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header, HTTPException, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.orm import Session

from app import config
from app.database import get_db
from app.models import OtpCode, User

MOBILE_RE = re.compile(r"^[6-9]\d{9}$")
_serializer = URLSafeTimedSerializer(config.SECRET_KEY, salt="session")


def valid_mobile(mobile: str) -> bool:
    return bool(MOBILE_RE.match(mobile or ""))


def _hash_otp(mobile: str, code: str) -> str:
    return hmac.new(config.SECRET_KEY.encode(), f"{mobile}:{code}".encode(), hashlib.sha256).hexdigest()


def issue_otp(db: Session, mobile: str) -> str:
    """Create a fresh 6-digit OTP for the mobile number and invalidate older ones."""
    db.query(OtpCode).filter(OtpCode.mobile == mobile, OtpCode.used.is_(False)).update({"used": True})
    code = f"{secrets.randbelow(1_000_000):06d}"
    db.add(OtpCode(
        mobile=mobile,
        code_hash=_hash_otp(mobile, code),
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=config.OTP_TTL_SECONDS),
    ))
    db.commit()
    return code


def check_otp(db: Session, mobile: str, code: str) -> bool:
    otp = (db.query(OtpCode)
           .filter(OtpCode.mobile == mobile, OtpCode.used.is_(False))
           .order_by(OtpCode.id.desc()).first())
    if not otp:
        return False
    expires = otp.expires_at if otp.expires_at.tzinfo else otp.expires_at.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc) or otp.attempts >= config.OTP_MAX_ATTEMPTS:
        otp.used = True
        db.commit()
        return False
    otp.attempts += 1
    ok = hmac.compare_digest(otp.code_hash, _hash_otp(mobile, code or ""))
    if ok:
        otp.used = True
    db.commit()
    return ok


def make_token(user: User) -> str:
    return _serializer.dumps({"uid": user.id})


def get_current_user(authorization: str = Header(default=""), db: Session = Depends(get_db)) -> User:
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Login required")
    try:
        data = _serializer.loads(authorization[7:], max_age=config.SESSION_MAX_AGE_SECONDS)
    except SignatureExpired:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expired, please log in again")
    except BadSignature:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid session")
    user = db.get(User, data.get("uid"))
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid session")
    return user


def get_optional_user(authorization: str = Header(default=""), db: Session = Depends(get_db)) -> User | None:
    if not authorization:
        return None
    try:
        return get_current_user(authorization, db)
    except HTTPException:
        return None


def require_official(user: User = Depends(get_current_user)) -> User:
    if user.role != "official":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Officials only")
    return user
