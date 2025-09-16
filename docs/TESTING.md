# SlashRun Testing Guide

This guide explains how to run different types of tests for the SlashRun economic simulation application.

## Test Types

### Unit Tests (Fast, Isolated)
- **Database**: SQLite in-memory database
- **HTTP Client**: ASGI transport (no network calls)
- **Speed**: Fast (~30 seconds)
- **Purpose**: Test business logic, models, and API endpoints in isolation
- **Coverage**: Code coverage reports generated

### Integration Tests (Slow, Real Environment)
- **Database**: PostgreSQL running in Docker Compose
- **HTTP Client**: Real HTTP requests to localhost:8000
- **Speed**: Slower (~2-3 minutes)
- **Purpose**: Test full stack integration, database persistence, and API integration
- **Coverage**: End-to-end functionality validation

## Quick Commands

### Run Unit Tests Only
```bash
# Fast unit tests with SQLite
python run_tests.py unit

# Or using uv directly
uv run pytest backend/tests/ --ignore=backend/tests/test_api_integration.py -v
```

### Run Integration Tests Only
```bash
# Integration tests against Docker Compose (starts services automatically)
python run_tests.py integration

# Or using uv directly (requires Docker Compose running)
uv run pytest backend/tests/test_api_integration.py -v
```

### Run All Tests
```bash
# Run unit tests first, then integration tests
python run_tests.py all
```

### Run Specific Test Categories
```bash
# Core simulation tests
python run_tests.py core

# API endpoint tests
python run_tests.py api

# Database model tests
python run_tests.py database

# Tests with coverage report
python run_tests.py coverage

# Fast tests only (excludes slow external API calls)
python run_tests.py fast
```

## Integration Test Requirements

### Prerequisites
1. **Docker Compose**: Services must be running
   ```bash
   docker compose up -d
   ```

2. **PostgreSQL**: Database accessible at localhost:5432
3. **API Server**: Backend accessible at localhost:8000

### Automatic Service Management
The `python run_tests.py integration` command will:
- Check if Docker Compose services are running
- Start services automatically if needed
- Wait for services to be ready
- Verify PostgreSQL and API connectivity

## Test Configuration Files

### Unit Test Configuration
- **File**: `backend/tests/conftest.py`
- **Database**: `sqlite+aiosqlite:///:memory:`
- **Client**: `AsyncClient` with `ASGITransport`
- **Fixtures**: `client`, `test_user`, `auth_headers`

### Integration Test Configuration
- **File**: `backend/tests/conftest_integration.py`
- **Database**: `postgresql+asyncpg://postgres:postgres@localhost:5432/slashrun_test`
- **Client**: `AsyncClient` with real HTTP calls
- **Fixtures**: `integration_client`, `integration_auth_headers`

## Test Database Management

### Unit Tests
- Uses SQLite in-memory database
- Fresh database for each test function
- No cleanup needed (memory-based)

### Integration Tests
- Creates separate `slashrun_test` database
- Automatic database creation/cleanup
- Transaction rollback per test for isolation
- Separate from production `slashrun` database

## What Integration Tests Cover

### Database Integration
- ✅ PostgreSQL-specific JSON storage
- ✅ Complex nested data persistence
- ✅ Database constraints and relationships
- ✅ Multi-user data isolation

### API Integration
- ✅ Real HTTP requests/responses
- ✅ Authentication flow with PostgreSQL
- ✅ Scenario CRUD with database persistence
- ✅ Simulation step execution and state storage

### Full Stack Integration
- ✅ JWT authentication end-to-end
- ✅ User registration and login
- ✅ Protected endpoint authorization
- ✅ Multi-step simulation persistence

## Debugging Failed Tests

### Unit Test Failures
```bash
# Run with more verbose output
uv run pytest backend/tests/test_api.py::TestAuthentication::test_user_login -vvv

# Run with debugger
uv run pytest --pdb backend/tests/test_api.py::TestAuthentication::test_user_login
```

