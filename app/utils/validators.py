"""
URL validation utilities.
Prevents SSRF via private IP blocking and validates URL format.
"""

import re
from urllib.parse import urlparse
import ipaddress
import logging

logger = logging.getLogger(__name__)

# Private/reserved IP ranges that should be blocked (SSRF prevention)
BLOCKED_IP_RANGES = [
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16",
    "127.0.0.0/8",
    "169.254.0.0/16",
    "0.0.0.0/8",
    "100.64.0.0/10",  # Carrier-grade NAT
    "::1/128",
    "fc00::/7",
    "fe80::/10",
]

BLOCKED_NETWORKS = [ipaddress.ip_network(r) for r in BLOCKED_IP_RANGES]


def is_valid_url(url: str) -> bool:
    """
    Validate URL format.

    Checks:
    - Must start with http:// or https://
    - Must have a valid hostname
    - Must be under 2048 characters
    """
    if not url or len(url) > 2048:
        return False

    if not url.startswith(("http://", "https://")):
        return False

    try:
        parsed = urlparse(url)
        if not parsed.hostname:
            return False
        if not parsed.scheme in ("http", "https"):
            return False
        return True
    except Exception:
        return False


def is_private_ip(hostname: str) -> bool:
    """
    Check if a hostname resolves to a private/reserved IP.
    Prevents SSRF attacks.
    """
    try:
        ip = ipaddress.ip_address(hostname)
        for network in BLOCKED_NETWORKS:
            if ip in network:
                return True
    except ValueError:
        # Not a direct IP, could be a domain — safe to proceed
        pass
    return False


def validate_url_safety(url: str) -> tuple[bool, str]:
    """
    Validate URL for safety concerns.

    Returns:
        (is_safe, reason) tuple
    """
    if not is_valid_url(url):
        return False, "Invalid URL format"

    parsed = urlparse(url)

    # Block private IPs (SSRF prevention)
    if is_private_ip(parsed.hostname or ""):
        return False, "URLs pointing to private/internal IPs are not allowed"

    # Block dangerous file extensions
    dangerous_extensions = [
        ".exe", ".bat", ".cmd", ".msi", ".scr",
        ".pif", ".vbs", ".js", ".wsf", ".ps1",
    ]
    path_lower = (parsed.path or "").lower()
    for ext in dangerous_extensions:
        if path_lower.endswith(ext):
            return False, f"URLs with {ext} extension are blocked for safety"

    return True, "URL is safe"
