from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_session
from app.schemas.url import URLCreateRequest
from app.services.url_service import url_service
from app.services.rate_limiter import rate_limiter
from app.utils.url_helpers import get_public_base_url

router = APIRouter()


@router.get("/debug/config", tags=["Debug"])
async def debug_config():
    from app.config import settings
    return {
        "ngrok_url": settings.ngrok_url,
        "base_url": settings.base_url,
        "get_public_base_url()": get_public_base_url(),
    }


@router.post("/shorten", tags=["URL"])
async def shorten_url(body: URLCreateRequest, request: Request,
                      session: AsyncSession = Depends(get_session)):
    ip = request.client.host if request.client else "unknown"
    is_limited, remaining, retry_after = await rate_limiter.is_rate_limited(ip, "create")
    if is_limited:
        return JSONResponse(status_code=429, content={
            "error": "Rate Limit Exceeded", "detail": "Too many URL creation requests",
            "code": 429}, headers={"Retry-After": str(retry_after),
                                    "X-RateLimit-Remaining": "0"})

    response, error = await url_service.create_short_url(session, body)
    if error:
        return JSONResponse(status_code=error["code"], content=error)
    return response
