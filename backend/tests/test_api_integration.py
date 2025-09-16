"""Integration API tests running against actual Docker Compose PostgreSQL and HTTP server."""

import pytest
from httpx import AsyncClient

# Import integration test fixtures
from .conftest_integration import (
    integration_client, 
    integration_auth_headers, 
    integration_test_user,
    integration_db,
    sample_integration_mvs_state,
    requires_docker_compose
)


class TestIntegrationHealthAndInfo:
    """Test basic API health and info endpoints against running server."""
    
    @requires_docker_compose
    async def test_health_check_integration(self, integration_client: AsyncClient):
        """Test API health check against running Docker Compose service."""
        response = await integration_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "SlashRun Simulation API"
    
    @requires_docker_compose
    async def test_api_health_check_integration(self, integration_client: AsyncClient):
        """Test API health check with prefix against running service."""
        response = await integration_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "SlashRun Simulation API"
    
    @requires_docker_compose
    async def test_version_info_integration(self, integration_client: AsyncClient):
        """Test API version endpoint against running service."""
        response = await integration_client.get("/version")
        assert response.status_code == 200
    
    @requires_docker_compose
    async def test_root_endpoint_integration(self, integration_client: AsyncClient):
        """Test API root endpoint against running service."""
        response = await integration_client.get("/")
        assert response.status_code == 200


