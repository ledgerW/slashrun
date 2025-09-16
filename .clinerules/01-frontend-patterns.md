# Frontend Development Patterns & Best Practices

## Architecture Overview

**Three-Tier Architecture:**
- **`main.py`**: Root FastAPI orchestrator serving both API and frontend
- **`backend/`**: Python API endpoints and business logic
- **`frontend/`**: HTML/JS/CSS user interface
- **`db/`**: SQLModel definitions, migrations, database layer

## Project Structure Standards

### 1. Frontend Directory Organization
```
frontend/
├── index.html              # Main application entry point
├── login.html              # Authentication pages
├── dashboard.html          # Main application views
├── css/
│   ├── main.css           # Global styles
│   ├── components/        # Component-specific styles
│   │   ├── auth.css
│   │   ├── simulation.css
│   │   └── dashboard.css
│   └── vendor/            # Third-party CSS libraries
├── js/
│   ├── main.js            # Application initialization
│   ├── auth.js            # Authentication handling
│   ├── api.js             # Backend API integration
│   ├── components/        # UI component modules
│   │   ├── simulation.js
│   │   ├── dashboard.js
│   │   └── websocket.js
│   └── utils/             # Utility functions
│       ├── storage.js     # localStorage/sessionStorage helpers
│       └── validation.js  # Client-side validation
└── assets/
    ├── images/
    ├── icons/
    └── fonts/
```

## FastAPI Static File Integration

### 1. Root Application Configuration
**In `main.py`:**
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount frontend static files AFTER API routes
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# Catch-all for SPA routing (optional)
@app.get("/{path:path}")
async def serve_frontend(path: str):
    """Serve frontend for client-side routing."""
    return FileResponse("frontend/index.html")
```

### 2. Development vs Production Serving
**Development Pattern:**
```python
# main.py - Development mode
if settings.debug:
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
```

**Production Pattern:**
```python
# For production, consider using nginx for static files
# But FastAPI StaticFiles works fine for most applications
app.mount("/static", StaticFiles(directory="frontend"), name="static")
```

## Authentication Integration Patterns

### 1. JWT Token Management
**Frontend auth.js:**
```javascript
// ✅ CORRECT - Token storage and management
class AuthManager {
    constructor() {
        this.tokenKey = 'slashrun_access_token';
        this.userKey = 'slashrun_user';
    }
    
    // Store token and user data
    storeAuth(loginResponse) {
        localStorage.setItem(this.tokenKey, loginResponse.access_token);
        localStorage.setItem(this.userKey, JSON.stringify({
            user_id: loginResponse.user_id,
            username: loginResponse.username,
            email: loginResponse.email,
            expires_at: Date.now() + (loginResponse.expires_in * 1000)
        }));
    }
    
    // Get valid token or null if expired
    getToken() {
        const user = this.getUser();
        if (!user || Date.now() > user.expires_at) {
            this.clearAuth();
            return null;
        }
        return localStorage.getItem(this.tokenKey);
    }
    
    // Get user data
    getUser() {
        const userStr = localStorage.getItem(this.userKey);
        return userStr ? JSON.parse(userStr) : null;
    }
    
    // Clear authentication
    clearAuth() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.userKey);
    }
    
    // Check if user is authenticated
    isAuthenticated() {
        return this.getToken() !== null;
    }
}

const auth = new AuthManager();
```

### 2. Login Flow Implementation
**Frontend login handling:**
```javascript
// ✅ CORRECT - Login form handling
async function handleLogin(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const loginData = {
        email: formData.get('email'),
        password: formData.get('password')
    };
    
    try {
        const response = await api.post('/api/auth/login', loginData);
        
        if (response.ok) {
            const loginResponse = await response.json();
            auth.storeAuth(loginResponse);
            
            // Redirect to dashboard
            window.location.href = '/dashboard.html';
        } else {
            const error = await response.json();
            showError(error.detail || 'Login failed');
        }
    } catch (error) {
        showError('Network error. Please try again.');
    }
}
```

### 3. Protected Page Patterns
**Page-level authentication check:**
```javascript
// ✅ CORRECT - Protected page initialization
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication on page load
    if (!auth.isAuthenticated()) {
        window.location.href = '/login.html';
        return;
    }
    
    // Initialize page content
    initializePage();
});
```

## API Communication Standards

### 1. Centralized API Client
**Frontend api.js:**
```javascript
// ✅ CORRECT - Centralized API client
class APIClient {
    constructor() {
        this.baseURL = '/api'; // Same origin - no CORS issues
    }
    
    // Get authorization headers
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        const token = auth.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        return headers;
    }
    
    // Generic request method
    async request(method, endpoint, data = null) {
        const config = {
            method,
            headers: this.getHeaders()
        };
        
        if (data && method !== 'GET') {
            config.body = JSON.stringify(data);
        }
        
        const response = await fetch(`${this.baseURL}${endpoint}`, config);
        
        // Handle authentication errors
        if (response.status === 401) {
            auth.clearAuth();
            window.location.href = '/login.html';
            return;
        }
        
        return response;
    }
    
    // Convenience methods
    async get(endpoint) { return this.request('GET', endpoint); }
    async post(endpoint, data) { return this.request('POST', endpoint, data); }
    async put(endpoint, data) { return this.request('PUT', endpoint, data); }
    async delete(endpoint) { return this.request('DELETE', endpoint); }
}

