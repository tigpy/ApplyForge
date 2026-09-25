"""
Settings Router
"""
from fastapi import APIRouter
from packages.shared.config import settings

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/config")
def get_system_config():
    return {
        "app_name": settings.APP_NAME,
        "app_env": settings.APP_ENV,
        "database_url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "sqlite",
        "llm_provider": settings.LLM_PROVIDER,
        "ai_match_enabled": settings.AI_MATCH_ENABLED,
        "safe_mode": True,
        "zero_silent_submissions": True,
        "candidate_ground_truth": "Aryan Singh (Verified)"
    }
