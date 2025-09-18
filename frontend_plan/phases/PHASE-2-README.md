# Phase 2 — Timeline & Evidence Rail (Auditability Core, Next.js / React Translation)

## Purpose

Transform the workspace footer and right rail into the investigative heart of SlashRun. Build a timeline scrubber synchronized with simulation state, and an evidence rail surfacing `StepAudit`, reducer sequences, triggers, and diffs. All components become client-side React modules backed by the shared `SimulationProvider`, TanStack Query caches, and strongly typed data derived from `GlobalState` and `StepAudit` in [`db/models/state.py`](../../db/models/state.py).

## Inputs

**From Phase 1:**
- Authenticated workspace shell with `SimulationProvider` tracking active scenario and baseline timeline metadata
- Scenario list + selection logic, `useScenarioList`, `useActiveScenario`
- API utilities and auth-protected Route Handlers

**Backend Dependencies:**
- `GET /api/simulation/scenarios/{id}/states/{t}` → returns `SimulationStepResponse`
- `GET /api/simulation/scenarios/{id}/history?start_timestep=&end_timestep=`
- `POST /api/simulation/scenarios/{id}/step`
- `GlobalState`, `StepAudit`, `FieldChange`, `TriggerLog` schemas

## Deliverables

```
frontend/
├── app/(workspace)/page.tsx                     # Hydrates timeline data for initial timestep
├── app/(workspace)/timeline/TimelinePanel.tsx   # Client component containing scrubber + controls
├── app/(workspace)/timeline/TimelineScrubber.tsx
├── app/(workspace)/timeline/TimelineEvents.tsx  # Renders pins for triggers/events
├── app/(workspace)/timeline/PlaybackControls.tsx
├── app/(workspace)/evidence/
│   ├── EvidenceRail.tsx                         # Composes audit, reducer, trigger, diff sections
│   ├── AuditTrail.tsx                           # Virtualized list of `FieldChange`
│   ├── ReducerSequence.tsx                      # Step audit reducer order visualization
│   ├── TriggerLog.tsx                           # Trigger history display
│   ├── StateInspector.tsx                       # JSON viewer with search
│   └── DiffViewer.tsx                           # Side-by-side diff of `GlobalState`
├── app/(workspace)/_hooks/
│   ├── useTimelineController.ts                 # Encapsulates fetching/stepping logic
│   ├── useAuditData.ts                          # Returns audit trail + diff data
│   └── useTimelineKeyboardShortcuts.ts          # Binds key events to controller actions
├── app/(workspace)/_providers/
│   └── TimelineCacheProvider.tsx                # React context for cached `SimulationStepResponse`
├── lib/
│   ├── timeline.ts                              # Data selectors, diff utilities, caching helpers
│   └── diff.ts                                  # JSON diff implementation (e.g., `fast-json-patch`)
├── components/ui/
│   ├── VirtualList.tsx                          # Reusable virtualization component
│   ├── ToolbarButton.tsx                        # Shared Gotham-styled buttons
│   └── JSONViewer.tsx                           # Pretty-print JSON with collapse controls
└── docs/PHASE-2-README.md
```

## Implementation Checklist

### Timeline Controller & State
- [ ] Build `TimelineCacheProvider` storing `Record<number, SimulationStepResponse>` keyed by timestep
- [ ] Implement `useTimelineController` hook exposing:
  - `current`, `max`, `status`
  - `goTo(timestep)`, `stepForward()`, `stepBackward()`, `jumpToStart()`, `jumpToEnd()`
  - `scrub(toTimestep)` with debounced API fetch + optimistic preview
  - `runUntil(target)` calling `/step` sequentially with progress events
- [ ] Integrate TanStack Query for fetching states (`useSimulationStateQuery(timestep)`) with caching + suspense
- [ ] Prefetch adjacent timesteps when scrubbing stops

