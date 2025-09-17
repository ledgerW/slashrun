# Phase 2 — Timeline & Evidence Rail (Auditability Core)

## Purpose

Implement the **Timeline & Evidence Rail** - the core investigative interface that makes time and audit trails first-class citizens in SlashRun. This phase creates the foundation for all investigative workflows by providing timeline navigation, comprehensive audit visualization, and state transparency. This mirrors Palantir's emphasis on time-series analysis and evidence-based investigation patterns.

The timeline becomes the central navigation mechanism, while the evidence rail provides complete transparency into simulation mechanics - what changed, why it changed, and how calculations were performed.

## Inputs

**From Phase 1:**
- Authenticated user sessions and JWT token management
- Protected routing and state management foundation
- API client with automatic auth header handling
- App shell with right rail and timeline footer areas prepared

**Backend Dependencies:**
- `/api/simulation/scenarios/{id}/states/{t}` - Get state at specific timestep
- `/api/simulation/scenarios/{id}/step` - Execute simulation step with audit
- `/api/simulation/scenarios/{id}/history` - Get simulation history range
- Audit data structure: `StepAudit` with field changes, reducer sequence, triggers

## Deliverables

```
frontend/
├── css/
│   └── components/
│       ├── timeline.css          # Timeline scrubber and pins
│       ├── audit.css            # Audit trail styling
│       ├── diff-viewer.css      # JSON diff visualization
│       └── evidence-rail.css    # Right rail container
├── js/
│   ├── components/
│   │   ├── timeline.js          # Timeline scrubber component
│   │   ├── audit-trail.js       # Field changes viewer
│   │   ├── reducer-chain.js     # Reducer sequence visualization
│   │   ├── trigger-log.js       # Trigger status display
│   │   └── state-diff.js        # JSON state comparison
│   ├── features/
│   │   ├── timeline/            # Timeline feature module
│   │   │   ├── timeline-controller.js
│   │   │   └── timeline-events.js
│   │   └── evidence/            # Evidence rail feature module
│   │       ├── evidence-controller.js
│   │       └── evidence-events.js
│   └── utils/
│       ├── diff-utils.js        # JSON diffing utilities
│       ├── format-utils.js      # Data formatting helpers
│       └── debounce.js          # Performance utilities
└── docs/
    └── PHASE-2-README.md        # This file
```

## Implementation Checklist

### Timeline Component
- [ ] **Timeline scrubber**: Range input with smooth 60fps updates
- [ ] **Event pins**: Visual markers for trigger firings and significant events
- [ ] **Timestep display**: Current step indicator with total steps
- [ ] **Navigation controls**: Step forward/back, jump to start/end
- [ ] **Keyboard shortcuts**: Arrow keys for navigation, spacebar for play/pause
- [ ] **Progress indicators**: Visual representation of simulation progress
- [ ] **Time caching**: Cache recent states for smooth scrubbing

### Evidence Rail Structure
- [ ] **Accordion layout**: Collapsible sections for different evidence types
- [ ] **Audit Trail section**: Field-level changes with old→new values
- [ ] **Reducer Chain section**: Ordered sequence of calculations performed
- [ ] **Trigger Log section**: Fired, pending, and expired triggers
- [ ] **State Inspector**: Raw JSON viewer with search and filtering
- [ ] **Diff Viewer**: Side-by-side comparison of timesteps
- [ ] **Performance optimization**: Virtual scrolling for large data sets

### Audit Trail Visualization
- [ ] **Field changes list**: Hierarchical display of state modifications
- [ ] **Change attribution**: Link each change to specific reducer/trigger
- [ ] **Value formatting**: Human-readable display of numeric changes
- [ ] **Change magnitude**: Visual indicators for significance of changes
- [ ] **Expandable details**: Show calculation parameters and context
- [ ] **Search/filter**: Find specific field paths or change types
- [ ] **Export functionality**: Copy audit data as JSON or CSV

### State Management Integration
- [ ] **Timeline state**: Current timestep, max timestep, history cache
- [ ] **Audit caching**: Store recent audit data for performance
- [ ] **State comparison**: Efficient diffing between timesteps
- [ ] **Loading states**: Show progress during data fetching
- [ ] **Error recovery**: Handle missing or corrupted audit data
- [ ] **Optimistic updates**: Immediate UI feedback for user actions

