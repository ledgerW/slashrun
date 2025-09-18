# Phase 3 — Map View (Geospatial Layers, Next.js / React Translation)

## Purpose

Introduce a Gotham-inspired geospatial panel that visualizes scenario relationships in space and time. The map becomes a synchronized client component inside the workspace center column, reflecting data from `GlobalState.trade_matrix`, `alliances`, `sanctions`, `interbank_matrix`, and `countries`. This phase connects timeline changes to animated overlays and feeds country selections back into the evidence rail and time-series views.

## Inputs

**From Phase 2:**
- Timeline controller emitting timestep change events and cached `SimulationStepResponse`
- Evidence rail capable of filtering by selected entities
- `SimulationProvider` aware of active scenario, timeline status, and caches

**Backend Dependencies:**
- `GlobalState` fields: `countries`, `trade_matrix`, `alliances`, `sanctions`, `interbank_matrix`, `events`
- Optional geospatial metadata endpoint (if available) or static GeoJSON assets

**External Libraries:**
- **MapLibre GL JS** (preferred) or **Deck.gl** for base map rendering
- `react-map-gl` bindings for React integration
- Natural Earth / OSM vector tiles for basemap styling

## Deliverables

```
frontend/
├── app/(workspace)/map/MapPanel.tsx                 # Suspense-wrapped map container
├── app/(workspace)/map/MapViewport.tsx              # Client component hosting MapLibre canvas
├── app/(workspace)/map/layers/
│   ├── TradeFlowsLayer.tsx                          # Animated arcs using Deck.gl Layer or custom MapLibre source
│   ├── SanctionsLayer.tsx                           # Choropleth + link overlays
│   ├── AlliancesLayer.tsx                           # Network lines w/ strength encoding
│   ├── InterbankLayer.tsx                           # Directed financial exposure flows
│   └── CountryMetricsLayer.tsx                      # Choropleth for macro indicators
├── app/(workspace)/map/controls/
│   ├── LayerTogglePanel.tsx                         # UI for toggling overlays, opacity sliders
│   ├── TimeSyncBadge.tsx                            # Displays timeline sync status
│   ├── SearchControl.tsx                            # Country search (Combobox)
│   └── BasemapStyleSwitch.tsx                       # Toggle between dark/light basemap (if needed)
├── app/(workspace)/map/hooks/
│   ├── useMapDataSources.ts                         # Builds GeoJSON/flow data from `GlobalState`
│   ├── useTimelineSync.ts                           # Subscribes to timeline events and updates map
│   └── useCountrySelection.ts                       # Handles click/hover interactions and updates provider
├── data/geo/
│   ├── countries.geojson                            # Preprocessed boundaries with ISO codes
│   └── centroids.json                               # Country centroid coordinates for flows/labels
├── styles/map.module.css                            # Layout for map panel + overlays
├── styles/map-tokens.css                            # Elevation, glow, accent variables for map-specific UI
└── docs/PHASE-3-README.md
```

## Implementation Checklist

### Map Infrastructure
- [ ] Set up MapLibre GL with Gotham dark style (`map-style-dark.json`) and OSM vector tiles
- [ ] Build `MapPanel` as a client component wrapped in Suspense (loading skeleton while resources initialize)
- [ ] Implement `MapViewport` using `react-map-gl` with device pixel ratio awareness and WebGL context cleanup
- [ ] Add responsive layout rules—map should resize with window, maintain min height 600px
- [ ] Provide keyboard-accessible controls (layer toggles, search) with ARIA labels

### Data Preparation
- [ ] `useMapDataSources` transforms `GlobalState` into overlay-ready structures:
  - Countries: merge simulation metrics with GeoJSON features via ISO code
  - Trade flows/interbank exposures: convert matrix entries into arc segments with weights and direction
  - Sanctions/alliances: adjacency lists for network overlays
  - Events: geolocate from `GlobalState.events` payloads (requires backend lat/lon or country mapping)
