"""
구조화 로깅 설정 — stdlib logging + JSON 포매터
외부 의존성 없이 JSON 형식 로그 출력
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict

import config

# ── 컨텍스트 변수 (상관관계 ID 등) ────────────────────────────

_log_context: Dict[str, Any] = {}


def set_log_context(**kwargs: Any) -> None:
    """현재 요청의 로그 컨텍스트 설정 (예: correlation_id)"""
    _log_context.update(kwargs)


def clear_log_context() -> None:
    """로그 컨텍스트 초기화"""
    _log_context.clear()


def get_log_context() -> Dict[str, Any]:
    """현재 로그 컨텍스트 반환"""
    return dict(_log_context)


# ── JSON 포매터 ────────────────────────────────────────────────

class JsonFormatter(logging.Formatter):
    """로그 레코드를 JSON 한 줄로 직렬화"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if _log_context:
            log_entry["context"] = dict(_log_context)

        if record.exc_info and record.exc_info[1] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        extra_keys = {
            k: v
            for k, v in record.__dict__.items()
            if k not in logging.LogRecord(
                "", 0, "", 0, "", (), None
            ).__dict__
            and k not in ("message", "msg", "args")
        }
        if extra_keys:
            log_entry["extra"] = extra_keys

        return json.dumps(log_entry, ensure_ascii=False, default=str)


# ── 로깅 초기화 ───────────────────────────────────────────────

def setup_logging(level: str | None = None) -> None:
    """
    애플리케이션 로깅 초기화.
    JSON 포매터를 stdout 핸들러에 적용한다.
    """
    log_level = (level or config.LOG_LEVEL).upper()

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 기존 핸들러 제거 (중복 방지)
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(JsonFormatter())
    root_logger.addHandler(handler)

    # 외부 라이브러리 로그 레벨 조정
    for noisy in ("uvicorn.access", "httpcore", "httpx", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        "로깅 초기화 완료 (level=%s)", log_level
    )
