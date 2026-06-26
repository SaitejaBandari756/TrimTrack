"""
IP-to-Country geolocation resolution.
Uses ip-api.com (free tier) with caching.
"""

import httpx
import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

# In-memory LRU cache for geo lookups to avoid hammering external API
_geo_cache: dict[str, str] = {}
_GEO_CACHE_MAX = 10_000


async def lookup_country(ip_address: str) -> Optional[str]:
    """
    Resolve an IP address to a country name.

    Uses ip-api.com free tier (max 45 req/min).
    Results are cached in-memory.

    Args:
        ip_address: IPv4 or IPv6 address string

    Returns:
        Country name or None if resolution fails
    """
    if not ip_address or ip_address in ("127.0.0.1", "::1", "localhost"):
        return "Localhost"

    # Check in-memory cache
    if ip_address in _geo_cache:
        return _geo_cache[ip_address]

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(
                f"{settings.geo_api_url}/{ip_address}",
                params={"fields": "status,country"},
            )
            data = response.json()

            if data.get("status") == "success":
                country = data.get("country", "Unknown")
                # Cache result
                if len(_geo_cache) < _GEO_CACHE_MAX:
                    _geo_cache[ip_address] = country
                return country

    except Exception as e:
        logger.debug(f"Geo lookup failed for {ip_address}: {e}")

    return "Unknown"
