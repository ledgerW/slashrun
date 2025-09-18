# Phase 4 — Network View (Link Analysis, Next.js / React Translation)

## Purpose

Deliver a link-analysis workspace that surfaces structural relationships independent of geography. Build a force-directed / analytic graph viewer showing trade, sanctions, alliances, and interbank dependencies derived from `GlobalState` matrices. Integrate with timeline state, map selections, and evidence rail filters to maintain Gotham’s single-pane-of-truth experience.

## Inputs

**From Phase 3:**
- Shared `SimulationProvider` with active scenario, timestep, and selected countries (single/multi)
- Map data selectors (adjacency lists, centroids) ready for reuse
- Layer toggles and UI styling tokens for dark Gotham theme

**Backend Dependencies:**
- `GlobalState.trade_matrix`, `alliances`, `sanctions`, `interbank_matrix`
- Country metadata (region, GDP, classification) from `countries`
- Optional server-provided network analytics (if available) to reduce client cost

**Libraries:**
- `@visx/network` or custom D3-force implementation with React bindings
- `d3-force-3d` (optional) for z-depth separation
- `d3-hierarchy` for alternate layouts

## Deliverables

```
frontend/
├── app/(workspace)/network/NetworkPanel.tsx          # Suspense boundary + layout shell
├── app/(workspace)/network/GraphCanvas.tsx           # Client component rendering SVG/WebGL graph
├── app/(workspace)/network/hooks/
│   ├── useNetworkData.ts                             # Transforms matrices into nodes/edges
│   ├── useNetworkLayout.ts                           # D3 force simulation + alternate layouts
│   ├── useNetworkMetrics.ts                          # Centrality, clustering, path computations
│   └── useNetworkInteractions.ts                     # Handles selection, drag, tooltip logic
├── app/(workspace)/network/components/
│   ├── NetworkControls.tsx                           # Layer toggles, layout switcher, filters
│   ├── NetworkLegend.tsx                             # Encodes node/edge semantics
│   ├── NetworkSidebar.tsx                            # Shows metrics for selected nodes/edges
│   ├── NodeDetailCard.tsx                            # Mini evidence summary for selected country
│   └── PathExplorer.tsx                              # UI for shortest path / ego network focus
├── app/(workspace)/network/utils/
│   ├── graphBuilders.ts                              # Helpers to build weighted adjacency from `GlobalState`
│   ├── colorScales.ts                                # Consistent palettes (trade=teal, sanctions=amber, etc.)
│   ├── layoutPresets.ts                              # Force parameters tuned per layer type
│   └── svgExport.ts                                  # Export current layout as SVG/PNG
├── styles/network.module.css                         # Grid layout + HUD styling
└── docs/PHASE-4-README.md
```

## Implementation Checklist

### Data & Layout
- [ ] `useNetworkData` merges selected matrices into unified node/edge arrays with metadata (type, weight, timestamp)
- [ ] Provide filtering by layer (trade/sanctions/alliances/interbank) and minimum weight threshold
- [ ] Derive node attributes: GDP (size), region (color accent), sentiment (glow intensity)
- [ ] Implement `useNetworkLayout` using D3 force simulation with physics parameters configurable per layer
- [ ] Support alternate layouts: force-directed, circular by region, hierarchical by alliances, geographic (reuse map centroids)
- [ ] Persist user layout preference & pinned node positions via localStorage

### Rendering
- [ ] `GraphCanvas` renders nodes/edges using SVG (for <500 edges) or Canvas/WebGL fallback for larger graphs
- [ ] Use GPU acceleration (Pixi.js or regl) if network exceeds 1k edges (feature flag)
- [ ] Provide smooth transitions when timeline updates weights—animate stroke width/opacity rather than reposition entire graph
- [ ] Display directional arrows for asymmetric matrices (trade exports, sanctions)
- [ ] Visualize edge magnitude with thickness + animated particles (optional) for active flows

