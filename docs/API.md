# API reference

Base URL: `http://127.0.0.1:8000`. Interactive documentation (try every call): **`/docs`** (Swagger) and `/redoc`.

- All requests and responses are JSON.
- **Authentication:** `Authorization: Bearer <token>` from `POST /api/auth/verify-otp`. Tokens expire after 8 hours.
- **Language:** most endpoints take `?lang=en|te|hi|ur` for names and messages.
- **Errors:** `{"detail": "<message>"}` with 401 (login needed), 403 (officials only), 404, 409 (wrong state), 422 (validation).
- External APIs: **Azure OpenAI** chat completions (optional, server-side only), **Google Maps** links (no key; links only).

## Authentication

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| POST | `/api/auth/request-otp` | – | Send a 6-digit OTP to a mobile number |
| POST | `/api/auth/verify-otp` | – | Check the OTP, create the account on first login, return a token |
| GET | `/api/auth/me` | citizen | Current profile |
| PATCH | `/api/auth/me` | citizen | Update name, language, district |

```http
POST /api/auth/request-otp
{"mobile": "9876543210"}
→ 200 {"sent": true, "expires_in_seconds": 300, "demo_otp": "482913"}   # demo_otp only when DEMO_OTP_MODE=true
```

```http
POST /api/auth/verify-otp
{"mobile": "9876543210", "otp": "482913", "name": "Ravi Kumar", "preferred_lang": "te"}
→ 200 {"token": "eyJ1aWQiOjJ9...", "user": {"id": 2, "mobile": "9876543210", "name": "Ravi Kumar", "preferred_lang": "te", "district_id": null, "role": "citizen"}}
→ 401 {"detail": "Wrong or expired OTP"}
```

## Ask Saathi (AI assistant)

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| POST | `/api/assistant/ask` | optional | Answer a question in any of the four languages |

```http
POST /api/assistant/ask
{"text": "నాకు ఆదాయ ధృవీకరణ పత్రం కావాలి", "lang": "te"}
→ 200 {
  "reply": "ఆదాయ ధృవీకరణ పత్రం కోసం మీరు ఏదైనా మీసేవ కేంద్రంలో ...",
  "lang": "te",
  "service": {"id": 1, "code": "INC", "name": "ఆదాయ ధృవీకరణ పత్రం", "fee_inr": 45, "sla_days": 7,
              "documents": [{"code": "AADHAAR", "name": "ఆధార్ కార్డు", "mandatory": true}, ...]},
  "suggestions": [...], "confidence": 1.0, "source": "ai" | "rules", "query_id": 17
}
```

`source` shows which engine answered. Every question is stored (without personal data beyond the optional
user id) for the officials' insights.

## Catalogue and centres (public)

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/services?lang=&q=&category=` | List services, or search in any language |
| GET | `/api/services/{id}?lang=` | Service details: eligibility, documents, fee, time |
| GET | `/api/districts` | Districts (English and Telugu names) |
| GET | `/api/centres?lat=&lng=&district_id=&limit=` | Nearest centres (haversine distance) or a district's centres, with a map link |

## Applications (citizen)

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/applications` | My applications |
| POST | `/api/applications` | Start an application (draft) with a document checklist |
| GET | `/api/applications/{id}` | Details, checklist and plain-language status |
| PATCH | `/api/applications/{id}` | Edit a draft (applicant name, purpose) |
| PUT | `/api/applications/{id}/checklist/{item_id}` | Tick or untick a document |
| POST | `/api/applications/{id}/submit` | Submit (only when every document is ticked) |
| DELETE | `/api/applications/{id}` | Delete a draft |

```http
POST /api/applications?lang=en
{"service_id": 3, "applicant_name": "Ravi Kumar", "purpose": "School admission"}
→ 201 {"id": 5, "reference_no": "MS2610A1B2C3", "status": "draft", "ready": false,
       "checklist": [{"id": 11, "document": "Aadhaar card", "provided": false}, ...],
       "status_explained": {"meaning": "Your application is saved but not submitted yet.",
                            "next_step": "Tick each document you have, then press Submit."}, ...}

POST /api/applications/5/submit
→ 422 {"detail": {"message": "Documents missing", "missing": ["Aadhaar card", ...]}}
```

Statuses: `draft → submitted → under_verification → needs_documents | approved | rejected`.
Citizens only ever see their own applications (another citizen's id returns 404).

## Feedback and notifications (citizen)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/feedback` | Rate an answer or service (1–5) with an optional comment; returns AI-tagged sentiment and topic |
| GET | `/api/notifications` | My notifications and unread count |
| POST | `/api/notifications/{id}/read` | Mark as read |

```http
POST /api/feedback
{"rating": 2, "comment": "Too slow, waited many days", "query_id": 17}
→ 201 {"id": 4, "sentiment": "negative", "topic": "delay"}
```

## Officials (role = official)

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/admin/insights` | Questions (total, answered %, by language, top services, unanswered), feedback (rating, sentiment, topics), applications by status |
| GET | `/api/admin/applications?status=` | Applications to process |
| POST | `/api/admin/applications/{id}/status` | Set status and remarks; notifies the citizen in their language |

```http
POST /api/admin/applications/5/status
{"status": "needs_documents", "remarks": "Please bring the rent agreement."}
→ 200 {"id": 5, "status": "needs_documents"}
```

## System

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | `{"status": "ok", "ai_engine": "azure-openai" | "rules"}` |
