from fastapi import APIRouter

from app.errors import ServiceError
from app.schemas import TestEmailOut
from app.services.notification_service import Notification, get_notification_service

router = APIRouter(prefix="/settings", tags=["settings"])


@router.post("/test-email", response_model=TestEmailOut)
def test_email():
    notifier = get_notification_service()
    try:
        notifier.send(Notification(subject="ApplyForge test notification", body="Notifications are working."))
    except Exception as exc:  # noqa: BLE001
        raise ServiceError(502, f"Sending failed ({type(exc).__name__}). Check SMTP settings.") from exc
    detail = "Recorded by the mock notifier (SMTP not configured)" if notifier.mode == "mock" else "Email sent"
    return TestEmailOut(sent=True, mode=notifier.mode, detail=detail)
