# Phase 1 — Authentication & Core State Management

## Purpose

Implement JWT-based authentication system with protected routing and centralized state management. This phase establishes the security foundation and user session management that all subsequent phases depend upon. The authentication flow follows modern web security practices while maintaining the clean Gotham aesthetic.

## Inputs

**From Phase 0:**
- App shell HTML structure with login/main app containers
- Basic CSS foundation with design tokens
- Router.js skeleton and API client foundation
- Loading states and transitions

**Backend Dependencies:**
- `/api/auth/login` - JWT login endpoint
- `/api/auth/logout` - Logout endpoint (client-side token clearing)
- `/api/simulation/scenarios` - Protected scenario listing
- JWT token validation via `get_current_user` dependency

## Deliverables

```
frontend/
├── login.html                     # Authentication page
├── css/
│   ├── auth.css                  # Login page styles
│   └── components/
│       ├── forms.css             # Form component styles
│       └── buttons.css           # Button component styles
├── js/
│   ├── auth.js                   # Authentication manager
│   ├── state.js                  # Centralized state management
│   ├── router.js                 # Enhanced routing with guards
│   ├── api.js                    # Enhanced API client with JWT
│   └── utils/
│       ├── validation.js         # Input validation utilities
│       └── storage.js            # LocalStorage/SessionStorage helpers
└── docs/
    └── PHASE-1-README.md         # This file
```

## Implementation Checklist

### Authentication System
- [ ] **login.html**: Clean authentication form with email/password fields
- [ ] **auth.css**: Gotham-inspired dark theme for login page
- [ ] **auth.js**: JWT token management (store, retrieve, validate expiration)
- [ ] **Login flow**: Handle form submission, API calls, error states
- [ ] **Token storage**: Configurable localStorage vs sessionStorage
- [ ] **Session persistence**: Remember user across browser sessions
- [ ] **Logout functionality**: Clear tokens and redirect to login

### Protected Routing
- [ ] **Route guards**: Check authentication before accessing protected routes
- [ ] **Automatic redirects**: Unauthenticated users → login, authenticated users → dashboard
- [ ] **Deep linking**: Preserve intended destination after login
- [ ] **Token expiration handling**: Automatic logout and redirect when token expires
- [ ] **Navigation state**: Update UI based on authentication status

### API Integration
- [ ] **JWT headers**: Automatic token attachment to all API requests
- [ ] **401 handling**: Intercept unauthorized responses and redirect to login
- [ ] **Error states**: User-friendly error messages for auth failures
- [ ] **Loading states**: Show appropriate loading indicators during auth operations
- [ ] **Retry logic**: Handle network failures gracefully

### State Management
- [ ] **User state**: Store current user info (id, username, email)
- [ ] **Authentication state**: Track login status, token expiration
- [ ] **Scenario state**: Basic scenario metadata (current scenario ID)
- [ ] **UI state**: Navigation state, loading states, error states
- [ ] **Event system**: Custom events for state changes
- [ ] **Persistence**: Save/restore relevant state across sessions

### Form Validation & UX
- [ ] **Client-side validation**: Email format, required fields
- [ ] **Real-time feedback**: Validation messages as user types
- [ ] **Accessible forms**: Proper labels, error associations, keyboard navigation
- [ ] **Loading states**: Disable form during submission
- [ ] **Error handling**: Clear, actionable error messages

## API Integration Details

### Authentication Endpoints

```javascript
// Login request
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

// Expected response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "John Doe",
  "email": "user@example.com"
}
```

### Protected Resource Access

```javascript
// All subsequent requests include JWT header
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

// Test protected endpoint
GET /api/simulation/scenarios
```

### Error Handling Patterns

```javascript
// Authentication errors
401 Unauthorized → Redirect to login
403 Forbidden → Show "Access denied" message
422 Validation → Show field-specific errors
500 Server Error → Show "Please try again" message
```

## Validation Tests

