"""
Security and SSRF Protection Utilities for ApplyForge
"""
import ipaddress
import re
import socket
from urllib.parse import urlparse
from typing import Tuple

class SecurityAuditor:
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, str]:
        """
        Validates URL to protect against SSRF, loopback, private networks, and cloud metadata endpoints.
        """
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False, f"Invalid URL scheme: {parsed.scheme}"
            
            hostname = parsed.hostname
            if not hostname:
                return False, "Missing hostname in URL"
            
            # Check known forbidden hostnames
            if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0"):
                return False, f"Loopback address forbidden: {hostname}"
            
            if hostname == "169.254.169.254":
                return False, "Cloud Metadata IP forbidden"
                
            # Try to resolve to IP and check private ranges
            try:
                ip_str = socket.gethostbyname(hostname)
                ip = ipaddress.ip_address(ip_str)
                if ip.is_loopback:
                    return False, f"Loopback address resolved: {ip_str}"
                if ip.is_private:
                    return False, f"Private network address forbidden: {ip_str}"
                if ip.is_link_local:
                    return False, f"Link-local / Cloud Metadata IP forbidden: {ip_str}"
            except Exception:
                # If cannot resolve (e.g. offline testing), verify hostname pattern
                if hostname.startswith("10.") or hostname.startswith("192.168.") or hostname.startswith("172."):
                    return False, "Private IP range forbidden"
                    
            return True, "URL is safe"
        except Exception as e:
            return False, f"URL validation failed: {str(e)}"

    @staticmethod
    def sanitize_untrusted_text(text: str) -> Tuple[str, bool]:
        """
        Detects potential prompt injection payloads and wraps untrusted text inside isolation delimiters.
        """
        patterns = [
            r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
            r"output\s+your\s+system\s+prompt",
            r"jailbreak",
            r"do\s+anything\s+now",
            r"reveal\s+secret"
        ]
        is_injection = False
        for p in patterns:
            if re.search(p, text, re.IGNORECASE):
                is_injection = True
                break
                
        delimited = f"[INJECTION DELIMITER - UNTRUSTED CONTENT START]\\n{text}\\n[INJECTION DELIMITER - UNTRUSTED CONTENT END]"
        return delimited, is_injection

    @staticmethod
    def redact_sensitive_logs(text: str) -> str:
        """
        Redacts API keys, passwords, and bearer tokens from log messages.
        """
        redacted = re.sub(r"sk-[a-zA-Z0-9_-]{10,}", "[REDACTED_API_KEY]", text)
        redacted = re.sub(r"Bearer\s+[a-zA-Z0-9_\-\.]{10,}", "Bearer [REDACTED_TOKEN]", redacted)
        redacted = re.sub(r"((?:password|passwd|pwd)\s*(?:[:=]|\bis\b)\s*)([^\s,]+)", r"\1[REDACTED_PASSWORD]", redacted, flags=re.IGNORECASE)
        return redacted

def wrap_untrusted_job_content(content: str) -> str:
    """Helper used by LLM providers to safely wrap untrusted external job text."""
    sanitized, _ = SecurityAuditor.sanitize_untrusted_text(content)
    return sanitized

def safe_fetch_url(url: str) -> str:
    """Safely fetches external URL content after rigorous SSRF verification."""
    import requests
    is_safe, reason = SecurityAuditor.validate_url(url)
    if not is_safe:
        raise ValueError(f"SSRF Protection Blocked URL: {reason}")
    resp = requests.get(url, timeout=10, headers={"User-Agent": "ApplyForgeBot/1.0"})
    resp.raise_for_status()
    return resp.text
