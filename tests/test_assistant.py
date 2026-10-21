"""The multilingual assistant: language detection, service matching, AI path and safe fallback."""
import pytest

from app import assistant, config


@pytest.mark.parametrize("text,lang,code", [
    ("I need an income certificate for my scholarship", "en", "INC"),
    ("నాకు ఆదాయ ధృవీకరణ పత్రం కావాలి", "te", "INC"),
    ("मुझे जाति प्रमाण पत्र चाहिए", "hi", "CST"),
    ("مجھے پیدائش سرٹیفکیٹ چاہیے", "ur", "BIR"),
    ("police verification for my new job", "en", "PVC"),
    ("how do I pay my current bill", "en", "ELB"),
])
def test_matches_service_in_four_languages(client, text, lang, code):
    r = client.post("/api/assistant/ask", json={"text": text, "lang": "en"}).json()
    assert r["lang"] == lang
    assert r["service"]["code"] == code
    assert r["service"]["documents"], "answer should list the documents to carry"
    assert r["source"] == "rules"


def test_reply_written_in_detected_language(client):
    r = client.post("/api/assistant/ask", json={"text": "ఆదాయ ధృవీకరణ పత్రం", "lang": "en"}).json()
    assert "మీసేవ" in r["reply"]  # Telugu template used


def test_unknown_request_suggests_popular_services(client):
    r = client.post("/api/assistant/ask", json={"text": "how do I renew my passport", "lang": "en"}).json()
    assert r["service"] is None and len(r["suggestions"]) >= 3


def test_question_is_logged_for_insights(client, login):
    client.post("/api/assistant/ask", json={"text": "income certificate", "lang": "en"})
    client.post("/api/assistant/ask", json={"text": "something unrelated", "lang": "en"})
    off = login(mobile="9000000001")
    q = client.get("/api/admin/insights", headers=off).json()["queries"]
    assert q["total"] == 2 and q["unmatched"] == 1


def test_text_too_short_rejected(client):
    assert client.post("/api/assistant/ask", json={"text": "a", "lang": "en"}).status_code == 422


def test_detect_lang_scripts():
    assert assistant.detect_lang("hello") == "en"
    assert assistant.detect_lang("hello", "te") == "te"
    assert assistant.detect_lang("నమస్తే") == "te"
    assert assistant.detect_lang("नमस्ते") == "hi"
    assert assistant.detect_lang("سلام") == "ur"


def test_ai_engine_used_when_configured(client, monkeypatch):
    monkeypatch.setattr(config, "ai_enabled", lambda: True)
    monkeypatch.setattr(assistant, "_llm_answer", lambda db, text, lang, hints=None: {"service_code": "RES", "reply": "AI reply"})
    r = client.post("/api/assistant/ask", json={"text": "I moved to Hyderabad, need proof of address", "lang": "en"}).json()
    assert r["source"] == "ai" and r["service"]["code"] == "RES" and r["reply"] == "AI reply"


def test_falls_back_to_rules_when_ai_fails(client, monkeypatch):
    def boom(*_):
        raise TimeoutError("LLM down")
    monkeypatch.setattr(config, "ai_enabled", lambda: True)
    monkeypatch.setattr(assistant, "_llm_answer", boom)
    r = client.post("/api/assistant/ask", json={"text": "birth certificate", "lang": "en"}).json()
    assert r["source"] == "rules" and r["service"]["code"] == "BIR"


def test_echoed_names_and_codes_removed(client):
    from app.database import SessionLocal
    from app.models import Service
    with SessionLocal() as db:
        svcs = db.query(Service).all()
    text = "You need a Death Certificate (DTH) (service: Death Certificate) (confirm at the centre)."
    assert assistant._strip_echoes(text, svcs) == "You need a Death Certificate (confirm at the centre)."
