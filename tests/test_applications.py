"""Applications: create, read, update, delete, checklist and submit rules."""


def _service_id(client, code):
    return next(s["id"] for s in client.get("/api/services").json() if s["code"] == code)


def test_create_application_builds_checklist(client, login):
    h = login()
    r = client.post("/api/applications", json={"service_id": _service_id(client, "INC"), "applicant_name": "Ravi Kumar"}, headers=h)
    assert r.status_code == 201
    a = r.json()
    assert a["status"] == "draft" and a["reference_no"].startswith("MS")
    assert len(a["checklist"]) == 4 and not a["ready"]
    assert a["status_explained"]["meaning"]


def test_cannot_submit_with_missing_documents(client, login):
    h = login()
    a = client.post("/api/applications", json={"service_id": _service_id(client, "RES"), "applicant_name": "Ravi"}, headers=h).json()
    r = client.post(f"/api/applications/{a['id']}/submit", headers=h)
    assert r.status_code == 422 and len(r.json()["detail"]["missing"]) == 3


def test_tick_all_and_submit(client, login):
    h = login()
    a = client.post("/api/applications", json={"service_id": _service_id(client, "RES"), "applicant_name": "Ravi"}, headers=h).json()
    for item in a["checklist"]:
        client.put(f"/api/applications/{a['id']}/checklist/{item['id']}", json={"provided": True}, headers=h)
    r = client.post(f"/api/applications/{a['id']}/submit", headers=h)
    assert r.status_code == 200 and r.json()["status"] == "submitted"
    # once submitted it is locked
    assert client.patch(f"/api/applications/{a['id']}", json={"applicant_name": "Other"}, headers=h).status_code == 409
    assert client.delete(f"/api/applications/{a['id']}", headers=h).status_code == 409


def test_update_list_and_delete_draft(client, login):
    h = login()
    a = client.post("/api/applications", json={"service_id": _service_id(client, "BIR"), "applicant_name": "Baby Kumar"}, headers=h).json()
    upd = client.patch(f"/api/applications/{a['id']}", json={"purpose": "School admission"}, headers=h).json()
    assert upd["purpose"] == "School admission"
    assert len(client.get("/api/applications", headers=h).json()) == 1
    assert client.delete(f"/api/applications/{a['id']}", headers=h).status_code == 204
    assert client.get("/api/applications", headers=h).json() == []


def test_citizens_cannot_see_each_others_applications(client, login):
    h1 = login(mobile="9876543210")
    a = client.post("/api/applications", json={"service_id": _service_id(client, "INC"), "applicant_name": "Ravi"}, headers=h1).json()
    h2 = login(mobile="9123456780")
    assert client.get(f"/api/applications/{a['id']}", headers=h2).status_code == 404


def test_validation_errors(client, login):
    h = login()
    assert client.post("/api/applications", json={"service_id": 9999, "applicant_name": "Ravi"}, headers=h).status_code == 422
    assert client.post("/api/applications", json={"service_id": 1, "applicant_name": "R"}, headers=h).status_code == 422
