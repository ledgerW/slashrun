# Phase 5 — Time-Series Panel (Economic Analytics)

## Purpose

Implement the **Time-Series Panel** - multi-series economic indicator charts with advanced analytics capabilities inspired by Palantir Quiver's time-series analysis patterns. This phase provides quantitative analysis tools for exploring economic trends, correlations, and policy impacts across countries and time periods. The time-series view reveals temporal patterns, cyclical behaviors, and causal relationships that may not be apparent in spatial or network visualizations.

This visualization transforms temporal state data into interactive charts that support brush-to-zoom, multi-country comparison, statistical analysis, and event correlation.

## Inputs

**From Phase 4:**
- Network view integration and coordinated country selection
- Map view integration for geographical context
- Timeline controller with precise timestep navigation
- Evidence rail integration for change attribution

**Backend Dependencies:**
- Historical state data: `GET /api/simulation/scenarios/{id}/history`
- Economic indicators: `countries.*.macro.*`, `commodity_prices`, `global_metrics`
- Event data: Trigger firings, policy changes, external shocks
- Statistical analysis capabilities (correlations, trends)

**External Dependencies:**
- D3.js for chart rendering and interaction
- Statistical libraries for analysis (regression, correlation, etc.)
- Mathematical utilities for time-series processing

## Deliverables

```
frontend/
├── css/
│   └── components/
│       ├── time-series.css      # Base time-series styling
│       ├── charts.css           # Chart-specific styles
│       ├── series-controls.css  # Series selection and controls
│       ├── chart-legends.css    # Chart legends and annotations
│       └── analysis-panels.css  # Analysis results panels
├── js/
│   ├── components/
│   │   ├── time-series-view.js  # Main time-series component
│   │   ├── chart-container.js   # Individual chart container
│   │   ├── series-selector.js   # Series selection interface
│   │   ├── chart-controls.js    # Chart interaction controls
│   │   └── analysis-panel.js    # Statistical analysis display
│   ├── features/
│   │   └── time-series/
│   │       ├── time-series-controller.js  # Time-series state management
│   │       ├── charts/
│   │       │   ├── line-chart.js         # Line chart implementation
│   │       │   ├── area-chart.js         # Area chart implementation
│   │       │   ├── bar-chart.js          # Bar chart implementation
│   │       │   ├── scatter-plot.js       # Scatter plot for correlations
│   │       │   └── multi-series.js       # Multi-series overlay charts
│   │       ├── analysis/
│   │       │   ├── correlation.js        # Correlation analysis
│   │       │   ├── regression.js         # Trend line analysis
│   │       │   ├── forecasting.js        # Basic forecasting
│   │       │   ├── statistics.js         # Descriptive statistics
│   │       │   └── events.js             # Event impact analysis
│   │       └── utils/
│   │           ├── data-processing.js    # Time-series data processing
│   │           ├── scales.js             # D3 scale utilities
│   │           ├── annotations.js        # Event annotation system
│   │           └── export.js             # Chart export utilities
└── docs/
    └── PHASE-5-README.md         # This file
```

## Implementation Checklist

### Chart Infrastructure
- [ ] **D3.js chart foundation**: Scalable SVG-based chart system
- [ ] **Multiple chart types**: Line, area, bar, scatter plot implementations
- [ ] **Responsive design**: Charts adapt to container size and window resize
- [ ] **High-DPI support**: Crisp rendering on retina and high-DPI displays
- [ ] **Performance optimization**: Efficient rendering of long time series
- [ ] **Zoom and pan**: Smooth navigation with mouse wheel and drag
- [ ] **Brush selection**: Time range selection for detailed analysis

### Series Management
- [ ] **Series selector**: Interface to choose economic indicators and countries
- [ ] **Multi-series overlay**: Display multiple indicators on same chart
- [ ] **Series styling**: Configurable colors, line styles, and opacity
- [ ] **Legend system**: Clear identification of all displayed series
- [ ] **Series filtering**: Show/hide series dynamically
- [ ] **Data normalization**: Options for scaling different indicator ranges
- [ ] **Missing data handling**: Graceful handling of gaps in time series

### Time Navigation Integration
- [ ] **Timeline synchronization**: Charts update with global timeline navigation
- [ ] **Brush-to-timeline**: Chart brush selection updates global time range
- [ ] **Event markers**: Visual indicators for triggers and policy changes
- [ ] **Current timestep indicator**: Clear marking of current simulation position
- [ ] **Time range selection**: Tools for focusing on specific time periods
- [ ] **Playback integration**: Charts animate during timeline auto-play
- [ ] **Performance optimization**: Smooth updates during timeline scrubbing

