# Cross-Phase Architecture Documentation

## Overview

This document provides technical architecture guidance that spans all implementation phases, covering shared patterns, integration points, and system-wide design decisions. This serves as the technical foundation for implementing the Palantir Gotham-inspired SlashRun frontend across all phases.

## System Architecture Overview

### Three-Tier Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND TIER                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Static HTML   │  │   CSS Modules   │  │  JavaScript ES6 │  │
│  │   - Semantic    │  │   - Design      │  │   - State Mgmt  │  │
│  │   - A11y Ready  │  │     Tokens      │  │   - API Client  │  │
│  │   - Progressive │  │   - Components  │  │   - WebSockets  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND TIER                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   FastAPI App   │  │   JWT Auth      │  │   WebSocket     │  │
│  │   - API Routes  │  │   - Protected   │  │   - Real-time   │  │
│  │   - Validation  │  │     Endpoints   │  │   - Simulation  │  │
│  │   - CORS Config │  │   - User Mgmt   │  │   - State Sync  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                        DATABASE TIER                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   SQLModel      │  │   Audit Trail   │  │   State Store   │  │
│  │   - Domain      │  │   - All Changes │  │   - Snapshots   │  │
│  │     Models      │  │   - User        │  │   - Timeline    │  │
│  │   - Relations   │  │     Actions     │  │   - Diffs       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Shared Design Patterns

### 1. Component Architecture Pattern

**Standardized Component Structure:**
```javascript
// Every component follows this pattern
class ComponentName {
    constructor(container, options = {}) {
        this.container = container;
        this.options = { ...this.defaults, ...options };
        this.state = this.initializeState();
        this.ui = this.createUIElements();
        this.bindEvents();
        this.render();
    }
    
    defaults = { /* component defaults */ };
    initializeState() { /* return initial state */ }
    createUIElements() { /* return DOM structure */ }
    bindEvents() { /* attach event listeners */ }
    render() { /* update UI from state */ }
    destroy() { /* cleanup */ }
}
```

**Used in Phases:**
- Phase 0: Base component foundation
- Phase 1: Authentication components
- Phase 2-5: All visualization components
- Phase 6-7: Form and builder components
- Phase 8: Narrative components

### 2. State Management Pattern

**Centralized State Store:**
```javascript
// Global state management across all phases
class StateManager {
    constructor() {
        this.state = {
            auth: { user: null, token: null },
            timeline: { currentTime: null, events: [] },
            simulation: { scenarios: [], activeScenario: null },
            ui: { activeView: null, sidebarOpen: true }
        };
        this.subscribers = new Map();
        this.middleware = [];
    }
    
    // Observable pattern for state updates
    subscribe(path, callback) { /* */ }
    unsubscribe(path, callback) { /* */ }
    setState(path, value) { /* trigger updates */ }
    getState(path) { /* get state slice */ }
}
```

**State Persistence Strategy:**
- Authentication: localStorage (token) + sessionStorage (temp data)
- Timeline: IndexedDB for large datasets
- UI Preferences: localStorage
- Temporary State: memory only

### 3. API Integration Pattern

**Consistent API Client:**
```javascript
// Used across all phases for backend communication
class APIClient {
    constructor() {
        this.baseURL = '/api';
        this.defaultHeaders = { 'Content-Type': 'application/json' };
        this.interceptors = { request: [], response: [] };
    }
    
    // Automatic auth header injection
    async request(method, endpoint, data = null) {
        const token = auth.getToken();
        const headers = {
            ...this.defaultHeaders,
            ...(token && { 'Authorization': `Bearer ${token}` })
        };
        
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method,
            headers,
            body: data ? JSON.stringify(data) : null
        });
        
        // Global error handling
        if (response.status === 401) {
            auth.logout();
            router.navigate('/login');
            throw new AuthError('Authentication required');
        }
        
        return response;
    }
}
```

## Cross-Phase Integration Points

### 1. Authentication Flow (Phase 1 → All Phases)

**Integration Pattern:**
```javascript
// Every protected component checks auth status
class ProtectedComponent extends BaseComponent {
    constructor(container, options) {
        // Auth check before initialization
        if (!auth.isAuthenticated()) {
            router.navigate('/login');
            return;
        }
        super(container, options);
    }
}

// Route guards for navigation
router.beforeEach((to, from, next) => {
    if (to.meta.requiresAuth && !auth.isAuthenticated()) {
        next('/login');
    } else {
        next();
    }
});
```

