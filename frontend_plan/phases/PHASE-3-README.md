# Phase 3 — Map View (Geospatial Layers)

## Purpose

Implement the **Map View** - an interactive world map with time-bound overlays that visualize global relationships and events. This phase brings geospatial intelligence to SlashRun, mirroring Palantir Gotham's emphasis on map-centric investigation and analysis. The map becomes a primary interface for exploring country interactions, trade flows, sanctions, alliances, and economic relationships across time.

This visualization transforms abstract economic data into intuitive spatial relationships, allowing analysts to see how geographical proximity influences economic outcomes and policy decisions.

## Inputs

**From Phase 2:**
- Timeline controller with smooth timestep navigation
- State management with caching and performance optimization
- Evidence rail integration for contextual data display
- Audit trail system for tracking changes

**Backend Dependencies:**
- State data: `countries.*`, `trade_matrix`, `sanctions`, `alliances`, `interbank`
- Geospatial data: Country boundaries, centroids, coordinate mapping
- Time-series data: Historical values for overlay animations

**External Dependencies:**
- MapLibre GL JS (recommended) or Leaflet for base mapping
- Natural Earth data for country boundaries (GeoJSON)
- Map tiles (OpenStreetMap, Mapbox, or custom styling)

## Deliverables

```
frontend/
├── css/
│   └── components/
│       ├── map.css               # Base map styling
│       ├── map-controls.css      # Layer controls and UI
│       ├── map-overlays.css      # Overlay styling (flows, choropleths)
│       └── map-popups.css        # Country info popups
├── js/
│   ├── components/
│   │   ├── map-view.js          # Main map component
│   │   ├── map-controls.js      # Layer toggles and settings
│   │   ├── country-popup.js     # Country detail popup
│   │   └── map-legends.js       # Legend components for overlays
│   ├── features/
│   │   └── map/
│   │       ├── map-controller.js     # Map state management
│   │       ├── layers/
│   │       │   ├── base-layer.js     # Base map configuration
│   │       │   ├── trade-flows.js    # Trade relationship arcs
│   │       │   ├── sanctions.js      # Sanctions overlay
│   │       │   ├── alliances.js      # Alliance networks
│   │       │   ├── choropleth.js     # Country data visualization
│   │       │   └── interbank.js      # Financial exposure flows
│   │       └── utils/
│   │           ├── geo-utils.js      # Geospatial calculations
│   │           ├── projection.js     # Coordinate transformations
│   │           └── animation.js      # Time-based animations
├── assets/
│   └── geo/
│       ├── countries.geojson     # Country boundary data
│       ├── centroids.json        # Country center coordinates
│       └── map-style.json        # Custom map styling
└── docs/
    └── PHASE-3-README.md         # This file
```

## Implementation Checklist

### Base Map Setup
- [ ] **MapLibre GL JS integration**: Initialize map with custom dark theme
- [ ] **Country boundaries**: Load and render country GeoJSON data
- [ ] **Map styling**: Gotham-inspired dark theme with high contrast
- [ ] **Performance optimization**: Efficient rendering of world-scale data
- [ ] **Responsive design**: Map adapts to different screen sizes
- [ ] **Navigation controls**: Zoom, pan, reset view, full-screen toggle
- [ ] **Loading states**: Progressive map loading with skeleton UI

### Layer System Architecture
- [ ] **Layer manager**: Unified system for managing overlay visibility and data
- [ ] **Trade flows layer**: Animated arcs showing bilateral trade relationships
- [ ] **Sanctions layer**: Choropleth and network visualization of sanctions
- [ ] **Alliance layer**: Network connections showing diplomatic relationships
- [ ] **Interbank layer**: Financial exposure flows between countries
- [ ] **Economic indicators**: Choropleth overlays for GDP, inflation, etc.
- [ ] **Layer controls**: Toggle visibility, adjust opacity, layer ordering

### Time Integration
- [ ] **Timeline synchronization**: Map updates automatically with timeline changes
- [ ] **Animation system**: Smooth transitions between timesteps
- [ ] **Historical overlays**: Show evolution of relationships over time
- [ ] **Event markers**: Visual indicators for significant events on map
- [ ] **Playback controls**: Auto-play timeline with map animations
- [ ] **Performance optimization**: Efficient re-rendering during time navigation
- [ ] **State persistence**: Remember map position and layer settings

