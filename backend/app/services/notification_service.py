"""Notifications: real SMTP email or a mock that records messages in memory."""
import logging
import smtplib
from abc import ABC, abstractmethod
from email.message import EmailMessage

from pydantic import BaseModel

from app.config import settings

log = logging.getLogger(__name__)


class Notification(BaseModel):
    subject: str
    body: str


class NotificationService(ABC):
    mode: str

    @abstractmethod
    def send(self, notification: Notification) -> None: ...


class MockNotificationService(NotificationService):
    mode = "mock"
    sent: list[Notification] = []  # class-level so tests/dev can inspect

    def send(self, notification: Notification) -> None:
        MockNotificationService.sent.append(notification)
        log.info("Mock notification: %s", notification.subject)


class EmailNotificationService(NotificationService):
    mode = "email"

    def send(self, notification: Notification) -> None:
        msg = EmailMessage()
        msg["Subject"], msg["From"], msg["To"] = notification.subject, settings.smtp_username or settings.notification_email, settings.notification_email
        msg.set_content(notification.body)
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(msg)


def get_notification_service() -> NotificationService:
    configured = bool(settings.smtp_host and settings.notification_email)
    mode = settings.notification_mode.lower()
    if mode == "email" or (mode == "auto" and configured):
        return EmailNotificationService()
    return MockNotificationService()


def build_application_notification(app) -> Notification:
    """`app` is an Application ORM object with job and resume loaded."""
    when = (app.submitted_at or app.updated_at).strftime("%d %b %Y")
    body = (
        "Applied Successfully\n\n"
        f"Company: {app.job.company}\n"
        f"Role: {app.job.title}\n"
        f"Resume used: {app.resume.filename if app.resume else 'unknown'}\n"
        f"Match: {app.match_score}%\n"
        f"Application URL: {app.application_url}\n"
        f"Status: Applied\n"
        f"Date: {when}"
    )
    return Notification(subject=f"Applied: {app.job.title} at {app.job.company}", body=body)
