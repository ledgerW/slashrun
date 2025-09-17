# Phase 4 — Network View (Link Analysis)

## Purpose

Implement the **Network View** - a force-directed graph visualization of country relationships that provides link analysis capabilities inspired by Palantir Gotham. This phase creates an alternative perspective to the map view, focusing on relationship strength and network topology rather than geographical proximity. The network view reveals hidden patterns in global relationships, influence networks, and systemic risks.

This visualization transforms relationship matrices into interactive network graphs, allowing analysts to explore centrality, clustering, and network effects that may not be obvious in geographical representations.

## Inputs

**From Phase 3:**
- Map view integration and shared country selection state
- Timeline controller with smooth animations
- State management with relationship matrices (trade, sanctions, alliances)
- Evidence rail integration for contextual analysis

**Backend Dependencies:**
- Relationship data: `trade_matrix`, `sanctions`, `alliances`, `interbank`
- Country metadata for node attributes (GDP, population, region)
- Historical relationship data for temporal network evolution

**External Dependencies:**
- D3.js for force simulation and network rendering
- Optional: WebGL acceleration libraries for large networks
- Graph analysis algorithms for centrality and clustering calculations

## Deliverables

```
frontend/
├── css/
│   └── components/
│       ├── network.css           # Base network styling
│       ├── network-controls.css  # Network controls and filters
│       ├── network-nodes.css     # Node styling and states
│       ├── network-edges.css     # Edge styling and animations
│       └── network-panels.css    # Info panels and legends
├── js/
│   ├── components/
│   │   ├── network-view.js      # Main network component
│   │   ├── network-controls.js  # Network controls and filters
│   │   ├── node-popup.js        # Node detail popup
│   │   ├── network-legend.js    # Legend for nodes and edges
│   │   └── network-search.js    # Node search and highlighting
│   ├── features/
│   │   └── network/
│   │       ├── network-controller.js    # Network state management
│   │       ├── layouts/
│   │       │   ├── force-layout.js      # D3 force simulation
│   │       │   ├── circle-layout.js     # Circular layout option
│   │       │   ├── hierarchical.js      # Hierarchical layouts
│   │       │   └── geographic.js        # Geography-informed layout
│   │       ├── analysis/
│   │       │   ├── centrality.js        # Centrality calculations
│   │       │   ├── clustering.js        # Community detection
│   │       │   ├── paths.js             # Shortest path analysis
│   │       │   └── metrics.js           # Network metrics
│   │       └── utils/
│   │           ├── graph-utils.js       # Graph data processing
│   │           ├── physics.js           # Force simulation tuning
│   │           └── edge-bundling.js     # Edge bundling algorithms
└── docs/
    └── PHASE-4-README.md         # This file
```

## Implementation Checklist

### Network Infrastructure
- [ ] **D3.js integration**: Set up force simulation with custom parameters
- [ ] **Graph data structure**: Convert relationship matrices to nodes/edges format
- [ ] **Performance optimization**: Efficient rendering for 50+ nodes and 200+ edges
- [ ] **Responsive canvas**: Network adapts to container size changes
- [ ] **Zoom and pan**: Smooth navigation with mouse wheel and drag
- [ ] **Node positioning**: Stable layouts that don't jitter during updates
- [ ] **Memory management**: Efficient cleanup of simulation objects

### Node System
- [ ] **Country nodes**: Visual representation of countries with size/color encoding
- [ ] **Node attributes**: Encode GDP, population, or other metrics in visual properties
- [ ] **Node states**: Visual feedback for selection, hover, and highlighting
- [ ] **Node labels**: Country names with collision detection and zoom-based visibility
- [ ] **Node clustering**: Group nodes by region, alliance, or other criteria
- [ ] **Node filtering**: Show/hide nodes based on various criteria
- [ ] **Performance**: Efficient node rendering and updates

### Edge System  
- [ ] **Relationship edges**: Visual connections for trade, sanctions, alliances
- [ ] **Edge attributes**: Encode relationship strength in thickness, color, opacity
- [ ] **Edge types**: Different visual styles for different relationship types
- [ ] **Directional arrows**: Show directional relationships where appropriate
- [ ] **Edge bundling**: Reduce visual clutter with curved or bundled edges
- [ ] **Edge filtering**: Show/hide edges based on type or strength thresholds
- [ ] **Animation**: Smooth edge transitions during timeline changes

### Layout Algorithms
- [ ] **Force-directed layout**: Physics simulation for natural clustering
- [ ] **Circular layout**: Arrange nodes in circles (e.g., by region)
- [ ] **Hierarchical layout**: Tree-like arrangements for power structures
- [ ] **Geographic layout**: Network layout informed by real geography
- [ ] **Custom constraints**: Pin important nodes or create custom groupings
- [ ] **Layout persistence**: Save and restore layout preferences
- [ ] **Smooth transitions**: Animate between different layout types

