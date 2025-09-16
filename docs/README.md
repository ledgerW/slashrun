# SlashRun

**AI-Powered Simulation Platform for Research and Wargaming**

SlashRun is a sophisticated simulation platform designed for political/policy research, social research, and geopolitical wargaming. It leverages advanced AI agents built with LangGraph to create realistic, dynamic simulations with complex multi-agent interactions.

## 🎯 Overview

SlashRun enables researchers, analysts, and decision-makers to:

- **Simulate Complex Scenarios**: Model diplomatic meetings, policy negotiations, social dynamics, and geopolitical situations
- **Deploy AI Personas**: Create detailed agent personas with realistic behavioral patterns and decision-making processes  
- **Access Real-World Data**: Integrate live data from GDELT, World Bank, UN Data, FRED, and news sources
- **Coordinate Multi-Agent Systems**: Manage turn-based execution with conflict resolution for simultaneous actions
- **Analyze Outcomes**: Track agent interactions, decisions, and scenario progression over time

### Key Features

- 🚀 **Next-Gen AI Models**: GPT-5 with advanced reasoning parameters and Claude Sonnet 4 integration
- 🤖 **Advanced AI Agents**: LangGraph-powered agents with dynamic persona injection and memory management
- ⚙️ **Centralized Model Configuration**: Easily configurable LLM models with custom parameters
- 🔐 **Secure API Key Management**: Encrypted storage and centralized configuration in settings
- 🌐 **External Data Integration**: Real-time access to global economic, political, and social datasets
- 🎮 **Turn-Based Execution**: Sophisticated coordination system for multi-agent scenarios
- 🧠 **Memory Systems**: Both short-term (conversation) and long-term (semantic) memory with vector search
- 🎨 **Modern UI**: Palantir-inspired dark theme with real-time monitoring and control
- 🐳 **Containerized**: Full Docker setup for easy deployment and scaling
- 📊 **RESTful API**: Complete API for programmatic access and integration
- 🧪 **Comprehensive Testing**: Full test suite with economic scenario validation and API testing

## 🧪 Testing

SlashRun includes a comprehensive dual testing architecture that separates unit testing from scenario validation.

### Test Architecture

**Unit Tests** - Standalone functionality validation
- ✅ **No Service Required**: Tests run independently without needing the API server
- ✅ **In-Memory Database**: Each test uses a clean SQLite in-memory database for isolation
- ✅ **Mock External APIs**: No external API calls during testing - all data is mocked
- ✅ **Fast Execution**: Complete test suite runs in seconds due to in-memory operations

**Scenario Tests** - Economic realism validation through dedicated framework
- ✅ **YAML Configuration**: Scenarios defined in human-readable YAML format
- ✅ **Economic Validation**: Taylor Rule compliance, Phillips Curve analysis, realistic bounds
- ✅ **Audit Analysis**: Complete field-level change tracking and economic relationship verification
- ✅ **Realism Scoring**: Automated assessment of economic behavior quality (0.85-0.92 scores achieved)

### Unit Test Suite Structure

**1. Configuration Tests** (`backend/tests/conftest.py`)
```python
# Provides fixtures for:
- Async database sessions (SQLite in-memory)
- HTTP test clients (FastAPI TestClient)  
- Authentication headers (JWT tokens)
- Sample economic data and state fixtures
```

**2. API Endpoint Tests** (`backend/tests/test_api.py`)
```python
# Tests core API functionality:
- Health checks and version info
- User registration and authentication
- Scenario CRUD operations
- Simulation execution workflows
- Template generation (MVS/FIS)
```

**3. Database Tests** (`backend/tests/test_database.py`)
```python
# Validates data persistence:
- User model operations
- Scenario JSON state storage/retrieval
- Audit trail chain integrity
- Trigger system storage
- Database constraints and relationships
```

**4. Simulation Core Tests** (`backend/tests/test_simulation_core.py`)
```python
# Tests standalone simulation components:
- Monetary policy reducers (Taylor Rule, FX Peg)
- Fiscal policy mechanisms (debt dynamics, wealth tax)
- Trade and external sector updates
- Trigger condition evaluation and action application
- Audit system functionality
- Economic calculation accuracy
```

### Scenario Testing Framework

The scenario testing framework validates economic realism through dedicated tooling in the `scenarios/` directory:

