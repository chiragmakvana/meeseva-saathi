"""MeeSeva Saathi: FastAPI application entry point.

Run:  uvicorn app.main:app --reload     (then open http://127.0.0.1:8000)
API docs: http://127.0.0.1:8000/docs
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app import config
from app.database import Base, SessionLocal, engine
from app.routers import admin, applications, assistant, auth, catalogue, engagement
from app.seed import seed

STATIC = Path(__file__).resolve().parent.parent / "static"
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("saathi")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
    log.info("MeeSeva Saathi ready (AI engine: %s)", "Azure OpenAI" if config.ai_enabled() else "built-in rules")
    yield


app = FastAPI(
    title="MeeSeva Saathi API",
    version="1.0.0",
    description="AI-assisted, multilingual guide to MeeSeva services (prototype; sample catalogue data).",
    lifespan=lifespan,
)

for r in (auth.router, catalogue.router, assistant.router, applications.router, engagement.router, admin.router):
    app.include_router(r)


@app.exception_handler(Exception)
async def unexpected_error(_: Request, exc: Exception):
    log.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Something went wrong. Please try again."})


@app.get("/api/health", tags=["system"])
def health():
    return {"status": "ok", "ai_engine": "azure-openai" if config.ai_enabled() else "rules"}


app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def citizen_app():
    return FileResponse(STATIC / "index.html")


@app.get("/official", include_in_schema=False)
def official_dashboard():
    return FileResponse(STATIC / "official.html")


@app.get("/manifest.webmanifest", include_in_schema=False)
def manifest():
    return FileResponse(STATIC / "manifest.webmanifest", media_type="application/manifest+json")
