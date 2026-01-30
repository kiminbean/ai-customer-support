"""
HTTP 미들웨어 — 상관관계 ID 주입 및 요청 로깅
"""

from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from logging_config import clear_log_context, set_log_context

logger = logging.getLogger(__name__)

CORRELATION_ID_HEADER = "X-Correlation-ID"


# ── 상관관계 ID 미들웨어 ───────────────────────────────────────

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    요청별 상관관계 ID를 관리하는 미들웨어.
    - 요청 헤더에 X-Correlation-ID가 있으면 사용, 없으면 생성
    - 응답 헤더에 X-Correlation-ID 추가
    - 로그 컨텍스트에 correlation_id 바인딩
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get(
            CORRELATION_ID_HEADER, str(uuid.uuid4())
        )

        set_log_context(
            correlation_id=correlation_id,
            method=request.method,
            path=request.url.path,
        )

        start = time.perf_counter()
        response: Response | None = None

        try:
            response = await call_next(request)
            return response
        except Exception:
            logger.exception("요청 처리 중 예외 발생")
            raise
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            status = response.status_code if response else "ERR"
            logger.info(
                "%s %s → %s (%.1fms)",
                request.method,
                request.url.path,
                status,
                elapsed_ms,
            )
            if response is not None:
                response.headers[CORRELATION_ID_HEADER] = correlation_id
            clear_log_context()
