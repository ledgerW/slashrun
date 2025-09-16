#!/usr/bin/env python3
"""
SlashRun Test Suite Runner
This Python script runs both unit tests (fast, SQLite) and integration tests (slow, PostgreSQL).
"""

import os
import subprocess
import sys
import time
import requests
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


def check_docker_compose():
    """Check if Docker Compose services are running and healthy."""
    try:
        # Check running containers with health status
        result = subprocess.run(["docker", "compose", "ps", "--format", "json"], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode != 0:
            print(f"   Docker compose ps failed: {result.stderr}")
            return False, {}
        
        if not result.stdout.strip():
            print("   No Docker Compose containers found")
            return False, {}
            
        # Parse JSON output to check for running services
        import json
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                try:
                    containers.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        running_services = [c['Service'] for c in containers if c.get('State') == 'running']
        health_status = {c['Service']: c.get('Health', 'unknown') for c in containers}
        
        print(f"   Found running services: {running_services}")
        if health_status:
            print(f"   Health status: {health_status}")
        
        # Check if required services are running
        services_running = 'db' in running_services and 'backend' in running_services
        
        # Check health status if available
        db_healthy = health_status.get('db', 'unknown') in ['healthy', 'unknown']
        backend_healthy = health_status.get('backend', 'unknown') in ['healthy', 'unknown']
        
        return services_running and db_healthy and backend_healthy, health_status
        
    except Exception as e:
        print(f"   Docker compose check failed: {e}")
        return False, {}


def check_postgresql():
    """Check if PostgreSQL is accessible."""
    try:
        import psycopg
        conn = psycopg.connect(
            host="localhost", 
            port=5432, 
            dbname="slashrun", 
            user="postgres", 
            password="postgres",
            connect_timeout=5
        )
        conn.close()
        print("   ✅ PostgreSQL connection successful")
        return True
    except ImportError:
        print("   ❌ psycopg module not found - install with: uv add psycopg")
        return False
    except Exception as e:
        print(f"   ❌ PostgreSQL connection failed: {e}")
        return False


def check_api_server():
    """Check if API server is responding."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ API server responding")
            return True
        else:
            print(f"   ❌ API server returned {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ API server connection failed: {e}")
        return False


def start_docker_services():
    """Start Docker Compose services."""
    print("🚀 Starting Docker Compose services...")
    try:
        result = subprocess.run(["docker", "compose", "up", "-d"], 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            print(f"❌ Failed to start services: {result.stderr}")
            return False
            
        print("✅ Docker Compose services started")
        print("⏳ Waiting for services to be ready...")
        time.sleep(10)
        return True
        
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        return False


def run_integration_tests():
    """Run integration tests against Docker Compose services."""
    print("🧪 Running integration tests (PostgreSQL + HTTP)...")
    print("=" * 50)
    
    # Check if services are running
    services_ready, health_status = check_docker_compose()
    if not services_ready:
        print("⚠️  Services not running, attempting to start...")
        if not start_docker_services():
            print("❌ Could not start Docker Compose services")
            return False
    
    # Wait for services to be ready with improved monitoring
    max_attempts = 45  # Increased from 30 to allow more startup time
    print("⏳ Waiting for services to be healthy...")
    
    for attempt in range(max_attempts):
        services_ready, health_status = check_docker_compose()
        postgresql_ready = check_postgresql()
        api_ready = check_api_server()
        
        if services_ready and postgresql_ready and api_ready:
            print("✅ All services are ready and healthy!")
            break
        
        if attempt < max_attempts - 1:
            print(f"   Waiting for services... ({attempt + 1}/{max_attempts})")
            if health_status:
                unhealthy = [svc for svc, status in health_status.items() if status not in ['healthy', 'unknown']]
                if unhealthy:
                    print(f"   Unhealthy services: {unhealthy}")
            time.sleep(3)  # Increased from 2 seconds
    else:
        print("❌ Services not ready after waiting")
        print("💡 Try running: docker-compose logs backend")
        return False
    
    # Set PYTHONPATH to include current directory for proper imports
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd()) + ":" + env.get("PYTHONPATH", "")
    
    # Run integration tests
    cmd = ["uv", "run", "pytest", "backend/tests/test_api_integration.py", "-v", "--tb=short"]
    
    try:
        result = subprocess.run(cmd, env=env, timeout=300)  # 5 minute timeout
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Integration tests timed out")
        return False


def run_unit_tests():
    """Run unit tests with SQLite in-memory database."""
    print("🧪 Running unit tests (SQLite in-memory)...")
    print("=" * 50)
    
    # Set PYTHONPATH to include current directory for proper imports
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd()) + ":" + env.get("PYTHONPATH", "")
    
    cmd = [
        "uv", "run", "pytest",
        "backend/tests/",
        "--ignore=backend/tests/test_api_integration.py",  # Exclude integration tests
        "-v", "--tb=short",
        "--cov=backend/app",
        "--cov-report=html:coverage_html",
        "--cov-report=term-missing"
    ]
    
    try:
        result = subprocess.run(cmd, env=env, timeout=180)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Unit tests timed out")
        return False


def main():
    """Main test runner function."""
    print("🏁 SlashRun Test Suite Runner")
    print("=" * 50)
    
    # Ensure we're in the correct directory
    if not Path("backend/tests").exists():
        print("❌ Error: backend/tests directory not found!")
        print("Make sure you're running this from the project root.")
        sys.exit(1)
    
    # Install dev dependencies
    if not run_command(["uv", "sync", "--dev"], "Installing dev dependencies"):
        sys.exit(1)
    
    # Parse command line arguments
    run_integration = False
    run_units = True  # Default to unit tests
    test_args = []
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg == "integration":
                run_integration = True
                run_units = False
            elif arg == "unit":
                run_units = True
                run_integration = False
            elif arg == "all":
                run_units = True
                run_integration = True
            elif arg == "core":
                test_args.extend(["backend/tests/test_simulation_core.py", "-v"])
                run_units = True
                run_integration = False
            elif arg == "api":
                test_args.extend(["backend/tests/test_api.py", "-v"])
                run_units = True
                run_integration = False
            elif arg == "database":
                test_args.extend(["backend/tests/test_database.py", "-v"])
                run_units = True
                run_integration = False
            elif arg == "coverage":
                test_args.extend(["--cov=backend/app", "--cov-report=html"])
            elif arg == "fast":
                test_args.extend(["-m", "not slow"])
            else:
                test_args.append(arg)
    
    success = True
    
    # Run unit tests
    if run_units:
        if test_args:
            # Run specific unit tests
            cmd = ["uv", "run", "pytest"] + test_args
            print(f"🚀 Running specific tests: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=False)
            success = result.returncode == 0
        else:
            success = run_unit_tests()
            if success:
                print("✅ Unit tests passed!")
            else:
                print("❌ Unit tests failed!")
    
    # Run integration tests
    if run_integration and success:  # Only run if unit tests passed
        integration_success = run_integration_tests()
        if integration_success:
            print("✅ Integration tests passed!")
        else:
            print("❌ Integration tests failed!")
            success = False
    
    # Final summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    # Show usage info
    print("\n📊 Usage:")
    print("   • Unit tests only:        python run_tests.py unit")
    print("   • Integration tests only: python run_tests.py integration")
    print("   • Both test types:        python run_tests.py all")
    print("   • Specific test files:    python run_tests.py core|api|database")
    print("   • With coverage:          python run_tests.py coverage")
    print("   • Fast tests only:        python run_tests.py fast")
    print("\n📋 Scenario Testing (dedicated framework):")
    print("   • cd scenarios && uv run python runner.py --all")
    print("   • cd scenarios && uv run python analyzer.py")
    
    if Path("coverage_html/index.html").exists():
        print("\n📈 Coverage report: coverage_html/index.html")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
