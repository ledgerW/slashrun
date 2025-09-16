# API Routing Patterns & Configuration

## Critical Rule: Consistent Route Prefixes
**Backend API must use consistent path prefixes for proper organization.**

## Current Configuration

### Backend (FastAPI)
- **Configuration**: `backend/app/core/config.py`
- **API Prefix**: `api_prefix: str = "/api"`
- **Route Mounting**: Routes mounted with `app.include_router(router, prefix=settings.api_prefix)`
- **Actual Endpoints**: `/api/auth/login`, `/api/simulation/scenarios`, etc.

### Docker Compose Environment
- **Backend**: Serves on port 8000
- **Environment Variable**: Backend accessible at `http://localhost:8000`

## Route Structure Standards

### 1. Backend Route Organization
```python
# ✅ CORRECT - Backend configuration
# config.py
api_prefix: str = "/api"

# main.py  
app.include_router(auth_router, prefix=settings.api_prefix)      # /api/auth/*
app.include_router(simulation_router, prefix=settings.api_prefix) # /api/simulation/*
```

## Common Pitfalls to Avoid

### 1. Inconsistent Prefix Configuration
```python
# ❌ WRONG - Inconsistent prefixes across routers
app.include_router(auth_router, prefix="/auth")        # Missing /api
app.include_router(simulation_router, prefix="/api")   # Has /api
```

### 2. Mismatched API Versions
```python
# ❌ WRONG - Mixed API versions
api_prefix: str = "/api/v1"    # Some endpoints
# Other endpoints still use "/api"
```

### 3. Environment Variable Configuration Issues
```yaml
# ⚠️  WATCH OUT - Docker can override at runtime
environment:
  - API_PREFIX=/api/v2  # Changed at runtime without updating code
```

## Debugging Routing Issues

### 1. Verify Backend Routes
```python
# Add to main.py for debugging
@app.on_event("startup")
async def log_routes():
    for route in app.routes:
        print(f"Route: {route.path}")
```

### 2. Test Backend Directly
```bash
# Test backend endpoints directly
curl http://localhost:8000/api/simulation/scenarios
curl http://localhost:8000/health  # Health check (no /api prefix)
```

## Configuration Checklist

- [ ] Backend `api_prefix` is consistent across all routers
- [ ] Docker Compose environment variables are correct  
- [ ] No route path duplication or conflicts
- [ ] Health check and root endpoints work without prefix
- [ ] CORS configuration allows required origins

## Migration Guide

### When Changing API Prefix:
1. **Update Backend**: Modify `backend/app/core/config.py` `api_prefix`
2. **Update Tests**: Update any hardcoded API paths in tests
3. **Update Documentation**: Update API docs and examples
4. **Update Docker**: Update environment variables if needed

### Version Migration Example:
```python
# OLD - v1 API
api_prefix: str = "/api/v1" 

# NEW - Simplified API  
api_prefix: str = "/api"
```

## Reference Examples

### Complete Working Configuration:
- **Backend Config**: `api_prefix: str = "/api"`
- **Docker Backend**: Accessible at `http://localhost:8000`
- **Result**: ✅ `http://localhost:8000/api/simulation/scenarios`

### Route Testing Commands:
```bash
# Start services
docker-compose up

# Test backend health
curl http://localhost:8000/health

# Test API endpoint
curl http://localhost:8000/api/simulation/scenarios
```

**Memory Aid**: "Consistent API prefix across all backend routes, proper environment configuration."