### Performance Optimizations
- [ ] **Debounced scrubbing**: Prevent excessive API calls during dragging
- [ ] **Virtual scrolling**: Handle large audit trails efficiently
- [ ] **State caching**: Cache frequently accessed timesteps
- [ ] **Progressive loading**: Load audit details on demand
- [ ] **Background prefetching**: Preload adjacent timesteps
- [ ] **Memory management**: Clean up old cache entries

## API Integration Details

### Timeline Navigation
```javascript
// Get state at specific timestep
GET /api/simulation/scenarios/{id}/states/{t}
Response: {
  "id": "state_uuid",
  "scenario_id": "scenario_uuid", 
  "timestep": 5,
  "state": { /* GlobalState object */ },
  "audit": { /* StepAudit object */ },
  "created_at": "2024-01-01T00:00:00Z"
}

// Get history range for timeline
GET /api/simulation/scenarios/{id}/history?start_timestep=0&end_timestep=10
Response: [ /* Array of SimulationStepResponse objects */ ]
```

### Simulation Stepping
```javascript
// Execute next simulation step
POST /api/simulation/scenarios/{id}/step
Response: {
  "timestep": 6,
  "state": { /* New GlobalState */ },
  "audit": {
    "scenario_id": "scenario_uuid",
    "timestep": 6,
    "step_start_time": "2024-01-01T00:00:00Z",
    "step_end_time": "2024-01-01T00:00:01Z", 
    "reducer_sequence": ["taylor_rule", "phillips_curve", "trade_balance"],
    "field_changes": [
      {
        "field_path": "countries.USA.macro.policy_rate",
        "old_value": 5.25,
        "new_value": 5.50,
        "change_reason": "taylor_rule",
        "calculation_details": { /* Rule parameters */ }
      }
    ],
    "triggers_fired": ["inflation_alert"],
    "errors": []
  }
}
```

## Component Specifications

### Timeline Controller
```javascript
class TimelineController {
  constructor(scenarioId, apiClient, stateManager)
  
  // Core navigation
  async goToTimestep(t)
  async stepForward()
  async stepBackward()
  async reset()
  
  // Timeline state
  getCurrentTimestep()
  getMaxTimestep()
  getProgress()
  
  // Caching
  preloadAdjacentStates(t)
  getCachedState(t)
  clearCache()
  
  // Events
  onTimestepChange(callback)
  onStateLoad(callback)
}
```

### Audit Trail Component
```javascript
class AuditTrail {
  constructor(container, formatUtils)
  
  // Rendering
  render(auditData)
  renderFieldChanges(changes)
  renderReducerChain(sequence) 
  renderTriggers(triggers)
  
  // Interaction
  expandDetails(fieldPath)
  searchChanges(query)
  filterBySource(source)
  
  // Export
  exportAsJSON()
  exportAsCSV()
}
```

### State Diff Viewer
```javascript
class StateDiffViewer {
  constructor(container, diffUtils)
  
  // Comparison
  async compare(stateA, stateB)
  highlightChanges(diff)
  navigateToPath(jsonPath)
  
  // Display
  renderSideBySide(diff)
  renderInline(diff) 
  toggleViewMode()
  
  // Performance
  virtualizeTree(largeObject)
  lazyLoadSubtrees()
}
```

## Validation Tests

### Timeline Functionality
- [ ] **Scrubbing**: Drag timeline → state updates smoothly without lag
- [ ] **Stepping**: Step buttons advance/retreat by exactly 1 timestep
- [ ] **Jump navigation**: Click timeline position → immediate state load
- [ ] **Keyboard shortcuts**: Arrow keys navigate, no conflicts with other controls
- [ ] **Visual feedback**: Current position clearly indicated, progress visible
- [ ] **Boundary handling**: Cannot go below 0 or above max timestep

### Evidence Rail Display  
- [ ] **Audit rendering**: Field changes display with clear old→new values
- [ ] **Reducer chain**: Shows ordered sequence with expandable calculation details
- [ ] **Trigger status**: Clearly distinguishes fired/pending/expired triggers
- [ ] **State inspector**: Raw JSON browsable with search functionality
- [ ] **Performance**: Large audit trails scroll smoothly with virtual scrolling
- [ ] **Accessibility**: Screen readers can navigate evidence rail sections

