# Authentication & Token Management

## Architecture Overview

**Full-Stack Authentication Flow:**
- **Frontend** (`frontend/`) manages user sessions and token storage
- **Backend** (`backend/app/api/auth.py`) provides JWT endpoints
- **Database** (`db/models/user.py`) stores user credentials and profiles
- **Root** (`main.py`) orchestrates CORS and static file serving

## Backend Patterns

### 1. Protected Route Pattern
**Add auth dependency to ALL protected endpoints**
```python
# ✅ CORRECT - Protected endpoint
@router.post("/agents")
async def create_agent(
    agent_data: AgentCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Required!
):
    # Only authenticated users can create agents
    return await agent_service.create(agent_data, current_user.id, db)
```

### 2. Complete Auth Models
**Backend models define the full API contract:**
```python
# backend/app/api/auth.py
class LoginRequest(BaseModel):
    email: str  # NOT username
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int                    # Duration in seconds
    user_id: str                       # For frontend user tracking
    username: str                      # Display name
    email: str                         # User email

class TokenPayload(BaseModel):
    sub: str                          # User ID
    exp: int                          # Expiration timestamp
```

### 3. JWT Configuration
**Proper JWT settings in environment:**
```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # JWT Configuration
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM") 
    jwt_access_token_expire_minutes: int = Field(10080, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")  # 7 days
    
    # CORS for frontend
    allowed_origins: list[str] = Field(default_factory=lambda: [
        "http://localhost:3000",      # Development frontend
        "http://127.0.0.1:3000",
    ])
```

## Frontend Integration Patterns

### 1. Authentication Manager
**Frontend token management (from frontend patterns):**
```javascript
// frontend/js/auth.js
class AuthManager {
    constructor() {
        this.tokenKey = 'slashrun_access_token';
        this.userKey = 'slashrun_user';
    }
    
    async login(email, password) {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        if (response.ok) {
            const loginData = await response.json();
            this.storeAuth(loginData);
            return { success: true, user: loginData };
        } else {
            const error = await response.json();
            return { success: false, error: error.detail };
        }
    }
    
    storeAuth(loginResponse) {
        localStorage.setItem(this.tokenKey, loginResponse.access_token);
        localStorage.setItem(this.userKey, JSON.stringify({
            user_id: loginResponse.user_id,
            username: loginResponse.username,
            email: loginResponse.email,
            expires_at: Date.now() + (loginResponse.expires_in * 1000)
        }));
    }
    
    isAuthenticated() {
        const user = this.getUser();
        return user && Date.now() < user.expires_at;
    }
}
```

### 2. API Client Integration
**Automatic token attachment:**
```javascript
// frontend/js/api.js
class APIClient {
    constructor() {
        this.baseURL = '/api';  // Same origin
    }
    
    getAuthHeaders() {
        const token = auth.getToken();
        return token ? {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        } : {
            'Content-Type': 'application/json'
        };
    }
    
    async request(method, endpoint, data = null) {
        const config = {
            method,
            headers: this.getAuthHeaders()
        };
        
        if (data && method !== 'GET') {
            config.body = JSON.stringify(data);
        }
        
        const response = await fetch(`${this.baseURL}${endpoint}`, config);
        
        // Handle auth failures globally
        if (response.status === 401) {
            auth.clearAuth();
            window.location.href = '/login.html';
            throw new Error('Authentication failed');
        }
        
        return response;
    }
}
```

## Full-Stack Authentication Flow

### 1. Login Process
**Complete login implementation:**

**Frontend (login.html + login.js):**
```javascript
async function handleLogin(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    
    const result = await auth.login(
        formData.get('email'),
        formData.get('password')
    );
    
    if (result.success) {
        window.location.href = '/dashboard.html';
    } else {
        showError(result.error);
    }
}
```

**Backend (auth.py):**
```python
@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Authenticate user
    user = await auth_service.authenticate_user(
        email=login_data.email,
        password=login_data.password,
        db=db
    )
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create token
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id)}, 
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        user_id=str(user.id),
        username=user.username,
        email=user.email
    )
```

### 2. Protected Resource Access
**End-to-end protected resource pattern:**

