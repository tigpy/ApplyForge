"""Connector registry. Add new job boards / application adapters here."""
from app.config import settings
from app.connectors.base import ApplicationConnector, JobConnector
from app.connectors.mock import MockApplicationConnector, MockJobConnector
from app.connectors.public_feed import PublicFeedJobConnector

JOB_CONNECTORS: dict[str, type[JobConnector]] = {
    "mock": MockJobConnector,
    "public_feed": PublicFeedJobConnector,
}


def get_job_connector(name: str) -> JobConnector:
    try:
        return JOB_CONNECTORS[name]()
    except KeyError:
        raise ValueError(f"Unknown job connector '{name}'. Available: {', '.join(JOB_CONNECTORS)}") from None


def get_application_connector() -> ApplicationConnector:
    if settings.application_connector == "playwright":
        from app.connectors.playwright_connector import PlaywrightApplicationConnector

        return PlaywrightApplicationConnector(headless=settings.browser_headless)
    return MockApplicationConnector()
