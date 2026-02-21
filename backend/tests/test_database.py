"""
데이터베이스 모듈 테스트
"""
from __future__ import annotations

import pytest

from database import (
    init_db,
    save_conversation,
    load_conversation,
    load_all_conversations,
    is_db_available,
    get_db,
    insert_analytics_event,
)


class TestInitDb:
    """데이터베이스 초기화 테스트"""

    @pytest.mark.asyncio
    async def test_init_db_creates_tables(self):
        """테이블 생성 테스트"""
        result = await init_db()
        assert result is True

    @pytest.mark.asyncio
    async def test_init_db_idempotent(self):
        """여러 번 초기화해도 에러 없음"""
        await init_db()
        result = await init_db()
        assert result is True


class TestIsDbAvailable:
    """DB 사용 가능 여부 테스트"""

    def test_is_db_available_returns_bool(self):
        """불리언 반환"""
        result = is_db_available()
        assert isinstance(result, bool)


class TestGetDb:
    """DB 연결 테스트"""

    @pytest.mark.asyncio
    async def test_get_db_returns_connection(self):
        """연결 반환"""
        async with get_db() as db:
            assert db is not None


class TestSaveConversation:
    """대화 저장 테스트"""

    @pytest.mark.asyncio
    async def test_save_new_conversation(self):
        """새 대화 저장"""
        await init_db()
        conv = {
            "id": "test-conv-1",
            "messages": [
                {"role": "user", "content": "안녕하세요"},
                {"role": "assistant", "content": "반갑습니다"}
            ],
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
        result = await save_conversation(conv)
        assert result is True

    @pytest.mark.asyncio
    async def test_update_existing_conversation(self):
        """기존 대화 업데이트"""
        await init_db()
        conv = {
            "id": "test-conv-2",
            "messages": [{"role": "user", "content": "첫 메시지"}],
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
        await save_conversation(conv)

        # 업데이트
        conv["messages"].append({"role": "assistant", "content": "응답"})
        result = await save_conversation(conv)
        assert result is True

    @pytest.mark.asyncio
    async def test_save_conversation_without_id(self):
        """ID 없이 대화 저장"""
        await init_db()
        conv = {
            "messages": [{"role": "user", "content": "ID 없는 대화"}],
            "created_at": "2024-01-01T00:00:00",
        }
        result = await save_conversation(conv)
        # ID가 없어도 처리되어야 함
        assert isinstance(result, bool)


class TestLoadConversation:
    """개별 대화 로드 테스트"""

    @pytest.mark.asyncio
    async def test_load_existing_conversation(self):
        """기존 대화 로드"""
        await init_db()
        conv = {
            "id": "test-conv-load",
            "messages": [{"role": "user", "content": "로드 테스트"}],
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
        await save_conversation(conv)

        loaded = await load_conversation("test-conv-load")
        assert loaded is not None
        assert loaded["id"] == "test-conv-load"

    @pytest.mark.asyncio
    async def test_load_nonexistent_conversation(self):
        """존재하지 않는 대화 로드"""
        await init_db()
        loaded = await load_conversation("nonexistent-id")
        assert loaded is None


class TestLoadAllConversations:
    """모든 대화 로드 테스트"""

    @pytest.mark.asyncio
    async def test_load_all_conversations(self):
        """모든 대화 로드"""
        await init_db()
        convs = await load_all_conversations()
        assert isinstance(convs, dict)

    @pytest.mark.asyncio
    async def test_load_returns_saved_conversations(self):
        """저장한 대화가 로드됨"""
        await init_db()
        conv = {
            "id": "test-conv-3",
            "messages": [{"role": "user", "content": "테스트"}],
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
        await save_conversation(conv)

        convs = await load_all_conversations()
        assert "test-conv-3" in convs


class TestInsertAnalyticsEvent:
    """분석 이벤트 저장 테스트"""

    @pytest.mark.asyncio
    async def test_insert_analytics_event(self):
        """분석 이벤트 저장"""
        await init_db()
        result = await insert_analytics_event(
            "chat",
            {"user_message": "안녕하세요", "bot_response": "반갑습니다"}
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_insert_analytics_event_without_data(self):
        """데이터 없이 이벤트 저장"""
        await init_db()
        result = await insert_analytics_event("page_view")
        assert result is True


class TestEdgeCases:
    """엣지 케이스 테스트"""

    @pytest.mark.asyncio
    async def test_save_conversation_with_empty_messages(self):
        """빈 메시지 목록으로 대화 저장"""
        await init_db()
        conv = {
            "id": "test-empty-messages",
            "messages": [],
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
        result = await save_conversation(conv)
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_save_conversation_with_special_characters(self):
        """특수 문자 포함 대화 저장"""
        await init_db()
        conv = {
            "id": "test-special-chars",
            "messages": [
                {"role": "user", "content": "Hello! @#$%^&*() 🎉"}
            ],
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
        result = await save_conversation(conv)
        assert result is True

    @pytest.mark.asyncio
    async def test_save_large_conversation(self):
        """대용량 대화 저장"""
        await init_db()
        conv = {
            "id": "test-large",
            "messages": [
                {"role": "user", "content": f"Message {i}"}
                for i in range(100)
            ],
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
        result = await save_conversation(conv)
        assert result is True
