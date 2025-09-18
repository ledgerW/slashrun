# Phase 6 — Scenario Builder (Next.js / React Translation)

## Purpose

Develop an ontology-aware form system for creating and editing scenarios, leveraging the rich `GlobalState`, `SimulationRules`, and trigger models defined in [`db/models/state.py`](../../db/models/state.py). The builder lets analysts assemble initial states, configure policy regimes, upload matrices, and preview impacts before persisting to the backend.

## Inputs

**From Phase 5:**
- Indicator catalog and statistics utilities for validation feedback
- Simulation providers exposing scenario metadata, active selection, and caches
- Authenticated workspace with API client + server actions

**Backend Dependencies:**
- `POST /api/simulation/scenarios` (create)
- `PATCH /api/simulation/scenarios/{id}` (update)
- Optional endpoints for template retrieval (`/api/simulation/templates/*`)
- Validation errors returned via FastAPI for mismatch with Pydantic models

**Libraries:**
- React Hook Form + Zod for schema-based form validation
- `react-dropzone` for CSV/JSON uploads (matrices)
- `react-aria` / Radix UI form components for accessibility

## Deliverables

```
frontend/
├── app/(workspace)/builder/page.tsx                        # Server component gating access + prefetching templates
├── app/(workspace)/builder/ScenarioBuilder.tsx             # Client orchestrator with multi-step wizard
├── app/(workspace)/builder/steps/
│   ├── OverviewStep.tsx                                    # Scenario name, description, metadata
│   ├── CountriesStep.tsx                                   # Country selection + initial metrics editor
│   ├── MatricesStep.tsx                                    # Trade/interbank/sanctions/alliance uploads + editors
│   ├── RulesStep.tsx                                       # Configure `SimulationRules` & `RegimeParams`
│   ├── EventsStep.tsx                                      # Configure `GlobalState.events` and timeline seeds
│   └── ReviewStep.tsx                                      # Summary, validation results, submit
├── app/(workspace)/builder/components/
│   ├── CountryEditor.tsx                                   # Inline table editing for `CountryState`
│   ├── MatrixUploader.tsx                                  # Upload + edit adjacency matrices with heatmap preview
│   ├── RulesForm.tsx                                       # Form fields for `RegimeParams` (monetary, fiscal, trade, etc.)
│   ├── TriggerBuilderPreview.tsx                           # Preview integration with Phase 7 components
│   ├── ValidationSummary.tsx                               # Displays errors/warnings referencing indicator catalog
│   └── AutosaveBanner.tsx                                  # Indicates unsaved changes, autosave status
├── app/(workspace)/builder/hooks/
│   ├── useScenarioDraft.ts                                 # Zustand store for form data (mirrors GlobalState structure)
│   ├── useMatrixImport.ts                                  # Parses CSV/JSON into `Matrix` typed objects
│   ├── useValidation.ts                                    # Runs synchronous & async validation
│   └── useAutosave.ts                                      # Periodically saves draft to localStorage or backend draft endpoint
├── app/(workspace)/builder/utils/
│   ├── defaultTemplates.ts                                 # Default values for new scenarios (baseline metrics)
│   ├── schema.ts                                           # Zod schemas aligned with backend Pydantic models
│   ├── transformers.ts                                     # Convert form state to API payload
│   └── diffPreview.ts                                      # Compute diff between draft and existing scenario
└── docs/PHASE-6-README.md
```

## Implementation Checklist

### Form Architecture
- [ ] Structure builder as multi-step wizard with progress indicator and ability to jump between steps
- [ ] Use React Hook Form contexts per step; maintain single source of truth in `useScenarioDraft`
- [ ] Provide undo/redo stack for changes (optional but recommended for analysts)
- [ ] Support loading existing scenario for editing (prefill fields from API)
- [ ] Implement autosave (localStorage or backend drafts) to prevent data loss

### Step Details
- **Overview**
  - [ ] Capture scenario metadata (name, description, tags) with validation
  - [ ] Display summary metrics (countries count, base currency, initial timestep)
