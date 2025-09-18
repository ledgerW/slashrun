# Cross-Phase Architecture Documentation (Next.js / React Translation)

## Overview

This document restates the cross-phase architectural guidance for the SlashRun frontend using a **Next.js 14 + React (App Router)** stack. Every reference to standalone HTML, vanilla CSS, or imperative JavaScript components has been converted into idiomatic React constructs, modern Next.js features, and TypeScript-first patterns. The design remains grounded in the Gotham-inspired aesthetic captured in the reference screenshots while aligning with the backend simulation models defined in [`db/models/state.py`](../db/models/state.py).

## System Architecture Overview

### Three-Tier Architecture (Next.js Edition)
```
┌─────────────────────────────────────────────────────────────────────────┐
│                             FRONTEND TIER                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────────┐ │
│  │  Next.js App Dir │  │  Styling System  │  │   React Client Logic   │ │
│  │  - Server Routes │  │  - CSS Modules   │  │  - Hooks & Context     │ │
│  │  - Metadata API  │  │  - Tailwind opt. │  │  - TanStack Query      │ │
│  │  - Streaming SSR │  │  - Theming API   │  │  - WebSocket client    │ │
│  └──────────────────┘  └──────────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────┐
│                             BACKEND TIER                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────────┐ │
│  │   FastAPI App    │  │   JWT Auth        │ │   WebSocket Simulator  │ │
│  │  - REST Endpoints│  │  - Token Issuer   │ │  - Real-time Updates   │ │
│  │  - Validation    │  │  - Session Mgmt   │ │  - State Sync          │ │
│  └──────────────────┘  └──────────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────┐
│                            DATABASE TIER                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────────┐ │
│  │    SQLModel      │  │    Audit Trail    │ │    Simulation State     │ │
│  │  - Domain Models │  │  - Field Changes  │ │  - `GlobalState` JSON   │ │
│  │  - Relations     │  │  - Trigger Logs   │ │  - Time-series History  │ │
│  └──────────────────┘  └──────────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

## Shared Design Patterns

### 1. Component Architecture Pattern

Every UI element becomes a typed React component. Core building blocks live under `frontend/app/(workspace)/_components` with co-located styles and tests.

```tsx
// Example structure for a reusable component
import type { ReactNode } from "react";

export interface PanelProps {
  title: string;
  toolbar?: ReactNode;
  children: ReactNode;
}

export function Panel({ title, toolbar, children }: PanelProps) {
  return (
    <section className="panel" aria-label={title}>
      <header className="panel__header">
        <h2>{title}</h2>
        {toolbar}
      </header>
      <div className="panel__body">{children}</div>
    </section>
  );
}
```

**Component conventions applied in every phase:**
- Co-locate component, styles, stories, and tests (`Panel.tsx`, `Panel.module.css`, `Panel.stories.tsx`, `Panel.test.tsx`).
- Prefer server components for static data and shell layout; use client components (`"use client"`) for interactive views (timeline scrubber, map, charts).
- Derive props types from backend models (e.g., `GlobalState`, `StepAudit`) using shared TypeScript definitions generated from Pydantic schemas or Zod adapters.

### 2. State Management Pattern

A centralized state layer orchestrated through **React Context + TanStack Query + Zustand slices** replaces the vanilla `StateManager` class. Simulation data mirrors the structure of `GlobalState` and `StepAudit` from the backend.

```tsx
// app/(workspace)/_providers/SimulationStore.tsx
"use client";
import { createContext, useContext } from "react";
import { createStore, useStore } from "zustand";
import type { GlobalState, StepAudit } from "@/types/simulation";

type TimelineState = {
  scenarioId: string | null;
  currentTimestep: number;
  maxTimestep: number;
  cache: Record<number, { state: GlobalState; audit: StepAudit | null }>;
};

const simulationStore = createStore<TimelineState>(() => ({
  scenarioId: null,
  currentTimestep: 0,
  maxTimestep: 0,
  cache: {},
}));

const SimulationContext = createContext(simulationStore);

export function SimulationProvider({ children }: { children: React.ReactNode }) {
  return <SimulationContext.Provider value={simulationStore}>{children}</SimulationContext.Provider>;
}