### Authentication Flow
- [ ] **Login success**: Valid credentials → dashboard with scenarios loaded
- [ ] **Login failure**: Invalid credentials → error message, no redirect
- [ ] **Token persistence**: Refresh page → still logged in (if token valid)
- [ ] **Token expiration**: Expired token → automatic redirect to login
- [ ] **Deep linking**: `/scenario/123` while logged out → login → `/scenario/123`

### API Integration  
- [ ] **Protected requests**: Include valid JWT token in Authorization header
- [ ] **Unauthorized handling**: 401 response → automatic logout and redirect
- [ ] **Network errors**: Failed requests → appropriate error messages
- [ ] **Loading states**: Show spinners during API calls

### User Experience
- [ ] **Form validation**: Email validation, required field checking
- [ ] **Error display**: Clear, accessible error messages
- [ ] **Keyboard navigation**: Tab through all interactive elements
- [ ] **Screen reader**: Proper announcements for state changes
- [ ] **Mobile responsive**: Login form works on mobile devices

### Security
- [ ] **Token security**: No tokens logged to console or visible in DOM
- [ ] **Session handling**: Logout clears all authentication data
- [ ] **HTTPS ready**: No mixed content warnings
- [ ] **XSS protection**: User input properly escaped

## Architecture Decisions

### Token Storage Strategy
**Decision**: Use localStorage by default with option for sessionStorage  
**Rationale**: Balance between user convenience and security  
**Implementation**: Configurable in auth.js constructor

### State Management Pattern
**Decision**: Custom event-driven state management  
**Rationale**: No external dependencies, perfect for our scale  
**Implementation**: Central state object with event emitters

### Route Protection Strategy
**Decision**: Route-level guards with automatic redirects  
**Rationale**: Clear separation of concerns, easy to debug  
**Implementation**: Check auth status before route activation

### Error Handling Philosophy
**Decision**: User-friendly messages with developer details in console  
**Rationale**: Good UX without hiding debugging information  
**Implementation**: Error message mapping with fallbacks

## Component Specifications

### AuthManager Class
```javascript
class AuthManager {
  constructor(useSessionStorage = false)
  async login(email, password)
  logout()
  isAuthenticated()
  getToken()
  getUser()
  onAuthChange(callback)
}
```

### APIClient Enhancement
```javascript
class APIClient {
  setAuthManager(authManager)
  async request(method, endpoint, data, options)
  handleAuthError(response)
  getAuthHeaders()
}
```

### Router Enhancement
```javascript
class Router {
  addGuard(guardFunction)
  requireAuth(routeConfig)
  redirect(path, replace = false)
}
```

## Handoff Memo → Phase 2

**What's Complete:**
- Robust JWT-based authentication system
- Protected routing with automatic redirects  
- Centralized state management foundation
- API client with automatic token management
- Login/logout user flow with proper error handling
- Accessibility-compliant form validation

**What's Next:**
Phase 2 will implement the **Timeline & Evidence Rail** - the core investigative interface. This includes:
- Timeline scrubber component for navigating simulation timesteps
- Audit trail viewer showing field-level changes
- Reducer chain visualization showing calculation steps
- State diff viewer with JSON comparison
- Integration with simulation step and history APIs

**Key Integration Points for Phase 2:**
- `state.js` will be extended with timeline state (current timestep, history)
- API client ready for simulation endpoints (`/scenarios/{id}/step`, `/scenarios/{id}/states/{t}`)
- Authentication ensures all simulation data is user-scoped
- Right rail HTML structure prepared for audit components

**State Management Notes:**
- Current scenario ID will be managed in state.js
- Timeline position (timestep) becomes central to app state
- Audit data will be cached for performance during scrubbing
- Consider implementing optimistic updates for stepping operations

**Performance Considerations:**
- Debounce timeline scrubbing to avoid excessive API calls
- Cache recent simulation states for smooth navigation
- Prepare for WebSocket integration in future phases
- Consider virtual scrolling for large audit trails

**UX Continuity:**
- Maintain loading states during simulation operations
- Preserve timeline position across route changes within scenarios
- Error recovery for failed simulation steps
- Clear visual feedback for long-running operations
