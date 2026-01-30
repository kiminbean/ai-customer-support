# Backend — FastAPI + RAG + Deep Agents

Python 3.14, FastAPI, Pydantic v2, LangChain, scikit-learn TF-IDF.
All modules follow: Korean docstrings, `from __future__ import annotations`, `# ── Section ──` separators, demo mode fallback.

## Commands

```bash
source venv/bin/activate
uvicorn main:app --reload --port 8000
pytest                                    # All 93 tests
pytest tests/test_api.py                  # API tests (18)
pytest tests/test_crawler.py              # Crawler tests (30)
pytest tests/test_datahub.py              # Datahub tests (33)
pytest tests/test_voice.py                # Voice tests (12)
pytest tests/ -v --cov=. --cov-report=term-missing  # Coverage
```

## Module Map

### main.py — App Entry
- Registers routers: `crawler_router`, `datahub_router`, `voice_router`
- Defines top-level Pydantic models: `ChatRequest`, `ChatResponse`, `SettingsRequest`
- Lifespan: `init_db()`, `init_conversations()`, `load_sample_docs()`, optional Sentry init
- Middleware stack (innermost → outermost): auth → correlation ID → slowapi → GZip → CORS
- Paginated list endpoints: `/api/documents?page=1&limit=50`, `/api/conversations?page=1&limit=20`
- Cache-Control headers on GET endpoints (analytics: 60s, conversations: 15s, documents: 30s)
- Direct endpoints: `/api/chat`, `/api/documents/*`, `/api/conversations/*`, `/api/analytics`, `/api/settings`, `/api/health`

### config.py — Central Config
- ALL settings as module-level vars (runtime-mutable)
- `DEMO_MODE = not bool(OPENAI_API_KEY)` — auto-detects
- Path constants: `BASE_DIR`, `DATA_DIR`, `SAMPLE_DOCS_DIR`, `UPLOAD_DIR`
- RAG params: `CHUNK_SIZE=1000`, `CHUNK_OVERLAP=200`, `RETRIEVAL_K=3`, `MIN_SIMILARITY=0.3`
- Security: `API_KEY`, `CORS_ORIGINS`, `SENTRY_DSN`

### auth.py — API Key Authentication
- Middleware function `api_key_auth_middleware`
- Checks `X-API-Key` header against `config.API_KEY`
- Bypasses: health endpoint, empty API_KEY config (demo mode)
- Returns 403 with Korean error message on failure

### database.py — SQLite Persistence
- Async SQLite via `aiosqlite`
- `init_db()` creates tables on startup
- `save_conversation()`, `get_conversations()`, `get_conversation()`
- File: `data/app.db`

### logging_config.py — Structured Logging
- `setup_logging()` configures JSON formatter for production
- Console + file handlers
- Log level from `config.LOG_LEVEL`

### middleware.py — Correlation IDs
- `CorrelationIdMiddleware` adds `X-Correlation-ID` header to every request/response
- UUID-based, propagated through logging context

### agents/ — Deep Agent Orchestration
- **orchestrator.py**: Intent classification → sub-agent routing. `process_message()` is the main entry.
  - `classify_intent(query)` → FAQ | ORDER | ESCALATION | GREETING
  - Auto-escalates FAQ responses with confidence < 0.3
  - SQLite-backed conversation persistence
- **faq_agent.py**: RAG search → demo keyword matching or LLM answer
- **order_agent.py**: Order lookup with mock data. Regex: `ORD-\d{4}-\d{3}`
- **escalation_agent.py**: Keyword-based escalation detection. Priority: 높음/보통/낮음

### rag/ — RAG Pipeline
- **vector_store.py**: `InMemoryVectorStore` — TF-IDF + cosine similarity (scikit-learn). Singleton via `get_store()`.
  - JSON persistence to `data/vector_store.json`
  - char_wb analyzer, ngram_range=(2,4), max_features=5000
- **retriever.py**: Thin wrapper. `search(query, k, min_similarity)` → `[{text, metadata, score, id}]`
- **document_loader.py**: File → chunks → vector store. Supports: .txt, .md, .pdf

### crawler/ — Web Scraping Pipeline
- **routes.py**: `APIRouter(prefix="/api/crawler")`. Background task pattern.
  - Demo detection: URL contains "demo", "example", "test", "localhost", "smartmall"
- **scraper.py**, **extractor.py**, **rag_converter.py**, **demo.py**

### datahub/ — HuggingFace Dataset Integration
- **routes.py**: `APIRouter(prefix="/api/datahub")`. Thread-based async jobs.
- **registry.py**, **downloader.py**, **processor.py**, **translator.py**

### voice/ — Audio → Knowledge Base
- **routes.py**: `APIRouter(prefix="/api/voice")`. Upload → transcribe → generate Q&A → approve.
- **processor.py**: `VoiceProcessor` orchestrator. `ProcessingStatus` enum.
- **transcriber.py**, **document_generator.py**, **demo.py**

## Shared Patterns

- **Router registration**: `app.include_router(router)` in `main.py`
- **In-memory stores**: Module-private dicts for transient job state. SQLite for persistent data.
- **Job pattern**: Background tasks + job_id polling. Create → poll `/status/{job_id}` → get results.
- **Demo mode**: Every module provides mock data. Check via `config.DEMO_MODE` or URL detection.
- **Response shape**: `{"status": "...", "message": "한국어 메시지", ...}` with domain-specific fields.
- **Pagination**: List endpoints accept `page` and `limit` query params. Return `total`, `page`, `limit`, `total_pages`.

## Infrastructure

- **Docker**: `Dockerfile` (multi-stage), `docker-compose.yml` (backend:8000 + frontend:3000)
- **CI/CD**: `.github/workflows/ci.yml` — pytest + npm build on push/PR
- **Sentry**: Optional — initializes when `SENTRY_DSN` env var is set
- **Rate Limiting**: slowapi, in-memory, 60/min default, 30/min for chat, 10/min for uploads

## Gotchas

- `config.py` runs at import time — directory creation happens on first import
- `vector_store.py` saves to JSON on every add/delete — O(n) rebuild on mutation
- Tests use module-level `TestClient(app)` — lifespan runs once for all tests
- `requirements.txt` lists `openai-whisper` as commented-out optional dep
- GZip middleware compresses responses > 500 bytes
