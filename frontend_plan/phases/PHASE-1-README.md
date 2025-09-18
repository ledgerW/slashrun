# Phase 1 — Authentication & Core State Management (Next.js / React Translation)

## Purpose

Harden the authentication workflow introduced in Phase 0 and establish the first shared client data stores. Users authenticate through Next.js Route Handlers with JWT cookies, workspace routes become fully protected, and foundational simulation context is introduced to mirror the backend `ScenarioResponse` and `GlobalState` contracts. This phase sets the baseline for all investigative experiences.

## Inputs

**From Phase 0:**
- Next.js App Router structure with `(auth)` and `(workspace)` segments
- `WorkspaceShell`, `TopBar`, `SidebarNav`, `EvidenceRail`, `TimelineFooter` skeleton components
- `apiFetch`, `AuthProvider`, `UIStateProvider`, and Gotham design tokens

**Backend Dependencies:**
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/simulation/scenarios`
- `GET /api/simulation/scenarios/{id}` (initial scenario context)

## Deliverables

```
frontend/
├── app/(auth)/login/page.tsx                 # Controlled form with server action handling
├── app/(auth)/login/LoginForm.tsx            # Client component using React Hook Form + Zod
├── app/(workspace)/layout.tsx                # Enforces auth via server-side session lookup
├── app/(workspace)/page.tsx                  # Fetches scenario summaries server-side, renders list
├── app/(workspace)/_components/
│   ├── ScenarioSwitcher.tsx                  # Client dropdown for selecting active scenario
│   ├── WorkspaceShell.tsx                    # Updated to accept user + scenario props
│   └── LoadingStates.tsx                     # Skeletons for initial data fetch
├── app/(workspace)/_providers/
│   ├── AuthProvider.tsx                      # Supplies user data + logout handler
│   ├── SimulationProvider.tsx                # New context (Zustand) for scenario + timeline metadata
│   └── QueryProvider.tsx                     # Wraps TanStack Query client with suspense support
├── lib/
│   ├── auth.ts                               # `login`, `logout`, `getUserSession` helpers
│   ├── simulation.ts                         # Scenario fetchers, data selectors
│   ├── server-actions.ts                     # Login/Logout server actions
│   └── types/simulation.ts                   # `ScenarioSummary`, `ScenarioDetail`, base `GlobalState` types
├── hooks/
│   ├── useScenarioList.ts                    # TanStack Query hook for scenario list
│   ├── useActiveScenario.ts                  # Reads/writes active scenario in provider & localStorage
│   └── useAuthRedirect.ts                    # Redirects unauthenticated clients (for legacy pages/tests)
├── middleware.ts                             # Edge middleware redirecting unauthenticated requests
└── docs/PHASE-1-README.md
```

## Implementation Checklist

### Authentication Flow
- [ ] Replace simple form submission with server action (`loginAction`) invoked from `LoginForm`
- [ ] Validate credentials client-side using Zod schemas (email/password)
- [ ] On success, set `slashrun_token` cookie (httpOnly, secure) and `redirect` to workspace
- [ ] Implement logout server action clearing cookies + invalidating client cache
- [ ] Update middleware to guard `/app/(workspace)` routes and static assets under workspace scope

### Protected Routing & Layout
- [ ] `getUserSession` fetches user details server-side; `WorkspaceLayout` redirects if absent
- [ ] Provide `AuthProvider` at the top of `(workspace)` layout with user metadata (id, email, roles)
- [ ] Render `WorkspaceShell` only after user + scenario data resolved (use Suspense fallback skeleton)

### Scenario & Simulation State
- [ ] Fetch scenario list server-side on workspace home (`page.tsx`) using `apiFetch`
- [ ] Hydrate TanStack Query cache with scenario list using `dehydrate` + `HydrationBoundary`
- [ ] Introduce `SimulationProvider` (Zustand store) storing:
  - `activeScenarioId`
  - `scenarioList: ScenarioSummary[]`
  - `timeline: { current: number; max: number; status: "idle" | "loading" }`
- [ ] Provide actions (`setActiveScenario`, `setTimeline`) accessible via hooks
- [ ] Persist last opened scenario to `localStorage` for user convenience

### API Client Enhancements
- [ ] Add helper `withAuthHeaders` for client-side `fetch` (used by TanStack Query hooks)
- [ ] Normalize error responses into discriminated unions for consistent UI handling
- [ ] Expand TypeScript definitions for `ScenarioResponse`, `GlobalState`, `SimulationRules`

### UI & UX
- [ ] Update `TopBar` to show signed-in user avatar/name and scenario switcher
- [ ] Provide global toast/notification system (e.g., Radix UI + `@/components/Toaster`) for auth errors
- [ ] Enhance login form with Gotham-inspired styling, error states, and loading spinner on submit
- [ ] Ensure focus management: on auth error, focus error summary; after login redirect, focus workspace heading

### Testing & Tooling
- [ ] Unit test `SimulationProvider` actions/selectors (Vitest)
- [ ] Component test for `LoginForm` using Testing Library
- [ ] Playwright test: login flow, redirect to workspace, scenario list visible
- [ ] Storybook story for `LoginForm` (default, error state)

## Validation Tests

### Authentication
- [ ] Valid credentials → cookie set, workspace rendered with user data
- [ ] Invalid credentials → inline error, focus returns to email input
- [ ] Logout clears cookie, redirects to `/login`, prevents workspace revisit without re-auth
- [ ] Middleware denies direct navigation to `/workspace` when not authenticated

### Scenario State
- [ ] Scenario list fetched and cached via TanStack Query (no duplicate network calls on navigation)
- [ ] Changing active scenario updates provider state and persists to `localStorage`
- [ ] Active scenario selection reflected in `TopBar` and placeholder content area

### Accessibility & Performance
- [ ] Axe audit passes on login and workspace home
- [ ] Keyboard-only navigation covers login form, scenario switcher, logout button
- [ ] First load of workspace with cached credentials renders in <2.5s with Suspense fallback

## API Integration Notes

- Use server components to fetch initial scenario data for SEO-less but data-secure rendering
- TanStack Query keys: `['scenarios', userId]` for list, `['scenario', id]` for details (future phases)
- Prepare `useActiveScenario` to fetch scenario detail lazily when selection changes

## Handoff Memo → Phase 2

**What’s Complete:**
- Authenticated Next.js workspace with secure cookie handling and route protection
- Scenario list hydration and active scenario selection stored in `SimulationProvider`
- Initial timeline metadata fields available in provider for upcoming scrubber
- Error handling and notification primitives standardized (toasts, inline errors)

**Up Next (Phase 2):**
- Build timeline scrubber UI as client component bound to `SimulationProvider`
- Fetch `SimulationStepResponse` data to populate timeline cache and evidence rail
- Extend provider with audit caches keyed by timestep
- Implement TanStack Query hooks for `/states/{t}` and `/step` endpoints

**Integration Notes:**
- Ensure `SimulationProvider` exposes setter for `maxTimestep` and caches to support scrubbing
- Align `ScenarioDetail` type with backend `GlobalState` to avoid mismatches during timeline implementation
- Confirm middleware and server-side auth helpers work with Playwright for upcoming end-to-end tests