### Data Accuracy
- [ ] **State consistency**: UI state matches API response data
- [ ] **Change attribution**: Each field change correctly links to source reducer/trigger
- [ ] **Diff accuracy**: State comparison shows all and only actual differences
- [ ] **Cache consistency**: Cached states match fresh API responses
- [ ] **Error handling**: Missing or malformed audit data handled gracefully

### Performance Benchmarks
- [ ] **Timeline scrubbing**: 60fps during continuous dragging
- [ ] **Large datasets**: 1000+ field changes render in <500ms
- [ ] **Memory usage**: Cache doesn't exceed 100MB for typical sessions
- [ ] **API efficiency**: <50ms average response time for cached states
- [ ] **UI responsiveness**: <100ms response to user interactions

## Architecture Decisions

### Timeline State Management
**Decision**: Centralized timeline state with caching strategy  
**Rationale**: Single source of truth for temporal navigation  
**Implementation**: TimelineController manages state and cache

### Audit Data Structure
**Decision**: Hierarchical display matching API response structure  
**Rationale**: Preserve full audit fidelity from backend  
**Implementation**: Recursive component rendering with lazy loading

### Caching Strategy  
**Decision**: LRU cache with configurable size limits  
**Rationale**: Balance performance with memory constraints  
**Implementation**: Map-based cache with automatic cleanup

### Diff Algorithm
**Decision**: Deep object comparison with path tracking  
**Rationale**: Precise change detection for complex nested state  
**Implementation**: Custom diff utility with optimization for large objects

## User Experience Design

### Timeline Interaction Patterns
- **Scrubbing**: Continuous drag updates state in real-time
- **Discrete stepping**: Button clicks for precise navigation
- **Event focus**: Click event pins to jump to significant moments
- **Keyboard shortcuts**: Power user navigation without mouse

### Evidence Rail Organization
- **Progressive disclosure**: Start with summary, expand for details
- **Visual hierarchy**: Use typography and color to guide attention  
- **Contextual actions**: Right-click for export, copy, or analysis
- **Search integration**: Quick filtering across all evidence types

### Error States & Edge Cases
- **Loading states**: Clear progress indicators during data fetching
- **Empty states**: Helpful messages when no audit data exists
- **Error recovery**: Retry mechanisms for failed API calls
- **Offline handling**: Graceful degradation when backend unavailable

## Handoff Memo → Phase 3

**What's Complete:**
- Timeline scrubber with smooth 60fps navigation
- Comprehensive audit trail with field-level change tracking
- Reducer chain visualization showing calculation flow
- State diff viewer for comparing timesteps
- Performance-optimized caching and virtual scrolling
- Full keyboard accessibility and screen reader support

**What's Next:**
Phase 3 will implement the **Map View (Geospatial Layers)** - interactive world map with time-bound overlays. This includes:
- MapLibre GL JS integration for base mapping
- Trade flow visualization with animated arcs
- Sanctions and alliance overlays with temporal changes
- Country selection integration with evidence rail
- Layer toggles and opacity controls

**Key Integration Points for Phase 3:**
- Timeline state will drive map layer animations
- Country selection on map will filter evidence rail to relevant changes
- Map interactions will trigger timeline navigation (e.g., click event → jump to timestep)
- State management will include map view preferences and layer settings

**Shared Components for Phase 3:**
- Timeline controller will be extended to support map layer updates
- State caching will include geospatial data optimization
- Evidence rail will add map-specific change filtering
- Performance monitoring will include map rendering metrics

**Architecture Notes:**
- Map component will subscribe to timeline change events
- Geospatial data will be cached separately from state data
- Consider WebGL optimization for large trade flow datasets
- Plan for map tile caching and offline map support

**Data Requirements for Phase 3:**
- Country boundary data (GeoJSON)  
- Trade matrix visualization (source/target/flow volume)
- Sanctions data with time ranges
- Alliance networks with temporal validity
- Coordinate mapping for country centroids
