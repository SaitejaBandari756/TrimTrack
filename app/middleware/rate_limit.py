from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health/metrics/docs
        path = request.url.path
        skip_paths = ("/health", "/metrics", "/docs", "/openapi.json", "/redoc")
        if any(path.startswith(p) for p in skip_paths):
            return await call_next(request)
        return await call_next(request)
