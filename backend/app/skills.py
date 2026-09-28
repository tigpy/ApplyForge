"""Shared skill vocabulary used by deterministic matching and the mock AI provider."""
import re

SKILL_TERMS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "bash", "powershell",
    "fastapi", "django", "flask", "react", "node.js", "sql", "postgresql", "mysql", "mongodb", "rest api",
    "git", "docker", "kubernetes", "aws", "azure", "gcp", "linux", "windows", "networking", "tcp/ip",
    "siem", "splunk", "wireshark", "nmap", "burp suite", "owasp", "incident response", "log analysis",
    "vulnerability assessment", "penetration testing", "threat hunting", "mitre att&ck", "firewall",
    "machine learning", "data analysis",
]

_PATTERNS = {t: re.compile(r"(?<![a-z0-9+#])" + re.escape(t) + r"s?(?![a-z0-9+#])", re.I) for t in SKILL_TERMS}


def find_skills(text: str) -> set[str]:
    return {t for t, p in _PATTERNS.items() if p.search(text or "")}
