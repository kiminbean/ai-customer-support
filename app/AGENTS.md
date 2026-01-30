# Frontend — Next.js 16 + React 19 + Tailwind v4

## Commands

```bash
npm run dev       # http://localhost:3000
npm run build     # Production build (type-checks included)
npm start         # Production server
```

## Structure

```
src/
  app/
    layout.tsx            # Root layout: Geist font, lang="ko", antialiased
    globals.css           # Tailwind v4 import + CSS custom props + animations
    page.tsx              # Landing page (~467 lines, all components inline)
    demo/page.tsx         # Chat demo interface — "use client"
    dashboard/page.tsx    # Admin dashboard — "use client"
    datahub/page.tsx      # HuggingFace dataset browser — "use client"
    crawler/page.tsx      # Web crawler UI — "use client"
    widget/page.tsx       # Embeddable chat widget — "use client"
  lib/
    api.ts                # ALL backend API calls — typed fetch wrappers
```

## Page Patterns

- **Server components** (default): `page.tsx` (landing) — no client interactivity needed
- **Client components**: All other pages use `"use client"` for state/effects
- **Inline components**: All components defined in the same page file (no `components/` dir)
- **Large pages**: Landing (467 lines), Crawler (864), Datahub (851), Dashboard (784) — all self-contained

## API Client (`lib/api.ts`)

- `API_BASE` from `NEXT_PUBLIC_API_URL` env var, defaults `http://localhost:8000`
- Every function follows pattern: `async function name(...): Promise<T>` with `if (!res.ok) throw new Error(...)`
- Interfaces defined at top of file: `ChatResponse`, `Document`, `Conversation`, `Analytics`, `Datahub*`, `Crawl*`
- All endpoints called via `fetch()` — no axios or other HTTP libs

## Styling

- **Tailwind v4** via `@import "tailwindcss"` in globals.css (not v3 config)
- **Brand color**: `#2563EB` (blue-600) — hardcoded in components, also as CSS var `--primary`
- **CSS custom properties**: `--background`, `--foreground`, `--primary`, `--gray-*` scale
- **Fonts**: Geist Sans + Geist Mono via `next/font/google`
- **Custom animations**: `typing-dot`, `fadeInUp`, `pulse-glow`, `grow-bar` in globals.css
- **No dark mode** — light theme only

## Conventions

- TypeScript `strict: true`, no `as any`, no `@ts-ignore`
- `interface` over `type` for object shapes
- `import type { X }` for type-only imports
- Path alias: `@/*` → `./src/*`
- No eslint, no prettier — rely on TS strict + Next.js defaults
- No test framework configured for frontend

## Gotchas

- No shared component library — every page rebuilds common UI (navbar, buttons)
- `page.tsx` (landing) is server component but other pages are client — don't mix patterns
- No loading/error boundaries defined yet
- No `middleware.ts` — no auth, redirects, or edge logic
- `postcss.config.mjs` exists (Tailwind v4 requirement)