class TestIntegrationAuthentication:
    """Test authentication flow against PostgreSQL database."""
    
    @requires_docker_compose
    async def test_user_registration_integration(self, integration_client: AsyncClient):
        """Test user registration against PostgreSQL database."""
        import time
        # Use timestamp to ensure unique user
        timestamp = int(time.time())
        user_data = {
            "email": f"newintegrationuser{timestamp}@example.com",
            "password": "securepassword123",
            "username": f"newintegrationuser{timestamp}",
            "full_name": "New Integration User"
        }
        response = await integration_client.post("/api/users/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "password" not in data
        assert "id" in data
    
    @requires_docker_compose
    async def test_user_login_integration(self, integration_client: AsyncClient):
        """Test user login against PostgreSQL database."""
        # First register a user
        user_data = {
            "email": "loginintegrationuser@example.com",
            "password": "loginpassword123",
            "username": "loginintegrationuser",
            "full_name": "Login Integration User"
        }
        await integration_client.post("/api/users/register", json=user_data)
        
        # Then login
        response = await integration_client.post("/api/auth/login/form", data={
            "username": user_data["email"],
            "password": user_data["password"]
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
        assert data["user_id"] is not None
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
    
    @requires_docker_compose
    async def test_get_current_user_integration(self, integration_client: AsyncClient, integration_auth_headers):
        """Test getting current user info from PostgreSQL."""
        response = await integration_client.get("/api/users/profile", headers=integration_auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Note: We now use admin user for auth, so check for admin or fallback test user
        assert data["email"] in ["admin@slashrun.com", "integration_auth@example.com"]
        assert data["username"] in ["admin", "integration_authuser"]
        assert "id" in data
    
    @requires_docker_compose
    async def test_protected_endpoint_without_auth_integration(self, integration_client: AsyncClient):
        """Test that protected endpoints require authentication."""
        response = await integration_client.get("/api/users/profile")
        assert response.status_code == 403  # FastAPI returns 403 for missing auth
    
    @requires_docker_compose
    async def test_update_current_user_integration(self, integration_client: AsyncClient, integration_auth_headers):
        """Test updating current user info in PostgreSQL."""
        update_data = {
            "full_name": "Updated Integration User Name",
            "bio": "Updated integration bio"
        }
        response = await integration_client.put("/api/users/profile", json=update_data, headers=integration_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Integration User Name"
        assert data["bio"] == "Updated integration bio"
    
    @requires_docker_compose
    async def test_change_password_integration(self, integration_client: AsyncClient):
        """Test changing user password in PostgreSQL using dedicated test user."""
        # Create a dedicated test user for password change testing
        import time
        timestamp = int(time.time())
        user_data = {
            "email": f"passwordtestuser{timestamp}@example.com",
            "password": "originalpassword123",
            "username": f"passwordtestuser{timestamp}",
            "full_name": "Password Test User"
        }
        
        # Register the test user
        register_response = await integration_client.post("/api/users/register", json=user_data)
        assert register_response.status_code == 201
        
        # Login to get auth headers for this specific user
        login_response = await integration_client.post("/api/auth/login/form", data={
            "username": user_data["email"],
            "password": user_data["password"]
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert login_response.status_code == 200
        
        test_user_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        # Now change the password using the dedicated test user
        password_data = {
            "current_password": "originalpassword123",
            "new_password": "newintegrationpass123"
        }
        response = await integration_client.post("/api/users/change-password", json=password_data, headers=test_user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Verify we can login with the new password
        new_login_response = await integration_client.post("/api/auth/login/form", data={
            "username": user_data["email"],
            "password": "newintegrationpass123"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert new_login_response.status_code == 200
    
    @requires_docker_compose
    async def test_logout_integration(self, integration_client: AsyncClient, integration_auth_headers):
        """Test user logout."""
        response = await integration_client.post("/api/auth/logout", headers=integration_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestIntegrationScenarioManagement:
    """Test scenario CRUD operations against PostgreSQL database."""
    
    @requires_docker_compose
    async def test_create_scenario_integration(self, integration_client: AsyncClient, integration_auth_headers, sample_integration_mvs_state):
        """Test creating a new scenario in PostgreSQL."""
        scenario_data = {
            "name": "Integration Test Scenario",
            "description": "A test economic scenario for integration testing",
            "initial_state": sample_integration_mvs_state,
            "triggers": []
        }
        response = await integration_client.post(
            "/api/simulation/scenarios",
            json=scenario_data,
            headers=integration_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == scenario_data["name"]
        assert data["description"] == scenario_data["description"]
        assert data["current_timestep"] == 0
        assert "id" in data
        assert data["current_state"]["t"] == 0
        assert "countries" in data["current_state"]
        return data["id"]
    
    @requires_docker_compose
    async def test_list_scenarios_integration(self, integration_client: AsyncClient, integration_auth_headers, sample_integration_mvs_state):
        """Test listing user scenarios from PostgreSQL."""
        # Create a scenario first
        scenario_id = await self.test_create_scenario_integration(integration_client, integration_auth_headers, sample_integration_mvs_state)
        
        response = await integration_client.get("/api/simulation/scenarios", headers=integration_auth_headers)
        assert response.status_code == 200
        scenarios = response.json()
        assert len(scenarios) >= 1
        
        # Find our created scenario
        created_scenario = next((s for s in scenarios if s["id"] == scenario_id), None)
        assert created_scenario is not None
        assert created_scenario["name"] == "Integration Test Scenario"
    
    @requires_docker_compose
    async def test_get_scenario_integration(self, integration_client: AsyncClient, integration_auth_headers, sample_integration_mvs_state):
        """Test getting a specific scenario from PostgreSQL."""
        scenario_id = await self.test_create_scenario_integration(integration_client, integration_auth_headers, sample_integration_mvs_state)
        
        response = await integration_client.get(
            f"/api/simulation/scenarios/{scenario_id}",
            headers=integration_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == scenario_id
        assert data["name"] == "Integration Test Scenario"
        assert "current_state" in data
        assert "countries" in data["current_state"]
    
    @requires_docker_compose
    async def test_update_scenario_integration(self, integration_client: AsyncClient, integration_auth_headers, sample_integration_mvs_state):
        """Test updating scenario metadata in PostgreSQL."""
        scenario_id = await self.test_create_scenario_integration(integration_client, integration_auth_headers, sample_integration_mvs_state)
        
        update_data = {
            "name": "Updated Integration Test Scenario",
            "description": "Updated description for integration testing"
        }
        response = await integration_client.put(
            f"/api/simulation/scenarios/{scenario_id}",
            json=update_data,
            headers=integration_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Integration Test Scenario"
        assert data["description"] == "Updated description for integration testing"
    
    @requires_docker_compose
    async def test_delete_scenario_integration(self, integration_client: AsyncClient, integration_auth_headers, sample_integration_mvs_state):
        """Test deleting a scenario from PostgreSQL."""
        scenario_id = await self.test_create_scenario_integration(integration_client, integration_auth_headers, sample_integration_mvs_state)
        
        response = await integration_client.delete(
            f"/api/simulation/scenarios/{scenario_id}",
            headers=integration_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        
        # Verify scenario is deleted
        get_response = await integration_client.get(
            f"/api/simulation/scenarios/{scenario_id}",
            headers=integration_auth_headers
        )
        assert get_response.status_code == 404


class TestIntegrationSimulationExecution:
    """Test simulation step execution against PostgreSQL database."""
    
    @requires_docker_compose
    async def test_simulation_step_integration(self, integration_client: AsyncClient, integration_auth_headers, sample_integration_mvs_state):
        """Test executing a simulation step with PostgreSQL persistence."""
        # Create scenario
        scenario_data = {
            "name": "Step Integration Test Scenario",
            "description": "Test simulation stepping with PostgreSQL",
            "initial_state": sample_integration_mvs_state,
            "triggers": []
        }
        response = await integration_client.post(
            "/api/simulation/scenarios",
            json=scenario_data,
            headers=integration_auth_headers
        )
        scenario_id = response.json()["id"]
        
        # Execute simulation step
        response = await integration_client.post(
            f"/api/simulation/scenarios/{scenario_id}/step",
            headers=integration_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["timestep"] == 1
        assert "state" in data
        assert "audit" in data
        assert data["audit"]["timestep"] == 1
        assert len(data["audit"]["field_changes"]) > 0
        
        # Verify state persisted in database
        get_response = await integration_client.get(
            f"/api/simulation/scenarios/{scenario_id}",
            headers=integration_auth_headers
        )
        assert get_response.status_code == 200
        scenario_data = get_response.json()
        assert scenario_data["current_timestep"] == 1
        assert scenario_data["current_state"]["t"] == 1
    
    @requires_docker_compose
    async def test_get_simulation_state_integration(self, integration_client: AsyncClient, integration_auth_headers, sample_integration_mvs_state):
        """Test getting simulation state at specific timestep from PostgreSQL."""
        # Create and step scenario
        scenario_data = {
            "name": "State Integration Test Scenario",
            "initial_state": sample_integration_mvs_state,
            "triggers": []
        }
        response = await integration_client.post(
            "/api/simulation/scenarios",
            json=scenario_data,
            headers=integration_auth_headers
        )
        scenario_id = response.json()["id"]
        
        # Step once
        await integration_client.post(f"/api/simulation/scenarios/{scenario_id}/step", headers=integration_auth_headers)
        
        # Get state at timestep 1
        response = await integration_client.get(
            f"/api/simulation/scenarios/{scenario_id}/states/1",
            headers=integration_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["timestep"] == 1
        assert "state" in data
        assert data["state"]["t"] == 1
    
    @requires_docker_compose 
    async def test_multiple_simulation_steps_integration(self, integration_client: AsyncClient, integration_auth_headers, sample_integration_mvs_state):
        """Test executing multiple simulation steps with PostgreSQL persistence."""
        # Create scenario
        scenario_data = {
            "name": "Multi-Step Integration Test",
            "initial_state": sample_integration_mvs_state,
            "triggers": []
        }
        response = await integration_client.post(
            "/api/simulation/scenarios",
            json=scenario_data,
            headers=integration_auth_headers
        )
        scenario_id = response.json()["id"]
        
        # Execute multiple steps
        for step in range(1, 4):
            response = await integration_client.post(
                f"/api/simulation/scenarios/{scenario_id}/step",
                headers=integration_auth_headers
            )
            assert response.status_code == 200
            data = response.json()
            assert data["timestep"] == step
            assert data["state"]["t"] == step
        
        # Verify final state
        get_response = await integration_client.get(
            f"/api/simulation/scenarios/{scenario_id}",
            headers=integration_auth_headers
        )
        final_data = get_response.json()
        assert final_data["current_timestep"] == 3
        assert final_data["current_state"]["t"] == 3


class TestIntegrationTriggerExamples:
    """Test trigger examples endpoint against running service."""
    
    @requires_docker_compose
    async def test_trigger_examples_integration(self, integration_client: AsyncClient):
        """Test trigger examples endpoint against running service."""
        response = await integration_client.get("/api/simulation/triggers/examples")
        assert response.status_code == 200
        examples = response.json()
        assert len(examples) > 0
        
        # Verify structure of first example
        first_example = list(examples.values())[0]
        assert "name" in first_example
        assert "condition" in first_example
        assert "action" in first_example


class TestIntegrationDatabaseConsistency:
    """Test database consistency and PostgreSQL-specific features."""
    
    @requires_docker_compose
    async def test_concurrent_user_scenarios_integration(self, integration_client: AsyncClient, sample_integration_mvs_state):
        """Test that different users can't see each other's scenarios."""
        # Create two different users
        user1_data = {
            "email": "user1@integration.com",
            "password": "password123",
            "username": "user1",
            "full_name": "User One"
        }
        user2_data = {
            "email": "user2@integration.com", 
            "password": "password123",
            "username": "user2",
            "full_name": "User Two"
        }
        
        # Register both users
        await integration_client.post("/api/users/register", json=user1_data)
        await integration_client.post("/api/users/register", json=user2_data)
        
        # Get auth headers for both users
        user1_login = await integration_client.post("/api/auth/login/form", data={
            "username": user1_data["email"],
            "password": user1_data["password"]
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        user1_headers = {"Authorization": f"Bearer {user1_login.json()['access_token']}"}
        
        user2_login = await integration_client.post("/api/auth/login/form", data={
            "username": user2_data["email"],
            "password": user2_data["password"]
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        user2_headers = {"Authorization": f"Bearer {user2_login.json()['access_token']}"}
        
        # User1 creates a scenario
        scenario_data = {
            "name": "User1's Private Scenario",
            "initial_state": sample_integration_mvs_state,
            "triggers": []
        }
        user1_scenario_response = await integration_client.post(
            "/api/simulation/scenarios",
            json=scenario_data,
            headers=user1_headers
        )
        user1_scenario_id = user1_scenario_response.json()["id"]
        
        # User2 should not see User1's scenario
        user2_scenarios = await integration_client.get("/api/simulation/scenarios", headers=user2_headers)
        user2_scenario_ids = [s["id"] for s in user2_scenarios.json()]
        assert user1_scenario_id not in user2_scenario_ids
        
        # User2 should not be able to access User1's scenario directly
        user2_access_response = await integration_client.get(
            f"/api/simulation/scenarios/{user1_scenario_id}",
            headers=user2_headers
        )
        assert user2_access_response.status_code in [403, 404]  # Forbidden or Not Found
    
    @requires_docker_compose
    async def test_postgresql_json_storage_integration(self, integration_client: AsyncClient, integration_auth_headers, sample_integration_mvs_state):
        """Test that complex JSON state is properly stored and retrieved from PostgreSQL."""
        # Create scenario with complex nested state
        complex_state = sample_integration_mvs_state.copy()
        complex_state["custom_metrics"] = {
            "financial_stability": {"score": 0.85, "components": {"banking": 0.9, "markets": 0.8}},
            "trade_flows": [{"from": "USA", "to": "CHN", "value": 120000, "growth_rate": 0.03}]
        }
        
        scenario_data = {
            "name": "PostgreSQL JSON Test",
            "initial_state": complex_state,
            "triggers": []
        }
        
        # Create scenario
        response = await integration_client.post(
            "/api/simulation/scenarios",
            json=scenario_data,
            headers=integration_auth_headers
        )
        scenario_id = response.json()["id"]
        
        # Retrieve and verify complex nested data is preserved
        get_response = await integration_client.get(
            f"/api/simulation/scenarios/{scenario_id}",
            headers=integration_auth_headers
        )
        retrieved_data = get_response.json()
        
        assert "custom_metrics" in retrieved_data["current_state"]
        assert retrieved_data["current_state"]["custom_metrics"]["financial_stability"]["score"] == 0.85
        assert retrieved_data["current_state"]["custom_metrics"]["trade_flows"][0]["value"] == 120000
