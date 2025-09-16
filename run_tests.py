#!/usr/bin/env python3
"""
SlashRun Test Suite Runner
This Python script runs the comprehensive pytest test suite for the economic simulation API.
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import List, Optional


def run_command(cmd: List[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            cmd, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=Path.cwd()
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    """Main test runner function."""
    print("🧪 SlashRun Test Suite Runner")
    print("=" * 40)
    
    # Ensure we're in the correct directory
    if not Path("backend/tests").exists():
        print("❌ Error: backend/tests directory not found!")
        print("Make sure you're running this from the project root.")
        sys.exit(1)
    
    # Install dev dependencies
    if not run_command(["uv", "sync", "--dev"], "Installing dev dependencies"):
        sys.exit(1)
    
    # Parse command line arguments for test selection
    test_args = []
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg == "core":
                test_args.extend(["backend/tests/test_simulation_core.py", "-v"])
            elif arg == "api":
                test_args.extend(["backend/tests/test_api.py", "-v"]) 
            elif arg == "database":
                test_args.extend(["backend/tests/test_database.py", "-v"])
            elif arg == "coverage":
                test_args.extend(["--cov=backend/app", "--cov-report=html"])
            elif arg == "fast":
                test_args.extend(["-m", "not slow"])
            else:
                test_args.append(arg)
    
    # Default: run all tests
    if not test_args:
        test_args = ["backend/tests/", "-v"]
    
    # Run pytest with specified arguments
    cmd = ["uv", "run", "pytest"] + test_args
    print(f"🚀 Running: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=False)
        exit_code = result.returncode
        
        print()
        if exit_code == 0:
            print("✅ All tests passed!")
        else:
            print(f"❌ Tests failed with exit code {exit_code}")
        
        print()
        print("📊 Additional commands:")
        print("   • Core simulation: python run_tests.py core")
        print("   • API tests: python run_tests.py api")
        print("   • Database tests: python run_tests.py database")
        print("   • Fast tests (no slow): python run_tests.py fast")
        print("   • With coverage: python run_tests.py coverage")
        print()
        print("📋 Scenario Testing (dedicated framework):")
        print("   • cd scenarios && uv run python runner.py --all")
        print("   • cd scenarios && uv run python analyzer.py")
        
        if Path("coverage_html/index.html").exists():
            print("📈 Coverage report: coverage_html/index.html")
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n🛑 Test execution interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