### Interactive Features
- [ ] **Country selection**: Click countries to select and highlight
- [ ] **Contextual popups**: Show country data and recent changes
- [ ] **Evidence rail integration**: Selected country filters audit trail
- [ ] **Multi-country comparison**: Select multiple countries for analysis
- [ ] **Search functionality**: Find and zoom to specific countries
- [ ] **Measurement tools**: Distance and area calculations
- [ ] **Export capabilities**: Save map views as images

### Data Visualization Layers

#### Trade Flows
- [ ] **Arc visualization**: Curved lines representing trade relationships
- [ ] **Flow direction**: Visual indicators showing import/export direction
- [ ] **Volume encoding**: Line thickness represents trade volume
- [ ] **Animation**: Flow particles moving along trade routes
- [ ] **Filtering**: Show specific commodities or trade partners
- [ ] **Temporal changes**: Highlight growing/declining trade relationships

#### Sanctions Overlay
- [ ] **Network visualization**: Countries and sanctioning relationships
- [ ] **Severity encoding**: Color intensity represents sanction severity
- [ ] **Type differentiation**: Different visual styles for different sanction types
- [ ] **Historical tracking**: Show when sanctions were imposed/lifted
- [ ] **Impact visualization**: Economic metrics affected by sanctions

#### Alliance Networks
- [ ] **Network connections**: Lines connecting allied countries
- [ ] **Alliance strength**: Line thickness represents alliance strength
- [ ] **Military vs economic**: Different visual styles for alliance types
- [ ] **Bloc visualization**: Group highlighting for major alliance blocs
- [ ] **Temporal evolution**: Show alliance formation and dissolution

## API Integration Details

### Geospatial Data Access
```javascript
// Access country data from GlobalState
const countryData = state.countries[countryCode];
const economicData = {
  gdp: countryData.macro.gdp,
  inflation: countryData.macro.cpi_rate,
  policy_rate: countryData.macro.policy_rate,
  // ... other indicators
};

// Trade matrix access
const tradeFlows = state.trade_matrix;
// Structure: { "USA->CHN": volume, "CHN->USA": volume, ... }

// Sanctions data
const sanctions = state.sanctions;
// Structure: { "source": "target": { severity, type, start_date } }
```

### Timeline Integration
```javascript
// Subscribe to timeline changes
timelineController.onTimestepChange((timestep) => {
  mapController.updateOverlays(timestep);
  mapController.animateToTimestep(timestep);
});

// Trigger timeline navigation from map events
mapController.onEventClick((event) => {
  timelineController.goToTimestep(event.timestep);
});
```

## Component Specifications

### Map Controller
```javascript
class MapController {
  constructor(container, timelineController, stateManager)
  
  // Core map functionality
  initializeMap(style, bounds)
  addLayer(layerConfig)
  removeLayer(layerId)
  updateOverlays(timestep)
  
  // Country interaction
  selectCountry(countryCode)
  highlightCountries(countryCodes)
  showCountryPopup(countryCode, data)
  
  // View management
  fitToBounds(bounds)
  setView(center, zoom)
  saveViewState()
  restoreViewState()
  
  // Animation
  animateToTimestep(timestep)
  playTimelineAnimation()
  pauseAnimation()
  
  // Events
  onCountryClick(callback)
  onLayerChange(callback)
}
```

### Trade Flows Layer
```javascript
class TradeFlowsLayer {
  constructor(map, stateManager)
  
  // Data processing
  processTradeMatrix(matrix)
  calculateFlowPaths(sourceCoords, targetCoords)
  
  // Visualization
  renderFlows(flows, options)
  animateFlowParticles()
  updateFlowsForTimestep(t)
  
  // Interaction
  filterByCountry(countryCode)
  filterByCommodity(commodity)
  setVolumeThreshold(minVolume)
  
  // Performance
  optimizeForZoomLevel(zoom)
  throttleAnimations()
}
```

### Country Choropleth Layer
```javascript
class ChoroplethLayer {
  constructor(map, stateManager)
  
  // Data mapping
  mapIndicatorToColors(indicator, colorScale)
  updateCountryColors(data, timestep)
  
  // Styling
  setColorScale(scale)
  updateOpacity(opacity)
  addLegend()
  
  // Interaction
  showDataTooltip(country, value)
  highlightCountry(countryCode)
}
```

## Validation Tests

### Map Functionality
- [ ] **Base map loading**: Map loads without errors, shows world view
- [ ] **Country boundaries**: All countries render correctly with proper boundaries
- [ ] **Navigation**: Pan, zoom, reset controls work smoothly
- [ ] **Performance**: Smooth interaction at all zoom levels
- [ ] **Responsive design**: Map adapts to container size changes
- [ ] **Touch support**: Mobile gestures work correctly

