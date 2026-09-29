"""Greenhouse ATS Application Connector.

Handles Greenhouse-hosted application pages (boards.greenhouse.io or embedded Greenhouse forms).
"""
import logging
from pathlib import Path
from urllib.parse import urlparse

from app.connectors.base import ApplicationConnector, FormField
from app.services.browser_service import BrowserAutomationService, PageType

log = logging.getLogger(__name__)

_GREENHOUSE_CONFIRM_PHRASES = (
    "thank you for applying",
    "your application was submitted",
    "your application has been received",
    "application submitted",
    "we have received your application",
    "thank you for your interest",
)


class GreenhouseApplicationConnector(ApplicationConnector):
    name = "greenhouse"

    def __init__(self, headless: bool = True, browser: BrowserAutomationService | None = None) -> None:
        self._browser = browser or BrowserAutomationService(headless=headless)
        self._owns_browser = browser is None
        self._url = ""

    @classmethod
    def matches(cls, url: str, html: str = "") -> bool:
        """Determines if the URL or page HTML belongs to Greenhouse ATS."""
        low_url = url.lower()
        if any(h in low_url for h in ("boards.greenhouse.io", "job-boards.greenhouse.io", "gh_jid=", "greenhouse.io")):
            return True
        low_html = (html or "").lower()
        if "action=\"https://boards.greenhouse.io" in low_html or "id=\"application_form\"" in low_html:
            return True
        if "id=\"apply_form\"" in low_html and "greenhouse" in low_html:
            return True
        return False

    def open(self, url: str) -> None:
        self._url = url
        self._browser.goto(url)

    def get_current_url(self) -> str:
        return self._browser.get_url()

    def detect_blocker(self) -> str | None:
        # Check standard CAPTCHA / bot challenge
        return self._browser.detect_blocker()

    def detect_page_state(self) -> tuple[str, str | None]:
        page = self._browser._ensure_page()
        # Check blockers
        blocker = self._browser.detect_blocker()
        if blocker:
            return "BLOCKED", blocker

        body = page.inner_text("body").lower() if page.locator("body").count() > 0 else ""
        for phrase in _GREENHOUSE_CONFIRM_PHRASES:
            if phrase in body:
                return "SUCCESSFUL_SUBMISSION", f"Greenhouse confirmation: '{phrase}'"

        # Check for Greenhouse form
        if page.locator('#application_form, #apply_form, form[action*="greenhouse.io"], form#application').count() > 0:
            return "FORM_FOUND", None

        # Check generic fields
        field_count = page.locator('input:not([type=hidden]), textarea, select').count()
        if field_count >= 2:
            return "FORM_FOUND", None

        return "UNSUPPORTED_FORM", "Greenhouse application form not found on page"

    def extract_fields(self) -> list[FormField]:
        """Extract fields using Greenhouse-aware identification and generic fallback."""
        page = self._browser._ensure_page()
        fields: list[FormField] = []

        # Standard Greenhouse inputs mapping: (id/selector, name, label, type, required)
        standard_mappings = [
            ("#first_name", "first_name", "First Name", "text", True),
            ("#last_name", "last_name", "Last Name", "text", True),
            ("#email", "email", "Email", "email", True),
            ("#phone", "phone", "Phone", "tel", False),
            ("#resume", "resume", "Resume", "file", True),
            ("#cover_letter", "cover_letter", "Cover Letter", "file", False),
        ]

        found_selectors = set()
        for sel, name, label, ftype, req in standard_mappings:
            loc = page.locator(sel)
            if loc.count() > 0:
                is_req = req or (loc.first.get_attribute("required") is not None)
                fields.append(FormField(
                    ref=sel,
                    name=name,
                    label=label,
                    type=ftype,
                    required=is_req,
                    id=sel.lstrip("#"),
                ))
                found_selectors.add(sel)

        # Extract remaining fields via BrowserAutomationService
        generic_fields = self._browser.extract_fields()
        for gf in generic_fields:
            # Avoid duplicating standard fields already captured
            if gf.get("id") and f"#{gf['id']}" in found_selectors:
                continue
            if gf.get("name") and any(f.name == gf["name"] for f in fields):
                continue
            fields.append(FormField(**gf))

        return fields

    def fill_field(self, field: FormField, value: str) -> None:
        page = self._browser._ensure_page()
        # If ref is a CSS selector
        if field.ref.startswith("#") or field.ref.startswith("input"):
            loc = page.locator(field.ref).first
            if field.type == "select":
                try:
                    loc.select_option(label=value)
                except Exception:
                    loc.select_option(value=value)
            elif field.type == "checkbox":
                if str(value).lower() in ("yes", "true", "1", "agree", "on"):
                    loc.check()
                else:
                    loc.uncheck()
            elif field.type == "radio":
                loc.check()
            else:
                loc.fill(value)
        else:
            self._browser.fill(field.ref, field.type, value)

    def upload_resume(self, field: FormField, path: Path) -> None:
        page = self._browser._ensure_page()
        if field.ref.startswith("#") or field.ref.startswith("input"):
            page.locator(field.ref).first.set_input_files(str(path))
        else:
            self._browser.upload(field.ref, path)

    def submit(self) -> str | None:
        page = self._browser._ensure_page()
        # Target Greenhouse submit button
        submit_btn = page.locator('#submit_app, input[type=submit]#submit_app, button[type=submit]#submit_app').first
        if submit_btn.count() == 0:
            submit_btn = page.locator('button[type=submit], input[type=submit], button:has-text("Submit Application")').first

        if submit_btn.count() > 0:
            submit_btn.click()
        else:
            page.keyboard.press("Enter")

        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass

        body = page.inner_text("body").lower() if page.locator("body").count() > 0 else ""
        for phrase in _GREENHOUSE_CONFIRM_PHRASES:
            if phrase in body:
                return f"Greenhouse confirmation: '{phrase}'"
        return None

    def close(self) -> None:
        if self._owns_browser:
            self._browser.close()