- **Countries**
  - [ ] List available countries with search/filter; allow adding/removing from scenario
  - [ ] For each selected country, allow editing macro/external/finance/trade/energy/sentiment fields with inline validation (range checks using indicator stats)
  - [ ] Provide quick set templates (e.g., use baseline, apply percentage delta)
- **Matrices**
  - [ ] Upload CSV/JSON for trade/interbank/sanctions/alliances; show validation results (square matrices, normalized values)
  - [ ] Provide manual editor with table/heatmap view for adjustments
  - [ ] Support symmetric enforcement or direction toggles per matrix
- **Rules**
  - [ ] Form controls for `RegimeParams` (monetary, fiscal, trade, security, labor, sentiment)
  - [ ] Inline documentation tooltips describing each parameter (phi_pi, tariff_multiplier, etc.) referencing backend defaults
  - [ ] Allow toggling invariants (`SimulationRules.invariants`)
- **Events**
  - [ ] Create initial events list populating `GlobalState.events.pending`
  - [ ] Provide timeline preview showing scheduled events and triggers interactions
- **Review**
  - [ ] Display diff vs baseline or existing scenario
  - [ ] Run validation summary showing blocking errors vs warnings (e.g., GDP missing, matrix imbalance)
  - [ ] Confirm submission with server action; handle backend errors gracefully (map Pydantic errors to fields)

### Integration & UX
- [ ] Use Stepper navigation with breadcrumbs; display unsaved changes indicator
- [ ] Provide "Preview Simulation" button to run single step using server action (calls `/step` with draft state without persisting) if backend supports
- [ ] Ensure builder respects user permissions (only creators can edit)
- [ ] Support import/export of full scenario draft as JSON for sharing
- [ ] Provide keyboard shortcuts for navigation (Ctrl+S to save, Ctrl+Arrow to move steps)

### Validation
- [ ] Synchronous validation via Zod ensures types align with `GlobalState`
- [ ] Async validation: call backend endpoint to validate scenario (if available) before final submit
- [ ] Use indicator stats to surface warnings (e.g., inflation > 50%) but allow override with explanation
- [ ] Validate matrices sum to expected totals; highlight rows/columns violating constraints

### Testing
- [ ] Unit tests for `transformers` ensuring final payload matches backend schema
- [ ] Tests for `useScenarioDraft` verifying add/remove/update operations
- [ ] Component tests for key steps (Countries, Matrices, Rules) covering validation error display
- [ ] Playwright flows: create new scenario, autosave, reload draft, submit successfully

## Validation Tests

### Functional
- [ ] Creating new scenario sends payload matching backend expectation (verify via mocked API)
- [ ] Editing existing scenario preloads data, saving updates backend and refreshes caches
- [ ] Autosave persists draft and restores after reload
- [ ] Matrix imports detect structural errors and provide actionable messaging

### Accessibility
- [ ] Forms include labels, descriptions, error messaging accessible via screen readers
- [ ] Stepper navigation operable via keyboard; focus management on step transitions
- [ ] Table editors support keyboard data entry with instructions for screen-reader users

### Performance
- [ ] Large matrix (200x200) import + render under 1.5s using virtualization
- [ ] Autosave runs without blocking UI (debounced, runs in background)
- [ ] Draft store memory usage stable after extended editing session

## API Integration Notes

- Utilize server actions for create/update to ensure cookies used securely
- After submission, invalidate scenario list + timeline caches via TanStack Query
- For preview simulation, consider backend endpoint that accepts draft without storing (if not available, document limitation)

## Handoff Memo → Phase 7

**What’s Complete:**
- Scenario creation/editing workflow covering metadata, countries, matrices, rules, and events
- Validated payload transformation aligned with backend Pydantic models
- Autosave + diff preview infrastructure for iterative editing

**Up Next (Phase 7):**
- Dedicated Trigger Designer with visual condition/action builder using same scenario draft context
- Integrate trigger previews with builder review step for complete scenario configuration
- Expand validation to include trigger conflicts and scheduling overlaps

**Integration Notes:**
- Ensure `useScenarioDraft` exposes trigger collection for upcoming designer
- Align event timeline preview with trigger scheduling to avoid duplication
- Maintain typed models for triggers (PolicyPatch, ReducerOverride, etc.) for reuse