### Layer System
- [ ] **Layer toggles**: Each layer can be independently shown/hidden
- [ ] **Opacity controls**: Layer opacity adjusts smoothly from 0-100%
- [ ] **Layer ordering**: Layers stack correctly with proper z-index
- [ ] **Data accuracy**: Overlay data matches backend state data
- [ ] **Performance**: Multiple layers render without significant lag

### Time Integration
- [ ] **Timeline sync**: Map updates automatically when timeline changes
- [ ] **Animation smooth**: Transitions between timesteps are fluid
- [ ] **Event integration**: Map events trigger appropriate timeline navigation
- [ ] **State persistence**: Map remembers position during time navigation
- [ ] **Performance**: Timeline scrubbing doesn't cause map lag

### Interactive Features
- [ ] **Country selection**: Click selects country, updates evidence rail
- [ ] **Multi-selection**: Ctrl+click allows multiple country selection
- [ ] **Popup accuracy**: Country popups show correct, current data
- [ ] **Search functionality**: Country search finds and zooms correctly
- [ ] **Evidence integration**: Map selection filters audit trail appropriately

## Architecture Decisions

### Mapping Library Choice
**Decision**: MapLibre GL JS over Leaflet  
**Rationale**: Better performance for complex overlays, WebGL acceleration  
**Implementation**: Progressive enhancement, fallback to Leaflet if needed

### Layer Architecture  
**Decision**: Modular layer system with unified interface  
**Rationale**: Easy to add new layers, maintain performance isolation  
**Implementation**: Base layer class with consistent API

### Animation Strategy
**Decision**: CSS transitions for simple animations, custom tweening for complex  
**Rationale**: Leverage browser optimization where possible  
**Implementation**: Animation utility with fallback strategies

### Data Caching
**Decision**: Separate geospatial cache from timeline state cache  
**Rationale**: Different access patterns and memory requirements  
**Implementation**: Specialized geo cache with spatial indexing

## Performance Considerations

### Rendering Optimization
- **Level-of-detail**: Simplify geometries at lower zoom levels
- **Viewport culling**: Only render features visible in current view
- **Batch updates**: Group layer updates to minimize re-renders
- **WebGL acceleration**: Use GPU for heavy computational overlays

### Data Loading
- **Progressive loading**: Load country boundaries first, overlays second
- **Lazy loading**: Load overlay data only when layers are activated
- **Compression**: Use compressed GeoJSON or vector tiles
- **CDN delivery**: Serve static geo assets from fast CDN

### Memory Management
- **Feature pooling**: Reuse map feature objects to reduce GC pressure
- **Layer cleanup**: Remove unused layers and their data from memory
- **Viewport-based loading**: Only keep features near current view in memory

## Handoff Memo → Phase 4

**What's Complete:**
- Interactive world map with Gotham-inspired dark theme
- Multiple overlay layers (trade flows, sanctions, alliances)
- Timeline integration with smooth time-based animations
- Country selection with evidence rail integration
- Performance-optimized rendering for world-scale data
- Layer controls with visibility and opacity management

**What's Next:**
Phase 4 will implement the **Network View (Link Analysis)** - force-directed graph visualization of country relationships. This includes:
- D3.js integration for interactive network graphs
- Multiple relationship types (trade, diplomatic, financial)
- Dynamic layouts with physics simulation
- Node filtering and ego-network highlighting
- Integration with map view for dual-perspective analysis

**Key Integration Points for Phase 4:**
- Shared country selection state between map and network views
- Timeline synchronization for both map and network animations
- Coordinated highlighting when selecting countries in either view
- Performance optimization for smooth view switching

**Shared Data Structures:**
- Country relationship matrices (trade, sanctions, alliances)
- Timeline state management for both visualizations
- Evidence rail filtering for network-selected countries
- Layout preferences and view state persistence

**Architecture Notes:**
- Network view will complement rather than replace map view
- Consider view switching animations for smooth user experience
- Plan for synchronized zoom/pan between map and network when appropriate
- Network layout algorithms should be optimized for real-time updates

**Data Processing Needs for Phase 4:**
- Convert matrix data to network graph format (nodes/edges)
- Calculate network metrics (centrality, clustering, etc.)
- Optimize edge bundling for visual clarity
- Prepare force simulation parameters for stable layouts