### Timeline UI
- [ ] `TimelinePanel` renders scrubber, controls, and metadata (current time, play status)
- [ ] `TimelineScrubber` built with `@radix-ui/react-slider` or custom canvas for 60fps updates
- [ ] Event pins derived from `StepAudit.triggers_fired`, `GlobalState.events.pending`, etc.
- [ ] Playback controls support keyboard shortcuts (←, →, space, shift+arrow for 10-step jumps)
- [ ] Display simulation clock, step duration, and progress indicator

### Evidence Rail Components
- [ ] `EvidenceRail` reads `current` timestep from provider and renders sections in accordions (Radix Accordion)
- [ ] `AuditTrail` uses virtualization (react-virtual) to render `FieldChange` items grouped by `field_path`
- [ ] `ReducerSequence` displays pipeline as vertical list with badges for duration/impact
- [ ] `TriggerLog` shows fired/pending triggers with status badges and metadata from `TriggerLog` entries
- [ ] `StateInspector` uses `JSONViewer` with search/filter by path (Levenshtein for fuzzy search optional)
- [ ] `DiffViewer` compares current vs previous timestep using diff utilities (highlight additions/removals)

### Data Processing
- [ ] Map `GlobalState` into summary stats for timeline header (e.g., GDP delta, inflation, triggers count)
- [ ] Build selectors for retrieving nested fields (`countries[code].macro.policy_rate`)
- [ ] Implement diff utilities using `jsondiffpatch` or custom tree diff optimized for `GlobalState` shape
- [ ] Provide export options (copy to clipboard, download JSON) with proper sanitization

### Performance & UX
- [ ] Debounce scrubbing at 150ms; display ghost indicator while data loads
- [ ] Cache up to N recent timesteps per scenario; purge oldest when exceeding limit
- [ ] Use Suspense boundaries around evidence sections to allow partial loading
- [ ] Provide "Live mode" indicator when stepping sequentially with spinner and ETA
- [ ] Ensure virtualization handles >5k field changes with smooth scrolling

### Testing
- [ ] Unit tests for `useTimelineController` (mock fetcher, verify caching/commands)
- [ ] Snapshot test for `AuditTrail` grouping logic
- [ ] Playwright test: scrub timeline, verify audit updates, triggers highlight
- [ ] Storybook stories for timeline states (empty, loading, populated, with errors)

## Validation Tests

### Functional
- [ ] Scrubbing updates `current` timestep, fetches state, updates evidence rail
- [ ] Stepping forward/back uses cached data when available (no duplicate requests)
- [ ] Trigger pins appear at correct timesteps and focus relevant evidence section when clicked
- [ ] Diff viewer accurately reflects numeric/string changes between timesteps

### Accessibility
- [ ] Timeline controls accessible via keyboard; slider has ARIA labels and announces values
- [ ] Evidence rail accordions respond to screen readers with appropriate headings
- [ ] Field change list supports "Jump to reducer" to maintain context

### Performance
- [ ] Scrubber at 60fps with large histories (test with 500 timesteps)
- [ ] Virtualized audit keeps FPS >50 when scrolling
- [ ] Prefetch success reduces API latency on immediate back-and-forth scrubbing

## API Integration Notes

- Query keys: `['scenario', scenarioId, 'state', timestep]` for step data; `['scenario', scenarioId, 'history', range]` for batches
- Use server actions for `POST /step` to keep credentials secure; optimistic update timeline state
- Align audit data shape with `StepAudit` (field path, reducer, calculation details) for consistent UI rendering

## Handoff Memo → Phase 3

**What’s Complete:**
- Interactive timeline + evidence rail synchronized to simulation state
- Cached `SimulationStepResponse` data with diffing utilities
- Hooks/providers supporting scrubbing, stepping, and audit visualization

**Up Next (Phase 3):**
- Introduce geospatial map panel as a client component synchronized with timeline and active scenario
- Reuse timeline state to animate overlays and highlight events triggered by current timestep
- Integrate selection events (country click on map) to feed evidence rail filters

**Integration Notes:**
- Ensure `SimulationProvider` exposes active country selection hooks for map/timeline interplay
- Timeline controller should emit events when timestep changes to notify map/time-series components
- Confirm diff utilities support partial data (some timesteps might lack full audit details)
