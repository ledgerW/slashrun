"""Simple scenario tests for basic economic simulation functionality."""

import pytest
from httpx import AsyncClient


class TestSimpleScenario:
    """Test simple single-country economic scenario."""
    
    async def test_single_country_basic_simulation(self, client: AsyncClient, auth_headers):
        """Test basic simulation with one country over multiple timesteps."""
        
        # Simple US-only scenario
        scenario_data = {
            "name": "Simple US Economy",
            "description": "Single country basic economic simulation",
            "initial_state": {
                "t": 0,
                "base_ccy": "USD",
                "countries": {
                    "USA": {
                        "name": "USA",
                        "macro": {
                            "gdp": 23000000,
                            "inflation": 0.025,
                            "unemployment": 0.037,
                            "policy_rate": 0.05,
                            "debt_gdp": 0.95,
                            "inflation_target": 0.02
                        }
                    }
                },
                "rules": {
                    "regimes": {
                        "monetary": {"taylor_rule_enabled": True}
                    },
                    "rng_seed": 42
                }
            },
            "triggers": []
        }
        
        # Create scenario
        response = await client.post(
            "/api/v1/simulation/scenarios",
            json=scenario_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        scenario_id = response.json()["id"]
        
        # Run simulation for 5 timesteps
        states = []
        for i in range(5):
            response = await client.post(
                f"/api/v1/simulation/scenarios/{scenario_id}/step",
                headers=auth_headers
            )
            assert response.status_code == 200
            step_data = response.json()
            states.append(step_data)
            
            # Verify timestep progression
            assert step_data["timestep"] == i + 1
            
            # Verify audit trail exists
            audit = step_data["audit"]
            assert audit["timestep"] == i + 1
            assert len(audit["field_changes"]) > 0
            assert len(audit["reducer_sequence"]) > 0
        
        # Verify economic variables evolved
        initial_inflation = 0.025
        final_inflation = states[-1]["state"]["countries"]["USA"]["macro"]["inflation"]
        
        # Inflation should have changed due to Taylor rule
        assert final_inflation != initial_inflation
        
        # Policy rate should respond to inflation gap
        initial_rate = 0.05
        final_rate = states[-1]["state"]["countries"]["USA"]["macro"]["policy_rate"]
        inflation_gap = final_inflation - 0.02  # target is 2%
        
        # Basic Taylor rule check: rate should move with inflation
        if inflation_gap > 0:
            assert final_rate >= initial_rate - 0.001  # Allow small tolerance
    
    async def test_simple_policy_shock(self, client: AsyncClient, auth_headers):
        """Test simple monetary policy shock scenario."""
        
        scenario_data = {
            "name": "Policy Shock Test",
            "description": "Test monetary policy rate shock",
            "initial_state": {
                "t": 0,
                "base_ccy": "USD",
                "countries": {
                    "USA": {
                        "name": "USA",
                        "macro": {
                            "gdp": 23000000,
                            "inflation": 0.025,
                            "unemployment": 0.037,
                            "policy_rate": 0.05,
                            "debt_gdp": 0.95
                        }
                    }
                },
                "rules": {
                    "regimes": {
                        "monetary": {"taylor_rule_enabled": True}
                    }
                }
            },
            "triggers": [
                {
                    "name": "Emergency Rate Cut",
                    "description": "Cut policy rate to zero at t=3",
                    "condition": {
                        "when": "t >= 3",
                        "once": True
                    },
                    "action": {
                        "patches": [
                            {
                                "path": "countries.USA.macro.policy_rate",
                                "op": "set",
                                "value": 0.0
                            }
                        ]
                    }
                }
            ]
        }
        
        # Create scenario
        response = await client.post(
            "/api/v1/simulation/scenarios",
            json=scenario_data,
            headers=auth_headers
        )
        scenario_id = response.json()["id"]
        
        # Step to t=2 (before trigger)
        for _ in range(2):
            await client.post(f"/api/v1/simulation/scenarios/{scenario_id}/step", headers=auth_headers)
        
        # Get state at t=2
        response = await client.get(
            f"/api/v1/simulation/scenarios/{scenario_id}/states/2",
            headers=auth_headers
        )
        pre_shock_rate = response.json()["state"]["countries"]["USA"]["macro"]["policy_rate"]
        
        # Step to t=3 (trigger fires)
        response = await client.post(
            f"/api/v1/simulation/scenarios/{scenario_id}/step",
            headers=auth_headers
        )
        step_data = response.json()
        
        # Verify trigger fired
        assert "Emergency Rate Cut" in step_data["audit"]["triggers_fired"]
        
        # Verify policy rate was set to 0
        post_shock_rate = step_data["state"]["countries"]["USA"]["macro"]["policy_rate"]
        assert post_shock_rate == 0.0
        assert pre_shock_rate != 0.0
        
        # Verify audit captured the change
        rate_changes = [
            change for change in step_data["audit"]["field_changes"]
            if "policy_rate" in change["field_path"]
        ]
        assert len(rate_changes) > 0
    
    async def test_inflation_targeting(self, client: AsyncClient, auth_headers):
        """Test inflation targeting behavior over time."""
        
        scenario_data = {
            "name": "Inflation Target Test",
            "description": "Test central bank inflation targeting",
            "initial_state": {
                "t": 0,
                "base_ccy": "USD",
                "countries": {
                    "USA": {
                        "name": "USA",
                        "macro": {
                            "gdp": 23000000,
                            "inflation": 0.08,  # Start with high inflation
                            "unemployment": 0.037,
                            "policy_rate": 0.02,  # Start with low rate
                            "debt_gdp": 0.95,
                            "inflation_target": 0.02
                        }
                    }
                },
                "rules": {
                    "regimes": {
                        "monetary": {"taylor_rule_enabled": True}
                    }
                }
            },
            "triggers": []
        }
        
        # Create scenario
        response = await client.post(
            "/api/v1/simulation/scenarios",
            json=scenario_data,
            headers=auth_headers
        )
        scenario_id = response.json()["id"]
        
        # Run for 10 steps to see convergence
        initial_inflation = 0.08
        initial_rate = 0.02
        
        for i in range(10):
            response = await client.post(
                f"/api/v1/simulation/scenarios/{scenario_id}/step",
                headers=auth_headers
            )
            step_data = response.json()
            
            current_inflation = step_data["state"]["countries"]["USA"]["macro"]["inflation"]
            current_rate = step_data["state"]["countries"]["USA"]["macro"]["policy_rate"]
            
            # After several steps, inflation should be moving toward target
            if i >= 5:
                assert current_inflation < initial_inflation  # Inflation decreasing
                assert current_rate > initial_rate  # Rate increasing to fight inflation
        
        # Final check: inflation should be closer to target
        final_step = response.json()
        final_inflation = final_step["state"]["countries"]["USA"]["macro"]["inflation"]
        inflation_gap_initial = abs(initial_inflation - 0.02)
        inflation_gap_final = abs(final_inflation - 0.02)
        
        # Gap should be smaller (inflation moving toward 2% target)
        assert inflation_gap_final < inflation_gap_initial
