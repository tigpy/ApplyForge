"""Adapter from the ApplicationConnector contract to BrowserAutomationService (Playwright).

Supports ATS-specific delegation (Greenhouse, Lever) with generic fallback and
application-page sanity checks.
"""
import logging
from pathlib import Path
from urllib.parse import urlparse

from app.connectors.base import ApplicationConnector, FormField
from app.connectors.greenhouse import GreenhouseApplicationConnector
from app.connectors.lever import LeverApplicationConnector
from app.services.browser_service import BrowserAutomationService

log = logging.getLogger(__name__)


class PlaywrightApplicationConnector(ApplicationConnector):
    name = "playwright"

    def __init__(self, headless: bool = True, browser: BrowserAutomationService | None = None) -> None:
        self._browser = browser or BrowserAutomationService(headless=headless)
        self._active_connector: ApplicationConnector | None = None
        self._current_url = ""

    def _get_domain(self) -> str:
        curr = self._browser.get_url() or self._current_url
        try:
            return urlparse(curr).netloc or "unknown"
        except Exception:
            return "unknown"

    def _is_valid_application_form(self, fields: list[dict] | list[FormField]) -> bool:
        """Sanity check: Ensures the page is an actual application form, not a job listing or portal."""
        if not fields:
            return False

        has_candidate_field = False
        non_search_fields = 0

        for item in fields:
            label = item.label if hasattr(item, "label") else item.get("label", "")
            name = item.name if hasattr(item, "name") else item.get("name", "")
            ftype = item.type if hasattr(item, "type") else item.get("type", "")
            combined = f"{label} {name}".lower()

            if any(k in combined for k in ("search", "find job", "newsletter", "subscribe")):
                continue

            non_search_fields += 1
            if ftype == "file" or any(k in combined for k in ("resume", "cv", "email", "name", "phone", "first", "last", "linkedin", "clearance")):
                has_candidate_field = True

        return has_candidate_field and non_search_fields >= 1

    def open(self, url: str) -> None:
        self._current_url = url
        self._browser.goto(url)

        # Detect if destination is an ATS platform
        curr_url = self._browser.get_url() or url
        page_html = ""
        try:
            page_html = self._browser._ensure_page().content()
        except Exception:
            pass

        if GreenhouseApplicationConnector.matches(curr_url, page_html):
            log.info("Greenhouse ATS detected for %s; delegating to Greenhouse connector", curr_url)
            self._active_connector = GreenhouseApplicationConnector(browser=self._browser)
        elif LeverApplicationConnector.matches(curr_url, page_html):
            log.info("Lever ATS detected for %s; delegating to Lever connector", curr_url)
            self._active_connector = LeverApplicationConnector(browser=self._browser)
        else:
            self._active_connector = None

    def get_current_url(self) -> str:
        return self._browser.get_url()

    def detect_blocker(self) -> str | None:
        if self._active_connector:
            return self._active_connector.detect_blocker()

        blocker = self._browser.detect_blocker()
        if blocker:
            return blocker

        # Sanity check for generic pages
        raw_fields = self._browser.extract_fields()
        if not self._is_valid_application_form(raw_fields):
            domain = self._get_domain()
            return f"Unsupported application platform: {domain} (not an application form)"

        return None

    def detect_page_state(self) -> tuple[str, str | None]:
        if self._active_connector:
            return self._active_connector.detect_page_state()

        page_type, reason = self._browser.detect_page_state()
        if page_type in ("CAPTCHA_DETECTED", "CLOUDFLARE_DETECTED", "LOGIN_REQUIRED", "ALREADY_APPLIED"):
            return page_type, reason

        raw_fields = self._browser.extract_fields()
        if not self._is_valid_application_form(raw_fields):
            domain = self._get_domain()
            return "UNSUPPORTED_FORM", f"Unsupported application platform: {domain} (not an application form)"

        return page_type, reason

    def extract_fields(self) -> list[FormField]:
        if self._active_connector:
            return self._active_connector.extract_fields()

        raw_fields = self._browser.extract_fields()
        if not self._is_valid_application_form(raw_fields):
            return []

        return [FormField(**f) for f in raw_fields]

    def fill_field(self, field: FormField, value: str) -> None:
        if self._active_connector:
            self._active_connector.fill_field(field, value)
        else:
            self._browser.fill(field.ref, field.type, value)

    def upload_resume(self, field: FormField, path: Path) -> None:
        if self._active_connector:
            self._active_connector.upload_resume(field, path)
        else:
            self._browser.upload(field.ref, path)

    def submit(self) -> str | None:
        if self._active_connector:
            return self._active_connector.submit()
        return self._browser.submit_and_confirm()

    def close(self) -> None:
        if self._active_connector:
            self._active_connector.close()
        self._browser.close()