**Framework Structure:**
```
scenarios/
├── definitions/          # YAML scenario configurations
│   ├── simple/          # Basic single-variable scenarios
│   ├── medium/          # Multi-variable scenarios  
│   └── complex/         # Full crisis scenarios
├── runner.py           # Scenario execution engine
├── analyzer.py         # Economic realism analysis
└── reports/            # Generated analysis reports
```

**Scenario Types:**
- **Simple**: Single-country basic simulations (inflation targeting, policy shocks)
- **Medium**: Multi-country interactions (trade wars, currency crises, supply chain disruptions)
- **Complex**: Multi-dimensional geopolitical scenarios (conflicts, financial crises, coordinated policy responses)

### Running Tests

**Python Test Runner** (Recommended)
```bash
# Install dependencies and run all tests
python run_tests.py

# Run specific test categories
python run_tests.py simple     # Simple economic scenarios
python run_tests.py medium     # Multi-country interactions  
python run_tests.py complex    # Geopolitical scenarios
python run_tests.py api        # API endpoint tests
python run_tests.py database   # Database operation tests

# Special execution modes
python run_tests.py fast       # Skip slow tests
python run_tests.py coverage   # Generate HTML coverage report
```

**Direct pytest Commands**
```bash
# Install dev dependencies first
uv sync --dev

# Run all unit tests with verbose output
uv run pytest backend/tests/ -v

# Run specific unit test files
uv run pytest backend/tests/test_simulation_core.py -v
uv run pytest backend/tests/test_api.py -v
uv run pytest backend/tests/test_database.py -v

# Run with coverage reporting
uv run pytest --cov=backend/app --cov-report=html backend/tests/

# Run fast tests only (skip slow markers)
uv run pytest -m "not slow" backend/tests/

# Run tests matching pattern
uv run pytest -k "test_taylor" backend/tests/
```

**Scenario Testing Commands**
```bash
# Run scenario tests (dedicated framework)
cd scenarios

# Run all scenarios
uv run python runner.py --all

# Run specific scenarios
uv run python runner.py definitions/simple/single_country_basic.yaml
uv run python runner.py definitions/medium/trade_war.yaml

# Analyze scenario results
uv run python analyzer.py
uv run python analyzer.py reports/audit_scenario_name.json
```

**Bash Script** (Alternative)
```bash
# Make executable and run
chmod +x run_tests.sh
./run_tests.sh
```

### Test Data Sources

**Mock Economic Data**
- Realistic GDP, inflation, unemployment figures based on actual country data
- Historical trade relationships (US-China bilateral trade volumes)
- Monetary policy parameters (Taylor rule coefficients, policy rates)
- Financial crisis scenarios based on 2008-2009 and European debt crisis patterns

**Sample Fixtures**
```python
# Example: US-China trade scenario data
sample_mvs_state = {
    "countries": {
        "USA": {"gdp": 23000000, "inflation": 0.025, "policy_rate": 0.05},
        "CHN": {"gdp": 17700000, "inflation": 0.021, "policy_rate": 0.035}
    },
    "trade_matrix": {"USA": {"CHN": 120000}, "CHN": {"USA": 450000}}
}
```

### Test Configuration

**pytest.ini Options** (in pyproject.toml)
```toml
[tool.pytest.ini_options]
testpaths = ["backend/tests"]
asyncio_mode = "auto"           # Automatic async test handling
addopts = ["-v", "--cov=backend/app", "--cov-report=html"]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests"
]
```

**Dependencies Required**
- `pytest>=7.4.0` - Test framework
- `pytest-asyncio>=0.21.0` - Async test support
- `pytest-cov>=4.1.0` - Coverage reporting
- `httpx` - HTTP client for API testing
- `sqlmodel` - Database ORM for test fixtures

The test suite ensures SlashRun's economic simulation engine works correctly across all complexity levels, from basic single-country scenarios to sophisticated multi-dimensional geopolitical simulations.

### 📋 Detailed Scenario Walkthroughs

For comprehensive step-by-step walkthroughs of each test scenario with plain language descriptions, state evolution tables, and audit trail visualizations, see:

**➡️ [SCENARIO_WALKTHROUGHS.md](./SCENARIO_WALKTHROUGHS.md)**

This document provides detailed breakdowns of all 8 test scenarios showing:
- **Timeline progression** (t=0, t=1, t=2, etc.) with exact state changes
- **Trigger events** and their economic rationale  
- **Audit trail details** with field-level change tracking
- **Expected outcomes** and validation logic
- **Economic realism** checks and policy transmission mechanisms

Perfect for understanding how complex economic phenomena are modeled and tested in SlashRun.