### Network Analysis Features
- [ ] **Centrality measures**: Calculate and visualize node importance
- [ ] **Community detection**: Identify and highlight network clusters
- [ ] **Shortest paths**: Find and highlight paths between selected nodes
- [ ] **Ego networks**: Show immediate neighbors of selected nodes
- [ ] **Network metrics**: Display graph density, clustering coefficient, etc.
- [ ] **Influence analysis**: Identify most influential nodes and connections
- [ ] **Structural holes**: Identify bridge nodes and strategic positions

### Timeline Integration
- [ ] **Temporal networks**: Show network evolution over time
- [ ] **Edge appearance/disappearance**: Animate relationship changes
- [ ] **Node attribute evolution**: Animate changes in node properties
- [ ] **Timeline synchronization**: Coordinate with map view and evidence rail
- [ ] **Network stability**: Maintain layout stability during time navigation
- [ ] **Performance optimization**: Efficient updates during timeline scrubbing

### Interactive Features
- [ ] **Node selection**: Click nodes to select and highlight ego network
- [ ] **Multi-selection**: Ctrl+click for multiple node selection
- [ ] **Drag nodes**: Manually position nodes and pin them in place
- [ ] **Context menus**: Right-click menus for nodes and edges
- [ ] **Search functionality**: Find and highlight specific countries
- [ ] **Evidence integration**: Selected nodes filter evidence rail
- [ ] **Export capabilities**: Save network layouts and analysis results

## API Integration Details

### Network Data Processing
```javascript
// Convert relationship matrices to network format
function buildNetworkGraph(state) {
  const nodes = Object.keys(state.countries).map(countryCode => ({
    id: countryCode,
    label: state.countries[countryCode].name,
    size: Math.log(state.countries[countryCode].macro.gdp),
    region: state.countries[countryCode].region,
    // ... other node attributes
  }));

  const edges = [];
  
  // Trade relationships
  Object.entries(state.trade_matrix).forEach(([key, volume]) => {
    const [source, target] = key.split('->');
    if (volume > TRADE_THRESHOLD) {
      edges.push({
        source, target, 
        type: 'trade',
        weight: Math.log(volume),
        value: volume
      });
    }
  });

  // Alliance relationships
  Object.entries(state.alliances).forEach(([key, strength]) => {
    const [source, target] = key.split('->');
    edges.push({
      source, target,
      type: 'alliance',
      weight: strength,
      value: strength
    });
  });

  return { nodes, edges };
}
```

### Timeline Integration
```javascript
// Update network for new timestep
timelineController.onTimestepChange(async (timestep) => {
  const state = await stateManager.getState(timestep);
  const networkData = buildNetworkGraph(state);
  
  networkController.updateNetwork(networkData, {
    animate: true,
    maintainPositions: true
  });
});
```

## Component Specifications

### Network Controller
```javascript
class NetworkController {
  constructor(container, timelineController, stateManager)
  
  // Core network functionality
  initializeNetwork(data, options)
  updateNetwork(data, options)
  setLayout(layoutType, options)
  
  // Node management
  selectNodes(nodeIds)
  highlightNodes(nodeIds)
  pinNodes(nodeIds, positions)
  filterNodes(criteria)
  
  // Analysis
  calculateCentrality(type)
  detectCommunities(algorithm)
  findShortestPath(sourceId, targetId)
  getEgoNetwork(nodeId, depth)
  
  // Layout and positioning
  fitToView(padding)
  zoomToNodes(nodeIds)
  saveLayout()
  restoreLayout()
  
  // Events
  onNodeClick(callback)
  onNodeHover(callback)
  onSelectionChange(callback)
}
```

### Force Layout Engine
```javascript
class ForceLayoutEngine {
  constructor(nodes, edges, options)
  
  // Simulation control
  start()
  stop()
  restart()
  alpha(value)
  
  // Force configuration
  addCenterForce(strength)
  addRepelForce(strength, radius)
  addLinkForce(strength, distance)
  addCollisionForce(radius)
  
  // Custom forces
  addRegionClustering()
  addGeographicConstraints()
  addHierarchicalForces()
  
  // Performance
  optimizeForSize(nodeCount)
  throttleUpdates(enabled)
}
```

### Network Analysis
```javascript
class NetworkAnalysis {
  constructor(networkData)
  
  // Centrality measures
  calculateDegreeCentrality()
  calculateBetweennessCentrality()
  calculateClosenessCentrality()
  calculateEigenvectorCentrality()
  
  // Community detection
  detectCommunities(algorithm = 'louvain')
  modularityScore()
  
  // Path analysis
  shortestPath(source, target)
  allShortestPaths(source)
  
  // Network metrics
  density()
  clustering()
  smallWorldness()
  assortativity()
}
```

## Validation Tests

