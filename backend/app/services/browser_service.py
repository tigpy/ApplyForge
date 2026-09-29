"""Playwright wrapper. The ONLY module that imports playwright.

Safety & Verification Rules:
- Validate URL before navigation.
- NEVER bypass CAPTCHA, Cloudflare, or anti-bot checks.
- On blocker detection, immediately halt and report BLOCKED.
- Detect login-required, already-applied, and closed jobs.
- Only report confirmation when the site explicitly confirms application receipt.
"""
import logging
from enum import Enum
from pathlib import Path

from app.security import validate_external_url

log = logging.getLogger(__name__)


class PageType(str, Enum):
    FORM_FOUND = "FORM_FOUND"
    ALREADY_APPLIED = "ALREADY_APPLIED"
    LOGIN_REQUIRED = "LOGIN_REQUIRED"
    CAPTCHA_DETECTED = "CAPTCHA_DETECTED"
    CLOUDFLARE_DETECTED = "CLOUDFLARE_DETECTED"
    UNSUPPORTED_FORM = "UNSUPPORTED_FORM"
    SUCCESSFUL_SUBMISSION = "SUCCESSFUL_SUBMISSION"
    UNKNOWN_FAILURE = "UNKNOWN_FAILURE"


_CAPTCHA_SELECTORS = (
    'iframe[src*="recaptcha"], iframe[src*="hcaptcha"], iframe[src*="arkose"], iframe[src*="geetest"], '
    ".g-recaptcha, .h-captcha, div[id*='captcha'], div[class*='captcha']"
)
_CLOUDFLARE_SELECTORS = (
    'iframe[src*="challenges.cloudflare"], .cf-turnstile, div[class*="cf-turnstile"], '
    "#cf-challenge-running, #challenge-form, #challenge-stage"
)

_CAPTCHA_PHRASES = (
    "verify you are human", "complete the captcha", "security check to continue",
    "unusual traffic from your computer network", "solve the challenge", "arkose labs",
    "please confirm you are a human"
)
_CLOUDFLARE_PHRASES = (
    "checking your browser", "just a moment...", "attention required! | cloudflare",
    "cloudflare turnstile", "performance & security by cloudflare"
)
_ALREADY_APPLIED_PHRASES = (
    "you have already applied", "application already submitted", "already applied to this job",
    "already applied for this position", "application on file for this position",
    "already submitted an application", "we have already received an application from you"
)
_LOGIN_REQUIRED_PHRASES = (
    "sign in to apply", "log in to apply", "login to continue", "please log in to apply",
    "you must be signed in to apply", "create an account to apply", "sign in with linkedin to apply"
)
_CLOSED_JOB_PHRASES = (
    "this job is no longer available", "job posting has expired", "no longer accepting applications",
    "this position has been filled", "this job has been closed", "job not found"
)
_CONFIRM_PHRASES = (
    "thank you for applying", "application received", "application submitted",
    "successfully submitted", "we have received your application", "application has been submitted",
    "thank you for your submission", "your application was sent"
)

