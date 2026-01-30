# Backend — FastAPI + RAG + Deep Agents

Python 3.14, FastAPI, Pydantic v2, LangChain, scikit-learn TF-IDF.
All modules follow: Korean docstrings, `from __future__ import annotations`, `# ── Section ──` separators, demo mode fallback.

## Commands

```bash
source venv/bin/activate
uvicorn main:app --reload --port 8000
pytest                                    # All tests
pytest tests/test_api.py::test_health     # Single test
pytest -v -s                              # Verbose
```

## Module Map

### main.py — App Entry
- Registers routers: `crawler_router`, `datahub_router` (voice registered here too)
- Defines top-level Pydantic models: `ChatRequest`, `ChatResponse`, `SettingsRequest`
- Startup event loads sample docs via `load_sample_docs()`
- Direct endpoints: `/api/chat`, `/api/documents/*`, `/api/conversations/*`, `/api/analytics`, `/api/settings`, `/api/health`

### config.py — Central Config
- ALL settings as module-level vars (runtime-mutable)
- `DEMO_MODE = not bool(OPENAI_API_KEY)` — auto-detects
- Path constants: `BASE_DIR`, `DATA_DIR`, `SAMPLE_DOCS_DIR`, `CHROMA_DB_DIR`, `UPLOAD_DIR`
- RAG params: `CHUNK_SIZE=1000`, `CHUNK_OVERLAP=200`, `RETRIEVAL_K=3`, `MIN_SIMILARITY=0.3`

### agents/ — Deep Agent Orchestration
- **orchestrator.py**: Intent classification → sub-agent routing. `process_message()` is the main entry.
  - `classify_intent(query)` → FAQ | ORDER | ESCALATION | GREETING
  - Auto-escalates FAQ responses with confidence < 0.3
  - In-memory conversation store: `_conversations: Dict[str, Dict]`
- **faq_agent.py**: RAG search → demo keyword matching or LLM answer. `handle(query)`
  - `_DEMO_RESPONSES` dict maps Korean keywords → canned answers
  - Production mode uses `ChatOpenAI` via LangChain
- **order_agent.py**: Order lookup with mock data. `handle(query)`, `is_order_query(query)`
  - Regex: `ORD-\d{4}-\d{3}` for order ID extraction
  - `_MOCK_ORDERS` dict with 4 demo orders
- **escalation_agent.py**: Keyword-based escalation detection. `handle(query)`, `needs_escalation(query)`
  - Three keyword lists: `_ANGRY_KEYWORDS`, `_EXPLICIT_ESCALATION`, `_COMPLEX_KEYWORDS`
  - Priority: 높음/보통/낮음

### rag/ — RAG Pipeline
- **vector_store.py**: `InMemoryVectorStore` — TF-IDF + cosine similarity (scikit-learn). Singleton via `get_store()`.
  - JSON persistence to `data/vector_store.json`
  - `_rebuild_index()` on every add/delete
  - char_wb analyzer, ngram_range=(2,4), max_features=5000
- **retriever.py**: Thin wrapper over vector_store. `search(query, k, min_similarity)` → `[{text, metadata, score, id}]`
- **document_loader.py**: File → chunks → vector store. `load_file(path)`, `load_text(text, source)`, `load_sample_docs()`
  - Uses `RecursiveCharacterTextSplitter` from langchain
  - Supports: .txt, .md, .pdf (PyPDF2 optional)
- **embeddings.py**: Embedding generation (currently TF-IDF in vector_store handles this)

### crawler/ — Web Scraping Pipeline
- **routes.py**: `APIRouter(prefix="/api/crawler")`. Background task pattern for async crawling.
  - `CrawlJob` class tracks status: pending → crawling → extracting → completed/failed
  - In-memory job store: `_jobs: dict[str, CrawlJob]`
  - Demo detection: URL contains "demo", "example", "test", "localhost", "smartmall"
- **scraper.py**: `WebCrawler(CrawlConfig)` with progress callback
- **extractor.py**: HTML → `ExtractedContent` (FAQs, articles, products, policies)
- **rag_converter.py**: `RAGConverter` → `RAGDocument` with Q&A pairs + markdown output
- **demo.py**: Static demo data for testing without real crawling
- **__init__.py**: Exports all public classes via `__all__`

### datahub/ — HuggingFace Dataset Integration
- **routes.py**: `APIRouter(prefix="/api/datahub")`. Thread-based async jobs.
  - In-memory job store: `_jobs: Dict[str, Dict[str, Any]]`
  - `_create_job()` / `_update_job()` pattern
- **registry.py**: Curated dataset catalog. `get_domains()`, `search_datasets(query)`
- **downloader.py**: HuggingFace `datasets` library download
- **processor.py**: Dataset → RAG-compatible format
- **translator.py**: English → Korean translation pipeline

### voice/ — Audio → Knowledge Base
- **routes.py**: `APIRouter(prefix="/api/voice")`. Upload audio → transcribe → generate Q&A docs.
- **processor.py**: `VoiceProcessor` orchestrator. `ProcessingStatus` enum.
- **transcriber.py**: `Transcriber` — Whisper STT (optional dependency)
- **document_generator.py**: Transcript → structured Q&A documents
- **demo.py**: Sample transcripts for demo mode
- **__init__.py**: Exports via `__all__`

## Shared Patterns

- **Router registration**: Each module's `router` is registered in `main.py` via `app.include_router(router)`
- **In-memory stores**: Module-private `_store: Dict = {}` with `_create_*()` helpers. Never share across modules.
- **Job pattern**: Long-running tasks (crawl, download, process) use background tasks + job_id polling.
  - Create job → return job_id → poll `/status/{job_id}` → get `/results/{job_id}`
- **Demo mode**: Every module provides mock/demo data. Check via `config.DEMO_MODE` or URL-based detection.
- **Response shape**: `{"status": "...", "message": "한국어 메시지", ...}` with domain-specific fields.

## Gotchas

- `config.py` runs at import time — directory creation happens on first import
- `vector_store.py` saves to JSON on every add/delete — watch for perf with large doc sets
- `_rebuild_index()` refits TF-IDF on entire corpus — O(n) on every mutation
- `main.py` voice router registration may be missing — verify `voice/routes.py` router is included
- `requirements.txt` lists `openai-whisper` as commented-out optional dep
- Tests use module-level `TestClient(app)` — startup event runs once for all tests
