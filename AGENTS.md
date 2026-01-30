# AI Customer Support Platform — Agent Context

**Generated:** 2026-01-31 | **Commit:** 9f8219e | **Branch:** main

## Overview

RAG + Deep Agents 기반 AI 고객지원 SaaS. Monorepo: `app/` (Next.js 16) + `backend/` (FastAPI).
All features work in demo mode without API keys. Korean-first UX.

## Structure

```
app/                     # Next.js 16, React 19, Tailwind v4, TypeScript
  src/app/               # App Router pages
    (admin)/             # Route group: dashboard, datahub, crawler, voice (shared sidebar layout)
    page.tsx             # Landing page
    demo/page.tsx        # Chat demo
    widget/page.tsx      # Embeddable widget preview + iframe mode
  src/components/        # Shared components: Navbar, DashboardSidebar, icons, BackendBadge
  src/hooks/             # Custom hooks: useHealthCheck
  src/lib/api.ts         # Typed fetch wrappers for ALL backend endpoints
  public/widget.js       # Embeddable chat widget (vanilla JS IIFE, <5KB)
backend/                 # FastAPI, Python 3.14, Pydantic v2
  main.py                # App entry + route registration + Pydantic models + middleware stack
  config.py              # ALL config (env vars, paths, model settings, RAG params)
  auth.py                # API Key authentication middleware
  database.py            # SQLite persistence layer (async, aiosqlite)
  logging_config.py      # Structured JSON logging setup
  middleware.py           # Correlation ID middleware
  agents/                # Deep Agent pattern: orchestrator → sub-agents
  rag/                   # RAG pipeline: loader → vector_store → retriever
  crawler/               # Web scraping → content extraction → RAG documents
  datahub/               # HuggingFace dataset browse/download/process/import
  voice/                 # Audio → STT → Q&A document generation
  tests/                 # Integration tests: test_api (18), test_crawler (30), test_datahub (33), test_voice (12)
  data/                  # Runtime: vector_store.json, uploads, sample_docs, app.db
Dockerfile               # Multi-stage Python backend image
docker-compose.yml       # Full stack: backend (8000) + frontend (3000)
.github/workflows/ci.yml # GitHub Actions: lint + test + build
```

## Commands

### Backend (working directory: `backend/`)
```bash
source venv/bin/activate
uvicorn main:app --reload --port 8000
pytest                               # All 93 tests
pytest tests/test_api.py             # API tests only (18)
pytest tests/ -v --cov=. --cov-report=term-missing  # Coverage
```

### Frontend (working directory: `app/`)
```bash
npm run dev       # Dev server (port 3000)
npm run build     # Production build
npm start         # Production server
```

### Docker
```bash
docker compose up -d      # Start both services
docker compose down        # Stop
docker compose logs -f     # Watch logs
```

