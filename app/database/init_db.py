from app.database.session import init_engine, async_session_factory
from app.models.url import URL
from app.models.analytics import Analytics
from app.services.bloom_filter import bloom_filter_service
from app.services.cache_service import cache_service
import logging

logger = logging.getLogger(__name__)


async def init_db():
    await init_engine()
    logger.info("All database tables created successfully")


async def warm_cache():
    from sqlalchemy import select
    from app.config import settings

    try:
        async with async_session_factory() as session:
            stmt = (
                select(URL)
                .where(URL.is_active == True)
                .order_by(URL.click_count.desc())
                .limit(settings.cache_warm_top_n)
            )
            result = await session.execute(stmt)
            urls = result.scalars().all()

            for url in urls:
                await cache_service.set_url(url.short_code, url.long_url)
                await bloom_filter_service.add(url.short_code)

            logger.info(f"Cache warmed with {len(urls)} URLs")
    except Exception as e:
        logger.warning(f"Cache warming failed (non-fatal): {e}")
