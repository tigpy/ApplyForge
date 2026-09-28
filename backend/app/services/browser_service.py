"""Playwright wrapper. The ONLY module that imports playwright. Generic and UNVERIFIED against real sites.

Rules: validate the URL first, never bypass CAPTCHA/MFA/bot checks, and only report a confirmation
when the page actually says the application was received.
"""
from pathlib import Path

from app.security import validate_external_url

_BLOCKER_SELECTORS = (
    'iframe[src*="recaptcha"], iframe[src*="hcaptcha"], iframe[src*="challenges.cloudflare"], '
    ".g-recaptcha, .h-captcha, .cf-turnstile"
)
_BLOCKER_PHRASES = ("verify you are human", "captcha", "verification code", "two-factor", "multi-factor")
_CONFIRM_PHRASES = ("thank you for applying", "application received", "application submitted",
                    "successfully submitted", "we have received your application")
_FIELD_JS = """() => [...document.querySelectorAll(
  'input:not([type=hidden]):not([type=submit]):not([type=button]), textarea, select')].map((el, i) => {
  const lab = (el.id && document.querySelector('label[for="' + el.id + '"]')?.innerText)
    || el.getAttribute('aria-label') || el.placeholder || el.name || '';
  const tag = el.tagName.toLowerCase();
  return {ref: String(i), name: el.name || el.id || String(i), label: lab.trim(),
          type: tag === 'select' ? 'select' : tag === 'textarea' ? 'textarea' : (el.type || 'text'),
          required: el.required, options: tag === 'select' ? [...el.options].map(o => o.text) : []};
})"""
_FIELD_SELECTOR = ('input:not([type=hidden]):not([type=submit]):not([type=button]), textarea, select')


class BrowserAutomationService:
    def __init__(self, headless: bool = True, timeout_ms: int = 20000) -> None:
        self._headless = headless
        self._timeout = timeout_ms
        self._pw = self._browser = self._page = None

    def _ensure_page(self):
        if self._page is None:
            from playwright.sync_api import sync_playwright

            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.launch(headless=self._headless)
            self._page = self._browser.new_page()
            self._page.set_default_timeout(self._timeout)
        return self._page

    def goto(self, url: str) -> None:
        validate_external_url(url)  # raises ValueError for private/invalid targets
        self._ensure_page().goto(url, wait_until="domcontentloaded")

    def detect_blocker(self) -> str | None:
        page = self._ensure_page()
        if page.locator(_BLOCKER_SELECTORS).count() > 0:
            return "CAPTCHA / bot verification present"
        body = page.inner_text("body").lower()
        for phrase in _BLOCKER_PHRASES:
            if phrase in body:
                return f"Verification step detected ('{phrase}')"
        return None

    def extract_fields(self) -> list[dict]:
        return self._ensure_page().evaluate(_FIELD_JS)

    def _el(self, ref: str):
        return self._ensure_page().locator(_FIELD_SELECTOR).nth(int(ref))

    def fill(self, ref: str, field_type: str, value: str) -> None:
        el = self._el(ref)
        if field_type == "select":
            try:
                el.select_option(label=value)
            except Exception:
                try:
                    el.select_option(value=value)
                except Exception:
                    el.select_option(index=1)
        else:
            el.fill(value)

    def upload(self, ref: str, path: Path) -> None:
        self._el(ref).set_input_files(str(path))

    def submit_and_confirm(self) -> str | None:
        page = self._ensure_page()
        page.locator('button[type=submit], input[type=submit]').first.click()
        try:
            page.wait_for_load_state("networkidle", timeout=4000)
        except Exception:
            pass
        body = page.inner_text("body").lower()
        for phrase in _CONFIRM_PHRASES:
            if phrase in body:
                return f"Site confirmation: '{phrase}'"
        return None  # no explicit confirmation -> caller must NOT mark APPLIED

    def close(self) -> None:
        for closer in (self._browser and self._browser.close, self._pw and self._pw.stop):
            try:
                if closer:
                    closer()
            except Exception:  # noqa: BLE001 - best-effort cleanup
                pass
        self._pw = self._browser = self._page = None