### Full Stack
- Backend: http://localhost:8000 (Swagger: /docs)
- Frontend: http://localhost:3000
- Connection: `NEXT_PUBLIC_API_URL` env var (defaults http://localhost:8000)

## Dependency Graph

```
main.py ──→ agents/orchestrator ──→ agents/{faq_agent, order_agent, escalation_agent}
   │                                    │
   │        rag/document_loader ──→ rag/retriever ──→ rag/vector_store
   │                                    ↑
   ├──→ crawler/routes ──→ crawler/{scraper, extractor, rag_converter, demo}
   │                       └──→ rag/document_loader (import to knowledge base)
   │
   ├──→ datahub/routes ──→ datahub/{registry, downloader, processor, translator}
   │                       └──→ rag/document_loader (import to knowledge base)
   │
   ├──→ voice/routes ──→ voice/{processor, transcriber, document_generator, demo}
   │
   ├──→ auth.py (API Key middleware)
   ├──→ database.py (SQLite via aiosqlite)
   ├──→ logging_config.py (JSON structured logging)
   └──→ middleware.py (correlation IDs)

config.py ← imported by ALL backend modules
```

## Code Style

### Python (Backend)
- `from __future__ import annotations` — EVERY file, first line after module docstring
- Imports: stdlib → third-party → local. Absolute only (`from rag.retriever import search`)
- Types: `Dict`, `List`, `Optional` from `typing`. Inline unions: `dict | list`
- Docstrings: Korean, triple-quoted, module + function level. Purpose over parameters.
- Naming: `snake_case` functions, `PascalCase` classes, `SCREAMING_SNAKE` constants, `_` prefix for private
- Sections: `# ── Section Name ──` with box-drawing chars
- Config: All in `config.py` as module-level vars. `os.getenv()` with defaults.
- Errors: `HTTPException` with Korean messages. Catch specific exceptions.
- Models: Pydantic models defined IN the route file that uses them
- Storage: SQLite for persistence (`database.py`), in-memory dicts for transient job state
- Demo mode: `config.DEMO_MODE` check → keyword-matched fallback responses

### TypeScript (Frontend)
- Path alias: `@/*` → `./src/*`
- `import type { X }` for type-only imports. Named exports.
- `interface` not `type` for object shapes. PascalCase.
- `camelCase` functions. `async/await`. Error: `if (!res.ok) throw new Error(...)`
- Shared components in `src/components/`. Page-specific components inline.
- `"use client"` only when needed
- Styling: Tailwind v4 inline. Brand: `#2563EB`. CSS vars in `globals.css`.
- TypeScript `strict: true`. No `as any`, no `@ts-ignore`.

## Golden Rules

1. **Demo mode always works** — Every feature functions without OPENAI_API_KEY
2. **Korean-first UX** — All user-facing strings, errors, docstrings in Korean
3. **SQLite persistence** — `backend/data/app.db` via `database.py`. No external DB.
4. **API Key auth** — `X-API-Key` header. Empty = demo mode (no auth required).
5. **API contract** — All endpoints under `/api/`. Paginated lists include `total`, `page`, `limit`.
6. **No linting config** — No eslint/prettier/pyproject.toml. Rely on TypeScript strict + conventions.

## Do's and Don'ts

- DO add `from __future__ import annotations` to every new Python file
- DO support demo mode fallback for any new feature
- DO define Pydantic models near their route handlers
- DO use section separator comments (`# ── ... ──`) in Python files
- DO use `API_BASE` from `lib/api.ts` for all frontend API calls
- DO add new admin pages under `app/src/app/(admin)/` route group
- DON'T use relative imports in backend Python code
- DON'T install deps without updating `requirements.txt`
- DON'T suppress TypeScript errors with `as any` or `@ts-ignore`
- DON'T hardcode API URLs in frontend

## Git

- Branch: `main`
- Commit style: Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`, `perf:`)
- `.gitignore` excludes: `__pycache__/`, `*.pyc`, `*.pyo`, `.env`, `*.db`, `venv/`, `node_modules/`, `.next/`, IDE files

## Where to Look

| Task | Location | Notes |
|------|----------|-------|
| Add API endpoint | `backend/main.py` or new `{module}/routes.py` | Register router in main.py |
| Add agent behavior | `backend/agents/` | Follow orchestrator routing pattern |
| Modify RAG pipeline | `backend/rag/` | vector_store is singleton via `get_store()` |
| Add admin page | `app/src/app/(admin)/{name}/page.tsx` | Uses shared sidebar layout |
| Add public page | `app/src/app/{name}/page.tsx` | Uses Navbar component |
| Add API client method | `app/src/lib/api.ts` | All backend calls go here |
| Add shared component | `app/src/components/` | Navbar, DashboardSidebar, icons |
| Change AI settings | `backend/config.py` | Module-level vars, runtime-mutable |
| Add test | `backend/tests/test_{module}.py` | Uses FastAPI TestClient |
| Styling/theme | `app/src/app/globals.css` | CSS custom properties + animations |
| Infrastructure | `Dockerfile`, `docker-compose.yml` | Multi-stage build |
| CI/CD | `.github/workflows/ci.yml` | pytest + npm build |

## Context Map

- **[Backend](./backend/AGENTS.md)** — Module APIs, dependency graph, per-module conventions
- **[Frontend](./app/AGENTS.md)** — Page patterns, component structure, API client
