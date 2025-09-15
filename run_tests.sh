#!/bin/bash

# SlashRun Test Runner
# This script runs the comprehensive pytest test suite for the economic simulation API

set -e

echo "🧪 Starting SlashRun Test Suite"
echo "================================="

# Install dev dependencies if not already installed
echo "📦 Installing test dependencies..."
uv sync --dev

# Run the full test suite
echo "🚀 Running pytest test suite..."
echo ""

# Basic test run
echo "Running basic test suite:"
uv run pytest backend/tests/ -v

echo ""
echo "✅ Test suite completed!"
echo ""
echo "📊 Coverage report generated in coverage_html/"
echo "🔍 For specific test categories:"
echo "   • Simple scenarios: uv run pytest backend/tests/test_scenarios_simple.py -v"
echo "   • Medium scenarios: uv run pytest backend/tests/test_scenarios_medium.py -v" 
echo "   • Complex scenarios: uv run pytest backend/tests/test_scenarios_complex.py -v"
echo "   • API tests: uv run pytest backend/tests/test_api.py -v"
echo "   • Database tests: uv run pytest backend/tests/test_database.py -v"
echo ""
echo "🏃 To run without slow tests: uv run pytest -m 'not slow' backend/tests/"
echo "📈 For coverage only: uv run pytest --cov=backend/app backend/tests/"