### Statistical Analysis
- [ ] **Correlation analysis**: Calculate and display correlations between series
- [ ] **Trend analysis**: Linear and polynomial trend lines
- [ ] **Descriptive statistics**: Mean, median, standard deviation, etc.
- [ ] **Change point detection**: Identify significant changes in time series
- [ ] **Volatility analysis**: Calculate rolling volatility and variance
- [ ] **Forecasting**: Simple forecasting based on historical trends
- [ ] **Event impact analysis**: Measure impact of triggers and policy changes

### Interactive Features
- [ ] **Hover tooltips**: Detailed data on hover with multiple series support
- [ ] **Click selection**: Click points to navigate to specific timesteps
- [ ] **Crosshairs**: Vertical lines to compare values across series
- [ ] **Data table view**: Tabular display of chart data with sorting
- [ ] **Export functionality**: Save charts as images or data as CSV
- [ ] **Comparison mode**: Side-by-side comparison of different countries
- [ ] **Annotation tools**: Add custom notes and observations

### Chart Types Implementation

#### Line Charts
- [ ] **Multi-series lines**: Multiple countries or indicators on same chart
- [ ] **Styling options**: Line thickness, color, dash patterns
- [ ] **Point markers**: Optional data point highlighting
- [ ] **Smooth curves**: Bezier curve interpolation options
- [ ] **Confidence bands**: Uncertainty visualization for forecasts

#### Area Charts  
- [ ] **Stacked areas**: Show composition and totals
- [ ] **Overlapping areas**: Semi-transparent overlays for comparison
- [ ] **Baseline options**: Zero baseline or floating baselines
- [ ] **Fill patterns**: Different patterns for visual distinction

#### Scatter Plots
- [ ] **Correlation visualization**: X-Y plots for relationship analysis
- [ ] **Regression lines**: Trend lines with R-squared values
- [ ] **Point sizing**: Encode third dimension in point size
- [ ] **Animation**: Show evolution of relationships over time

## API Integration Details

### Time-Series Data Processing
```javascript
// Extract time-series data from simulation history
async function extractTimeSeries(scenarioId, countryCode, indicator) {
  const history = await apiClient.get(`/simulation/scenarios/${scenarioId}/history`);
  
  return history.map(step => ({
    timestep: step.timestep,
    date: new Date(step.created_at),
    value: getNestedValue(step.state, `countries.${countryCode}.macro.${indicator}`),
    events: step.audit.triggers_fired || []
  }));
}

// Multi-country comparison data
async function getComparisonData(scenarioId, countries, indicator) {
  const allSeries = await Promise.all(
    countries.map(country => extractTimeSeries(scenarioId, country, indicator))
  );
  
  return countries.map((country, index) => ({
    id: country,
    name: getCountryName(country),
    data: allSeries[index]
  }));
}
```

### Statistical Analysis Integration
```javascript
// Calculate correlation between two time series
function calculateCorrelation(series1, series2) {
  // Align time series by timestep
  const aligned = alignTimeSeries(series1, series2);
  
  const correlation = pearsonCorrelation(
    aligned.map(d => d.value1),
    aligned.map(d => d.value2)
  );
  
  return {
    correlation,
    pValue: calculatePValue(correlation, aligned.length),
    significance: correlation > 0.7 ? 'strong' : correlation > 0.3 ? 'moderate' : 'weak'
  };
}
```

## Component Specifications

### Time-Series Controller
```javascript
class TimeSeriesController {
  constructor(container, timelineController, stateManager)
  
  // Chart management
  addChart(type, config)
  removeChart(chartId)
  updateCharts(timestep)
  
  // Series management
  addSeries(chartId, seriesConfig)
  removeSeries(chartId, seriesId)
  updateSeries(chartId, seriesId, data)
  
  // Analysis
  calculateCorrelation(series1Id, series2Id)
  addTrendLine(chartId, seriesId, type)
  detectChangePoints(seriesId)
  
  // View management
  setTimeRange(start, end)
  zoomToRange(start, end)
  resetZoom()
  
  // Export
  exportChart(chartId, format)
  exportData(seriesIds, format)
}
```

### Chart Component Base Class
```javascript
class Chart {
  constructor(container, config)
  
  // Core rendering
  render(data, options)
  update(data, options)
  resize()
  destroy()
  
  // Interaction
  enableBrush()
  enableZoom()
  enableTooltips()
  
  // Styling
  setTheme(theme)
  setColors(colorScale)
  updateLegend()
  
  // Data
  setData(data)
  addSeries(seriesData)
  removeSeries(seriesId)
  
  // Events
  onBrush(callback)
  onHover(callback)
  onClick(callback)
}
```

### Statistical Analysis Engine
```javascript
class StatisticalAnalysis {
  constructor(timeSeries)
  
  // Correlation analysis
  correlationMatrix(series)
  pairwiseCorrelation(series1, series2)
  
  // Trend analysis
  linearTrend(series)
  polynomialTrend(series, degree)
  seasonalDecomposition(series)
  
  // Descriptive statistics
  summary(series)
  rollingStatistics(series, window)
  
  // Change detection
  changePoints(series, method)
  outlierDetection(series)
  
  // Forecasting
  simpleForcast(series, periods)
  exponentialSmoothing(series, alpha)
}
```

