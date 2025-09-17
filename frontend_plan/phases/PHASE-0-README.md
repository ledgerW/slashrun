# Phase 0 — Project Skeleton & Conventions

## Purpose

Create a minimal, testable app shell with no heavy visuals, establish design tokens, routing, and API client foundation. Ground the layout in Gotham's "single pane of truth": top bar, left nav, center canvas, right evidence rail, timeline footer.

This phase establishes the foundational architecture that all subsequent phases will build upon, ensuring consistent patterns and a solid technical foundation.

## Inputs

- Backend API endpoints: `/api/auth/login`, `/api/simulation/scenarios`, `/api/simulation/scenarios/{id}/step`
- Gotham-inspired design tokens from FRONTEND_RESEARCH.md
- FastAPI serving static files pattern from .clinerules

## Deliverables

```
frontend/
├── index.html              # Main app entry point
├── login.html              # Authentication page
├── css/
│   ├── app.css            # Global styles and design tokens
│   ├── auth.css           # Authentication page styles
│   └── components/        # Component-specific styles (future phases)
├── js/
│   ├── app.js             # Application initialization
│   ├── api.js             # API client with JWT management
│   ├── auth.js            # Authentication handling
│   ├── state.js           # State management
│   ├── router.js          # Hash-based routing
│   └── utils/             # Utility functions
├── assets/                # Images, icons, fonts
└── docs/
    └── PHASE-0-README.md  # This file
```

## Implementation Checklist

### HTML Structure
- [ ] `index.html`: Semantic app shell (header/topbar, nav, stage panels, aside evidence, footer timeline)
- [ ] `login.html`: Clean authentication form with proper validation
- [ ] Proper semantic markup with ARIA labels for accessibility

### CSS Foundation  
- [ ] `app.css`: CSS variables for Gotham-inspired colors/spacing/elevation (dark, high-contrast)
- [ ] Typography system with Inter/IBM Plex Sans, small caps labels
- [ ] Focus rings and accessibility considerations
- [ ] Responsive layout foundation

### JavaScript Core
- [ ] `api.js`: Centralized API client with JWT token management and error handling
- [ ] `auth.js`: Authentication manager for login/logout/token storage
- [ ] `state.js`: In-memory store (currentScenarioId, t, currentState, audit)
- [ ] `router.js`: Hash-based routes (`#/workbench`, `#/scenario/:id`) with route guards
- [ ] `app.js`: Application initialization, event binding (Step/Run/Reset), scenario loading

### Integration Points
- [ ] JWT token storage and automatic header attachment
- [ ] Route protection for authenticated pages
- [ ] Error handling and user feedback system
- [ ] Loading states and transitions

## Validation Tests (Can be run manually)

### Basic Functionality
- [ ] Load app → no console errors
- [ ] Authentication flow works: login → redirect to dashboard
- [ ] API calls to `/api/simulation/scenarios` succeed with proper auth headers
- [ ] Route navigation works between login and main app
- [ ] Logout clears tokens and redirects appropriately

### Accessibility
- [ ] Keyboard navigation reaches all controls
- [ ] Focus states are visible and logical
- [ ] Screen reader announces page changes
- [ ] Color contrast meets WCAG AA standards (4.5:1)

### Performance
- [ ] Page loads in <2 seconds on typical connection
- [ ] No layout shifts during initial load
- [ ] Smooth transitions ≤150ms (Gotham-style minimal motion)

## API Endpoints Used

This phase integrates with these backend endpoints:

```javascript
// Authentication
POST /api/auth/login
POST /api/auth/logout

// Scenarios (basic loading)
GET /api/simulation/scenarios
GET /api/simulation/scenarios/{id}
```

## Key Architecture Decisions

### Authentication Pattern
- JWT tokens stored in localStorage for convenience (can be changed to sessionStorage for security)
- Automatic token attachment to API requests
- Route guards prevent access to protected pages
- Token expiration handling with automatic redirect

### State Management
- Simple in-memory store for current session state
- No complex state management library needed at this phase
- State updates trigger UI re-renders via event system

### Routing
- Hash-based routing for simplicity (no server configuration needed)
- Route guards check authentication status
- Clean URLs that map to app sections

### Styling Philosophy
- CSS custom properties for consistent theming
- Mobile-first responsive design
- Dark theme optimized for data visualization
- Minimal animations following Palantir's restrained motion principles

## Handoff Memo → Phase 1

**What's Complete:**
- App shell layout and navigation structure
- Authentication system with JWT token management  
- Basic API client with error handling
- Route protection and navigation
- Gotham-inspired dark theme foundation

**What's Next:**
Phase 1 will add the **Timeline & Evidence Rail** - the core investigative interface that makes time and audit trails first-class citizens. This includes:
- Timeline scrubber with event pins
- Right-rail audit viewer with field changes
- State inspector and JSON diff viewer
- Integration with simulation step API

**Key Integration Points for Phase 1:**
- `state.js` will be extended to handle timestep navigation
- API client will need `GET /scenarios/{id}/states/{t}` and `POST /scenarios/{id}/step` 
- Right rail HTML structure is already in place, ready for audit components
- Timeline footer area prepared for scrubber component

**Architecture Notes for Next Phase:**
- The evidence rail should update reactively when timeline position changes
- Consider debouncing timeline scrubbing to avoid excessive API calls
- Audit trail should show clear diff visualization with color coding
- Performance will be critical for smooth timeline scrubbing experience
