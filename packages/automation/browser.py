"""
Playwright Browser Automation Layer for ApplyForge
Strictly compliant: No CAPTCHA/bot evasion, modular connector interface.
"""
from typing import Any, Dict, Optional
from packages.shared.logger import logger
from packages.shared.security import SecurityAuditor

class PlaywrightBrowserService:
    def __init__(self, headless: bool = True):
        self.headless = headless

    async def extract_page_job_content(self, url: str) -> Dict[str, Any]:
        """
        Navigates to permitted public job page, captures text, title, and metadata.
        Validates URL with SecurityAuditor first.
        """
        is_safe, reason = SecurityAuditor.validate_url(url)
        if not is_safe:
            raise ValueError(f"SSRF Safety Guard Blocked URL: {reason}")

        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                context = await browser.new_context(user_agent="ApplyForge-Verification/1.0")
                page = await context.new_page()
                
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                title = await page.title()
                content = await page.content()
                inner_text = await page.evaluate("() => document.body.innerText")
                
                await browser.close()
                return {
                    "url": url,
                    "title": title,
                    "text": inner_text,
                    "html_length": len(content)
                }
        except ImportError:
            logger.warning("Playwright not installed, using HTTP client fallback")
            import requests
            resp = requests.get(url, timeout=10)
            return {
                "url": url,
                "title": "Fallback",
                "text": resp.text[:5000],
                "html_length": len(resp.text)
            }
        except Exception as e:
            logger.error(f"Playwright navigation failed for {url}: {e}")
            raise

    async def verify_application_submission_view(self, url: str) -> Dict[str, Any]:
        """
        Inspects application submission URL in sandbox/permitted environment.
        """
        return await self.extract_page_job_content(url)
