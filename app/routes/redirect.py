from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_session, async_session_factory
from app.services.url_service import url_service
from app.services.rate_limiter import rate_limiter
from app.services.analytics_service import analytics_service

router = APIRouter()


@router.get("/{short_code}", tags=["Redirect"])
async def redirect_url(short_code: str, request: Request,
                       background_tasks: BackgroundTasks,
                       session: AsyncSession = Depends(get_session)):
    if short_code in ("shorten", "health", "metrics", "docs", "openapi.json", "redoc", "dashboard", "favicon.ico"):
        return JSONResponse(status_code=404, content={"error": "Not Found", "detail": "Not a short code", "code": 404})

    ip = request.client.host if request.client else "unknown"
    is_limited, remaining, retry_after = await rate_limiter.is_rate_limited(ip, "redirect")
    if is_limited:
        return JSONResponse(status_code=429, content={
            "error": "Rate Limit Exceeded", "detail": "Too many redirect requests", "code": 429},
            headers={"Retry-After": str(retry_after)})

    url, error = await url_service.get_url(session, short_code)
    if error:
        return JSONResponse(status_code=error["code"], content=error)

    long_url = url.long_url
    url_type = url.url_type

    user_agent = request.headers.get("user-agent", "")

    async def _record():
        async with async_session_factory() as bg_session:
            await analytics_service.record_click(bg_session, short_code, ip, user_agent)

    background_tasks.add_task(_record)

    status_code = 301 if url_type == "301" else 302
    return RedirectResponse(url=long_url, status_code=status_code)


@router.delete("/{short_code}", tags=["URL"])
async def delete_url(short_code: str, session: AsyncSession = Depends(get_session)):
    error = await url_service.delete_url(session, short_code)
    if error:
        return JSONResponse(status_code=error["code"], content=error)
    return {"message": f"URL '{short_code}' has been deactivated"}