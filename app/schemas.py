"""Request/response models with validation (Pydantic v2)."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

Lang = Literal["en", "te", "hi", "ur"]
Status = Literal["draft", "submitted", "under_verification", "needs_documents", "approved", "rejected"]


class OtpRequest(BaseModel):
    mobile: str = Field(..., examples=["9876543210"])

    @field_validator("mobile")
    @classmethod
    def ten_digits(cls, v: str) -> str:
        v = v.strip().replace(" ", "")
        if v.startswith("+91"):
            v = v[3:]
        return v


class OtpVerify(OtpRequest):
    otp: str = Field(..., min_length=6, max_length=6, examples=["123456"])
    name: str = Field("", max_length=120)
    preferred_lang: Lang = "en"


class ProfileUpdate(BaseModel):
    name: str | None = Field(None, max_length=120)
    preferred_lang: Lang | None = None
    district_id: int | None = None


class UserOut(BaseModel):
    id: int
    mobile: str
    name: str
    preferred_lang: str
    district_id: int | None
    role: str


class AskIn(BaseModel):
    text: str = Field(..., min_length=2, max_length=500)
    lang: Lang = "en"


class ApplicationCreate(BaseModel):
    service_id: int
    applicant_name: str = Field(..., min_length=2, max_length=120)
    purpose: str = Field("", max_length=255)


class ApplicationUpdate(BaseModel):
    applicant_name: str | None = Field(None, min_length=2, max_length=120)
    purpose: str | None = Field(None, max_length=255)


class ChecklistUpdate(BaseModel):
    provided: bool


class StatusUpdate(BaseModel):
    status: Status
    remarks: str = Field("", max_length=1000)


class FeedbackIn(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field("", max_length=1000)
    query_id: int | None = None
    service_id: int | None = None


class NotificationOut(BaseModel):
    id: int
    title: str
    body: str
    read: bool
    created_at: datetime