## Validation Tests

### Chart Rendering
- [ ] **Basic display**: All chart types render correctly with sample data
- [ ] **Multi-series**: Multiple series display on same chart without overlap issues
- [ ] **Responsive design**: Charts resize properly with container changes
- [ ] **Performance**: Smooth rendering with 1000+ data points per series
- [ ] **Visual accuracy**: Chart data matches input data values
- [ ] **Legend accuracy**: Legends correctly identify all series

### Interactive Features
- [ ] **Brush selection**: Brush selection works and updates time range
- [ ] **Zoom/pan**: Mouse wheel zoom and drag pan work smoothly
- [ ] **Tooltips**: Hover tooltips show correct data for multiple series
- [ ] **Click navigation**: Clicking points navigates to correct timestep
- [ ] **Series toggling**: Series can be shown/hidden via legend clicks
- [ ] **Export functionality**: Charts export correctly as images and data

### Timeline Integration
- [ ] **Synchronization**: Charts update correctly with timeline navigation
- [ ] **Brush-to-timeline**: Chart brush selection updates global timeline
- [ ] **Event markers**: Event markers appear at correct timesteps
- [ ] **Performance**: Timeline scrubbing doesn't cause chart lag
- [ ] **State persistence**: Chart zoom and selection persist during navigation

### Statistical Analysis
- [ ] **Correlation accuracy**: Correlation calculations match expected values
- [ ] **Trend lines**: Trend lines fit data appropriately
- [ ] **Statistics accuracy**: Descriptive statistics match manual calculations
- [ ] **Change detection**: Change point detection identifies obvious breaks
- [ ] **Performance**: Analysis completes in reasonable time (<1s for typical data)

## Architecture Decisions

### Chart Library Choice
**Decision**: D3.js for custom chart implementation  
**Rationale**: Maximum flexibility, consistency with network view, performance control  
**Implementation**: Modular chart components with shared utilities

### Data Processing Strategy
**Decision**: Client-side processing with caching  
**Rationale**: Reduce server load, enable real-time analysis  
**Implementation**: Efficient data structures with incremental updates

### Statistical Analysis Approach
**Decision**: Basic statistics client-side, advanced analysis server-side  
**Rationale**: Balance performance with capability  
**Implementation**: Progressive enhancement from simple to complex analysis

### Chart Synchronization
**Decision**: Event-driven synchronization across charts and views  
**Rationale**: Maintain consistency without tight coupling  
**Implementation**: Central event bus with chart subscriptions

## Performance Considerations

### Rendering Optimization
- **Data aggregation**: Sample or aggregate large datasets for display
- **Virtual rendering**: Only render visible portions of long time series
- **Canvas fallback**: Use Canvas for very large datasets
- **Debounced updates**: Throttle updates during rapid timeline changes

### Data Processing
- **Incremental calculations**: Update analysis incrementally as data changes
- **Caching**: Cache expensive calculations with smart invalidation
- **Web Workers**: Offload heavy statistical calculations
- **Data streaming**: Stream data for real-time updates

### Memory Management
- **Data cleanup**: Remove old data outside current view window
- **Chart pooling**: Reuse chart instances to reduce memory allocation
- **Event listener cleanup**: Properly remove event listeners on destroy

## Handoff Memo → Phase 6

**What's Complete:**
- Multi-series time-series charts with D3.js rendering
- Brush-to-zoom functionality with timeline integration
- Statistical analysis tools (correlation, trends, descriptive statistics)
- Event markers and annotation system
- Multi-country comparison capabilities
- Export functionality for charts and data
- Performance optimization for large datasets

**What's Next:**
Phase 6 will implement the **Scenario Builder** - ontology-aware forms for creating and editing scenarios. This includes:
- Country data input forms with validation
- Relationship matrix editors (trade, sanctions, alliances)
- Rules and regime configuration interfaces
- Template system integration (MVS/FIS)
- Scenario validation and preview capabilities

**Key Integration Points for Phase 6:**
- Time-series analysis will inform scenario parameter selection
- Historical data visualization will guide scenario design
- Export capabilities will support scenario documentation
- Chart analysis will validate scenario realism

**Shared Data Requirements:**
- Country metadata and economic indicator definitions
- Historical ranges and validation rules for economic parameters
- Template data structures for MVS/FIS scenario generation
- Validation algorithms for scenario consistency

**Architecture Notes:**
- Scenario builder will be a separate major interface component
- Consider wizard-style workflow for complex scenario creation
- Plan for scenario versioning and comparison capabilities
- Integration with existing authentication and state management

**Data Validation Needs for Phase 6:**
- Economic parameter bounds and relationships
- Matrix consistency validation (trade flows, etc.)
- Rule parameter validation and conflict detection
- Historical data validation against known ranges
