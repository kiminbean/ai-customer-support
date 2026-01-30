"""
API 키 인증 모듈 — X-API-Key 헤더 기반 간편 인증
데모 모드(API_KEY 미설정)에서는 인증을 자동으로 건너뛴다.
"""

from __future__ import annotations

from fastapi import HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader
from starlette.responses import JSONResponse

import config

# ── 상수 ──────────────────────────────────────────────────────

API_KEY_HEADER_NAME = "X-API-Key"

API_KEY_HEADER = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)

AUTH_EXCLUDED_PATHS: frozenset[str] = frozenset({
    "/api/health",
    "/docs",
    "/redoc",
    "/openapi.json",
})


# ── 인증 의존성 함수 ─────────────────────────────────────────

async def verify_api_key(
    api_key: str | None = Security(API_KEY_HEADER),
) -> str | None:
    """
    API 키 검증 의존성.
    config.API_KEY가 비어 있으면(데모 모드) 인증을 건너뛴다.
    개별 라우트에 Depends(verify_api_key)로 적용 가능.
    """
    if not config.API_KEY:
        return None
    if not api_key or api_key != config.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="유효하지 않은 API 키입니다.",
        )
    return api_key


# ── 인증 미들웨어 핸들러 ─────────────────────────────────────

async def api_key_auth_middleware(request: Request, call_next):
    """
    모든 /api/* 요청에 API 키 인증을 적용하는 미들웨어 핸들러.
    데모 모드(API_KEY 미설정)에서는 모든 요청을 허용한다.
    제외 경로: /api/health, /docs, /redoc, /openapi.json
    """
    # API_KEY 미설정 → 데모 모드, 인증 건너뜀
    if not config.API_KEY:
        return await call_next(request)

    path = request.url.path

    # 제외 경로 → 인증 건너뜀
    if path in AUTH_EXCLUDED_PATHS:
        return await call_next(request)

    # /api/* 이외의 경로 → 인증 건너뜀
    if not path.startswith("/api/"):
        return await call_next(request)

    # API 키 검증
    api_key = request.headers.get("x-api-key", "")
    if api_key != config.API_KEY:
        return JSONResponse(
            status_code=403,
            content={"detail": "유효하지 않은 API 키입니다."},
        )

    return await call_next(request)
