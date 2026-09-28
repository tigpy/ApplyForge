from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.errors import ServiceError
from app.routers import applications, automation, health, jobs, profile, resumes
from app.routers import settings as settings_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="ApplyForge", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_methods=["*"], allow_headers=["*"],
)


@app.exception_handler(ServiceError)
async def service_error_handler(_req: Request, exc: ServiceError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


for r in (health.router, resumes.router, jobs.router, applications.router, profile.router, settings_router.router, automation.router):
    app.include_router(r, prefix="/api")