_FIELD_JS = """() => {
  const elements = [...document.querySelectorAll(
    'input:not([type=hidden]):not([type=submit]):not([type=button]):not([type=reset]), textarea, select'
  )];

  return elements.map((el, i) => {
    let lab = '';
    // 1. Associated <label for="...">
    if (el.id) {
      try {
        const l = document.querySelector('label[for="' + CSS.escape(el.id) + '"]');
        if (l) lab = l.innerText;
      } catch (e) {}
    }
    // 2. Parent label
    if (!lab) {
      const p = el.closest('label');
      if (p) lab = p.innerText;
    }
    // 3. aria-labelledby
    if (!lab && el.getAttribute('aria-labelledby')) {
      try {
        const refEl = document.getElementById(el.getAttribute('aria-labelledby'));
        if (refEl) lab = refEl.innerText;
      } catch (e) {}
    }
    // 4. aria-label
    if (!lab) lab = el.getAttribute('aria-label') || '';
    // 5. Parent fieldset legend
    if (!lab) {
      const fs = el.closest('fieldset');
      if (fs) {
        const leg = fs.querySelector('legend');
        if (leg) lab = leg.innerText;
      }
    }
    // 6. Preceding sibling or paragraph
    if (!lab) {
      let prev = el.previousElementSibling;
      while (prev && !lab) {
        if (['label', 'p', 'span', 'div', 'b', 'strong'].includes(prev.tagName.toLowerCase())) {
          lab = prev.innerText;
        }
        prev = prev.previousElementSibling;
      }
    }
    // 7. Fallbacks
    if (!lab) lab = el.placeholder || el.name || el.id || '';

    const tag = el.tagName.toLowerCase();
    const type = tag === 'select' ? 'select' : tag === 'textarea' ? 'textarea' : (el.type || 'text');

    let options = [];
    if (tag === 'select') {
      options = [...el.options].map(o => (o.text || o.value || '').trim()).filter(Boolean);
    } else if (type === 'radio' && el.name) {
      try {
        const group = [...document.querySelectorAll('input[type=radio][name="' + CSS.escape(el.name) + '"]')];
        options = group.map(r => {
          let rLab = '';
          if (r.id) {
            const l = document.querySelector('label[for="' + CSS.escape(r.id) + '"]');
            if (l) rLab = l.innerText;
          }
          if (!rLab) {
            const p = r.closest('label');
            if (p) rLab = p.innerText;
          }
          return (rLab || r.value || '').trim();
        }).filter(Boolean);
      } catch (e) {}
    }

    return {
      ref: String(i),
      name: el.name || el.id || String(i),
      label: lab.trim(),
      type: type,
      required: Boolean(el.required || el.getAttribute('aria-required') === 'true'),
      options: options,
      placeholder: el.placeholder || '',
      id: el.id || ''
    };
  });
}"""

