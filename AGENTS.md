# AI Customer Support Platform — Agent Context

**Generated:** 2026-01-30 | **Commit:** c6d3b1e | **Branch:** main

## Overview

RAG + Deep Agents 기반 AI 고객지원 SaaS. Monorepo: `app/` (Next.js 16) + `backend/` (FastAPI).
All features work in demo mode without API keys. Korean-first UX.

## Structure

```
app/                     # Next.js 16, React 19, Tailwind v4, TypeScript
  src/app/               # App Router pages (landing, demo, dashboard, datahub, crawler, widget)
  src/lib/api.ts         # Typed fetch wrappers for ALL backend endpoints
backend/                 # FastAPI, Python 3.14, Pydantic v2
  main.py                # App entry + route registration + Pydantic models
  config.py              # ALL config (env vars, paths, model settings, RAG params)
  agents/                # Deep Agent pattern: orchestrator → sub-agents
  rag/                   # RAG pipeline: loader → embeddings → vector_store → retriever
  crawler/               # Web scraping → content extraction → RAG documents
  datahub/               # HuggingFace dataset browse/download/process/import
  voice/                 # Audio → STT → Q&A document generation
  tests/test_api.py      # Integration tests (FastAPI TestClient)
  data/                  # Runtime: chroma_db, uploads, sample_docs (resets on restart)
```

## Commands

### Backend (working directory: `backend/`)
```bash
source venv/bin/activate          # Python 3.14 venv
uvicorn main:app --reload --port 8000  # Dev server
pytest                            # All tests
pytest tests/test_api.py          # Single file
pytest tests/test_api.py::test_health  # Single test
pytest -v -s                      # Verbose with stdout
pip install -r requirements.txt   # Install deps
```

### Frontend (working directory: `app/`)
```bash
npm run dev       # Dev server (port 3000)
npm run build     # Production build
npm start         # Production server
npm install       # Install deps
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
   └──→ voice/routes ──→ voice/{processor, transcriber, document_generator, demo}

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
- Storage: In-memory dicts (`_store: Dict[str, T] = {}`). Singleton pattern via `get_X()` functions.
- Demo mode: `config.DEMO_MODE` check → keyword-matched fallback responses

### TypeScript (Frontend)
- Path alias: `@/*` → `./src/*`
- `import type { X }` for type-only imports. Named exports.
- `interface` not `type` for object shapes. PascalCase.
- `camelCase` functions. `async/await`. Error: `if (!res.ok) throw new Error(...)`
- Components: PascalCase functions, defined in page file (no separate component files)
- `"use client"` only when needed
- Styling: Tailwind v4 inline. Brand: `#2563EB`. CSS vars in `globals.css`.
- TypeScript `strict: true`. No `as any`, no `@ts-ignore`.

## Golden Rules

1. **Demo mode always works** — Every feature functions without OPENAI_API_KEY
2. **Korean-first UX** — All user-facing strings, errors, docstrings in Korean
3. **No external DB** — In-memory storage (MVP phase). Data resets on restart.
4. **API contract** — All endpoints under `/api/`. Consistent response shapes.
5. **No linting config** — No eslint/prettier/pyproject.toml. Rely on TypeScript strict + conventions.

## Do's and Don'ts

- DO add `from __future__ import annotations` to every new Python file
- DO support demo mode fallback for any new feature
- DO define Pydantic models near their route handlers
- DO use section separator comments (`# ── ... ──`) in Python files
- DO use `API_BASE` from `lib/api.ts` for all frontend API calls
- DON'T add database migrations (in-memory storage phase)
- DON'T use relative imports in backend Python code
- DON'T install deps without updating `requirements.txt`
- DON'T suppress TypeScript errors with `as any` or `@ts-ignore`
- DON'T hardcode API URLs in frontend

## Git

- Branch: `main`
- Commit style: Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`)
- `.gitignore` only excludes `__pycache__/` — `venv/` and `node_modules/` are NOT gitignored

## Where to Look

| Task | Location | Notes |
|------|----------|-------|
| Add API endpoint | `backend/main.py` or new `{module}/routes.py` | Register router in main.py |
| Add agent behavior | `backend/agents/` | Follow orchestrator routing pattern |
| Modify RAG pipeline | `backend/rag/` | vector_store is singleton via `get_store()` |
| Add frontend page | `app/src/app/{name}/page.tsx` | App Router convention |
| Add API client method | `app/src/lib/api.ts` | All backend calls go here |
| Change AI settings | `backend/config.py` | Module-level vars, runtime-mutable |
| Add test | `backend/tests/test_api.py` | Uses FastAPI TestClient |
| Styling/theme | `app/src/app/globals.css` | CSS custom properties + animations |

## Context Map

- **[Backend](./backend/AGENTS.md)** — Module APIs, dependency graph, per-module conventions
- **[Frontend](./app/AGENTS.md)** — Page patterns, component structure, API client
