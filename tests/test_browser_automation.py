"""
Tests for Playwright Browser Automation Layer
"""
import pytest
from packages.automation.browser import PlaywrightBrowserService

@pytest.mark.asyncio
async def test_browser_automation_ssrf_blocking():
    service = PlaywrightBrowserService()
    with pytest.raises(ValueError) as exc:
        await service.extract_page_job_content("http://127.0.0.1:8000/secret")
    assert "SSRF Safety Guard Blocked URL" in str(exc.value)

    with pytest.raises(ValueError) as exc2:
        await service.extract_page_job_content("http://169.254.169.254/latest/meta-data")
    assert "SSRF Safety Guard Blocked URL" in str(exc2.value)
