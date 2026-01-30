"""
SQLite 영속화 모듈 — aiosqlite 기반 비동기 데이터베이스 접근
데모 모드 복원력: SQLite 실패 시 인메모리 폴백
"""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional

import aiosqlite

import config

logger = logging.getLogger(__name__)

# ── 데이터베이스 초기화 ────────────────────────────────────────

_CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS conversations (
    id          TEXT PRIMARY KEY,
    data        TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS analytics_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type  TEXT NOT NULL,
    data        TEXT NOT NULL DEFAULT '{}',
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

_db_available: bool = False


async def init_db() -> bool:
    """
    데이터베이스 테이블 생성.
    성공 시 True, 실패 시 False (인메모리 폴백 모드).
    """
    global _db_available
    try:
        async with get_db() as db:
            await db.executescript(_CREATE_TABLES_SQL)
            await db.commit()
        _db_available = True
        logger.info("SQLite 데이터베이스 초기화 완료: %s", config.DATABASE_PATH)
        return True
    except Exception:
        _db_available = False
        logger.warning(
            "SQLite 초기화 실패 — 인메모리 전용 모드로 동작합니다.",
            exc_info=True,
        )
        return False


def is_db_available() -> bool:
    """데이터베이스 사용 가능 여부"""
    return _db_available


# ── 데이터베이스 연결 ──────────────────────────────────────────

@asynccontextmanager
async def get_db() -> AsyncIterator[aiosqlite.Connection]:
    """비동기 SQLite 연결 컨텍스트 매니저"""
    db = await aiosqlite.connect(str(config.DATABASE_PATH))
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()


# ── 대화 저장/조회 ─────────────────────────────────────────────

async def save_conversation(conversation: Dict[str, Any]) -> bool:
    """
    대화 데이터를 SQLite에 저장 (upsert).
    실패 시 False 반환 (인메모리 폴백용).
    """
    if not _db_available:
        return False
    try:
        async with get_db() as db:
            now = datetime.now().isoformat()
            data_json = json.dumps(conversation, ensure_ascii=False)
            await db.execute(
                """
                INSERT INTO conversations (id, data, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    data = excluded.data,
                    updated_at = excluded.updated_at
                """,
                (
                    conversation["id"],
                    data_json,
                    conversation.get("created_at", now),
                    now,
                ),
            )
            await db.commit()
        return True
    except Exception:
        logger.warning("대화 저장 실패 (id=%s)", conversation.get("id"), exc_info=True)
        return False


async def load_conversation(conversation_id: str) -> Optional[Dict[str, Any]]:
    """SQLite에서 대화 로드. 실패 또는 미존재 시 None."""
    if not _db_available:
        return None
    try:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT data FROM conversations WHERE id = ?",
                (conversation_id,),
            )
            row = await cursor.fetchone()
            if row:
                return json.loads(row[0])
        return None
    except Exception:
        logger.warning("대화 로드 실패 (id=%s)", conversation_id, exc_info=True)
        return None


async def load_all_conversations() -> Dict[str, Dict[str, Any]]:
    """SQLite에서 모든 대화 로드. 실패 시 빈 딕셔너리."""
    if not _db_available:
        return {}
    try:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT id, data FROM conversations ORDER BY updated_at DESC"
            )
            rows = await cursor.fetchall()
            return {row[0]: json.loads(row[1]) for row in rows}
    except Exception:
        logger.warning("전체 대화 로드 실패", exc_info=True)
        return {}


# ── 분석 이벤트 ────────────────────────────────────────────────

async def insert_analytics_event(event_type: str, data: Dict[str, Any] | None = None) -> bool:
    """분석 이벤트 기록. 실패 시 False."""
    if not _db_available:
        return False
    try:
        async with get_db() as db:
            await db.execute(
                "INSERT INTO analytics_events (event_type, data) VALUES (?, ?)",
                (event_type, json.dumps(data or {}, ensure_ascii=False)),
            )
            await db.commit()
        return True
    except Exception:
        logger.warning("분석 이벤트 저장 실패 (type=%s)", event_type, exc_info=True)
        return False
