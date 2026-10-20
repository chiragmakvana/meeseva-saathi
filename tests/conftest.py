import os
from pathlib import Path

TEST_DB = Path(__file__).parent / "test_saathi.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["DEMO_OTP_MODE"] = "true"
# Blank (not unset): python-dotenv never overrides existing variables, so a local .env with real keys
# cannot switch the tests onto the live AI. Tests exercise the offline rules engine unless they patch it.
for k in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT"):
    os.environ[k] = ""

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import engine  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import reset_and_seed  # noqa: E402


@pytest.fixture()
def client():
    reset_and_seed(engine)  # fresh database with sample data for every test
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def login(client):
    def _login(mobile="9876543210", lang="en", name="Test Citizen"):
        otp = client.post("/api/auth/request-otp", json={"mobile": mobile}).json()["demo_otp"]
        r = client.post("/api/auth/verify-otp", json={"mobile": mobile, "otp": otp, "name": name, "preferred_lang": lang})
        assert r.status_code == 200, r.text
        return {"Authorization": f"Bearer {r.json()['token']}"}
    return _login


def pytest_sessionfinish(session, exitstatus):
    engine.dispose()
    TEST_DB.unlink(missing_ok=True)
