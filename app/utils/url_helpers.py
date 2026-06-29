"""
URL Helper utilities for managing public URL resolution.
Supports ngrok for local development and public deployment.
"""

import logging
from app.config import settings

logger = logging.getLogger(__name__)


def get_public_base_url() -> str:
    """
    Get the public base URL for QR codes and short URL responses.

    Priority:
    1. NGROK_URL environment variable (for ngrok tunneling)
    2. base_url setting (for direct/deployed instances)

    Returns:
        str: The public base URL without trailing slash
    """
    if settings.ngrok_url:
        # Remove trailing slash if present
        url = settings.ngrok_url.rstrip("/")
        logger.debug(f"Using ngrok URL: {url}")
        return url

    # Fallback to configured base_url
    url = settings.base_url.rstrip("/")
    logger.debug(f"Using configured base URL: {url}")
    return url


def is_using_ngrok() -> bool:
    """Check if ngrok URL is configured."""
    return bool(settings.ngrok_url)