const api = new APIClient();
```

### 2. Error Handling Patterns
**Consistent error handling:**
```javascript
// ✅ CORRECT - Comprehensive error handling
async function handleAPICall(apiFunction, successCallback, errorMessage = 'Operation failed') {
    try {
        const response = await apiFunction();
        
        if (response.ok) {
            const data = await response.json();
            successCallback(data);
        } else {
            const error = await response.json();
            showError(error.detail || errorMessage);
        }
    } catch (error) {
        console.error('API Error:', error);
        showError('Network error. Please check your connection.');
    }
}
```

## WebSocket Integration

### 1. Real-time Simulation Updates
**WebSocket connection management:**
```javascript
// ✅ CORRECT - WebSocket integration for simulations
class SimulationWebSocket {
    constructor(scenarioId) {
        this.scenarioId = scenarioId;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }
    
    connect() {
        // Use same origin WebSocket
        const wsUrl = `ws://localhost:8000/ws/simulation/${this.scenarioId}`;
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleSimulationUpdate(data);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.attemptReconnect();
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    handleSimulationUpdate(data) {
        // Update UI with simulation progress
        if (data.type === 'step_complete') {
            updateSimulationProgress(data.step, data.results);
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => this.connect(), 1000 * this.reconnectAttempts);
        }
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}
```

## Development Workflow

### 1. Docker Integration
**Updated docker-compose.yml:**
```yaml
services:
  backend:
    build:
      context: .
      dockerfile: ./backend/Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/app:/app/backend/app
      - ./frontend:/app/frontend        # Frontend live reload
      - ./db:/app/db                    # Database models
    command: uv run main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Live Development
**Frontend changes are immediately available:**
- HTML/CSS/JS changes reflect instantly (no rebuild needed)
- FastAPI serves static files directly from filesystem
- Backend API changes trigger uvicorn reload

## Security Best Practices

### 1. Token Storage Considerations
**localStorage vs sessionStorage:**
```javascript
// ✅ RECOMMENDED - Use localStorage for convenience, sessionStorage for security
class SecureAuthManager extends AuthManager {
    constructor(useSessionStorage = false) {
        super();
        this.storage = useSessionStorage ? sessionStorage : localStorage;
    }
    
    storeAuth(loginResponse) {
        // Store in chosen storage mechanism
        this.storage.setItem(this.tokenKey, loginResponse.access_token);
        this.storage.setItem(this.userKey, JSON.stringify(userData));
    }
}

// For high-security applications, use sessionStorage
const auth = new SecureAuthManager(true); // Uses sessionStorage
```

### 2. XSS Prevention
**Safe HTML manipulation:**
```javascript
// ✅ CORRECT - Prevent XSS
function safeInsertHTML(element, content) {
    element.textContent = content; // Not innerHTML
}

function safeCreateElement(tag, textContent) {
    const element = document.createElement(tag);
    element.textContent = textContent;
    return element;
}
```

### 3. Input Validation
**Client-side validation (with server-side backup):**
```javascript
// ✅ CORRECT - Input validation
function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

function validatePassword(password) {
    return password.length >= 8; // Basic validation
}
```

## Common Pitfalls to Avoid

### 1. Static File Mounting Order
```python
# ❌ WRONG - Static files mounted before API routes
app.mount("/", StaticFiles(directory="frontend"), name="frontend")
app.include_router(auth_router, prefix="/api/auth")  # This won't work!

# ✅ CORRECT - API routes first, then static files
app.include_router(auth_router, prefix="/api/auth")
app.mount("/", StaticFiles(directory="frontend"), name="frontend")
```

### 2. Token Expiration Handling
```javascript
// ❌ WRONG - No token expiration check
function getToken() {
    return localStorage.getItem('access_token');
}

// ✅ CORRECT - Check expiration
function getToken() {
    const user = getUser();
    if (!user || Date.now() > user.expires_at) {
        clearAuth();
        return null;
    }
    return localStorage.getItem('access_token');
}
```

### 3. CORS Confusion
```javascript
// ❌ WRONG - Assuming CORS issues with same-origin
const api = new APIClient('http://different-domain.com/api');

// ✅ CORRECT - Same origin, no CORS needed
const api = new APIClient('/api');
```

## Integration Checklist

### Frontend Setup:
- [ ] Create `frontend/` directory structure
- [ ] Implement `auth.js` with JWT token management
- [ ] Create `api.js` with centralized API client
- [ ] Add protected page authentication checks
- [ ] Implement error handling for API calls
- [ ] Set up WebSocket connections for real-time updates

### FastAPI Integration:
- [ ] Mount static files in `main.py` (after API routes)
- [ ] Configure CORS for development if needed
- [ ] Test API endpoints from frontend
- [ ] Verify JWT authentication flow
- [ ] Test WebSocket connections

### Development Workflow:
- [ ] Update docker-compose.yml for frontend volume mounting
- [ ] Test live reload for frontend changes
- [ ] Verify backend API integration
- [ ] Test authentication flow end-to-end
- [ ] Validate error handling and edge cases

## Reference Examples

### Complete Login Page:
- **HTML**: Simple form with email/password fields
- **CSS**: Clean, responsive authentication UI
- **JS**: Form handling with proper error display

### Dashboard Integration:
- **Authentication Check**: Verify token on page load
- **API Calls**: Fetch user-specific data
- **Real-time Updates**: WebSocket connection for live data

### Error Handling:
- **Network Errors**: User-friendly messages
- **Authentication Errors**: Automatic redirect to login
- **Validation Errors**: Inline form feedback

**Memory Aid**: "FastAPI serves frontend, same-origin API calls, JWT in localStorage, WebSocket for real-time."
