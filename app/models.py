"""Database tables. See docs/DATABASE.md for the entity-relationship view and db/schema.sql for the DDL."""
from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, Float, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

LANGS = ("en", "te", "hi", "ur")
ROLES = ("citizen", "official")
APPLICATION_STATUSES = ("draft", "submitted", "under_verification", "needs_documents", "approved", "rejected")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class District(Base):
    __tablename__ = "districts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name_en: Mapped[str] = mapped_column(String(80), unique=True)
    name_te: Mapped[str] = mapped_column(String(80))


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    mobile: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), default="")
    preferred_lang: Mapped[str] = mapped_column(String(2), default="en")
    district_id: Mapped[int | None] = mapped_column(ForeignKey("districts.id"), nullable=True)
    role: Mapped[str] = mapped_column(String(10), default="citizen")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    district: Mapped[District | None] = relationship()
    applications: Mapped[list["Application"]] = relationship(back_populates="user")

    __table_args__ = (
        CheckConstraint("role in ('citizen','official')", name="ck_user_role"),
        CheckConstraint("preferred_lang in ('en','te','hi','ur')", name="ck_user_lang"),
    )


class OtpCode(Base):
    __tablename__ = "otp_codes"
    id: Mapped[int] = mapped_column(primary_key=True)
    mobile: Mapped[str] = mapped_column(String(10), index=True)
    code_hash: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    used: Mapped[bool] = mapped_column(Boolean, default=False)


class Service(Base):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True)
    category: Mapped[str] = mapped_column(String(40))
    department: Mapped[str] = mapped_column(String(80))
    name_en: Mapped[str] = mapped_column(String(120))
    name_te: Mapped[str] = mapped_column(String(120))
    name_hi: Mapped[str] = mapped_column(String(120))
    name_ur: Mapped[str] = mapped_column(String(120))
    description_en: Mapped[str] = mapped_column(Text)
    eligibility_en: Mapped[str] = mapped_column(Text)
    fee_inr: Mapped[int] = mapped_column(Integer)
    sla_days: Mapped[int] = mapped_column(Integer)
    keywords: Mapped[str] = mapped_column(Text)  # comma-separated, all four languages

    documents: Mapped[list["ServiceDocument"]] = relationship(back_populates="service", cascade="all, delete-orphan")

    def name(self, lang: str) -> str:
        return getattr(self, f"name_{lang}", None) or self.name_en


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    name_en: Mapped[str] = mapped_column(String(120))
    name_te: Mapped[str] = mapped_column(String(120))
    name_hi: Mapped[str] = mapped_column(String(120))
    name_ur: Mapped[str] = mapped_column(String(120))

    def name(self, lang: str) -> str:
        return getattr(self, f"name_{lang}", None) or self.name_en


class ServiceDocument(Base):
    """Which documents a service needs (many-to-many with a 'mandatory' flag)."""
    __tablename__ = "service_documents"
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), primary_key=True)
    mandatory: Mapped[bool] = mapped_column(Boolean, default=True)

    service: Mapped[Service] = relationship(back_populates="documents")
    document: Mapped[Document] = relationship()


class Centre(Base):
    __tablename__ = "centres"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    district_id: Mapped[int] = mapped_column(ForeignKey("districts.id"))
    address: Mapped[str] = mapped_column(String(255))
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    open_hours: Mapped[str] = mapped_column(String(60))

    district: Mapped[District] = relationship()


class Application(Base):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(primary_key=True)
    reference_no: Mapped[str] = mapped_column(String(20), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    applicant_name: Mapped[str] = mapped_column(String(120))
    purpose: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    remarks: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    user: Mapped[User] = relationship(back_populates="applications")
    service: Mapped[Service] = relationship()
    documents: Mapped[list["ApplicationDocument"]] = relationship(back_populates="application", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "status in ('draft','submitted','under_verification','needs_documents','approved','rejected')",
            name="ck_application_status",
        ),
    )


class ApplicationDocument(Base):
    """Checklist line: has the citizen got this document ready?"""
    __tablename__ = "application_documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    provided: Mapped[bool] = mapped_column(Boolean, default=False)

    application: Mapped[Application] = relationship(back_populates="documents")
    document: Mapped[Document] = relationship()


class Query(Base):
    """Every question asked to the assistant, for the officials' insight dashboard."""
    __tablename__ = "queries"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    text: Mapped[str] = mapped_column(Text)
    lang: Mapped[str] = mapped_column(String(2))
    matched_service_id: Mapped[int | None] = mapped_column(ForeignKey("services.id"), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    source: Mapped[str] = mapped_column(String(10), default="rules")  # rules | ai
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    matched_service: Mapped[Service | None] = relationship()


class Feedback(Base):
    __tablename__ = "feedback"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    query_id: Mapped[int | None] = mapped_column(ForeignKey("queries.id"), nullable=True)
    service_id: Mapped[int | None] = mapped_column(ForeignKey("services.id"), nullable=True)
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str] = mapped_column(Text, default="")
    sentiment: Mapped[str] = mapped_column(String(10), default="neutral")  # positive | neutral | negative
    topic: Mapped[str] = mapped_column(String(30), default="other")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    __table_args__ = (CheckConstraint("rating between 1 and 5", name="ck_feedback_rating"),)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str] = mapped_column(Text)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