### 2. Timeline State (Phase 2 → Phases 3-8)

**Temporal Context Sharing:**
```javascript
// All visualization components subscribe to timeline
class VisualizationComponent extends BaseComponent {
    constructor(container, options) {
        super(container, options);
        
        // Subscribe to timeline changes
        timeline.subscribe('currentTime', (time) => {
            this.updateForTime(time);
        });
        
        timeline.subscribe('timeRange', (range) => {
            this.updateForTimeRange(range);
        });
    }
    
    updateForTime(time) {
        // Filter/highlight data for specific time
        this.render(this.getDataForTime(time));
    }
}
```

### 3. Evidence Collection (Phases 3-5 → Phase 8)

**Evidence Capture Pattern:**
```javascript
// Standardized evidence capture across visualizations
class EvidenceCapture {
    static capture(componentType, data, metadata = {}) {
        const evidence = {
            id: generateId(),
            type: componentType,
            timestamp: timeline.getCurrentTime(),
            data: data,
            metadata: {
                viewState: component.getViewState(),
                userContext: auth.getUser(),
                ...metadata
            },
            screenshot: await this.captureScreenshot()
        };
        
        evidenceStore.add(evidence);
        return evidence;
    }
}
```

### 4. WebSocket Integration (Backend → All Real-time Components)

