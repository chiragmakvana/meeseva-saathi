"""Login with mobile + OTP, sessions and authorisation."""


def test_invalid_mobile_rejected(client):
    r = client.post("/api/auth/request-otp", json={"mobile": "12345"})
    assert r.status_code == 422


def test_login_with_valid_otp_creates_account(client, login):
    headers = login(mobile="9876543210", lang="te", name="Ravi")
    me = client.get("/api/auth/me", headers=headers).json()
    assert me["mobile"] == "9876543210" and me["name"] == "Ravi" and me["preferred_lang"] == "te"
    assert me["role"] == "citizen"


def test_plus91_prefix_accepted(client):
    r = client.post("/api/auth/request-otp", json={"mobile": "+91 98765 43210"})
    assert r.status_code == 200


def test_wrong_otp_rejected(client):
    client.post("/api/auth/request-otp", json={"mobile": "9876543210"})
    r = client.post("/api/auth/verify-otp", json={"mobile": "9876543210", "otp": "000000"})
    assert r.status_code == 401


def test_otp_cannot_be_reused(client):
    otp = client.post("/api/auth/request-otp", json={"mobile": "9876543210"}).json()["demo_otp"]
    assert client.post("/api/auth/verify-otp", json={"mobile": "9876543210", "otp": otp}).status_code == 200
    assert client.post("/api/auth/verify-otp", json={"mobile": "9876543210", "otp": otp}).status_code == 401


def test_otp_locked_after_five_wrong_attempts(client):
    otp = client.post("/api/auth/request-otp", json={"mobile": "9876543210"}).json()["demo_otp"]
    for _ in range(5):
        client.post("/api/auth/verify-otp", json={"mobile": "9876543210", "otp": "111111" if otp != "111111" else "222222"})
    assert client.post("/api/auth/verify-otp", json={"mobile": "9876543210", "otp": otp}).status_code == 401


def test_protected_routes_need_login(client):
    assert client.get("/api/applications").status_code == 401
    assert client.get("/api/applications", headers={"Authorization": "Bearer forged.token"}).status_code == 401


def test_profile_update(client, login):
    h = login()
    r = client.patch("/api/auth/me", json={"preferred_lang": "ur", "district_id": 1}, headers=h)
    assert r.status_code == 200 and r.json()["preferred_lang"] == "ur"
    assert client.patch("/api/auth/me", json={"district_id": 999}, headers=h).status_code == 422
