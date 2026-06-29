from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database.session import get_session
from app.services.cache_service import cache_service

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check(session: AsyncSession = Depends(get_session)):
    health = {"status": "healthy", "services": {}}

    try:
        await session.execute(text("SELECT 1"))
        health["services"]["database"] = "up"
    except Exception as e:
        health["services"]["database"] = f"down: {str(e)}"
        health["status"] = "degraded"

    redis_ok = await cache_service.health_check()
    health["services"]["redis"] = "up" if redis_ok else "down"
    if not redis_ok:
        health["status"] = "degraded"

    return health
