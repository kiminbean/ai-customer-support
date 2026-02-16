# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

RAG + Deep Agents based AI customer support SaaS. Monorepo: `app/` (Next.js 16) + `backend/` (FastAPI).
Korean-first UX, demo mode (no API key required).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js 16)                │
│                    http://localhost:3000                  │
├─────────────────────────────────────────────────────────────┤
│                     Backend (FastAPI)                      │
│                    http://localhost:8000                  │
│  ┌──────────┐  ┌───────┐  ┌────────┐  ┌──────────┐  │
│  │ Agents   │→ │  RAG  │→ │Vector  │  │ SQLite   │  │
│  │Orchestr.│  │Pipeline│  │Store   │  │ Persistence│ │
│  └──────────┘  └───────┘  └────────┘  └──────────┘  │
├─────────────────────────────────────────────────────────────┤
│            Crawler    Datahub    Voice  (Sub-modules)      │
└─────────────────────────────────────────────────────────────┘
```

## Commands

### Backend (working directory: `backend/`)
```bash
source venv/bin/activate
uvicorn main:app --reload --port 8000           # Dev server
pytest                                           # All 93 tests
pytest tests/test_api.py                         # API tests (18)
pytest tests/test_crawler.py                     # Crawler tests (30)
pytest tests/test_datahub.py                     # Datahub tests (33)
pytest tests/test_voice.py                       # Voice tests (12)
pytest tests/ -v --cov=. --cov-report=term-missing # Coverage
```

### Frontend (working directory: `app/`)
```bash
npm run dev       # Dev server (port 3000)
npm run build     # Production build
npm start         # Production server
npx tsc --noEmit  # Type check only (used in CI)
```

### Docker
```bash
docker compose up -d    # Start both services
docker compose down      # Stop
docker compose logs -f   # Watch logs
```

### CI/CD
```bash
# GitHub Actions runs: pytest + npm build + tsc --noEmit
# Manual verification:
cd backend && pytest tests/ -v
cd app && npm run build
```

## Key Architectural Patterns

### Agent Orchestration (Backend)
- `main.py` → `agents/orchestrator.py` routes to sub-agents (faq_agent, order_agent, escalation_agent)
- Intent classification: FAQ | ORDER | ESCALATION | GREETING
- Demo mode fallback when `OPENAI_API_KEY` not set

### RAG Pipeline
- `rag/vector_store.py`: TF-IDF + cosine similarity (scikit-learn), singleton via `get_store()`
- Persistence: `backend/data/vector_store.json`
- Document loader supports: .txt, .md, .pdf

### Frontend Structure
- App Router with `(admin)/` route group for shared sidebar layout
- Server components default, `"use client"` only when needed
- All API calls through `src/lib/api.ts` (no hardcoded URLs)
- Dashboard uses modular tab components (OverviewTab, AnalyticsTab, ConversationsTab)

### Data Flow
- Knowledge sources → Crawler/Datahub/Voice → RAG pipeline → Vector store
- Chat request → Orchestrator → Agent → RAG retrieval → Response

### Embeddable Widget
- `app/public/widget.js` — Vanilla JS IIFE, <5KB
- Can be embedded on external sites with iframe mode support

## Critical Files

| File | Purpose |
|------|---------|
| `backend/config.py` | All config (env vars, RAG params, paths) - single source of truth |
| `backend/main.py` | App entry, route registration, Pydantic models, middleware stack |
| `backend/database.py` | SQLite persistence via aiosqlite |
| `app/src/lib/api.ts` | ALL backend API calls with types |
| `AGENTS.md` (root) | Comprehensive project documentation |

## Code Style

### Python (Backend)
- `from __future__ import annotations` - EVERY file, first line
- Absolute imports only (`from rag.retriever import search`)
- Korean docstrings, `# ── Section Name ──` separators
- Pydantic models defined near their route handlers

### TypeScript (Frontend)
- `interface` not `type` for object shapes
- `import type { X }` for type-only imports
- Path alias: `@/*` → `./src/*`
- `API_BASE` from `lib/api.ts` for all API calls

## Golden Rules

1. **Demo mode always works** - Every feature functions without OPENAI_API_KEY
2. **Korean-first UX** - All user-facing strings in Korean
3. **SQLite persistence** - `backend/data/app.db` via `database.py`
4. **API Key auth** - `X-API-Key` header. Empty = demo mode (no auth required)
5. **No external DB** - Use SQLite for all persistence
6. **No linting config** - Rely on TypeScript strict + conventions
7. **API contract** - All endpoints under `/api/`. Paginated lists include `total`, `page`, `limit`

## Where to Look

| Task | Location |
|------|----------|
| Add API endpoint | `backend/main.py` or new `{module}/routes.py` |
| Add agent behavior | `backend/agents/` |
| Modify RAG pipeline | `backend/rag/` |
| Add admin page | `app/src/app/(admin)/{name}/page.tsx` |
| Add API client method | `app/src/lib/api.ts` |
| Change AI settings | `backend/config.py` |
| Add test | `backend/tests/test_{module}.py` |

## Module Documentation

- **[Backend](./backend/AGENTS.md)** — Module APIs, dependency graph, per-module conventions
- **[Frontend](./app/AGENTS.md)** — Page patterns, component structure, API client
- **[Root](./AGENTS.md)** — Full project context, commands, dependency graph

## Environment

| Variable | Purpose | Default |
|----------|---------|----------|
| `OPENAI_API_KEY` | LLM integration | Empty = demo mode |
| `NEXT_PUBLIC_API_URL` | Backend URL | http://localhost:8000 |
| `API_KEY` | Backend auth | Empty = demo mode |
| `NEXT_PUBLIC_API_KEY` | Frontend auth (optional) | Empty |
| `SENTRY_DSN` | Error tracking | Empty (disabled) |