_FIELD_SELECTOR = "input:not([type=hidden]):not([type=submit]):not([type=button]):not([type=reset]), textarea, select"


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
        validate_external_url(url)
        self._ensure_page().goto(url, wait_until="domcontentloaded")

    def get_url(self) -> str:
        return self._ensure_page().url if self._page else ""

    def detect_page_state(self) -> tuple[PageType, str | None]:
        """Classify page state: Form found, Captcha, Cloudflare, Login Required, Already Applied, Closed, etc."""
        page = self._ensure_page()

        # 1. Cloudflare challenge detection
        if page.locator(_CLOUDFLARE_SELECTORS).count() > 0:
            return PageType.CLOUDFLARE_DETECTED, "Cloudflare challenge detected: automated submission is blocked"

        body_text = page.inner_text("body").lower() if page.locator("body").count() > 0 else ""

        for phrase in _CLOUDFLARE_PHRASES:
            if phrase in body_text:
                return PageType.CLOUDFLARE_DETECTED, f"Cloudflare challenge detected ('{phrase}')"

        # 2. CAPTCHA detection
        if page.locator(_CAPTCHA_SELECTORS).count() > 0:
            return PageType.CAPTCHA_DETECTED, "CAPTCHA verification detected: automated submission is blocked"

        for phrase in _CAPTCHA_PHRASES:
            if phrase in body_text:
                return PageType.CAPTCHA_DETECTED, f"CAPTCHA verification detected ('{phrase}')"

        # 3. Already applied detection
        for phrase in _ALREADY_APPLIED_PHRASES:
            if phrase in body_text:
                return PageType.ALREADY_APPLIED, f"Already applied on site ('{phrase}')"

        # 4. Confirmation / already submitted page
        for phrase in _CONFIRM_PHRASES:
            if phrase in body_text:
                return PageType.SUCCESSFUL_SUBMISSION, f"Confirmation detected ('{phrase}')"

        # 5. Login required detection
        curr_url = page.url.lower()
        if any(auth_path in curr_url for auth_path in ("/login", "/signin", "/auth/login")):
            return PageType.LOGIN_REQUIRED, "Login required to access application page"

        for phrase in _LOGIN_REQUIRED_PHRASES:
            if phrase in body_text:
                return PageType.LOGIN_REQUIRED, f"Login required ('{phrase}')"

        # 6. Closed / Expired job
        for phrase in _CLOSED_JOB_PHRASES:
            if phrase in body_text:
                return PageType.UNSUPPORTED_FORM, f"Job posting unavailable ('{phrase}')"

        # 7. Form found check
        field_count = page.locator(_FIELD_SELECTOR).count()
        if field_count > 0:
            return PageType.FORM_FOUND, None

        return PageType.UNSUPPORTED_FORM, "No interactive application form fields detected on page"

    def detect_blocker(self) -> str | None:
        """Returns descriptive blocker reason if CAPTCHA, Cloudflare, Login, or already-applied is present."""
        page_type, reason = self.detect_page_state()
        if page_type in (
            PageType.CAPTCHA_DETECTED,
            PageType.CLOUDFLARE_DETECTED,
            PageType.LOGIN_REQUIRED,
            PageType.ALREADY_APPLIED,
            PageType.UNSUPPORTED_FORM,
        ):
            return reason
        return None

    def extract_fields(self) -> list[dict]:
        return self._ensure_page().evaluate(_FIELD_JS)

    def _el(self, ref: str):
        return self._ensure_page().locator(_FIELD_SELECTOR).nth(int(ref))

    def fill(self, ref: str, field_type: str, value: str) -> None:
        page = self._ensure_page()
        el = self._el(ref)
        val_str = str(value).strip()

        if field_type == "select":
            # Select matching option: exact text, case-insensitive, or value
            selected = False
            try:
                el.select_option(label=val_str)
                selected = True
            except Exception:
                pass

            if not selected:
                try:
                    # Look for option text containing value or matching case-insensitively
                    opts = el.locator("option").all_inner_texts()
                    match = next((o for o in opts if val_str.lower() in o.lower()), None)
                    if match:
                        el.select_option(label=match)
                        selected = True
                except Exception:
                    pass

            if not selected:
                try:
                    el.select_option(value=val_str)
                    selected = True
                except Exception:
                    pass

            if not selected:
                try:
                    el.select_option(index=1)
                except Exception:
                    pass

        elif field_type == "checkbox":
            val_lower = val_str.lower()
            if val_lower in ("yes", "true", "1", "agree", "on", "checked"):
                el.check()
            else:
                el.uncheck()

        elif field_type == "radio":
            # For radio, check this radio or locate matching radio in the group
            try:
                name = el.get_attribute("name")
                if name:
                    # Look for radio with matching value or label
                    group = page.locator(f'input[type=radio][name="{name}"]')
                    matched = False
                    for i in range(group.count()):
                        r = group.nth(i)
                        r_val = r.get_attribute("value") or ""
                        if r_val.lower() == val_str.lower():
                            r.check()
                            matched = True
                            break
                    if not matched:
                        el.check()
                else:
                    el.check()
            except Exception:
                el.check()

        else:
            el.fill(val_str)

    def upload(self, ref: str, path: Path) -> None:
        if not path.exists():
            raise FileNotFoundError(f"Resume file not found at {path}")
        self._el(ref).set_input_files(str(path))

    def submit_and_confirm(self) -> str | None:
        page = self._ensure_page()
        # Look for standard submit button or button with submit-like text
        btn = page.locator(
            'button[type=submit], input[type=submit], button:has-text("Submit Application"), '
            'button:has-text("Submit"), button:has-text("Apply Now"), button:has-text("Apply")'
        ).first

        if btn.count() > 0:
            btn.click()
        else:
            # Fallback to pressing Enter on form
            page.keyboard.press("Enter")

        try:
            page.wait_for_load_state("networkidle", timeout=4000)
        except Exception:
            pass

        body = page.inner_text("body").lower() if page.locator("body").count() > 0 else ""
        for phrase in _CONFIRM_PHRASES:
            if phrase in body:
                return f"Site confirmation: '{phrase}'"
        return None

    def close(self) -> None:
        for closer in (self._browser and self._browser.close, self._pw and self._pw.stop):
            try:
                if closer:
                    closer()
            except Exception:
                pass
        self._pw = self._browser = self._page = None
