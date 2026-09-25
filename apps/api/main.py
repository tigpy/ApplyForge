"""
FastAPI Application Entry Point
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from packages.shared.config import settings
from packages.domain.database import init_db, SessionLocal
from packages.documents.seed_data import seed_database
from apps.api.routers import (
    candidate, resumes, jobs, applications, audit, connectors, settings as settings_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    init_db()
    # Seed candidate ground-truth and default sources
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Production Job Application Automation Platform with Human Approval Guardrails",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(candidate.router, prefix="/api/v1")
app.include_router(resumes.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(applications.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
app.include_router(connectors.router, prefix="/api/v1")
app.include_router(settings_router.router, prefix="/api/v1")

web_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web")
if os.path.exists(web_dir):
    app.mount("/static", StaticFiles(directory=web_dir), name="static")

    @app.get("/")
    def serve_frontend_root():
        index_file = os.path.join(web_dir, "index.html")
        return FileResponse(index_file)