### Network Rendering
- [ ] **Graph display**: Network renders correctly with all nodes and edges visible
- [ ] **Layout stability**: Force simulation converges to stable positions
- [ ] **Visual encoding**: Node sizes and edge weights correctly represent data
- [ ] **Performance**: Smooth interaction with 100+ nodes and 500+ edges
- [ ] **Zoom/pan**: Navigation works smoothly at all zoom levels
- [ ] **Labels**: Country labels appear at appropriate zoom levels

### Interactive Features
- [ ] **Node selection**: Click selection works, highlights ego network
- [ ] **Multi-selection**: Ctrl+click allows multiple node selection
- [ ] **Drag interaction**: Nodes can be dragged and pinned in position
- [ ] **Search functionality**: Search finds and highlights countries correctly
- [ ] **Context menus**: Right-click menus appear and function properly
- [ ] **Evidence integration**: Node selection filters evidence rail appropriately

### Timeline Integration
- [ ] **Network updates**: Network updates correctly when timeline changes
- [ ] **Edge animations**: Relationship changes animate smoothly
- [ ] **Layout stability**: Node positions remain stable during time navigation
- [ ] **Synchronization**: Network view syncs with map view selections
- [ ] **Performance**: Timeline scrubbing doesn't cause network lag

### Analysis Features
- [ ] **Centrality calculation**: Centrality measures calculate correctly
- [ ] **Community detection**: Community algorithms identify reasonable clusters
- [ ] **Path finding**: Shortest path calculations are accurate
- [ ] **Ego networks**: Ego network highlighting works correctly
- [ ] **Metrics accuracy**: Network metrics match expected values

## Architecture Decisions

### Layout Algorithm Choice
**Decision**: D3.js force simulation with custom forces  
**Rationale**: Flexible, well-tested, good performance for medium networks  
**Implementation**: Custom force functions for domain-specific clustering

### Data Structure
**Decision**: Adjacency list representation with separate edge objects  
**Rationale**: Efficient for sparse networks, easy to query relationships  
**Implementation**: Map-based lookups with array storage for performance

### Rendering Strategy
**Decision**: SVG for small networks, Canvas for large networks  
**Rationale**: SVG provides good interactivity, Canvas better performance  
**Implementation**: Automatic switching based on network size

### Analysis Integration
**Decision**: Real-time analysis with caching of expensive computations  
**Rationale**: Good user experience without blocking interactions  
**Implementation**: Web Workers for heavy analysis, incremental updates

## Performance Considerations

### Rendering Optimization
- **Level-of-detail**: Simplify rendering based on zoom level
- **Culling**: Only render nodes/edges visible in viewport
- **Batching**: Group drawing operations to minimize DOM updates
- **Canvas fallback**: Switch to Canvas rendering for large networks

### Computation Optimization
- **Incremental updates**: Only recalculate changed parts of analysis
- **Web Workers**: Offload heavy computations to background threads
- **Caching**: Cache expensive analysis results with invalidation
- **Approximation**: Use approximate algorithms for real-time feedback

### Memory Management
- **Object pooling**: Reuse node/edge objects to reduce garbage collection
- **Lazy loading**: Only load detailed data when nodes are selected
- **Cleanup**: Properly dispose of D3 simulations and event listeners

## Handoff Memo → Phase 5

**What's Complete:**
- Interactive force-directed network visualization with D3.js
- Multiple layout algorithms (force-directed, circular, hierarchical)
- Network analysis features (centrality, communities, shortest paths)
- Timeline integration with smooth network evolution animations
- Node and edge filtering with multiple relationship type support
- Evidence rail integration with network-based selection

**What's Next:**
Phase 5 will implement the **Time-Series Panel** - multi-series economic indicator charts with brush-to-zoom and comparison capabilities. This includes:
- D3.js line/area charts for economic indicators
- Multi-country comparison with overlay capabilities
- Brush-to-zoom for detailed time range analysis
- Event markers synchronized with timeline and trigger system
- Statistical analysis tools (correlation, trend analysis)

**Key Integration Points for Phase 5:**
- Shared timeline state for synchronized time range selection
- Country selection from map/network views drives time-series display
- Evidence rail will show time-series related field changes
- Export capabilities for chart data and analysis results

**Shared Data Requirements:**
- Country economic indicators over time (GDP, inflation, rates, etc.)
- Event data for timeline markers (triggers, policy changes)
- Statistical analysis results (correlations, trends, forecasts)
- Chart configuration and view state persistence

**Architecture Notes:**
- Time-series view complements rather than replaces network/map views
- Consider synchronized brushing across multiple chart types
- Plan for real-time updates during simulation stepping
- Chart performance optimization for long time series

**Data Processing Needs for Phase 5:**
- Time-series data extraction from state history
- Statistical analysis algorithms (correlation, regression, etc.)
- Chart data aggregation and resampling for performance
- Event detection and annotation systems
