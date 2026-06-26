import time
import logging
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


def setup_logging(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if debug else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(level=level, format="%(message)s")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000
        logger = structlog.get_logger()
        logger.info("request",
                     method=request.method,
                     path=str(request.url.path),
                     status=response.status_code,
                     duration_ms=round(duration_ms, 2),
                     client=request.client.host if request.client else "unknown")
        return response
