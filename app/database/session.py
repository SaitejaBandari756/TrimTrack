from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


def _get_engine_url() -> str:
    if settings.sqlite_fallback:
        logger.info("Using SQLite fallback database")
        return settings.sqlite_url
    return settings.database_url


def _get_engine_kwargs(url: str) -> dict:
    kwargs = {"echo": settings.debug}

    if "postgresql" in url:
        kwargs.update(
            {
                "pool_size": settings.db_pool_min,
                "max_overflow": settings.db_pool_max - settings.db_pool_min,
                "pool_pre_ping": True,
                "pool_recycle": 3600,
            }
        )
    return kwargs


def _create_engine(url: str):
    from sqlalchemy import event

    engine = create_async_engine(url, **_get_engine_kwargs(url))

    if "sqlite" in url:

        @event.listens_for(engine.sync_engine, "connect")
        def disable_foreign_keys(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys = OFF")
            cursor.close()

    return engine


_url = _get_engine_url()
engine = _create_engine(_url)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_engine():
    global engine, async_session_factory

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized")
    except Exception as e:
        if "postgresql" in str(settings.database_url) and not settings.sqlite_fallback:
            logger.warning(
                f"PostgreSQL connection failed: {e}. "
                f"Auto-falling back to SQLite at {settings.sqlite_url}"
            )
            await engine.dispose()

            engine = _create_engine(settings.sqlite_url)
            async_session_factory.configure(bind=engine)

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables initialized (SQLite fallback)")
        else:
            raise


async def dispose_engine():
    await engine.dispose()
    logger.info("Database engine disposed")