**Real-time Updates Pattern:**
```javascript
// WebSocket manager for real-time updates
class WebSocketManager {
    constructor() {
        this.connections = new Map();
        this.messageHandlers = new Map();
    }
    
    connect(endpoint, handlers = {}) {
        const ws = new WebSocket(`ws://localhost:8000/ws${endpoint}`);
        
        ws.onmessage = (event) => {
            const { type, data } = JSON.parse(event.data);
            const handler = this.messageHandlers.get(type);
            if (handler) handler(data);
        };
        
        this.connections.set(endpoint, ws);
        return ws;
    }
    
    // Used by simulation components for real-time updates
    onSimulationUpdate(callback) {
        this.messageHandlers.set('simulation_update', callback);
    }
}
```

## Technology Stack Integration

### Frontend Dependencies
```json
{
  "core": {
    "architecture": "Vanilla JS ES6+ with modules",
    "routing": "Custom hash-based router",
    "state": "Custom observable state manager",
    "build": "No build step - native ES modules"
  },
  "visualization": {
    "maps": "MapLibre GL JS v3.x",
    "charts": "D3.js v7.x",
    "networks": "D3.js force simulation",
    "ui": "Custom components"
  },
  "utilities": {
    "date": "Temporal API (polyfill)",
    "math": "Custom analytics functions",
    "validation": "Custom validation engine",
    "accessibility": "Custom a11y helpers"
  }
}
```

### Backend Integration Points
```python
# Consistent API patterns used across all phases
class BaseRouter:
    def __init__(self):
        self.router = APIRouter()
        self.dependencies = [Depends(get_current_user)]  # All routes protected
    
    def add_route(self, method, path, handler):
        """Add route with consistent error handling"""
        @wraps(handler)
        async def wrapper(*args, **kwargs):
            try:
                return await handler(*args, **kwargs)
            except Exception as e:
                logger.error(f"API Error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        self.router.add_api_route(path, wrapper, methods=[method])
```

## Performance Architecture

### 1. Data Flow Optimization

**Lazy Loading Strategy:**
```javascript
// Components load data only when needed
class LazyComponent extends BaseComponent {
    async initialize() {
        // Show loading state immediately
        this.showLoadingState();
        
        // Load data in background
        this.data = await this.loadData();
        this.render();
    }
    
    async loadData() {
        // Cache-first strategy
        const cached = cache.get(this.cacheKey);
        if (cached && !this.isStale(cached)) {
            return cached.data;
        }
        
        const fresh = await api.get(this.dataEndpoint);
        cache.set(this.cacheKey, fresh, this.cacheTTL);
        return fresh;
    }
}
```

### 2. Rendering Performance

**Virtual Scrolling for Large Datasets:**
```javascript
// Used in timeline, data tables, and lists
class VirtualScroller {
    constructor(container, itemHeight, renderItem) {
        this.container = container;
        this.itemHeight = itemHeight;
        this.renderItem = renderItem;
        this.visibleRange = { start: 0, end: 0 };
        this.setupScrollListener();
    }
    
    updateVisibleRange() {
        const scrollTop = this.container.scrollTop;
        const containerHeight = this.container.clientHeight;
        
        this.visibleRange = {
            start: Math.floor(scrollTop / this.itemHeight),
            end: Math.ceil((scrollTop + containerHeight) / this.itemHeight)
        };
        
        this.renderVisibleItems();
    }
}
```

### 3. Memory Management

**Resource Cleanup Pattern:**
```javascript
// Consistent cleanup across all components
class ResourceManager {
    constructor() {
        this.resources = new Set();
        this.intervals = new Set();
        this.observers = new Set();
    }
    
    addResource(resource) {
        this.resources.add(resource);
    }
    
    cleanup() {
        // Clear all resources
        this.resources.forEach(r => r.destroy?.());
        this.intervals.forEach(id => clearInterval(id));
        this.observers.forEach(obs => obs.disconnect());
    }
}
```

## Error Handling Architecture

### 1. Global Error Boundary

**Centralized Error Handling:**
```javascript
// Error boundary for all components
class ErrorBoundary {
    static wrap(component) {
        return new Proxy(component, {
            construct(target, args) {
                try {
                    return new target(...args);
                } catch (error) {
                    ErrorBoundary.handleError(error, target.name);
                    return ErrorBoundary.createErrorComponent(error);
                }
            }
        });
    }
    
    static handleError(error, context) {
        // Log error
        logger.error(`Component error in ${context}:`, error);
        
        // Report to monitoring
        monitoring.reportError(error, { context });
        
        // Show user-friendly message
        notifications.show({
            type: 'error',
            message: 'Something went wrong. Please try refreshing the page.',
            actions: [{ text: 'Refresh', action: () => window.location.reload() }]
        });
    }
}
```

### 2. API Error Handling

**Consistent API Error Processing:**
```javascript
// Standard error handling for all API calls
class APIErrorHandler {
    static async handleResponse(response) {
        if (!response.ok) {
            const error = await this.parseError(response);
            
            switch (response.status) {
                case 401:
                    auth.logout();
                    router.navigate('/login');
                    throw new AuthError('Authentication expired');
                
                case 403:
                    throw new PermissionError('Access denied');
                
                case 429:
                    throw new RateLimitError('Too many requests');
                
                case 500:
                    throw new ServerError('Server error occurred');
                
                default:
                    throw new APIError(error.detail || 'Unknown error');
            }
        }
        
        return response;
    }
}
```

## Security Architecture

### 1. Content Security Policy

**CSP Configuration:**
```html
<!-- Applied across all phases -->
<meta http-equiv="Content-Security-Policy" content="
    default-src 'self';
    script-src 'self' 'unsafe-inline';
    style-src 'self' 'unsafe-inline';
    img-src 'self' data: blob:;
    connect-src 'self' ws: wss:;
    font-src 'self';
    media-src 'self';
">
```

### 2. Input Sanitization

**XSS Prevention:**
```javascript
// Used across all form inputs and dynamic content
class SecurityUtils {
    static sanitizeHTML(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }
    
    static validateInput(input, type) {
        const validators = {
            email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            numeric: /^\d+(\.\d+)?$/,
            alphanumeric: /^[a-zA-Z0-9]+$/
        };
        
        return validators[type]?.test(input) ?? false;
    }
}
```

## Testing Architecture

### 1. Component Testing Pattern

**Consistent Test Structure:**
```javascript
// Test pattern used across all phases
describe('ComponentName', () => {
    let component;
    let container;
    
    beforeEach(() => {
        container = document.createElement('div');
        document.body.appendChild(container);
        component = new ComponentName(container);
    });
    
    afterEach(() => {
        component.destroy();
        container.remove();
    });
    
    it('should initialize correctly', () => {
        expect(component.container).toBe(container);
        expect(component.state).toBeDefined();
    });
    
    it('should render without errors', () => {
        expect(() => component.render()).not.toThrow();
    });
    
    it('should handle user interactions', () => {
        const spy = jest.fn();
        component.on('action', spy);
        
        // Simulate user interaction
        component.container.click();
        
        expect(spy).toHaveBeenCalled();
    });
});
```

### 2. Integration Testing

**Cross-Component Testing:**
```javascript
// Tests component interactions across phases
describe('Integration Tests', () => {
    it('should sync timeline across visualizations', async () => {
        const map = new GeospatialMap(mapContainer);
        const chart = new TimeSeriesChart(chartContainer);
        
        // Change timeline
        timeline.setCurrentTime('2024-01-15');
        
        // Both components should update
        await waitFor(() => {
            expect(map.getCurrentTime()).toBe('2024-01-15');
            expect(chart.getCurrentTime()).toBe('2024-01-15');
        });
    });
});
```

## Documentation Standards

### 1. Code Documentation

**JSDoc Standards:**
```javascript
/**
 * Component for visualizing network relationships
 * @class NetworkVisualization
 * @extends BaseComponent
 * @param {HTMLElement} container - DOM container element
 * @param {Object} options - Configuration options
 * @param {Array} options.data - Network data nodes and edges
 * @param {string} options.layout - Layout algorithm ('force'|'hierarchical')
 * @example
 * const network = new NetworkVisualization(container, {
 *   data: { nodes: [...], edges: [...] },
 *   layout: 'force'
 * });
 */
```

### 2. README Structure

**Phase Documentation Template:**
```markdown
# Phase N: Component Name

## Purpose
Brief description of what this phase accomplishes

## Dependencies
- Previous phases required
- External dependencies
- Backend API requirements

## Implementation
Step-by-step implementation guide

## Testing
How to test the phase

## Integration
How this phase integrates with others
```

## Deployment Architecture

### 1. Static File Serving

**FastAPI Integration:**
```python
# Consistent across all phases
from fastapi.staticfiles import StaticFiles

# Mount frontend after API routes
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# Environment-specific configuration
if settings.environment == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

### 2. Docker Integration

**Multi-stage Build Strategy:**
```dockerfile
# Development stage
FROM python:3.11-slim as development
COPY frontend/ /app/frontend/
VOLUME ["/app/frontend"]  # Live reload

# Production stage  
FROM python:3.11-slim as production
COPY frontend/ /app/frontend/
# Optimize static files
RUN find /app/frontend -name "*.js" -exec gzip -k {} \;
```

## Phase Dependencies Matrix

| Phase | Depends On | Provides To | Critical Integrations |
|-------|------------|-------------|----------------------|
| 0 | None | All | Foundation, routing, API client |
| 1 | 0 | All | Authentication, protected routes |
| 2 | 0,1 | 3,4,5,8 | Timeline state, evidence capture |
| 3 | 0,1,2 | 8 | Geospatial evidence, timeline sync |
| 4 | 0,1,2 | 8 | Network evidence, timeline sync |
| 5 | 0,1,2 | 8 | Chart evidence, timeline sync |
| 6 | 0,1 | 7,8 | Scenario data, validation |
| 7 | 0,1,6 | 8 | Trigger definitions, testing |
| 8 | 0,1,2,3,4,5 | 9 | Evidence compilation, narrative |
| 9 | All | None | Performance, accessibility, deployment |

## Quality Assurance Standards

### 1. Performance Benchmarks

**Target Metrics:**
- Initial page load: < 2 seconds
- Component render: < 100ms
- Timeline scrubbing: 60 FPS
- Memory usage: < 100MB sustained
- Network requests: < 10 concurrent

### 2. Accessibility Requirements

**WCAG 2.1 AA Compliance:**
- Keyboard navigation for all interactions
- Screen reader compatibility
- Color contrast ratio > 4.5:1
- Focus indicators on all interactive elements
- Alternative text for all images and visualizations

### 3. Browser Support

**Target Browsers:**
- Chrome/Edge: Last 2 versions
- Firefox: Last 2 versions  
- Safari: Last 2 versions
- Mobile: iOS Safari, Chrome Mobile

## Migration and Versioning

### 1. State Migration

**Schema Evolution:**
```javascript
class StateMigrator {
    static migrations = {
        '1.0.0': (oldState) => ({
            ...oldState,
            version: '1.0.0'
        }),
        '1.1.0': (oldState) => ({
            ...oldState,
            ui: { ...oldState.ui, newFeature: true },
            version: '1.1.0'
        })
    };
    
    static migrate(state) {
        const currentVersion = state.version || '0.0.0';
        const targetVersion = this.getLatestVersion();
        
        if (currentVersion === targetVersion) return state;
        
        return this.applyMigrations(state, currentVersion, targetVersion);
    }
}
```

### 2. API Versioning

**Backward Compatibility:**
```python
# Backend API versioning strategy
@router.get("/api/v1/scenarios")  # Legacy support
@router.get("/api/scenarios")     # Current version
async def get_scenarios():
    # Maintain backward compatibility
    pass
```

This architecture provides the technical foundation for implementing all phases cohesively while maintaining consistency, performance, and maintainability across the entire SlashRun frontend application.
