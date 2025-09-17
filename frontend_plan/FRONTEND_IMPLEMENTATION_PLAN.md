# SlashRun Frontend Implementation Plan
## Gotham-Inspired Multi-Phase Development Strategy

## Overview

This document outlines a comprehensive 10-phase implementation strategy for building the SlashRun frontend application. The approach is inspired by Palantir Gotham's design principles and user experience patterns, focusing on investigative workflows, geospatial analysis, timeline-based exploration, and audit transparency.

### Design Philosophy

**Core Principles (from Palantir Gotham):**
- **Single pane of truth**: One workspace for investigation, simulation, and analysis
- **Investigative workflow first**: Drive interactions from questions → evidence → decisions  
- **Spacetime native**: Time and geography as first-class UI objects
- **Ontology-aware**: UI components bound to domain entities (countries, rules, triggers)
- **Explainability & audit**: Complete transparency of what changed and why
- **Performance under stress**: Progressive rendering of complex visualizations

### Visual Language
- **Dark theme**: `--ink-900` backgrounds with high-contrast text
- **Signal colors**: Blue palette for interactive elements and data highlights
- **Typography**: Inter/IBM Plex Sans with tight tracking and small caps labels
- **Motion**: Minimal micro-transitions ≤150ms, 60fps timeline scrubbing
- **Accessibility**: WCAG AA compliance, full keyboard navigation

## Phase Structure

Each phase follows this consistent structure:
- **Purpose**: Clear goals and context
- **Inputs**: Dependencies and requirements
- **Deliverables**: Specific files and components to be built
- **Implementation Checklist**: Detailed tasks
- **Validation Tests**: Acceptance criteria
- **API Integration**: Backend endpoint usage
- **Handoff Memo**: Context for next phase

## Phase Overview

### Phase 0: Project Skeleton & Conventions ⚡ FOUNDATION
**Duration**: 1-2 days  
**Priority**: Critical  
Create app shell, design tokens, routing, and API client foundation. Establish the core architecture that all other phases build upon.

### Phase 1: Authentication & Core State Management 🔐 FOUNDATION  
**Duration**: 1-2 days  
**Priority**: Critical  
JWT-based authentication system, protected routing, and centralized state management for scenarios and user sessions.

### Phase 2: Timeline & Evidence Rail 🕒 CORE
**Duration**: 2-3 days  
**Priority**: High  
Timeline scrubber with event pins, audit trail viewer, reducer chain visualization, and state diff inspector. This is the investigative heart of the application.

### Phase 3: Map View (Geospatial Layers) 🗺 VISUALIZATION
**Duration**: 3-4 days  
**Priority**: High  
Interactive world map with overlays for trade flows, sanctions, alliances, and interbank exposures. Time-bound animations and country selection.

### Phase 4: Network View (Link Analysis) 🔗 VISUALIZATION
**Duration**: 2-3 days  
**Priority**: Medium-High  
Force-directed graph visualization of country relationships with interactive node selection and ego-network highlighting.

### Phase 5: Time-Series Panel 📈 VISUALIZATION
**Duration**: 2-3 days  
**Priority**: Medium-High  
Multi-series economic indicator charts with brush-to-zoom, event markers, and country comparison capabilities.

### Phase 6: Scenario Builder 🔧 PRODUCTIVITY
**Duration**: 3-4 days  
**Priority**: Medium  
Ontology-aware forms for creating scenarios with country data, rules, matrices, and validation. Template integration (MVS/FIS).

### Phase 7: Trigger Designer ⚡ PRODUCTIVITY
**Duration**: 2-3 days  
**Priority**: Medium  
Advanced trigger creation interface with condition builder, action composer, and dry-run preview system.

### Phase 8: Walkthroughs & Sharing 📋 COLLABORATION
**Duration**: 2-3 days  
**Priority**: Low-Medium  
Pin-based narrative creation, guided investigation flows, and export functionality for sharing analyses.

