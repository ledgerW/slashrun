# SlashRun

**AI-Powered Economic Simulation Platform for Research and Wargaming**

SlashRun is a sophisticated simulation platform designed for political/policy research, social research, and geopolitical wargaming. It leverages advanced AI agents and complex economic modeling to create realistic, dynamic simulations.

## 🎯 Quick Start

```bash
# Clone and start the application
git clone https://github.com/ledgerW/slashrun.git
cd slashrun

# Start with Docker Compose
docker compose up -d

# Or run tests
uv run python run_tests.py
```

## 🚀 Key Features

- **Economic Simulation Engine**: Complex multi-country economic modeling with realistic policy transmission mechanisms
- **Scenario Testing Framework**: Comprehensive scenario definitions with YAML configurations  
- **Advanced Trigger System**: Dynamic policy interventions and regime switches during simulation
- **Audit & Analytics**: Complete field-level change tracking and economic realism validation
- **Docker Deployment**: Full containerized setup for easy deployment and scaling

## 📚 Documentation

Comprehensive documentation is available in the `docs/` folder:

- **[README.md](docs/README.md)** - Complete platform overview and setup instructions
- **[SCENARIO_CREATION_GUIDE.md](docs/SCENARIO_CREATION_GUIDE.md)** - Detailed guide for creating simulation scenarios
- **[SCENARIO_TESTING_SUMMARY.md](docs/SCENARIO_TESTING_SUMMARY.md)** - Framework implementation and validation results
- **[SCENARIO_WALKTHROUGHS.md](docs/SCENARIO_WALKTHROUGHS.md)** - Step-by-step scenario examples with analysis
- **[simulation_state.md](docs/simulation_state.md)** - Technical documentation of state models
- **[implementation_plan.md](docs/implementation_plan.md)** - Development roadmap and architecture decisions

## 🧪 Testing

SlashRun includes comprehensive testing capabilities:

### Unit Tests (Standalone Functionality)
```bash
# Test core simulation components
uv run pytest backend/tests/test_simulation_core.py -v
uv run pytest backend/tests/test_api.py -v  
uv run pytest backend/tests/test_database.py -v
```

### Scenario Testing Framework
```bash
# Test economic scenarios (dedicated framework)
cd scenarios
uv run python runner.py --all
uv run python analyzer.py  # Analyze results
```

## 📊 Architecture

- **Backend**: FastAPI with Pydantic v2 models
- **Database**: SQLModel with JSON state storage
- **Testing**: Pytest with comprehensive economic validation
- **Deployment**: Docker Compose with multi-service architecture
- **Package Management**: UV for fast dependency resolution

## 🛠 Development

```bash
# Install dependencies
uv sync --dev

# Run development server
cd backend && uv run uvicorn app.main:app --reload

# Run all tests
uv run python run_tests.py

# Generate coverage report  
uv run pytest --cov=backend/app --cov-report=html backend/tests/
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

For detailed setup instructions, API documentation, and comprehensive guides, see the **[docs/](docs/)** directory.