export function useSimulationState() {
  return useStore(useContext(SimulationContext));
}
```

**Persistence Strategy:**
- Authentication tokens in `httpOnly` cookies managed by Next.js Route Handlers.
- Lightweight UI preferences stored via `localStorage` hook (`useLocalStorage`) in client components.
- Simulation history cached with TanStack Query and memoized selectors.
- IndexedDB integration managed through a custom React hook when large datasets (timelines, audits) require offline persistence (Phase 2+).

### 3. API Integration Pattern

Replace manual `fetch` wrapper with a typed **API layer** exposed through Next.js Route Handlers and `@tanstack/react-query` hooks.

```tsx
// app/api/client.ts
import "server-only";
import { cookies } from "next/headers";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export async function apiFetch<T>(input: string, init?: RequestInit): Promise<T> {
  const token = cookies().get("slashrun_token");
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token.value}` } : {}),
    ...init?.headers,
  };

  const res = await fetch(`${BASE_URL}${input}`, {
    ...init,
    headers,
    cache: "no-store",
  });

  if (res.status === 401) {
    // Trigger soft logout on client via query invalidation
    throw new Error("AUTH_REQUIRED");
  }

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return res.json() as Promise<T>;
}
```

Client components consume this API through dedicated hooks (`useScenarios`, `useSimulationStep`, etc.) with optimistic updates and error boundaries.

## Cross-Phase Integration Points

### 1. Authentication Flow (Phase 1 → All Phases)

- Next.js Route Handlers `/api/auth/*` proxy FastAPI endpoints and manage cookie storage.
- Protected layouts implemented using server components that verify authentication in `generateMetadata` / `layout.tsx` before streaming workspace UI.
- `withAuth` higher-order layout pattern wraps every page inside `(workspace)` segment.

```tsx
// app/(workspace)/layout.tsx
import { redirect } from "next/navigation";
import { getUserSession } from "@/lib/auth";

export default async function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  const session = await getUserSession();
  if (!session) redirect("/login");
  return (
    <SimulationProvider>
      <WorkspaceShell user={session.user}>{children}</WorkspaceShell>
    </SimulationProvider>
  );
}
```

### 2. Simulation Data Contracts

- Shared TypeScript types derived from Pydantic models ensure strong typing. Example mapping:
  - `GlobalState` → `types/simulation.ts` with nested interfaces for `CountryState`, `Macro`, `External`, etc.
  - `StepAudit`, `FieldChange`, `Trigger`, `ScenarioResponse`, `SimulationStepResponse` mapped 1:1.
- Utility selectors convert deeply nested `GlobalState` slices into visualization-friendly data structures.

### 3. Eventing and Real-Time Updates

- WebSocket integration implemented via a dedicated client hook (`useSimulationSocket`) using the browser `WebSocket` API inside client components.
- Server actions trigger simulation steps and invalidate relevant query caches.
- React Suspense boundaries allow streaming updates while heavy visualizations progressively hydrate.

### 4. Styling System

- Gotham-inspired token set defined in `frontend/styles/tokens.css` and re-exported through CSS variables + Tailwind theme extension (optional but recommended for rapid layout work).
- Component-level styles rely on CSS Modules or Tailwind utility classes combined with `clsx` helpers.
- Dark mode is the default; design tokens expose semantic roles (surface, accent, warning, success) for charts and overlays.

### 5. Testing & Quality

- Unit tests with Vitest + Testing Library for React components.
- Playwright integration tests for navigation, authentication, timeline scrubbing, and audit interactions.
- Storybook for visual documentation of components per phase.

## Simulation State Awareness

The UI must internalize the backend simulation schema:
- **GlobalState**: Primary data object; timeline navigation fetches successive `GlobalState` snapshots.
- **CountryState**: Basis for panels, metrics, and map overlays; selection events narrow charts/network context.
- **SimulationRules & Regimes**: Exposed in builder phases to configure policy scenarios.
- **Events & Triggers**: Populate evidence rail, timeline pins, and narrative builders.

React components should avoid duplicating backend calculations—render data from API responses, using selectors purely for presentation.

## Technology Guardrails

- Use **TypeScript** everywhere for parity with backend models.
- Favor **React Server Components** for static layout and data that can be fetched on the server; switch to **Client Components** only when stateful interactivity is required.
- Avoid global mutable singletons; encapsulate state via providers/hooks.
- Ensure all data-fetching hooks support suspense (`enabled`, `suspense: true`) to fit Next.js streaming model.
- Maintain strict linting (`eslint-config-next`, custom rules for accessibility, imports).

## Next Steps

This architectural baseline informs each phase’s translation. Refer to the per-phase documents for concrete deliverables expressed as Next.js pages, layouts, components, hooks, and styles.
