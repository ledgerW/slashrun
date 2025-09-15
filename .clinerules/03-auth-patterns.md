# Authentication & Token Management

## Critical Rule: Consistent Token Keys
**ALWAYS use `access_token` as the localStorage key everywhere**

```typescript
// ✅ CORRECT
localStorage.getItem('access_token');
localStorage.setItem('access_token', token);

// ❌ WRONG - Different keys cause bugs
localStorage.getItem('token');        // Different key
localStorage.getItem('authToken');    // Different key  
```

## Essential Patterns

### 1. Centralized API Client
**Use the centralized API client, never manual fetch calls**
- **Implementation**: `app/ui/src/lib/api.ts`
- **Usage**: `await authApi.login(formData)` - handles token storage automatically
- **Auto-logout**: 401 responses redirect to login automatically

### 2. Protected Route Pattern
**Add auth dependency to ALL protected endpoints**
```python
# ✅ CORRECT - Protected endpoint
@router.post("/agents")
async def create_agent(
    agent_data: AgentCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Required!
):
```

### 3. Frontend/Backend Model Alignment
**Models must match exactly:**
```python
# Backend: app/api/auth.py
class LoginRequest(BaseModel):
    email: str  # NOT username
    password: str
```
```typescript
// Frontend: app/ui/src/types/index.ts  
export interface LoginRequest {
  email: string;      // NOT username
  password: string;
}
```

## Common Pitfalls

### 1. Token Key Inconsistency
```typescript
// ❌ WRONG - Mixed keys
localStorage.setItem('token', response.token);      // Login
const token = localStorage.getItem('access_token'); // Usage

// ✅ CORRECT - Same key everywhere  
localStorage.setItem('access_token', response.access_token);
```

### 2. Manual Token Handling
```tsx
// ❌ WRONG - Manual checks everywhere
const token = localStorage.getItem('access_token');
if (!token) return <div>Not authenticated</div>;

// ✅ CORRECT - Use centralized API
await agentApi.create(data);  // Auth handled automatically
```

### 3. Unprotected Endpoints
```python
# ❌ WRONG - Missing auth dependency
@router.post("/agents")
async def create_agent(agent_data: AgentCreateRequest):
    # Anyone can create agents!

# ✅ CORRECT - Auth required
async def create_agent(..., current_user: User = Depends(get_current_user)):
```

### 4. Hardcoded URLs
```typescript
// ❌ WRONG
fetch('http://localhost:8000/api/auth/login')

// ✅ CORRECT
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
```

## Reference Examples
- **API Client**: `app/ui/src/lib/api.ts` - Complete centralized implementation
- **Login Component**: `app/ui/src/app/login/page.tsx` - Proper auth usage
- **Backend Auth**: `app/api/auth.py` - JWT endpoints and validation
- **Protected Route**: `app/api/agents.py` - Auth dependency pattern

## Quick Testing
```bash
# Check for inconsistent token keys
grep -r "localStorage.*token" app/ui/src/ | grep -v access_token

# Find unprotected endpoints
grep -r "@router\." app/api/ | grep -v "get_current_user"
```

## Integration Checklist
- [ ] Use `access_token` key consistently everywhere
- [ ] Import from centralized API client (`app/ui/src/lib/api.ts`)
- [ ] Add `Depends(get_current_user)` to protected endpoints
- [ ] Match LoginRequest interface exactly between frontend/backend
- [ ] Use environment variables for API URLs
- [ ] Test both successful and failed auth flows

**Memory Aid**: "One token key, centralized API client, automatic auth handling, protected endpoints."
