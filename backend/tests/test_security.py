import pytest

from app.security import validate_external_url


@pytest.mark.parametrize("url", [
    "http://localhost:8000/x", "http://127.0.0.1/", "http://192.168.1.10/", "http://10.0.0.5/",
    "http://169.254.169.254/latest/meta-data", "file:///etc/passwd", "ftp://example.com/", "http://user:pw@example.com/",
])
def test_blocked_urls(url):
    with pytest.raises(ValueError):
        validate_external_url(url)
