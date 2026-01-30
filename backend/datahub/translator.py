"""
데이터 허브 번역기 — 영어 → 한국어 번역

LLM API 사용 가능 시 실제 번역, 미사용 시 데모 모드 동작.
번역 캐시로 중복 번역을 방지하며, 배치 처리와 속도 제한을 지원한다.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

import config

# ── 상수 ───────────────────────────────────────────────────

TRANSLATION_CACHE_DIR = config.DATA_DIR / "translation_cache"
TRANSLATION_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# 배치 번역 속도 제한 (초)
RATE_LIMIT_SECONDS = 0.5

# 데모 모드 여부
DEMO_MODE = config.DEMO_MODE


# ── 번역 캐시 ─────────────────────────────────────────────

_cache: Dict[str, str] = {}
_cache_loaded = False


def _load_cache() -> None:
    """디스크에서 번역 캐시를 로드한다."""
    global _cache, _cache_loaded
    if _cache_loaded:
        return

    cache_file = TRANSLATION_CACHE_DIR / "translations.json"
    if cache_file.exists():
        try:
            _cache = json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("번역 캐시 로드 실패: %s", e)
            _cache = {}

    _cache_loaded = True


def _save_cache() -> None:
    """번역 캐시를 디스크에 저장한다."""
    cache_file = TRANSLATION_CACHE_DIR / "translations.json"
    try:
        cache_file.write_text(
            json.dumps(_cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        logger.warning("번역 캐시 저장 실패: %s", e)


def _cache_key(text: str) -> str:
    """텍스트의 캐시 키를 생성한다."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def _get_cached(text: str) -> Optional[str]:
    """캐시된 번역을 반환한다."""
    _load_cache()
    return _cache.get(_cache_key(text))


def _set_cached(original: str, translated: str) -> None:
    """번역 결과를 캐시에 저장한다."""
    _cache[_cache_key(original)] = translated


# ── 언어 감지 ─────────────────────────────────────────────


def is_korean(text: str) -> bool:
    """텍스트가 한국어인지 간이 판별한다."""
    korean_chars = sum(1 for c in text if "\uac00" <= c <= "\ud7a3")
    return korean_chars > len(text) * 0.1


def needs_translation(text: str) -> bool:
    """번역이 필요한 영어 텍스트인지 판별한다."""
    if not text or not text.strip():
        return False
    return not is_korean(text)


# ── 번역 엔진 ─────────────────────────────────────────────


def translate_text(text: str, source_lang: str = "en", target_lang: str = "ko") -> str:
    """
    텍스트를 번역한다.

    API 키가 설정되어 있으면 LLM API로 번역하고,
    없으면 데모 모드로 원문에 "[번역 필요]" 표시를 붙인다.

    Args:
        text: 번역할 텍스트
        source_lang: 원본 언어 (기본: "en")
        target_lang: 목표 언어 (기본: "ko")

    Returns:
        번역된 텍스트
    """
    if not text or not text.strip():
        return text

    # 이미 한국어면 그대로 반환
    if is_korean(text):
        return text

    # 캐시 확인
    cached = _get_cached(text)
    if cached:
        return cached

    # LLM API 번역 시도
    if not DEMO_MODE:
        translated = _translate_via_llm(text, source_lang, target_lang)
        if translated:
            _set_cached(text, translated)
            _save_cache()
            return translated

    # 데모 모드: 원문 유지 + 번역 필요 마킹
    demo_result = f"[번역 필요] {text}"
    _set_cached(text, demo_result)
    _save_cache()
    return demo_result


def _translate_via_llm(text: str, source_lang: str, target_lang: str) -> Optional[str]:
    """
    LLM API를 사용하여 번역한다.
    OpenAI API → Anthropic API 순으로 시도.
    """
    # OpenAI API 시도
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key:
        try:
            return _translate_openai(text, source_lang, target_lang, openai_key)
        except Exception as e:
            logger.warning("OpenAI 번역 실패: %s", e)

    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    if anthropic_key:
        try:
            return _translate_anthropic(text, source_lang, target_lang, anthropic_key)
        except Exception as e:
            logger.warning("Anthropic 번역 실패: %s", e)

    return None


def _translate_openai(text: str, source_lang: str, target_lang: str, api_key: str) -> str:
    """OpenAI API로 번역한다."""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"고객지원 도메인 전문 번역가입니다. "
                        f"{source_lang}에서 {target_lang}로 자연스럽게 번역하세요. "
                        f"고객지원 용어와 존댓말을 적절히 사용하세요. "
                        f"번역만 출력하세요."
                    ),
                },
                {"role": "user", "content": text},
            ],
            temperature=0.3,
            max_tokens=1024,
        )
        return response.choices[0].message.content.strip()
    except ImportError:
        # openai 패키지 미설치 — requests 폴백
        import requests as req

        resp = req.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            f"고객지원 도메인 전문 번역가입니다. "
                            f"{source_lang}에서 {target_lang}로 자연스럽게 번역하세요. "
                            f"번역만 출력하세요."
                        ),
                    },
                    {"role": "user", "content": text},
                ],
                "temperature": 0.3,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()


def _translate_anthropic(text: str, source_lang: str, target_lang: str, api_key: str) -> str:
    """Anthropic API로 번역한다."""
    import requests as req

    resp = req.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"다음 고객지원 텍스트를 {source_lang}에서 {target_lang}로 "
                        f"자연스럽게 번역하세요. 번역만 출력하세요.\n\n{text}"
                    ),
                },
            ],
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"].strip()


# ── 배치 번역 ─────────────────────────────────────────────


def translate_batch(
    qa_pairs: List[Dict],
    progress_callback: Optional[Any] = None,
) -> List[Dict]:
    """
    Q&A 쌍 리스트를 배치 번역한다.

    Args:
        qa_pairs: [{"question": ..., "answer": ..., ...}, ...]
        progress_callback: 진행 상태 콜백

    Returns:
        번역된 Q&A 쌍 리스트
    """
    total = len(qa_pairs)
    translated: List[Dict] = []

    for idx, pair in enumerate(qa_pairs):
        new_pair = dict(pair)

        # 질문 번역
        if needs_translation(pair.get("question", "")):
            new_pair["question"] = translate_text(pair["question"])

        # 답변 번역
        if needs_translation(pair.get("answer", "")):
            new_pair["answer"] = translate_text(pair["answer"])

        # 카테고리는 이미 한국어인 경우가 많으므로 건너뜀

        translated.append(new_pair)

        # 속도 제한 (API 호출 시)
        if not DEMO_MODE:
            time.sleep(RATE_LIMIT_SECONDS)

        # 진행 상태 보고
        if progress_callback and (idx + 1) % 10 == 0:
            progress = (idx + 1) / total
            progress_callback(f"번역 진행: {idx + 1}/{total}", progress)

    # 캐시 저장
    _save_cache()

    return translated


# ── 캐시 관리 ─────────────────────────────────────────────


def get_cache_stats() -> Dict[str, Any]:
    """번역 캐시 통계를 반환한다."""
    _load_cache()
    return {
        "cached_entries": len(_cache),
        "cache_path": str(TRANSLATION_CACHE_DIR),
    }


def clear_translation_cache() -> Dict[str, Any]:
    """번역 캐시를 초기화한다."""
    global _cache
    _cache = {}
    _save_cache()
    return {"status": "cleared", "message": "번역 캐시가 초기화되었습니다."}
