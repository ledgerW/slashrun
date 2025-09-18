# Phase 5 — Time-Series Panel (Next.js / React Translation)

## Purpose

Create a data-rich analytics panel that renders historical and comparative metrics for selected entities. Time-series charts respond to timeline scrubbing, selections from map/network, and highlight audit events to explain changes. The panel enables analysts to explore trends across macro, finance, trade, sentiment, and energy slices within `GlobalState`.

## Inputs

**From Phase 4:**
- `SimulationProvider` exposing active countries (single + multi-select) and timeline position
- Timeline controller with cached `SimulationStepResponse` history
- Evidence rail exposing triggers/events for annotation

**Backend Dependencies:**
- `GET /api/simulation/scenarios/{id}/history?start_timestep=&end_timestep=`
- Fields from `GlobalState.countries[code].{macro,external,finance,trade,energy,sentiment}`
- `GlobalState.commodity_prices`, `io_coefficients`, `events`

**Libraries:**
- `@visx/xychart` or `recharts` for declarative React charts (preference: visx for customization)
- `d3-scale`, `d3-array` for domain calculations
- `@tanstack/react-query` for history fetching + caching
- `date-fns` for formatting

## Deliverables

```
frontend/
├── app/(workspace)/analytics/TimeSeriesPanel.tsx        # Panel container with layout + Suspense
├── app/(workspace)/analytics/components/
│   ├── IndicatorChart.tsx                               # Generic chart wrapper (line/area/bar)
│   ├── IndicatorLegend.tsx                              # Legend w/ color sync to selections
│   ├── ComparisonTable.tsx                              # Tabular view of selected metrics
│   ├── BrushToolbar.tsx                                 # Brush range selector + presets
│   ├── EventMarkers.tsx                                 # Renders trigger annotations on charts
│   └── AnalysisSidebar.tsx                              # Displays correlation/trend insights
├── app/(workspace)/analytics/hooks/
│   ├── useTimeSeriesData.ts                             # Fetches + memoizes history windows
│   ├── useIndicatorSelection.ts                         # Manages selected indicators per panel
│   ├── useChartInteractions.ts                          # Hover syncing, crosshair, tooltip coordination
│   └── useStatistics.ts                                 # Calculates rolling stats, correlations
├── app/(workspace)/analytics/utils/
│   ├── indicatorCatalog.ts                              # Maps UI selections to `GlobalState` paths
│   ├── formatter.ts                                     # Number/percentage formatting functions
│   ├── diffSelectors.ts                                 # Helpers to compute delta vs previous timestep
│   └── exportHelpers.ts                                 # PNG/SVG/CSV export utilities
├── styles/analytics.module.css                          # Panel layout, chart area styling
└── docs/PHASE-5-README.md
```

## Implementation Checklist

### Data Acquisition & Caching
- [ ] `useTimeSeriesData` loads scenario history in paginated windows (e.g., 200 steps) using TanStack Query and caches by `scenarioId`
- [ ] Provide derived selectors to extract indicator series for selected countries + indicators
- [ ] Support normalization options: absolute, indexed to 100, per capita (requires `CountryState` population if available)
- [ ] Prefetch adjacent history ranges when user brushes beyond cached window

### Chart System
- [ ] `IndicatorChart` supports line (default), stacked area, bar (for discrete metrics), and scatter (for correlations)
- [ ] Implement responsive container using ResizeObserver; maintain minimum height 320px per chart
- [ ] Use shared color palette consistent with map/network selections (color from provider)
- [ ] Provide crosshair + synced tooltips across all charts to compare values at same timestep
- [ ] Integrate brush component to select time range; update timeline controller when brush released (optional setting)
- [ ] Add event markers from triggers (`StepAudit.triggers_fired`) and policy changes (diff of `SimulationRules`)

### Indicator Management
- [ ] `indicatorCatalog` enumerates available metrics grouped by domain (Macro, Trade, Finance, Energy, Sentiment)
- [ ] UI allows selecting up to N indicators per chart; multi-country overlay toggled via checkboxes
- [ ] Provide presets (e.g., "Inflation vs Policy Rate", "Trade Balance", "Sentiment Composite")
- [ ] Persist indicator selections per user via localStorage or server preference endpoint

### Analytics & Insights
- [ ] `useStatistics` computes rolling averages, volatility, growth rates, correlation matrix for selected series
- [ ] Display correlation heatmap/summary within `AnalysisSidebar`
- [ ] Provide trendline overlay (linear regression) with slope and R² values
- [ ] Highlight change points by analyzing diff thresholds; annotate on charts
- [ ] Offer comparison table summarizing latest value, change vs previous timestep, change vs baseline (timestep 0)

### Interaction & UX
- [ ] Hovering chart updates timeline tooltip but does not change global timestep unless user clicks (configurable)
- [ ] Clicking data point navigates timeline controller to that timestep and updates evidence rail
- [ ] Keyboard shortcuts for switching indicators (e.g., `[` `]` to cycle), `Alt+scroll` to zoom time range
- [ ] Export controls: PNG snapshot (via `html-to-image`), CSV download of current series, copy data to clipboard
- [ ] Provide empty states with guidance when no indicators selected or data missing

### Testing
- [ ] Unit tests for `indicatorCatalog` path resolution to ensure alignment with `GlobalState`
- [ ] Tests for `useTimeSeriesData` verifying caching window & normalization
- [ ] Component tests for `IndicatorChart` verifying multi-series legend/tooltip accuracy
- [ ] Playwright scenario: select countries/indicators, brush range, click event marker → timeline updates

## Validation Tests

### Functional
- [ ] Charts render values consistent with backend history data
- [ ] Timeline scrub updates crosshair and highlighted timestep in charts
- [ ] Brush selection optionally adjusts global timeline range when enabled
- [ ] Export features output accurate data and follow dark theme aesthetics

### Accessibility
- [ ] Charts expose data summaries via accessible tables / aria-live updates
- [ ] Controls keyboard navigable; focus indicators visible on dark background
- [ ] Tooltips provide text alternative accessible to screen readers

### Performance
- [ ] Rendering 5 charts with 1,000 points each maintains >45 FPS on modern hardware
- [ ] History fetch + transform for 1,000 timesteps completes <300ms with memoization
- [ ] Memory usage stable when switching between scenarios (cache eviction validated)

## API Integration Notes

- When requesting `/history`, request only needed range to reduce payload; implement query params for `start/end`
- Consider backend enhancements to pre-compute summary stats if real-time analytics become heavy
- Align indicator keys with backend naming (e.g., `macro.inflation`, `trade.exports_gdp`) to avoid brittle string paths

## Handoff Memo → Phase 6

**What’s Complete:**
- Time-series analytics panel integrated with timeline, map, and network selections
- Indicator catalog + analytics hooks for deriving insights from `GlobalState`
- Exportable chart experiences with event annotations tied to triggers

**Up Next (Phase 6):**
- Scenario Builder forms to create/edit `GlobalState` seeds, `SimulationRules`, matrices, and triggers
- Reuse indicator catalog + stats to provide validation hints in builder (e.g., baseline GDP, default policy rates)
- Ensure provider exposes functions to update scenario locally before submitting to backend

**Integration Notes:**
- Confirm indicator paths used here align with builder validation rules
- Maintain consistent color assignments (per country) between charts and other panels
- Provide typed interfaces for indicator definitions to reuse in forms and analytics
