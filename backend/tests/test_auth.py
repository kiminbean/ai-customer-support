"""
Tests for auth module
Target: Increase coverage from 46% to 80%+
"""

from __future__ import annotations

from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from fastapi import HTTPException, Request
from fastapi.security import APIKeyHeader
from starlette.responses import JSONResponse

import auth
import config


class TestVerifyApiKey:
    """verify_api_key 함수 테스트"""

    @pytest.mark.asyncio
    async def test_demo_mode_no_api_key_required(self, monkeypatch):
        """데모 모드: API_KEY 미설정 시 인증 건너뜀"""
        monkeypatch.setattr(config, "API_KEY", "")

        result = await auth.verify_api_key(api_key=None)

        assert result is None

    @pytest.mark.asyncio
    async def test_demo_mode_with_any_key(self, monkeypatch):
        """데모 모드: 아무 키나 전달해도 통과"""
        monkeypatch.setattr(config, "API_KEY", "")

        result = await auth.verify_api_key(api_key="any-key")

        assert result is None

    @pytest.mark.asyncio
    async def test_valid_api_key(self, monkeypatch):
        """유효한 API 키"""
        monkeypatch.setattr(config, "API_KEY", "test-secret-key")

        result = await auth.verify_api_key(api_key="test-secret-key")

        assert result == "test-secret-key"

    @pytest.mark.asyncio
    async def test_invalid_api_key(self, monkeypatch):
        """잘못된 API 키"""
        monkeypatch.setattr(config, "API_KEY", "test-secret-key")

        with pytest.raises(HTTPException) as exc_info:
            await auth.verify_api_key(api_key="wrong-key")

        assert exc_info.value.status_code == 403
        assert "유효하지 않은" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_missing_api_key(self, monkeypatch):
        """API 키 미제공"""
        monkeypatch.setattr(config, "API_KEY", "test-secret-key")

        with pytest.raises(HTTPException) as exc_info:
            await auth.verify_api_key(api_key=None)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_empty_api_key(self, monkeypatch):
        """빈 API 키"""
        monkeypatch.setattr(config, "API_KEY", "test-secret-key")

        with pytest.raises(HTTPException) as exc_info:
            await auth.verify_api_key(api_key="")

        assert exc_info.value.status_code == 403


class TestApiKeyAuthMiddleware:
    """api_key_auth_middleware 함수 테스트"""

    @pytest.fixture
    def mock_request(self):
        """요청 모킹"""
        request = MagicMock(spec=Request)
        request.url = MagicMock()
        request.headers = {}
        return request

    @pytest.fixture
    def mock_call_next(self):
        """call_next 모킹"""
        async def call_next(request):
            return JSONResponse(content={"status": "ok"})
        return call_next

    @pytest.mark.asyncio
    async def test_demo_mode_allows_all(self, mock_request, mock_call_next, monkeypatch):
        """데모 모드: 모든 요청 허용"""
        monkeypatch.setattr(config, "API_KEY", "")
        mock_request.url.path = "/api/chat"

        response = await auth.api_key_auth_middleware(mock_request, mock_call_next)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_excluded_path_health(self, mock_request, mock_call_next, monkeypatch):
        """제외 경로: /api/health"""
        monkeypatch.setattr(config, "API_KEY", "secret")
        mock_request.url.path = "/api/health"

        response = await auth.api_key_auth_middleware(mock_request, mock_call_next)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_excluded_path_docs(self, mock_request, mock_call_next, monkeypatch):
        """제외 경로: /docs"""
        monkeypatch.setattr(config, "API_KEY", "secret")
        mock_request.url.path = "/docs"

        response = await auth.api_key_auth_middleware(mock_request, mock_call_next)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_excluded_path_redoc(self, mock_request, mock_call_next, monkeypatch):
        """제외 경로: /redoc"""
        monkeypatch.setattr(config, "API_KEY", "secret")
        mock_request.url.path = "/redoc"

        response = await auth.api_key_auth_middleware(mock_request, mock_call_next)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_excluded_path_openapi(self, mock_request, mock_call_next, monkeypatch):
        """제외 경로: /openapi.json"""
        monkeypatch.setattr(config, "API_KEY", "secret")
        mock_request.url.path = "/openapi.json"

        response = await auth.api_key_auth_middleware(mock_request, mock_call_next)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_non_api_path_allowed(self, mock_request, mock_call_next, monkeypatch):
        """API 외 경로: 인증 없이 허용"""
        monkeypatch.setattr(config, "API_KEY", "secret")
        mock_request.url.path = "/static/style.css"

        response = await auth.api_key_auth_middleware(mock_request, mock_call_next)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_api_path_valid_key(self, mock_request, mock_call_next, monkeypatch):
        """API 경로: 유효한 키로 접근"""
        monkeypatch.setattr(config, "API_KEY", "secret-key")
        mock_request.url.path = "/api/chat"
        mock_request.headers = {"x-api-key": "secret-key"}

        response = await auth.api_key_auth_middleware(mock_request, mock_call_next)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_api_path_invalid_key(self, mock_request, mock_call_next, monkeypatch):
        """API 경로: 잘못된 키로 403"""
        monkeypatch.setattr(config, "API_KEY", "secret-key")
        mock_request.url.path = "/api/chat"
        mock_request.headers = {"x-api-key": "wrong-key"}

        response = await auth.api_key_auth_middleware(mock_request, mock_call_next)

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_api_path_missing_key(self, mock_request, mock_call_next, monkeypatch):
        """API 경로: 키 없이 403"""
        monkeypatch.setattr(config, "API_KEY", "secret-key")
        mock_request.url.path = "/api/chat"
        mock_request.headers = {}

        response = await auth.api_key_auth_middleware(mock_request, mock_call_next)

        assert response.status_code == 403


class TestAuthConstants:
    """상수 테스트"""

    def test_api_key_header_name(self):
        """API 키 헤더 이름"""
        assert auth.API_KEY_HEADER_NAME == "X-API-Key"

    def test_excluded_paths_contains_health(self):
        """제외 경로에 health 포함"""
        assert "/api/health" in auth.AUTH_EXCLUDED_PATHS

    def test_excluded_paths_contains_docs(self):
        """제외 경로에 docs 포함"""
        assert "/docs" in auth.AUTH_EXCLUDED_PATHS
        assert "/redoc" in auth.AUTH_EXCLUDED_PATHS
        assert "/openapi.json" in auth.AUTH_EXCLUDED_PATHS

    def test_excluded_paths_is_frozenset(self):
        """제외 경로가 frozenset"""
        assert isinstance(auth.AUTH_EXCLUDED_PATHS, frozenset)


class TestErrorResponse:
    """에러 응답 형식 테스트"""

    @pytest.fixture
    def mock_request_for_error(self):
        """요청 모킹"""
        request = MagicMock(spec=Request)
        request.url = MagicMock()
        request.headers = {}
        return request

    @pytest.fixture
    def mock_call_next_for_error(self):
        """call_next 모킹"""
        async def call_next(request):
            return JSONResponse(content={"status": "ok"})
        return call_next

    @pytest.mark.asyncio
    async def test_middleware_error_format(self, mock_request_for_error, mock_call_next_for_error, monkeypatch):
        """미들웨어 에러 응답 형식"""
        monkeypatch.setattr(config, "API_KEY", "secret")
        mock_request_for_error.url.path = "/api/chat"
        mock_request_for_error.headers = {}

        response = await auth.api_key_auth_middleware(mock_request_for_error, mock_call_next_for_error)

        assert response.status_code == 403
