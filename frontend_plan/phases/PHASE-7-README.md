# Phase 7 — Trigger Designer (Next.js / React Translation)

## Purpose

Build a visual trigger authoring environment that lets analysts compose conditions and actions for scenario automation. Integrate tightly with the scenario builder draft so triggers operate on the same `GlobalState` shape and policy parameters defined in [`db/models/state.py`](../../db/models/state.py).

## Inputs

**From Phase 6:**
- `useScenarioDraft` storing draft scenario including triggers placeholder
- Validation utilities, matrix editors, and rules data for referencing available paths
- Autosave + review infrastructure for summarizing configuration

**Backend Dependencies:**
- Trigger schema: `Trigger`, `TriggerCondition`, `TriggerAction`, `PolicyPatch`, `ReducerOverride`, `NetworkRewrite`, `EventInject`
- `POST /api/simulation/scenarios/{id}` (create triggers alongside scenario)
- `PATCH /api/simulation/scenarios/{id}` (update triggers)
- Optional validation endpoint for DSL expressions (e.g., `/api/simulation/triggers/validate`)

**Libraries:**
- React Flow or similar for visual node editor (optional) or custom UI using Radix primitives
- Monaco Editor for DSL/JSON editing fallback

## Deliverables

```
frontend/
├── app/(workspace)/builder/trigger-designer/
│   ├── TriggerDesigner.tsx                          # Entry point orchestrating tabs (visual vs advanced)
│   ├── ConditionBuilder.tsx                         # Visual condition builder (filters, comparators)
│   ├── ActionComposer.tsx                           # UI for constructing patches/overrides/events
│   ├── TimelinePreview.tsx                          # Simulated timeline showing trigger scheduling
│   ├── TriggerList.tsx                              # Table of existing triggers with status badges
│   └── AdvancedEditor.tsx                           # Monaco-based editor for power users (JSON/DSL)
├── app/(workspace)/builder/hooks/
│   ├── useTriggerDraft.ts                           # Zustand store for triggers integrated with `useScenarioDraft`
│   ├── useConditionDSL.ts                           # Helper to parse/validate condition strings
│   ├── useTriggerSimulation.ts                      # Executes dry-run preview via backend endpoint (if available)
│   └── useTriggerConflicts.ts                       # Detect overlapping/conflicting triggers
├── app/(workspace)/builder/utils/
│   ├── triggerSchema.ts                             # Zod schema mapping to backend trigger models
│   ├── dslTemplates.ts                              # Predefined condition snippets (inflation thresholds, date checks)
│   ├── actionCatalog.ts                             # Metadata for patchable fields (paths, types, ranges)
│   └── timelineLayout.ts                            # Positions triggers on preview timeline
└── docs/PHASE-7-README.md
```

## Implementation Checklist

### Trigger Lifecycle
- [ ] CRUD operations for triggers within scenario draft (create, duplicate, delete)
- [ ] Autosave integration: triggers persist with scenario draft and included in final payload
- [ ] Display version history of edits (optional) for auditing changes

### Condition Builder
- [ ] UI to assemble conditions using dropdowns referencing countries, indicators, comparisons, logical operators
- [ ] Support compound expressions (AND/OR groups) and `once` flag configuration
- [ ] Provide inline preview of generated DSL string (e.g., `country('USA').macro.inflation > 0.05`)
- [ ] Validate expressions against available data paths (use indicator catalog + scenario draft fields)
- [ ] Offer time-based conditions (date >=, timestep >=) with date picker + timezone awareness

### Action Composer
- [ ] Allow selecting action type: Policy Patch, Reducer Override, Network Rewrite, Event Inject
- [ ] Provide field path picker for patches referencing `GlobalState` or `SimulationRules`
- [ ] Validate values against schema (number ranges, enums, etc.)
- [ ] Support multiple actions per trigger; reorder via drag-and-drop
- [ ] Provide preview of resulting patch JSON for transparency

### Timeline Preview & Simulation
- [ ] Visual timeline showing triggers with optional expiry (`expires_after_turns`)
- [ ] Simulate expected firing windows based on condition definitions (approximate)
- [ ] Integrate with `useTriggerSimulation` to dry-run against sample history (if backend endpoint exists)
- [ ] Highlight conflicts (multiple triggers modifying same field simultaneously)

### Advanced Editor & Export
- [ ] Offer JSON/DSL editor with Monaco for direct editing (sync with visual builder)
- [ ] Provide import/export functionality for triggers (JSON)
- [ ] Syntax highlighting, autocomplete for known field paths and functions
- [ ] Validation errors displayed inline with references to offending segments

### UX & Accessibility
- [ ] Tabbed interface switching between Visual and Advanced modes
- [ ] Keyboard navigation for building conditions/actions
- [ ] Contextual help popovers describing trigger concepts and example use cases
- [ ] Confirmation dialogs before deleting triggers; ability to disable instead of delete

### Testing
- [ ] Unit tests for `triggerSchema` ensuring parity with backend models
- [ ] Tests for `useConditionDSL` verifying DSL generation/parsing
- [ ] Component tests covering condition builder interactions and validation errors
- [ ] Playwright scenario: create trigger (condition + action), preview timeline, save, reload draft

## Validation Tests

### Functional
- [ ] Created triggers appear in review step and final payload
- [ ] Condition builder prevents invalid paths/operators and surfaces helpful errors
- [ ] Dry-run (if supported) returns results displayed in UI (success/failure)
- [ ] Trigger conflicts detection warns when same field mutated by overlapping triggers

### Accessibility
- [ ] Builder components accessible via keyboard and screen reader announcements
- [ ] Monaco editor fallback has accessible alternative (download/upload JSON) if screen reader incompatible
- [ ] Timeline preview provides textual description for triggers/events

### Performance
- [ ] Trigger list handles 50+ triggers without sluggishness
- [ ] DSL validation executes under 200ms per change (debounced)
- [ ] Dry-run simulation requests handled asynchronously with loading indicators

## API Integration Notes

- Ensure final scenario submission merges triggers from `useTriggerDraft` into payload
- If backend lacks DSL validation endpoint, implement front-end parser mirroring server rules or provide manual validation instructions
- Respect backend field naming; use canonical dotpaths (e.g., `rules.regimes.trade.tariff_multiplier`)

## Handoff Memo → Phase 8

**What’s Complete:**
- Trigger creation pipeline integrated with scenario builder, including validation and timeline preview
- Action catalog referencing simulation rules and state slices to avoid invalid patches
- Export/import support enabling sharing of trigger definitions

**Up Next (Phase 8):**
- Walkthrough & narrative tooling built atop triggers/events for storytelling and collaboration
- Use triggers metadata in walkthrough steps to highlight key inflection points
- Integrate with sharing/export flows to package scenarios + triggers + evidence

**Integration Notes:**
- Provide APIs/hooks for walkthrough module to fetch trigger metadata (names, descriptions, expected outcomes)
- Ensure triggers include optional descriptions to display in narratives
- Keep DSL generation utilities reusable for narrative filters and audit queries
