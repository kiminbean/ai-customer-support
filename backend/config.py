"""
설정 모듈 — API 키, 모델 설정, 경로 등
데모 모드: OPENAI_API_KEY 미설정 시 자동 전환
"""

import os
from pathlib import Path

# ── 경로 설정 ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_DOCS_DIR = DATA_DIR / "sample_docs"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"
UPLOAD_DIR = DATA_DIR / "uploads"

# 디렉토리 자동 생성
for d in [DATA_DIR, SAMPLE_DOCS_DIR, CHROMA_DB_DIR, UPLOAD_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── OpenAI 설정 ────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEMO_MODE = not bool(OPENAI_API_KEY)

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
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:3001", "*"]

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
