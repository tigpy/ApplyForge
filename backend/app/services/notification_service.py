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
    when = (app.submitted_at or app.updated_at).strftime("%d %b %Y %H:%M")
    resume_name = app.resume.filename if app.resume else "None"
    status_str = str(app.status)
    if status_str == "APPLIED":
        subject = f"Applied: {app.job.title} at {app.job.company}"
        body = (
            "Applied Successfully\n"
            "Application submitted successfully.\n\n"
            f"Company: {app.job.company}\n"
            f"Role: {app.job.title}\n"
            f"Resume used: {resume_name}\n"
            f"Match: {app.match_score}%\n"
            f"Status: Applied\n"
            f"Date: {when}\n"
            f"URL: {app.application_url}"
        )
    else:
        subject = f"Application {status_str}: {app.job.title} at {app.job.company}"
        reason = app.failure_reason or "Requirements could not be satisfied"
        body = (
            "Application could not be completed.\n\n"
            f"Company: {app.job.company}\n"
            f"Role: {app.job.title}\n"
            f"Resume used: {resume_name}\n"
            f"Match: {app.match_score}%\n"
            f"Status: {status_str}\n"
            f"Reason: {reason}\n"
            f"URL: {app.application_url}"
        )
    return Notification(subject=subject, body=body)
