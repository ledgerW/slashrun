# SlashRun Frontend Implementation Plan (Next.js / React Translation)
## Gotham-Inspired Multi-Phase Development Strategy

## Overview

This plan reinterprets the original HTML/CSS/vanilla JS implementation roadmap for a **Next.js 14 (App Router) + React + TypeScript** codebase. Each phase documents deliverables in terms of Next.js routes, layouts, components, hooks, and styling resources while preserving Gotham-inspired workflows and visual language. Backend integration continues to rely on the FastAPI endpoints and simulation schema defined in [`db/models/state.py`](../db/models/state.py).

### Design Philosophy

**Core Principles (unchanged):**
- **Single pane of truth**: Consolidated investigative workspace with persistent navigation shell.
- **Investigative workflow first**: React flows prioritize context → evidence → decisions.
- **Spacetime native**: Timeline and geospatial components are first-class client components.
- **Ontology-aware**: Components consume strongly typed `GlobalState`, `CountryState`, `StepAudit`, and trigger models.
- **Explainability & audit**: Evidence rail and audit viewers expose reducer chains, triggers, and diffs.
- **Performance under stress**: Streaming SSR, Suspense, React Server Components, and data virtualization keep interactions fluid.

### Visual Language
- **Dark theme tokens** exposed via CSS variables (`styles/tokens.css`) and optionally Tailwind theme extension.
- **Signal colors**: Blues/greens for positive signals, ambers/reds for warnings across charts and overlays.
- **Typography**: Inter + IBM Plex Sans served via `next/font` with utility classes for small caps labels.
- **Motion**: Framer Motion or CSS transitions ≤150ms for scrubbing, card expansions, and subtle emphasis.
- **Accessibility**: WCAG AA, keyboard-first interactions, ARIA-rich React components.

## Phase Structure

Each phase contains:
- **Purpose**
- **Inputs** (backend dependencies, upstream components)
- **Deliverables** (Next.js pages/layouts/components/hooks/tests)
- **Implementation Checklist**
- **Validation Tests**
- **API Integration**
- **Handoff Memo**

## Phase Overview (React Translation)

### Phase 0: Project Skeleton & Conventions ⚡ FOUNDATION
Create Next.js workspace shell, shared design tokens, and API utilities.

### Phase 1: Authentication & Core State Management 🔐 FOUNDATION
Implement cookie-based JWT auth, protected layouts, and initial simulation context.

### Phase 2: Timeline & Evidence Rail 🕒 CORE
Interactive timeline scrubber, audit rail, reducer chain visualization, diff inspector.

### Phase 3: Map View (Geospatial Layers) 🗺 VISUALIZATION
MapLibre/Deck.gl client component with time-aware overlays, synchronized with timeline state.

### Phase 4: Network View (Link Analysis) 🔗 VISUALIZATION
Force-directed graph via React + D3/visx showing alliances, sanctions, interbank ties.

### Phase 5: Time-Series Panel 📈 VISUALIZATION
Composable chart system for macro/finance/trade indicators with brushes and event markers.

### Phase 6: Scenario Builder 🔧 PRODUCTIVITY
Multi-step forms for scenarios/rules/trade matrices using React Hook Form + Zod.

### Phase 7: Trigger Designer ⚡ PRODUCTIVITY
Visual DSL builder for trigger conditions, policy patches, and dry-run preview.

### Phase 8: Walkthroughs & Sharing 📋 COLLABORATION
Narrative playlist builder, guided tours, export/share flows.

### Phase 9: Performance & Polish ✨ OPTIMIZATION
Workers, memoization, virtualization, accessibility audits, micro-interactions.

## Cross-Phase Architecture (Summary)

- **Data fetching**: Server Actions + TanStack Query hooks per resource (`useScenarioList`, `useSimulationHistory`).
- **State coordination**: Providers for auth, simulation timeline, UI preferences; context stored under `app/(workspace)/_providers`.
- **Routing**: App Router with segmented layouts (`(auth)`, `(workspace)`, nested routes for timeline/map/network modules).
- **Styling**: CSS Modules + Tailwind (optional) + Radix UI primitives extended with Gotham theming.
- **Testing**: Vitest, Testing Library, Playwright, Storybook in sync with Next environment.

## Dependencies & Tooling

- **Next.js 14**, **React 18**, **TypeScript**
- **@tanstack/react-query** for data synchronization
- **Zustand** for lightweight local state slices
- **React Hook Form + Zod** for complex forms (phases 6-7)
- **MapLibre GL** / **Deck.gl**, **visx** (charts + network)
- **Framer Motion** for orchestrated transitions (Phase 5+)
- **Storybook 8** for component documentation
- **Playwright** for end-to-end validation

## Quality Assurance Strategy

- **Linting**: `eslint-config-next` with custom rules for accessibility and imports
- **Formatting**: Prettier
- **Type safety**: `tsconfig` set to `strict`
- **Testing cadence**: Unit + integration tests added per phase; regression suites run via CI
- **Performance budgets**: Core Web Vitals thresholds enforced with Lighthouse CI and React Profiler snapshots

## Risk Mitigation

- **Visualization complexity**: Ship progressively with feature flags and fallback renderers
- **Performance**: Use Suspense, streaming, virtualization, and selective memoization early
- **Schema drift**: Generate TypeScript types from backend Pydantic models (e.g., via `datamodel-code-generator`)
- **Auth nuances**: Centralize cookie management, refresh flows, and route guards to avoid drift across phases

## Success Criteria

1. Every phase satisfies deliverables/tests defined in its README
2. No unhandled promise rejections or React hydration mismatches
3. Streaming SSR remains <3s to first paint on broadband
4. Accessibility audits (Axe/Deque) pass for critical flows
5. Stakeholder sign-off on Gotham aesthetic parity with reference screenshots

## Next Steps

1. Review translated plan with stakeholders
2. Initialize Next.js project skeleton (Phase 0)
3. Establish automated pipelines (lint/test/storybook/playwright)
4. Proceed iteratively through phases, validating against backend simulation state and audit requirements
