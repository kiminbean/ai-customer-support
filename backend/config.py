"""
설정 모듈 — API 키, 모델 설정, 경로 등
데모 모드: OPENAI_API_KEY 미설정 시 자동 전환
"""

from __future__ import annotations

import os
from pathlib import Path

# ── 경로 설정 ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_DOCS_DIR = DATA_DIR / "sample_docs"
UPLOAD_DIR = DATA_DIR / "uploads"
DATABASE_PATH = DATA_DIR / "app.db"

# 디렉토리 자동 생성
for d in [DATA_DIR, SAMPLE_DOCS_DIR, UPLOAD_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── OpenAI 설정 ────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEMO_MODE = not bool(OPENAI_API_KEY)

# ── API 인증 설정 ─────────────────────────────────────────
# NOTE: API_KEY should be server-side only. Do NOT set NEXT_PUBLIC_API_KEY in frontend.
# For production, implement proper session/token-based authentication.
API_KEY = os.getenv("API_KEY", "").strip()

# ── 요청 제한 설정 ───────────────────────────────────────
MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE", str(10 * 1024 * 1024)))  # 10MB
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))  # 30 seconds
MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "5"))  # 최대 동시 작업 수

# ── 로깅 설정 ─────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").strip()

# ── 백업 설정 ─────────────────────────────────────────────
BACKUP_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))

# ── Sentry 설정 ───────────────────────────────────────────
SENTRY_DSN = os.getenv("SENTRY_DSN", "").strip()

# ── 모델 설정 (런타임에 변경 가능) ─────────────────────────
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))

# ── RAG 설정 ───────────────────────────────────────────────
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
RETRIEVAL_K = 3
MIN_SIMILARITY = 0.3

# ── 앱 설정 ────────────────────────────────────────────────
APP_TITLE = "AI 고객지원 플랫폼"
APP_VERSION = "1.0.0"
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:3001"
    ).split(",")
    if origin.strip()
]

# ── 모델 허용 목록 ───────────────────────────────────────
ALLOWED_MODELS = {
    "gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-4-turbo",
    "gpt-3.5-turbo", "gpt-3.5-turbo-16k",
}


def get_settings_dict() -> dict:
    """현재 설정을 딕셔너리로 반환"""
    return {
        "demo_mode": DEMO_MODE,
        "model_name": MODEL_NAME,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "chunk_size": CHUNK_SIZE,
        "retrieval_k": RETRIEVAL_K,
    }
