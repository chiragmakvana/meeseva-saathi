"""Application settings, read from environment variables (see .env.example).

Nothing secret is hard-coded: the defaults below are only safe for local demos.
"""
import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./meeseva_saathi.db")

# Used to sign session tokens and hash OTPs. Always set a long random value outside local demos.
SECRET_KEY = os.getenv("SECRET_KEY", "local-demo-only-change-me")

# Demo mode returns the OTP in the API response because no SMS gateway is connected.
DEMO_OTP_MODE = os.getenv("DEMO_OTP_MODE", "true").lower() == "true"
OTP_TTL_SECONDS = 300
OTP_MAX_ATTEMPTS = 5
SESSION_MAX_AGE_SECONDS = 8 * 60 * 60

# Optional AI provider (Azure OpenAI). Without it the assistant uses the built-in rules engine.
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")


def ai_enabled() -> bool:
    return bool(AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY and AZURE_OPENAI_DEPLOYMENT)