### Integration Test Failures
```bash
# Check Docker Compose status
docker compose ps

# Check PostgreSQL logs
docker compose logs db

# Check API server logs
docker compose logs backend

# Run specific integration test
uv run pytest backend/tests/test_api_integration.py::TestIntegrationAuthentication::test_user_login_integration -vvv
```

### Common Issues

#### "Docker Compose not running"
```bash
docker compose up -d
python run_tests.py integration
```

#### "PostgreSQL connection failed"
```bash
# Check if PostgreSQL port is accessible
telnet localhost 5432

# Check Docker network
docker compose ps
```

#### "API server is not responding"
```bash
# Check API server logs
docker compose logs backend

# Test API manually
curl http://localhost:8000/health
```

## Environment Variables

### Test Environment Variables (Unit Tests)
```bash
DATABASE_URL="sqlite+aiosqlite:///:memory:"
SECRET_KEY="test-secret-key-for-testing-only"
JWT_SECRET_KEY="test-jwt-secret-key-for-testing-only"
ENVIRONMENT="test"
```

### Integration Test Environment Variables
- Uses Docker Compose `.env` file
- PostgreSQL connection: `postgresql+asyncpg://postgres:postgres@db:5432/slashrun`
- Test database: `postgresql+asyncpg://postgres:postgres@localhost:5432/slashrun_test`

## CI/CD Considerations

### Development Workflow
1. **Fast feedback**: Run unit tests during development
2. **Pre-commit**: Unit tests in git hooks
3. **PR validation**: Both unit and integration tests
4. **Production deployment**: Integration tests as smoke tests

### GitHub Actions Example
```yaml
# Unit tests (fast)
- name: Run Unit Tests
  run: python run_tests.py unit

# Integration tests (slower)
- name: Start Docker Compose
  run: docker compose up -d
  
- name: Run Integration Tests
  run: python run_tests.py integration
```

## Performance Benchmarks

### Unit Tests
- **Time**: ~30 seconds
- **Tests**: ~54 tests
- **Database**: SQLite in-memory
- **Coverage**: Business logic and API contracts

### Integration Tests
- **Time**: ~2-3 minutes
- **Tests**: ~15 comprehensive integration tests
- **Database**: PostgreSQL with full persistence
- **Coverage**: End-to-end workflows

## Adding New Tests

### Adding Unit Tests
1. Add to existing test files in `backend/tests/`
2. Use fixtures from `conftest.py`
3. Mock external dependencies
4. Focus on business logic testing

### Adding Integration Tests
1. Add to `backend/tests/test_api_integration.py`
2. Use fixtures from `conftest_integration.py`
3. Test real database interactions
4. Verify full request/response cycles
5. Use `@requires_docker_compose` decorator

## Test Data Management

### Unit Test Data
- Fixtures create minimal test data
- In-memory database is reset per test
- Sample states and triggers provided

### Integration Test Data
- Tests create and clean up their own data
- Database transactions rolled back per test
- Realistic data scenarios for complex testing
- User isolation verified

## Monitoring and Maintenance

### Regular Checks
- Unit tests should run in < 1 minute
- Integration tests should complete successfully
- Coverage reports should be generated
- All fixtures should work correctly

### Troubleshooting
- Check Docker Compose health regularly
- Monitor test execution times
- Verify database connections
- Update test data as models change

---

## Summary

- **Single Test Runner**: Use `python run_tests.py` with different arguments
- **Unit Tests**: Fast, isolated, SQLite-based testing for development
- **Integration Tests**: Slow, comprehensive, PostgreSQL-based testing for confidence
- **Both are important**: Unit tests for speed, integration tests for reliability
- **Easy commands**: 
  - `python run_tests.py unit` - Fast unit tests
  - `python run_tests.py integration` - Full integration tests
  - `python run_tests.py all` - Both test types
