"""The AI layer: understand what the citizen needs, in their language, and answer from the service catalogue.

Two engines, same output:
1. Rules engine (always available, no external calls): script-based language detection plus
   multilingual keyword scoring against the catalogue.
2. LLM engine (optional, Azure OpenAI): used when configured; grounded in the same catalogue and
   forced to return JSON. Any failure falls back to the rules engine, so the service never goes down.

Feedback is classified (sentiment + topic) the same way.
"""
import json
import logging
import re

import httpx
from sqlalchemy.orm import Session

from app import config
from app.models import Service
from app.texts import APPLY_INTRO, FEE_TIME, NEXT_STEP, NOT_FOUND, pick

log = logging.getLogger("saathi.assistant")

LANG_NAMES = {"en": "English", "te": "Telugu", "hi": "Hindi", "ur": "Urdu"}


def detect_lang(text: str, default: str = "en") -> str:
    """Detect the script the citizen typed in. Latin text keeps the user's chosen language."""
    if re.search(r"[ఀ-౿]", text):
        return "te"
    if re.search(r"[؀-ۿ]", text):
        return "ur"
    if re.search(r"[ऀ-ॿ]", text):
        return "hi"
    return default if default in LANG_NAMES else "en"


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def score_services(db: Session, text: str) -> list[tuple[Service, float]]:
    """Score every service by keyword hits; longer (more specific) keywords weigh more."""
    q = _normalise(text)
    scored = []
    for svc in db.query(Service).all():
        score = 0.0
        terms = [k.strip().lower() for k in svc.keywords.split(",") if k.strip()]
        terms += [svc.name_en.lower(), svc.name_te, svc.name_hi, svc.name_ur]
        for term in terms:
            if term and term in q:
                score += 1.0 + min(len(term), 20) / 20
        if score:
            scored.append((svc, score))
    return sorted(scored, key=lambda s: s[1], reverse=True)


def service_card(svc: Service, lang: str) -> dict:
    docs = [{"code": sd.document.code, "name": sd.document.name(lang), "mandatory": sd.mandatory}
            for sd in svc.documents]
    return {
        "id": svc.id, "code": svc.code, "name": svc.name(lang), "name_en": svc.name_en,
        "department": svc.department, "category": svc.category,
        "eligibility": svc.eligibility_en, "fee_inr": svc.fee_inr, "sla_days": svc.sla_days,
        "documents": docs,
    }


def compose_reply(svc: Service, lang: str) -> str:
    docs = "\n".join(f"• {sd.document.name(lang)}" for sd in svc.documents)
    return "\n".join([
        pick(APPLY_INTRO, lang).format(name=svc.name(lang)),
        docs,
        pick(FEE_TIME, lang).format(fee=svc.fee_inr, days=svc.sla_days),
        pick(NEXT_STEP, lang),
    ])


def popular(db: Session, lang: str, n: int = 4) -> list[dict]:
    codes = ["INC", "CST", "RES", "BIR"]
    svcs = db.query(Service).filter(Service.code.in_(codes)).all()
    return [{"id": s.id, "code": s.code, "name": s.name(lang)} for s in svcs][:n]


def _catalogue_text(db: Session, lang: str) -> str:
    """The catalogue as the model sees it, with official names in the citizen's language to copy verbatim."""
    lines = []
    for s in db.query(Service).all():
        docs = "; ".join(sd.document.name(lang) for sd in s.documents)
        name = s.name(lang) if lang == "en" else f"{s.name(lang)} ({s.name_en})"
        lines.append(f"{s.code} | {name} | {s.department} | eligibility: {s.eligibility_en} | "
                     f"documents: {docs} | fee ₹{s.fee_inr} | ~{s.sla_days} working days")
    return "\n".join(lines)


def _llm_chat(system: str, user: str, max_tokens: int = 2000) -> dict:
    url = (f"{config.AZURE_OPENAI_ENDPOINT}/openai/deployments/{config.AZURE_OPENAI_DEPLOYMENT}"
           f"/chat/completions?api-version={config.AZURE_OPENAI_API_VERSION}")
    body = {
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "response_format": {"type": "json_object"},
        # Reasoning models spend completion tokens on thinking first; keep it minimal so the
        # answer (especially in Telugu/Urdu, which use more tokens) is never cut off.
        "reasoning_effort": "minimal",
        "max_completion_tokens": max_tokens,
    }
    r = httpx.post(url, json=body, headers={"api-key": config.AZURE_OPENAI_API_KEY}, timeout=30)
    r.raise_for_status()
    return json.loads(r.json()["choices"][0]["message"]["content"])