### Phase 9: Performance & Polish ✨ OPTIMIZATION
**Duration**: 2-3 days  
**Priority**: Medium  
Web Workers, accessibility audit, mobile responsiveness, and performance optimization for large datasets.

## Cross-Phase Architecture

### State Management Strategy
- **Phase 0-1**: Simple in-memory store with event-driven updates
- **Phase 2+**: Extended state management for timeline, audit, and UI state
- **No external libraries**: Vanilla JavaScript with custom event system

### API Integration Pattern
- **Centralized client**: Single API class with JWT token management
- **Error handling**: Consistent error states and user feedback
- **Loading states**: Progressive loading with skeleton screens
- **Real-time updates**: WebSocket integration in later phases

### Component Architecture
- **Modular design**: Each major feature as self-contained module
- **Event-driven**: Components communicate via custom events
- **Progressive enhancement**: Features work independently and enhance each other

### Performance Considerations
- **Lazy loading**: Load visualization libraries only when needed
- **Virtualization**: Handle large datasets efficiently
- **Debouncing**: Prevent excessive API calls during interactions
- **Web Workers**: Offload heavy computations (Phase 9)

## Dependencies & Prerequisites

### Backend API Requirements
- Authentication endpoints (`/api/auth/login`, `/api/auth/logout`)
- Scenario CRUD (`/api/simulation/scenarios/*`)  
- Simulation stepping (`/api/simulation/scenarios/{id}/step`)
- State history (`/api/simulation/scenarios/{id}/states/{t}`)
- Template generation (`/api/simulation/templates/*`)

### External Libraries (Introduced Progressively)
- **Phase 3**: MapLibre GL JS or Leaflet for maps
- **Phase 4**: D3.js for network visualization  
- **Phase 5**: D3.js for time-series charts
- **Phase 8**: jsPDF for export functionality

### Browser Support
- Modern browsers (Chrome 90+, Firefox 88+, Safari 14+)
- ES2020+ features available
- CSS Grid and Flexbox support required

## Quality Assurance Strategy

### Testing Approach
- **Manual testing**: Detailed checklists for each phase
- **Visual regression**: Screenshot comparisons for UI consistency  
- **Performance testing**: Lighthouse audits and FPS monitoring
- **Accessibility testing**: WCAG AA compliance verification

### Code Quality
- **ESLint**: JavaScript linting with strict rules
- **Prettier**: Consistent code formatting
- **JSDoc**: Documentation for complex functions
- **Performance monitoring**: Core Web Vitals tracking

## Risk Mitigation

### Technical Risks
- **Visualization complexity**: Start with simple implementations, enhance incrementally
- **Performance issues**: Profile early and often, implement optimization strategies
- **Browser compatibility**: Use progressive enhancement and feature detection

### Project Risks  
- **Scope creep**: Strict phase boundaries with clear handoff criteria
- **Timeline pressure**: Each phase designed for 1-4 day completion
- **Integration issues**: Continuous testing of phase interactions

## Success Criteria

### Phase Completion Criteria
1. All implementation checklist items completed
2. Validation tests passing
3. No console errors in browser
4. Handoff memo completed for next phase
5. User acceptance of functionality

### Overall Project Success
- **Functional**: All core simulation workflows operational
- **Performance**: <3s initial load, <100ms interaction response
- **Accessibility**: WCAG AA compliance achieved
- **Usability**: Clear investigative workflow from scenario to insights
- **Maintainability**: Clean, documented, modular codebase

## Next Steps

1. **Review this plan** with stakeholders for approval
2. **Begin Phase 0** implementation with project skeleton
3. **Validate architecture** decisions with first working prototype
4. **Iterate and refine** based on user feedback after each phase

This plan provides a clear roadmap from concept to production-ready application while maintaining the investigative, data-rich experience that defines the Palantir Gotham aesthetic.