### Interaction
- [ ] Click/keyboard selection updates `SimulationProvider.activeCountries` and evidence rail filters
- [ ] Hover tooltips show country summary + latest audit change affecting that node
- [ ] Drag-and-pin nodes; pinned state stored in provider to persist across timeline steps
- [ ] Multi-select: shift+click to build comparison set; PathExplorer finds shortest path between two selections
- [ ] Provide minimap/overview for orienting in large networks
- [ ] Implement search combobox (reuse from map) focusing nodes inside graph

### Analytics & Timeline Sync
- [ ] `useNetworkMetrics` calculates degree, betweenness, clustering coefficient per node using cached results
- [ ] Display metrics in `NetworkSidebar` with badges/trend indicators (based on previous timestep comparison)
- [ ] Timeline updates trigger incremental edge weight adjustments; highlight edges that appeared/disappeared since prior timestep
- [ ] Provide playback overlay showing how network evolves (fade edges in/out)
- [ ] Optionally integrate Web Worker for heavy analytics to keep UI responsive

### Controls & UX
- [ ] `NetworkControls` includes toggles for each relationship layer, slider for weight threshold, layout selector, play/pause timeline sync
- [ ] Provide "Focus on selection" button to zoom to ego network, "Reset layout" to default
- [ ] Legends describing color semantics, edge thickness, animation meaning; accessible with ARIA descriptions
- [ ] Show sync badge when network is locked to timeline vs user-scrubbed time offset (if implemented)

### Testing
- [ ] Unit tests for `graphBuilders` to ensure accurate translation from matrices to edges (trade_matrix is directional, alliances undirected)
- [ ] Tests for `useNetworkLayout` verifying deterministic outputs when seeded (for snapshot comparisons)
- [ ] Component tests ensuring selecting a node updates provider and evidence rail mocks
- [ ] Playwright scenario: enable sanctions layer, select node, view metrics, change layout, scrub timeline

## Validation Tests

### Functional
- [ ] Layer toggles correctly add/remove edges without re-creating entire simulation
- [ ] Selecting node updates evidence rail and timeline summary
- [ ] Timeline scrub updates weights and highlights new/removed edges
- [ ] Export function generates SVG/PNG reflecting current view

### Accessibility
- [ ] Controls reachable via keyboard with logical focus order
- [ ] Provide textual list representation of selected nodes/edges for screen readers
- [ ] Announce key state changes (e.g., "Sanctions layer enabled") via ARIA live region

### Performance
- [ ] Maintain >40 FPS for 80 nodes / 400 edges, >25 FPS for 150 nodes / 800 edges
- [ ] Force simulation stabilizes within 2s for medium-size graphs; layout caching prevents jitter on repeated timesteps
- [ ] Worker-based analytics complete within 500ms for 150-node graph

## API Integration Notes

- Reuse timeline data fetched in Phase 2; no additional endpoints required unless requesting aggregated analytics
- If backend can provide precomputed centrality metrics per timestep, integrate via TanStack Query to avoid client CPU cost
- Align node identifiers with ISO codes used across map/time-series for consistent selection

## Handoff Memo → Phase 5

**What’s Complete:**
- Link-analysis panel synchronized with timeline and shared selection state
- Data transformation utilities bridging matrices to visualization-friendly structures
- Analytics hooks providing centrality/clustering metrics for chosen nodes

**Up Next (Phase 5):**
- Build time-series charts that react to selected countries (from map/network) and timeline scrubbing
- Share selectors for macro indicators across network + charts to maintain consistent formatting
- Extend provider to broadcast indicator selections for chart overlays and comparative metrics

**Integration Notes:**
- Ensure `SimulationProvider` exposes derived metrics (selected countries, comparison sets) for charts
- Keep color assignments consistent (country colors reused in time-series lines and network nodes)
- Provide events when analytics computations finish to allow charts/evidence rail to display insights
