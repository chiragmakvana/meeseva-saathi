"""Officials' dashboard, status notifications and AI-tagged feedback."""


def _submitted_app(client, h):
    sid = next(s["id"] for s in client.get("/api/services").json() if s["code"] == "RES")
    a = client.post("/api/applications", json={"service_id": sid, "applicant_name": "Lakshmi"}, headers=h).json()
    for item in a["checklist"]:
        client.put(f"/api/applications/{a['id']}/checklist/{item['id']}", json={"provided": True}, headers=h)
    client.post(f"/api/applications/{a['id']}/submit", headers=h)
    return a


def test_citizen_cannot_open_dashboard(client, login):
    h = login()
    assert client.get("/api/admin/insights", headers=h).status_code == 403
    assert client.get("/api/admin/applications", headers=h).status_code == 403


def test_status_change_notifies_citizen_in_their_language(client, login):
    citizen = login(mobile="9876543210", lang="te")
    a = _submitted_app(client, citizen)
    official = login(mobile="9000000001")
    r = client.post(f"/api/admin/applications/{a['id']}/status",
                    json={"status": "needs_documents", "remarks": "Please bring the rent agreement."}, headers=official)
    assert r.status_code == 200
    n = client.get("/api/notifications", headers=citizen).json()
    assert n["unread"] == 1
    assert "అధికారికి" in n["items"][0]["body"] and "rent agreement" in n["items"][0]["body"]
    client.post(f"/api/notifications/{n['items'][0]['id']}/read", headers=citizen)
    assert client.get("/api/notifications", headers=citizen).json()["unread"] == 0
    # the citizen sees the plain-language explanation too
    detail = client.get(f"/api/applications/{a['id']}?lang=te", headers=citizen).json()
    assert detail["status"] == "needs_documents" and detail["remarks"]


def test_official_cannot_act_on_unsubmitted_draft(client, login):
    citizen = login()
    sid = client.get("/api/services").json()[0]["id"]
    a = client.post("/api/applications", json={"service_id": sid, "applicant_name": "Ravi"}, headers=citizen).json()
    official = login(mobile="9000000001")
    r = client.post(f"/api/admin/applications/{a['id']}/status", json={"status": "approved"}, headers=official)
    assert r.status_code == 409


def test_invalid_status_rejected(client, login):
    citizen = login()
    a = _submitted_app(client, citizen)
    official = login(mobile="9000000001")
    r = client.post(f"/api/admin/applications/{a['id']}/status", json={"status": "lost"}, headers=official)
    assert r.status_code == 422


def test_feedback_is_classified(client, login):
    h = login()
    neg = client.post("/api/feedback", json={"rating": 2, "comment": "Too slow, waited many days"}, headers=h).json()
    assert neg["sentiment"] == "negative" and neg["topic"] == "delay"
    pos = client.post("/api/feedback", json={"rating": 5, "comment": "చాలా సులభం, ధన్యవాదాలు"}, headers=h).json()
    assert pos["sentiment"] == "positive"
    official = login(mobile="9000000001")
    f = client.get("/api/admin/insights", headers=official).json()["feedback"]
    assert f["count"] == 2 and f["avg_rating"] == 3.5


def test_feedback_rating_validated(client, login):
    h = login()
    assert client.post("/api/feedback", json={"rating": 0}, headers=h).status_code == 422
    assert client.post("/api/feedback", json={"rating": 6}, headers=h).status_code == 422


def test_health_and_pages(client):
    assert client.get("/api/health").json()["status"] == "ok"
    assert "MeeSeva Saathi" in client.get("/").text
    assert "Officials" in client.get("/official").text
