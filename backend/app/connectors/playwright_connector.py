"""Adapter from the ApplicationConnector contract to BrowserAutomationService (Playwright)."""
from pathlib import Path

from app.connectors.base import ApplicationConnector, FormField
from app.services.browser_service import BrowserAutomationService


class PlaywrightApplicationConnector(ApplicationConnector):
    name = "playwright"

    def __init__(self, headless: bool = True) -> None:
        self._browser = BrowserAutomationService(headless=headless)

    def open(self, url: str) -> None:
        self._browser.goto(url)

    def detect_blocker(self) -> str | None:
        return self._browser.detect_blocker()

    def extract_fields(self) -> list[FormField]:
        return [FormField(**f) for f in self._browser.extract_fields()]

    def fill_field(self, field: FormField, value: str) -> None:
        self._browser.fill(field.ref, field.type, value)

    def upload_resume(self, field: FormField, path: Path) -> None:
        self._browser.upload(field.ref, path)

    def submit(self) -> str | None:
        return self._browser.submit_and_confirm()

    def close(self) -> None:
        self._browser.close()
