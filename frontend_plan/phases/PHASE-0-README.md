# Phase 0 — Project Skeleton & Conventions (Next.js / React Translation)

## Purpose

Bootstrap the SlashRun Gotham-inspired workspace using **Next.js 14 (App Router) + TypeScript**. Establish the foundational layout (top bar, left nav, central canvas, evidence rail, timeline footer), shared design tokens, routing primitives, and API utilities that every subsequent phase extends. No visualization logic yet—focus on structure, theming, and developer experience.

## Inputs

- Backend endpoints for smoke testing: `/api/auth/login`, `/api/simulation/scenarios`, `/api/simulation/scenarios/{id}/step`
- Simulation schema definitions from [`db/models/state.py`](../../db/models/state.py) to shape TypeScript types
- Gotham visual references (provided screenshots)

## Deliverables

```
frontend/
├── app/
│   ├── layout.tsx                     # Root layout applying fonts, theme, providers
│   ├── globals.css                    # Imports design tokens, resets, base styles
│   ├── (auth)/login/page.tsx          # Public login route
│   ├── (auth)/layout.tsx              # Auth layout (without workspace chrome)
│   ├── (workspace)/layout.tsx         # Protected workspace layout shell
│   ├── (workspace)/page.tsx           # Placeholder workspace home (skeleton panels)
│   ├── api/
│   │   ├── auth/login/route.ts        # Route handler proxying FastAPI login
│   │   └── auth/logout/route.ts       # Route handler for logout
│   └── (workspace)/_components/
│       ├── WorkspaceShell.tsx         # Composes top bar, nav, main canvas, evidence rail
│       ├── SidebarNav.tsx             # Vertical navigation placeholders
│       ├── TopBar.tsx                 # Global controls (scenario selector stub)
│       ├── EvidenceRail.tsx           # Empty accordion containers
│       ├── TimelineFooter.tsx         # Footer region reserved for scrubber
│       └── Panel.tsx                  # Reusable Gotham-styled panel wrapper
├── styles/
│   ├── tokens.css                     # CSS variables for dark theme + spacing
│   ├── layout.css                     # CSS Modules for shell layout
│   └── typography.css                 # Font stack + utility classes
├── lib/
│   ├── api.ts                         # `apiFetch` helper for server/client usage
│   ├── auth.ts                        # Session helpers (getUserSession, setAuthCookies)
│   └── types.ts                       # Base TypeScript interfaces (`ScenarioSummary`, etc.)
├── app/(workspace)/_providers/
│   ├── AuthProvider.tsx               # Client provider for auth context + logout
│   └── UIStateProvider.tsx            # Controls sidebar/timeline collapsed state
├── public/
│   └── icons/                         # Placeholder SVGs (to be replaced later)
└── docs/
    └── PHASE-0-README.md              # This file
```

## Implementation Checklist

### Project Setup
- [ ] Initialize Next.js 14 project with App Router, TypeScript, ESLint, Prettier, Jest/Vitest baseline
- [ ] Configure path aliases (`@/app`, `@/lib`, `@/types`, etc.)
- [ ] Add `next/font` setup for Inter & IBM Plex Sans in root layout

### Theming & Layout
- [ ] Define Gotham-inspired design tokens in `styles/tokens.css` (colors, elevation, spacing, typography scale)
- [ ] Build responsive workspace grid: left nav (min 72px), central content, right evidence rail (360px), timeline footer (120px)
- [ ] Implement `WorkspaceShell` composition with ARIA landmarks (`header`, `nav`, `main`, `aside`, `footer`)
- [ ] Provide focus outlines, skip-links, and keyboard navigation scaffolding

### Authentication Skeleton
- [ ] Create `/login` form with controlled inputs, client validation, and submission to `app/api/auth/login`
- [ ] Store JWT in `httpOnly` cookie via route handler; maintain minimal session object (user id/email)
- [ ] Implement `getUserSession` helper for server components; redirect unauthenticated users away from workspace routes
- [ ] Add logout handler that clears cookies and redirects

### API & State Utilities
- [ ] Implement `apiFetch` abstraction supporting server/client contexts, automatic auth headers, and 401 handling
- [ ] Stub `AuthProvider` with React context (user, logout) using client component
- [ ] Scaffold `UIStateProvider` with Zustand for sidebar/timeline toggles (no timeline logic yet)
- [ ] Create TypeScript interfaces for `ScenarioResponse` summaries used in nav placeholders

### Developer Experience
- [ ] Add ESLint config extending `eslint-config-next` with accessibility rules
- [ ] Configure Prettier + lint staged hooks
- [ ] Initialize Storybook with dark theme previews for shell components
- [ ] Provide initial unit tests (Vitest/Testing Library) for `Panel` and `WorkspaceShell` structure

## Validation Tests

### Functional
- [ ] Access `/login` without auth → login form renders, workspace layout not loaded
- [ ] Submit valid credentials (mock FastAPI) → cookie created, redirect to workspace home
- [ ] Attempt to access workspace route without cookie → redirected to `/login`
- [ ] Workspace skeleton renders top bar, nav, evidence rail, timeline footer with placeholder content

### Accessibility
- [ ] Axe audit: no critical violations on login or workspace skeleton
- [ ] Keyboard navigation traverses primary regions in logical order
- [ ] Skip link jumps to main content

### Performance
- [ ] Initial load LCP < 2s with skeleton content
- [ ] Zero hydration mismatches between server and client render

## API Endpoints Used

- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/simulation/scenarios` (used to validate API client; display placeholder list)

## Key Architecture Decisions

- App Router segmentation: `(auth)` for unauthenticated pages, `(workspace)` for protected shell
- Auth stored in cookies to leverage server components without manual token threading
- Foundational providers created now to avoid refactors later (auth context, UI state)
- Design tokens centralized for re-use in charts, maps, and cards downstream

## Handoff Memo → Phase 1

**What’s Complete:**
- Gotham-aligned workspace shell rendered through Next.js layouts/components
- Auth pipeline (login/logout) with cookie storage and protected routes
- API helper + base types bridging to backend simulation endpoints
- Providers for auth and UI state scaffolding

**What’s Next (Phase 1):**
- Flesh out scenario listing + selection via TanStack Query
- Introduce simulation context provider aware of `GlobalState` schema
- Prepare hooks for timeline state (current timestep, max, cache) without UI yet
- Expand tests to cover authenticated navigation

**Integration Notes:**
- Ensure `ScenarioResponse` typing aligns with backend shape for upcoming lists
- Keep workspace layout flexible for future insertion of timeline/map/network components
- Confirm auth cookie naming and expiration with backend team before Phase 1 rollout
