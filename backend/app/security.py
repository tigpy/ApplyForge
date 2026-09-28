"""Small safety helpers: filename sanitising and SSRF-safe URL validation."""
import ipaddress
import re
import socket
from urllib.parse import urlparse

_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_filename(name: str) -> str:
    base = name.replace("\\", "/").split("/")[-1].strip()
    base = _UNSAFE.sub("_", base).strip("._")
    return base[:100] or "resume.pdf"


def validate_external_url(url: str) -> str:
    """Allow only public http(s) URLs. Raises ValueError otherwise.

    Note: resolution is checked once; DNS rebinding is out of scope for this skeleton.
    """
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.hostname:
        raise ValueError("Only http(s) URLs with a hostname are allowed")
    if p.username or p.password:
        raise ValueError("Credentials in URLs are not allowed")
    host = p.hostname.lower()
    if host == "localhost" or host.endswith(".localhost"):
        raise ValueError("Localhost URLs are not allowed")
    try:
        infos = socket.getaddrinfo(host, p.port or (443 if p.scheme == "https" else 80), proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise ValueError("Host could not be resolved") from exc
    for info in infos:
        if not ipaddress.ip_address(info[4][0].split("%")[0]).is_global:
            raise ValueError("URL resolves to a private or reserved address")
    return url
