"""High-level API endpoint tests for SlashRun Simulation API."""

import pytest
from httpx import AsyncClient


class TestHealthAndInfo:
    """Test basic API health and info endpoints."""
    
    async def test_health_check(self, client: AsyncClient):
        """Test API health check."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "SlashRun Simulation API"
    
    async def test_version_info(self, client: AsyncClient):
        """Test API version endpoint."""
        response = await client.get("/version")
        assert response.status_code == 200
    
    async def test_root_endpoint(self, client: AsyncClient):
        """Test API root endpoint."""
        response = await client.get("/")
        assert response.status_code == 200


class TestAuthentication:
    """Test authentication flow."""
    
    async def test_user_registration(self, client: AsyncClient):
        """Test user registration."""
        user_data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "username": "newuser",
            "full_name": "New User"
        }
        response = await client.post("/api/v1/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "password" not in data
    
    async def test_user_login(self, client: AsyncClient, test_user):
        """Test user login."""
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = await client.post("/api/v1/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
    
    async def test_get_current_user(self, client: AsyncClient, auth_headers):
        """Test getting current user info."""
        response = await client.get("/api/v1/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
    
    async def test_protected_endpoint_without_auth(self, client: AsyncClient):
        """Test that protected endpoints require authentication."""
        response = await client.get("/api/v1/me")
        assert response.status_code == 403  # FastAPI returns 403 for missing auth
    
    async def test_update_current_user(self, client: AsyncClient, auth_headers):
        """Test updating current user info."""
        update_data = {
            "full_name": "Updated User Name",
            "bio": "Updated bio"
        }
        response = await client.put("/api/v1/me", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated User Name"
        assert data["bio"] == "Updated bio"
    
    async def test_logout(self, client: AsyncClient, auth_headers):
        """Test user logout."""
        response = await client.post("/api/v1/logout", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestScenarioManagement:
    """Test scenario CRUD operations."""
    
    async def test_create_scenario(self, client: AsyncClient, auth_headers, sample_mvs_state):
        """Test creating a new scenario."""
        scenario_data = {
            "name": "Test Scenario",
            "description": "A test economic scenario",
            "initial_state": sample_mvs_state,
            "triggers": []
        }
        response = await client.post(
            "/api/v1/simulation/scenarios",
            json=scenario_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == scenario_data["name"]
        assert data["description"] == scenario_data["description"]
        assert data["current_timestep"] == 0
        assert "id" in data
        return data["id"]
    
    async def test_list_scenarios(self, client: AsyncClient, auth_headers, sample_mvs_state):
        """Test listing user scenarios."""
        # Create a scenario first
        await self.test_create_scenario(client, auth_headers, sample_mvs_state)
        
        response = await client.get("/api/v1/simulation/scenarios", headers=auth_headers)
        assert response.status_code == 200
        scenarios = response.json()
        assert len(scenarios) >= 1
        assert scenarios[0]["name"] == "Test Scenario"
    
    async def test_get_scenario(self, client: AsyncClient, auth_headers, sample_mvs_state):
        """Test getting a specific scenario."""
        scenario_id = await self.test_create_scenario(client, auth_headers, sample_mvs_state)
        
        response = await client.get(
            f"/api/v1/simulation/scenarios/{scenario_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == scenario_id
        assert data["name"] == "Test Scenario"
    
    async def test_update_scenario(self, client: AsyncClient, auth_headers, sample_mvs_state):
        """Test updating scenario metadata."""
        scenario_id = await self.test_create_scenario(client, auth_headers, sample_mvs_state)
        
        update_data = {
            "name": "Updated Test Scenario",
            "description": "Updated description"
        }
        response = await client.put(
            f"/api/v1/simulation/scenarios/{scenario_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Test Scenario"
        assert data["description"] == "Updated description"
    
    async def test_delete_scenario(self, client: AsyncClient, auth_headers, sample_mvs_state):
        """Test deleting a scenario."""
        scenario_id = await self.test_create_scenario(client, auth_headers, sample_mvs_state)
        
        response = await client.delete(
            f"/api/v1/simulation/scenarios/{scenario_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestSimulationExecution:
    """Test simulation step execution."""
    
    async def test_simulation_step(self, client: AsyncClient, auth_headers, sample_mvs_state):
        """Test executing a simulation step."""
        # Create scenario
        scenario_data = {
            "name": "Step Test Scenario",
            "description": "Test simulation stepping",
            "initial_state": sample_mvs_state,
            "triggers": []
        }
        response = await client.post(
            "/api/v1/simulation/scenarios",
            json=scenario_data,
            headers=auth_headers
        )
        scenario_id = response.json()["id"]
        
        # Execute simulation step
        response = await client.post(
            f"/api/v1/simulation/scenarios/{scenario_id}/step",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["timestep"] == 1
        assert "state" in data
        assert "audit" in data
        assert data["audit"]["timestep"] == 1
        assert len(data["audit"]["field_changes"]) > 0
    
    async def test_get_simulation_state(self, client: AsyncClient, auth_headers, sample_mvs_state):
        """Test getting simulation state at specific timestep."""
        # Create and step scenario
        scenario_data = {
            "name": "State Test Scenario",
            "initial_state": sample_mvs_state,
            "triggers": []
        }
        response = await client.post(
            "/api/v1/simulation/scenarios",
            json=scenario_data,
            headers=auth_headers
        )
        scenario_id = response.json()["id"]
        
        # Step once
        await client.post(f"/api/v1/simulation/scenarios/{scenario_id}/step", headers=auth_headers)
        
        # Get state at timestep 1
        response = await client.get(
            f"/api/v1/simulation/scenarios/{scenario_id}/states/1",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["timestep"] == 1
        assert "state" in data


class TestTemplateGeneration:
    """Test scenario template generation."""
    
    async def test_mvs_template_generation(self, client: AsyncClient):
        """Test MVS template generation."""
        response = await client.post("/api/v1/simulation/templates/mvs")
        assert response.status_code == 200
        data = response.json()
        assert "template_type" in data
        assert "state" in data
        assert "countries" in data["state"]
        assert "trade_matrix" in data["state"]
        assert "rules" in data["state"]
    
    async def test_fis_template_generation(self, client: AsyncClient):
        """Test FIS template generation."""
        response = await client.post("/api/v1/simulation/templates/fis")
        assert response.status_code == 200
        data = response.json()
        assert "template_type" in data
        assert "state" in data
        assert "countries" in data["state"]
        assert "trade_matrix" in data["state"]
        assert "rules" in data["state"]
    
    async def test_trigger_examples(self, client: AsyncClient):
        """Test trigger examples endpoint."""
        response = await client.get("/api/v1/simulation/triggers/examples")
        assert response.status_code == 200
        examples = response.json()
        assert len(examples) > 0
        # Verify structure of first example
        first_example = list(examples.values())[0]
        assert "name" in first_example
        assert "condition" in first_example
        assert "action" in first_example
