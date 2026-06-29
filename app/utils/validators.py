from urllib.parse import urlparse
import ipaddress
import logging

logger = logging.getLogger(__name__)

BLOCKED_IP_RANGES = [
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16",
    "127.0.0.0/8",
    "169.254.0.0/16",
    "0.0.0.0/8",
    "100.64.0.0/10",
    "::1/128",
    "fc00::/7",
    "fe80::/10",
]

BLOCKED_NETWORKS = [ipaddress.ip_network(r) for r in BLOCKED_IP_RANGES]


def is_valid_url(url: str) -> bool:
    
    if not url or len(url) > 2048:
        return False

    if not url.startswith(("http://", "https://")):
        return False

    try:
        parsed = urlparse(url)
        if not parsed.hostname:
            return False
        if parsed.scheme not in ("http", "https"):
            return False
        return True
    except Exception:
        return False


def is_private_ip(hostname: str) -> bool:
    
    try:
        ip = ipaddress.ip_address(hostname)
        for network in BLOCKED_NETWORKS:
            if ip in network:
                return True
    except ValueError:
        pass
    return False


def validate_url_safety(url: str) -> tuple[bool, str]:
    
    if not is_valid_url(url):
        return False, "Invalid URL format"

    parsed = urlparse(url)

    if is_private_ip(parsed.hostname or ""):
        return False, "URLs pointing to private/internal IPs are not allowed"

    dangerous_extensions = [
        ".exe", ".bat", ".cmd", ".msi", ".scr",
        ".pif", ".vbs", ".js", ".wsf", ".ps1",
    ]
    path_lower = (parsed.path or "").lower()
    for ext in dangerous_extensions:
        if path_lower.endswith(ext):
            return False, f"URLs with {ext} extension are blocked for safety"

    return True, "URL is safe"