**Frontend:**
```javascript
// Protected page check
document.addEventListener('DOMContentLoaded', function() {
    if (!auth.isAuthenticated()) {
        window.location.href = '/login.html';
        return;
    }
    loadUserDashboard();
});

async function loadUserDashboard() {
    try {
        const response = await api.get('/simulation/scenarios');
        if (response.ok) {
            const scenarios = await response.json();
            displayScenarios(scenarios);
        }
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}
```

**Backend:**
```python
@router.get("/simulation/scenarios")
async def get_user_scenarios(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Auth required
):
    scenarios = await scenario_service.get_by_user(current_user.id, db)
    return scenarios
```

## CORS Configuration

### 1. FastAPI CORS Setup
**Proper CORS for frontend integration:**
```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins + [
        "http://localhost:8000",      # Same origin
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,           # Required for auth headers
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

### 2. Same-Origin Benefits
**Why serving frontend from FastAPI eliminates CORS complexity:**
- API calls to `/api/*` are same-origin (no preflight requests)
- Cookies and credentials work automatically
- WebSocket connections work seamlessly
- No complex CORS debugging

## Common Pitfalls

### 1. Unprotected Endpoints
```python
# ❌ WRONG - Missing auth dependency
@router.post("/agents")
async def create_agent(agent_data: AgentCreateRequest):
    # Anyone can create agents!

# ✅ CORRECT - Auth required
async def create_agent(..., current_user: User = Depends(get_current_user)):
```

### 2. Frontend Token Expiration
```javascript
// ❌ WRONG - No expiration check
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

### 3. Incomplete Error Handling
```python
# ❌ WRONG - Generic error messages
raise HTTPException(status_code=401, detail="Unauthorized")

# ✅ CORRECT - Specific error messages
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect email or password",
    headers={"WWW-Authenticate": "Bearer"}
)
```

### 4. Environment Configuration Issues
```python
# ❌ WRONG - Hardcoded secrets
SECRET_KEY = "my-secret-key"

# ✅ CORRECT - Environment variables
jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
```

## Security Best Practices

### 1. Token Storage Security
**Choose appropriate storage mechanism:**
```javascript
// Production: Use sessionStorage for higher security
const auth = new AuthManager(true);  // Uses sessionStorage

// Development: localStorage for convenience
const auth = new AuthManager(false); // Uses localStorage
```

### 2. Password Security
**Backend password handling:**
```python
# backend/app/services/auth_service.py
from passlib.context import CryptContext

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
```

### 3. Token Validation
**Robust token validation:**
```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    user = await auth_service.get_user_by_token(credentials.credentials, db)
    
    if not user or not user.is_active:
        raise credentials_exception
    
    return user
```

## Reference Examples
- **Backend Auth**: `backend/app/api/auth.py` - JWT endpoints and validation
- **Protected Routes**: `backend/app/api/*.py` - Auth dependency pattern  
- **User Service**: `backend/app/services/auth_service.py` - Authentication logic
- **Frontend Auth**: `frontend/js/auth.js` - Token management and login
- **API Client**: `frontend/js/api.js` - Authenticated API calls

## Quick Testing
```bash
# Find unprotected endpoints
grep -r "@router\." backend/app/api/ | grep -v "get_current_user"

# Test login flow
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@slashrun.com","password":"admin123"}'

# Test protected endpoint
curl -X GET http://localhost:8000/api/simulation/scenarios \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Integration Checklist

### Backend Setup:
- [ ] Add `Depends(get_current_user)` to protected endpoints
- [ ] Use consistent model schemas (LoginRequest, LoginResponse)
- [ ] Configure JWT settings in environment variables
- [ ] Implement proper error handling for 401/403 responses
- [ ] Set up CORS middleware for frontend origins

### Frontend Setup:
- [ ] Implement AuthManager for token storage and validation
- [ ] Create APIClient with automatic auth header attachment
- [ ] Add protected page authentication checks
- [ ] Implement login/logout flow with proper error handling
- [ ] Test token expiration and renewal

### Full-Stack Testing:
- [ ] Test successful login flow
- [ ] Test failed authentication attempts
- [ ] Verify protected route access
- [ ] Test token expiration handling
- [ ] Validate logout functionality

**Memory Aid**: "Backend protects with get_current_user, frontend manages with AuthManager, same-origin eliminates CORS complexity."