def _llm_answer(db: Session, text: str, lang: str, hints: list[str] | None = None) -> dict:
    hint = f"Keyword search suggests: {', '.join(hints)} (verify against the question). " if hints else ""
    system = (
        "You are MeeSeva Saathi, a friendly assistant that helps citizens of Telangana use MeeSeva "
        "government services. Many users are first-time digital users, senior citizens or have limited "
        "literacy: use short sentences and simple words. Answer ONLY from the service catalogue below; "
        "never invent services, fees, documents or timelines. If the request does not match a service, "
        "say so politely and ask one clarifying question. Fees and timelines are sample data: say "
        "'confirm at the centre'. Citizens often describe a need, not a certificate: map it, e.g. "
        "scholarship or fee reimbursement -> Income Certificate (INC); proof of address for school or a "
        "connection -> Residence Certificate (RES); pension or claims after a death -> Death Certificate "
        "(DTH), then Family Member Certificate (FMC); job or site access -> Police Verification (PVC). "
        "Use the service and document names exactly as written in the catalogue; the English name in parentheses is for your reference only, do not repeat it. Never write service "
        "codes such as INC or DTH in the reply. Keep the reply under 90 words, in flowing sentences, not a form: "
        "first one warm sentence confirming what the citizen needs and which service it is, then the "
        "documents to carry, the fee and time, and one short next step. " + hint +
        f"Reply in {LANG_NAMES[lang]}. Return JSON: "
        '{"service_code": "<code from catalogue or null>", "reply": "<answer for the citizen>"}\n\n'
        "CATALOGUE (code | name | department | eligibility | documents | fee | time):\n" + _catalogue_text(db, lang)
    )
    return _llm_chat(system, text)


def answer(db: Session, text: str, lang_hint: str = "en") -> dict:
    """Answer a citizen question. Returns reply text, the matched service card, suggestions and the engine used."""
    lang = detect_lang(text, lang_hint)
    ranked = score_services(db, text)

    if config.ai_enabled():
        try:
            out = _llm_answer(db, text, lang, [svc.code for svc, _ in ranked[:3]])
            svc = db.query(Service).filter(Service.code == out.get("service_code")).first() if out.get("service_code") else None
            if lang != "en" and out.get("reply"):  # the model sometimes echoes the English reference name; citizens do not need it
                for s_ in db.query(Service).all():
                    out["reply"] = out["reply"].replace(f" ({s_.name_en})", "").replace(f"({s_.name_en})", "")
            return {
                "reply": out.get("reply") or (compose_reply(svc, lang) if svc else pick(NOT_FOUND, lang)),
                "lang": lang, "service": service_card(svc, lang) if svc else None,
                "suggestions": [] if svc else popular(db, lang),
                "confidence": 0.9 if svc else 0.0, "source": "ai",
            }
        except Exception as exc:  # network, quota, bad JSON: fall back, never fail the citizen
            log.warning("LLM unavailable, using rules engine: %s", exc)

    if ranked:
        svc, score = ranked[0]
        return {
            "reply": compose_reply(svc, lang), "lang": lang, "service": service_card(svc, lang),
            "suggestions": [{"id": s.id, "code": s.code, "name": s.name(lang)} for s, _ in ranked[1:4]],
            "confidence": round(min(score / 3, 1.0), 2), "source": "rules",
        }
    return {"reply": pick(NOT_FOUND, lang), "lang": lang, "service": None,
            "suggestions": popular(db, lang), "confidence": 0.0, "source": "rules"}


# ---------- feedback classification ----------

_NEG = ["not", "no ", "slow", "late", "wrong", "bad", "difficult", "confus", "error", "fail", "rude", "long queue",
        "లేదు", "ఆలస్యం", "కష్టం", "తప్పు", "नहीं", "देर", "मुश्किल", "गलत", "نہیں", "دیر", "مشکل", "غلط"]
_POS = ["good", "great", "easy", "fast", "thank", "helpful", "quick", "clear",
        "బాగుంది", "సులభం", "ధన్యవాదాలు", "अच्छा", "आसान", "धन्यवाद", "اچھا", "آسان", "شکریہ"]
_TOPICS = {
    "documents": ["document", "certificate copy", "upload", "పత్ర", "दस्तावेज़", "دستاویز"],
    "fees": ["fee", "charge", "money", "payment", "రుసుము", "शुल्क", "فیس"],
    "delay": ["slow", "late", "delay", "days", "waiting", "ఆలస్యం", "देर", "دیر"],
    "website": ["site", "portal", "page", "login", "otp", "app", "పోర్టల్", "पोर्टल", "پورٹل"],
    "language": ["language", "telugu", "hindi", "urdu", "english", "భాష", "भाषा", "زبان"],
    "staff": ["staff", "centre", "center", "officer", "queue", "సిబ్బంది", "कर्मचारी", "عملہ"],
}


def classify_feedback(comment: str, rating: int) -> tuple[str, str]:
    """Return (sentiment, topic). Uses the LLM when configured, otherwise a multilingual lexicon."""
    if config.ai_enabled() and comment.strip():
        try:
            out = _llm_chat(
                "Classify citizen feedback about a government service. Return JSON "
                '{"sentiment": "positive|neutral|negative", "topic": "documents|fees|delay|website|language|staff|other"}',
                f"Rating {rating}/5. Comment: {comment}", max_tokens=400)
            s, t = out.get("sentiment", "neutral"), out.get("topic", "other")
            if s in ("positive", "neutral", "negative") and t in list(_TOPICS) + ["other"]:
                return s, t
        except Exception as exc:
            log.warning("LLM classify failed, using lexicon: %s", exc)
    c = comment.lower()
    neg, pos = sum(w in c for w in _NEG), sum(w in c for w in _POS)
    if rating <= 2 or neg > pos:
        sentiment = "negative"
    elif rating >= 4 or pos > neg:
        sentiment = "positive"
    else:
        sentiment = "neutral"
    topic = next((t for t, words in _TOPICS.items() if any(w in c for w in words)), "other")
    return sentiment, topic
