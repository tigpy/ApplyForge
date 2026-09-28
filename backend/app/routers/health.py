from fastapi import APIRouter

from app.ai.client import get_ai_provider
from app.config import settings
from app.schemas import HealthOut
from app.services.notification_service import get_notification_service

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(
        status="ok", version="0.1.0", ai_provider=get_ai_provider().name,
        application_connector=settings.application_connector, notification_mode=get_notification_service().mode,
    )
