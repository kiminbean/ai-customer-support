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
    layout.tsx            # Root layout: Geist font, lang="ko", preconnect to API
    globals.css           # Tailwind v4 import + CSS custom props + animations
    page.tsx              # Landing page (server component)
    error.tsx             # Global error boundary (Sentry integration)
    loading.tsx           # Global loading state
    not-found.tsx         # Custom 404 page
    demo/page.tsx         # Chat demo interface
    widget/page.tsx       # Embeddable widget preview + iframe mode
    (admin)/              # Route group — shared sidebar layout
      layout.tsx          # DashboardSidebar + useHealthCheck
      dashboard/
        page.tsx          # Admin dashboard (real API data + demo fallback)
        error.tsx         # Dashboard error boundary
        loading.tsx       # Dashboard loading state
      datahub/page.tsx    # HuggingFace dataset browser
      crawler/page.tsx    # Web crawler UI
      voice/page.tsx      # Voice-to-knowledge-base pipeline
  components/
    Navbar.tsx            # Shared navbar (landing/app variants, mobile hamburger)
    DashboardSidebar.tsx  # Admin sidebar (desktop fixed, mobile overlay)
    BackendBadge.tsx      # Backend online/offline indicator
    icons.tsx             # SVG icon components (LogoIcon)
  hooks/
    useHealthCheck.ts     # Backend health polling hook
  lib/
    api.ts                # ALL backend API calls — typed fetch wrappers (493 lines)
public/
  widget.js               # Embeddable chat widget IIFE (<5KB, vanilla JS)
```

## Page Patterns

- **Server components** (default): `page.tsx` (landing), `layout.tsx`
- **Client components**: All other pages use `"use client"` for state/effects
- **Admin pages**: Under `(admin)/` route group, sidebar provided by shared layout
- **Error boundaries**: `error.tsx` at root and dashboard level, with Sentry capture

## Shared Components

- **Navbar**: `variant="landing"` (features/pricing links) or `variant="app"` (nav links only). Mobile hamburger menu on < md.
- **DashboardSidebar**: 5 nav items (dashboard, datahub, crawler, voice, knowledge). Props: `activePage`, `backendOnline`, `mobileOpen`, `onMobileClose`. Mobile overlay with backdrop.
- **BackendBadge**: Green/red dot with Korean status text. Used in sidebar footer.

## API Client (`lib/api.ts`)

- `API_BASE` from `NEXT_PUBLIC_API_URL` env var, defaults `http://localhost:8000`
- `getAuthHeaders()` adds `X-API-Key` when `NEXT_PUBLIC_API_KEY` is set
- Interfaces: `ChatResponse`, `Document`, `Conversation`, `Analytics`, `Datahub*`, `Crawl*`, `Voice*`
- Voice API: 7 interfaces + 7 fetch functions (upload, demo, status, transcript, document, approve, jobs)
- All endpoints via `fetch()` — no axios

## Styling

- **Tailwind v4** via `@import "tailwindcss"` in globals.css (not v3 config)
- **Brand color**: `#2563EB` (blue-600)
- **CSS custom properties**: `--background`, `--foreground`, `--primary`, `--gray-*` scale
- **Fonts**: Geist Sans + Geist Mono via `next/font/google`
- **Custom animations**: `typing-dot`, `fadeInUp`, `pulse-glow`, `grow-bar`
- **No dark mode** — light theme only
- **Mobile responsive**: Hamburger menu on Navbar (< md), sidebar overlay on admin (< lg)

## Sentry Integration

- `sentry.client.config.ts`, `sentry.server.config.ts`, `sentry.edge.config.ts`
- `next.config.ts` wrapped with `withSentryConfig`
- Error boundaries call `Sentry.captureException`
- Only active when `NEXT_PUBLIC_SENTRY_DSN` is set

## Conventions

- TypeScript `strict: true`, no `as any`, no `@ts-ignore`
- `interface` over `type` for object shapes
- `import type { X }` for type-only imports
- Path alias: `@/*` → `./src/*`
- No eslint, no prettier — rely on TS strict + Next.js defaults
- No test framework configured for frontend

## Gotchas

- `postcss.config.mjs` exists (Tailwind v4 requirement)
- Widget page has dual mode: normal preview vs iframe embed (`?embed=true`)
- Dashboard fetches real data on mount, falls back to mock data if backend offline
- Admin pages should go under `(admin)/` route group, NOT at app root