- [ ] Memoize derived data keyed by `scenarioId + timestep`
- [ ] Provide filtering utilities (e.g., min threshold slider for flows)

### Timeline Synchronization
- [ ] `useTimelineSync` subscribes to `SimulationProvider` timestep changes and updates map layers
- [ ] Animate transitions between timesteps (ease-in-out) for choropleth intensity and arc opacity
- [ ] Provide playback mode indicator when timeline is auto-advancing; pause/resume controls integrated with timeline
- [ ] Prefetch upcoming layer data using TanStack Query when user scrubs timeline

### Interaction & Selection
- [ ] Enable hover tooltips showing key metrics (GDP, inflation, alliances count) using MapLibre popups or custom overlays
- [ ] Clicking a country sets `SimulationProvider.activeCountry` and triggers evidence rail filter + time-series selection
- [ ] Support multi-select via modifier key (e.g., shift+click) to compare multiple countries (store array in provider)
- [ ] Implement search combobox (Radix UI + `cmd+k` style) to jump to a country and set selection
- [ ] Provide layer-specific legends explaining color/width encodings; legends update when timeline changes

### Performance & UX
- [ ] Use WebGL instancing (Deck.gl) or data-driven styling (MapLibre) for large flow sets (thousands of edges)
- [ ] Debounce hover events; throttle map updates during continuous scrubbing
- [ ] Offload expensive calculations (e.g., great-circle arcs) to Web Worker via `comlink` if necessary
- [ ] Persist layer visibility and map camera (lat/lon/zoom) per user in localStorage
- [ ] Provide fallback message if WebGL unsupported with guidance on enabling hardware acceleration

### Testing
- [ ] Unit test `useMapDataSources` to ensure correct transformation from matrices to flow objects
- [ ] Snapshot tests for legend/controls states (light/dark, toggled layers)
- [ ] Playwright scenario: select scenario, toggle layers, scrub timeline, ensure map updates and evidence rail filters
- [ ] Visual regression via Storybook/Chromatic for base map + overlays

## Validation Tests

### Functional
- [ ] Timeline scrub updates choropleth colors and flow intensities accordingly
- [ ] Layer toggles show/hide overlays without reloading map
- [ ] Selecting a country updates evidence rail filters and timeline header summary
- [ ] Multi-select retains highlight styling and updates time-series comparison (Phase 5 dependency)

### Accessibility
- [ ] All controls reachable via keyboard; focus ring visible against dark theme
- [ ] Tooltip content accessible via programmatic focus (fallback list in DOM for screen readers)
- [ ] Map operations have ARIA live region to announce timeline sync status

### Performance
- [ ] Maintain >45 FPS when displaying 200+ trade arcs and 150 sanctions edges simultaneously
- [ ] Initial map load under 3s including GeoJSON fetch (cache results locally)
- [ ] Memory footprint remains stable when scrubbing through 100 timesteps (cache management validated)

## API Integration Notes

- Map relies on timeline data already fetched in Phase 2; no additional endpoints unless geospatial metadata provided
- For large matrices, consider backend-provided aggregated layers to reduce client transformation cost
- Use TanStack Query’s `prefetchQuery` to warm caches for adjacent timesteps when map data derived from remote requests

## Handoff Memo → Phase 4

**What’s Complete:**
- Geospatial visualization synchronized with timeline and evidence rail
- Country selection + multi-select stored in provider for cross-component communication
- Layer management infrastructure for relationships (trade, sanctions, alliances, interbank)

**Up Next (Phase 4):**
- Build network view (link analysis) reusing selection state and timeline synchronization
- Share data transformation utilities between map and network layers (e.g., adjacency lists, weights)
- Extend provider to broadcast selections/events to network panel for consistent highlighting

**Integration Notes:**
- Ensure `useMapDataSources` exports shareable selectors for network view (avoid duplication)
- Maintain consistent color palettes for entity categories across map and upcoming network view
- Validate that provider events fire once per timestep to avoid redundant renders in other panels
