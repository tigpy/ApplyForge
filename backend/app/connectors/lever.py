"""Lever ATS Application Connector.

Handles Lever-hosted application pages (jobs.lever.co or embedded Lever forms).
"""
import logging
from pathlib import Path

from app.connectors.base import ApplicationConnector, FormField
from app.services.browser_service import BrowserAutomationService

log = logging.getLogger(__name__)

_LEVER_CONFIRM_PHRASES = (
    "thank you for applying",
    "application submitted",
    "we have received your application",
    "your application has been sent",
    "thank you for your submission",
    "thanks for applying",
)


class LeverApplicationConnector(ApplicationConnector):
    name = "lever"

    def __init__(self, headless: bool = True, browser: BrowserAutomationService | None = None) -> None:
        self._browser = browser or BrowserAutomationService(headless=headless)
        self._owns_browser = browser is None
        self._url = ""

    @classmethod
    def matches(cls, url: str, html: str = "") -> bool:
        """Determines if the URL or page HTML belongs to Lever ATS."""
        low_url = url.lower()
        if "jobs.lever.co" in low_url or "lever.co" in low_url:
            return True
        low_html = (html or "").lower()
        if "action=\"https://jobs.lever.co" in low_html or "id=\"application-form\"" in low_html:
            return True
        if "class=\"application-form\"" in low_html or "class=\"template-btn-submit\"" in low_html:
            return True
        return False

    def open(self, url: str) -> None:
        self._url = url
        self._browser.goto(url)

    def get_current_url(self) -> str:
        return self._browser.get_url()

    def detect_blocker(self) -> str | None:
        return self._browser.detect_blocker()

    def detect_page_state(self) -> tuple[str, str | None]:
        page = self._browser._ensure_page()
        blocker = self._browser.detect_blocker()
        if blocker:
            return "BLOCKED", blocker

        body = page.inner_text("body").lower() if page.locator("body").count() > 0 else ""
        for phrase in _LEVER_CONFIRM_PHRASES:
            if phrase in body:
                return "SUCCESSFUL_SUBMISSION", f"Lever confirmation: '{phrase}'"

        if page.locator('#application-form, .application-form, form[action*="lever.co"]').count() > 0:
            return "FORM_FOUND", None

        field_count = page.locator('input:not([type=hidden]), textarea, select').count()
        if field_count >= 2:
            return "FORM_FOUND", None

        return "UNSUPPORTED_FORM", "Lever application form not found on page"

    def extract_fields(self) -> list[FormField]:
        """Extract fields using Lever-specific identifiers and generic fallback."""
        page = self._browser._ensure_page()
        fields: list[FormField] = []

        standard_mappings = [
            ('input[name="name"]', "name", "Full Name", "text", True),
            ('input[name="email"]', "email", "Email", "email", True),
            ('input[name="phone"]', "phone", "Phone", "tel", False),
            ('input[name="org"]', "org", "Current Company", "text", False),
            ('input[name="urls[LinkedIn]"]', "urls[LinkedIn]", "LinkedIn URL", "url", False),
            ('input[name="urls[GitHub]"]', "urls[GitHub]", "GitHub URL", "url", False),
            ('input[name="urls[Portfolio]"]', "urls[Portfolio]", "Portfolio URL", "url", False),
            ('input[name="resume"], #resume-upload-input, input[type="file"]', "resume", "Resume", "file", True),
            ('textarea[name="comments"]', "comments", "Additional Information", "textarea", False),
        ]

        found_names = set()
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
                ))
                found_names.add(name)

        generic_fields = self._browser.extract_fields()
        for gf in generic_fields:
            if gf.get("name") and gf["name"] in found_names:
                continue
            fields.append(FormField(**gf))

        return fields

    def fill_field(self, field: FormField, value: str) -> None:
        page = self._browser._ensure_page()
        if field.ref.startswith("input") or field.ref.startswith("textarea") or field.ref.startswith("#"):
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
        if field.ref.startswith("input") or field.ref.startswith("#"):
            page.locator(field.ref).first.set_input_files(str(path))
        else:
            self._browser.upload(field.ref, path)

    def submit(self) -> str | None:
        page = self._browser._ensure_page()
        submit_btn = page.locator(
            '#btn-submit, button.template-btn-submit, button[type=submit], input[type=submit], button:has-text("Submit Application")'
        ).first

        if submit_btn.count() > 0:
            submit_btn.click()
        else:
            page.keyboard.press("Enter")

        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass

        body = page.inner_text("body").lower() if page.locator("body").count() > 0 else ""
        for phrase in _LEVER_CONFIRM_PHRASES:
            if phrase in body:
                return f"Lever confirmation: '{phrase}'"
        return None

    def close(self) -> None:
        if self._owns_browser:
            self._browser.close()
