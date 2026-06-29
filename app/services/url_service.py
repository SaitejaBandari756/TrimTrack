import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.url import URL
from app.schemas.url import URLCreateRequest, URLResponse
from app.utils.id_generator import generate_id
from app.utils.base62 import encode as base62_encode
from app.utils.validators import validate_url_safety
from app.utils.url_helpers import get_public_base_url
from app.services.cache_service import cache_service
from app.services.bloom_filter import bloom_filter_service
from app.services.url_safety import url_safety_service

logger = logging.getLogger(__name__)


class URLService:
    async def create_short_url(self, session: AsyncSession, request: URLCreateRequest) -> tuple[Optional[URLResponse], Optional[dict]]:
        is_safe, reason = validate_url_safety(request.url)
        if not is_safe:
            return None, {"error": "Invalid URL", "detail": reason, "code": 422}

        safety_score, is_safe, reason, warnings = url_safety_service.check_url(request.url)
        if not is_safe:
            is_adult_warning = warnings.get("warning_type") == "ADULT_CONTENT"
            if is_adult_warning and request.force_adult:
                pass
            else:
                return None, {"error": "Unsafe URL", "detail": reason, "code": 422, "warnings": warnings}

        if request.custom_alias:
            short_code = request.custom_alias
            if await bloom_filter_service.check(short_code):
                existing = await session.execute(select(URL).where(URL.short_code == short_code))
                if existing.scalar_one_or_none():
                    return None, {"error": "Conflict", "detail": f"Alias '{short_code}' is already taken", "code": 409}
            snowflake_id = generate_id()
        else:
            snowflake_id = generate_id()
            short_code = base62_encode(snowflake_id)

        url = URL(
            id=snowflake_id, short_code=short_code, long_url=request.url,
            expiry_date=request.expiry_date, url_type=request.url_type or "302",
            safety_score=safety_score,
        )
        session.add(url)
        await session.flush()
        await session.commit()

        await bloom_filter_service.add(short_code)
        await cache_service.set_url(short_code, request.url)
        await cache_service.set_url_metadata(short_code, {
            "long_url": request.url, "url_type": url.url_type,
            "expiry_date": str(url.expiry_date) if url.expiry_date else None,
            "is_active": True,
        })

        response = URLResponse(
            id=url.id, short_code=url.short_code,
            short_url=f"{get_public_base_url()}/{url.short_code}",
            long_url=url.long_url, created_at=url.created_at or datetime.now(timezone.utc),
            expiry_date=url.expiry_date, url_type=url.url_type, safety_score=url.safety_score,
            warnings=warnings if warnings else None,
            has_warnings=bool(warnings),
        )
        logger.info(f"Created short URL: {response.short_url} using public_base_url: {get_public_base_url()}")
        return response, None

    async def get_url(self, session: AsyncSession, short_code: str) -> tuple[Optional[URL], Optional[dict]]:
        cached_meta = await cache_service.get_url_metadata(short_code)
        if cached_meta:
            if not cached_meta.get("is_active", True):
                return None, {"error": "Gone", "detail": "This URL has been deleted", "code": 410}
            if cached_meta.get("expiry_date"):
                try:
                    expiry = datetime.fromisoformat(cached_meta["expiry_date"])
                    if expiry < datetime.now(timezone.utc):
                        return None, {"error": "Gone", "detail": "This URL has expired", "code": 410}
                except (ValueError, TypeError):
                    pass

        cached_url = await cache_service.get_url(short_code)
        if cached_url and cached_meta:
            url_obj = URL(short_code=short_code, long_url=cached_url,
                          url_type=cached_meta.get("url_type", "302"), is_active=True)
            return url_obj, None

        result = await session.execute(select(URL).where(URL.short_code == short_code))
        url = result.scalar_one_or_none()
        if not url:
            return None, {"error": "Not Found", "detail": f"Short code '{short_code}' does not exist", "code": 404}
        if not url.is_active:
            return None, {"error": "Gone", "detail": "This URL has been deleted", "code": 410}
        if url.expiry_date and url.expiry_date.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            return None, {"error": "Gone", "detail": "This URL has expired", "code": 410}

        await bloom_filter_service.add(short_code)

        await cache_service.set_url(short_code, url.long_url)
        await cache_service.set_url_metadata(short_code, {
            "long_url": url.long_url, "url_type": url.url_type,
            "expiry_date": str(url.expiry_date) if url.expiry_date else None,
            "is_active": url.is_active,
        })
        return url, None

    async def delete_url(self, session: AsyncSession, short_code: str) -> Optional[dict]:
        result = await session.execute(select(URL).where(URL.short_code == short_code))
        url = result.scalar_one_or_none()
        if not url:
            return {"error": "Not Found", "detail": f"Short code '{short_code}' does not exist", "code": 404}
        url.is_active = False
        await session.commit()
        await cache_service.delete_url(short_code)
        return None

    async def cleanup_expired(self, session: AsyncSession) -> int:
        now = datetime.now(timezone.utc)
        result = await session.execute(
            select(URL).where(URL.expiry_date <= now, URL.is_active))
        expired_urls = result.scalars().all()
        count = 0
        for url in expired_urls:
            url.is_active = False
            await cache_service.delete_url(url.short_code)
            count += 1
        await session.commit()
        return count

url_service = URLService()