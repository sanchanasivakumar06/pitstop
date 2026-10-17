"""
HTTP request and latency logging middleware.
"""

import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("pitstop.api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        # Don't clutter logs with websocket upgrades or health polling
        if not request.url.path.endswith("/health"):
            logger.info(
                f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.1f}ms)"
            )
        return response
