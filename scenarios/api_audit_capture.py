#!/usr/bin/env python3
"""
Simple API-based audit trail capture script.
Uses the running Docker services to create scenarios and capture audit data.
"""

import asyncio
import json
import httpx
from datetime import datetime
from pathlib import Path


class APIAuditCapture:
    """Capture audit trails using the real API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = {}
    
    async def login(self, email: str = "newuser@example.com", password: str = "testpassword123"):
        """Login and get auth token."""
        async with httpx.AsyncClient() as client:
            # First register user
            try:
                register_response = await client.post(f"{self.base_url}/api/v1/register", json={
                    "email": email,
                    "password": password,
                    "full_name": "Test User"
                })
                print(f"Registration: {register_response.status_code}")
            except Exception as e:
                print(f"Registration failed (user may exist): {e}")
            
            # Login
            response = await client.post(f"{self.base_url}/api/v1/login", json={
                "email": email,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
    
    def get_sample_mvs_state(self):
        """Get sample MVS state for testing."""
        return {
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
                    },
                    "external": {
                        "fx_rate": 1.0,
                        "reserves_usd": 150000,
                        "current_account_gdp": -0.025
                    },
                    "trade": {
                        "exports_gdp": 0.12,
                        "imports_gdp": 0.15,
                        "tariff_mfn_avg": 0.032
                    }
                },
                "CHN": {
                    "name": "CHN", 
                    "macro": {
                        "gdp": 17700000,
                        "inflation": 0.021,
                        "unemployment": 0.039,
                        "policy_rate": 0.035,
                        "debt_gdp": 0.67
                    },
                    "external": {
                        "fx_rate": 6.8,
                        "reserves_usd": 3200000,
                        "current_account_gdp": 0.015
                    },
                    "trade": {
                        "exports_gdp": 0.18,
                        "imports_gdp": 0.16,
                        "tariff_mfn_avg": 0.076
                    }
                }
            },
            "trade_matrix": {
                "USA": {"CHN": 120000},
                "CHN": {"USA": 450000}
            },
            "rules": {
                "regimes": {
                    "monetary": {"taylor_rule_enabled": True},
                    "fiscal": {"debt_sustainability": True}
                },
                "rng_seed": 42
            }
        }
    
    async def capture_scenario_audit(self, scenario_name: str, steps: int = 5):
        """Create scenario, run steps, and capture audit trail."""
        print(f"\n🔄 Starting audit capture for: {scenario_name}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Create scenario
            create_data = {
                "name": scenario_name,
                "description": f"Audit capture test for {scenario_name}",
                "initial_state": self.get_sample_mvs_state()
            }
            
            create_response = await client.post(
                f"{self.base_url}/api/v1/simulation/scenarios",
                json=create_data,
                headers=self.headers
            )
            
            if create_response.status_code != 200:
                print(f"❌ Failed to create scenario: {create_response.status_code} - {create_response.text}")
                return None
            
            scenario = create_response.json()
            scenario_id = scenario["id"]
            print(f"✅ Created scenario: {scenario_id}")
            
            # Capture audit trail for each step
            audit_trail = {
                "scenario_id": scenario_id,
                "scenario_name": scenario_name,
                "description": create_data["description"],
                "captured_at": datetime.utcnow().isoformat(),
                "steps": []
            }
            
            # Run simulation steps
            for step in range(steps):
                print(f"   Step {step + 1}/{steps}")
                
                step_response = await client.post(
                    f"{self.base_url}/api/v1/simulation/scenarios/{scenario_id}/step",
                    headers=self.headers
                )
                
                if step_response.status_code == 200:
                    step_data = step_response.json()
                    audit_trail["steps"].append({
                        "timestep": step_data["timestep"],
                        "state": step_data["state"],
                        "audit": step_data["audit"],
                        "created_at": step_data["created_at"]
                    })
                    print(f"   ✅ Step {step + 1} complete (timestep {step_data['timestep']})")
                else:
                    print(f"   ❌ Step {step + 1} failed: {step_response.status_code}")
                    break
            
            return audit_trail
    
    async def save_audit_to_file(self, audit_data: dict, filename: str):
        """Save audit data to JSON file."""
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        filepath = data_dir / f"{filename}.json"
        
        with open(filepath, 'w') as f:
            json.dump(audit_data, f, indent=2, default=str)
        
        print(f"💾 Saved audit trail to: {filepath}")
        return filepath


async def main():
    """Main execution function."""
    print("🚀 SlashRun API Audit Capture")
    print("=" * 50)
    
    capture = APIAuditCapture()
    
    # Login
    if not await capture.login():
        print("Failed to authenticate")
        return
    
    # Test scenarios
    scenarios = [
        ("Single_Country_Basic", 3),
        ("Policy_Shock_Scenario", 5),
        ("Trade_War_Simulation", 4)
    ]
    
    for scenario_name, steps in scenarios:
        try:
            audit_data = await capture.capture_scenario_audit(scenario_name, steps)
            if audit_data:
                filename = f"audit_{scenario_name.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                await capture.save_audit_to_file(audit_data, filename)
                
                # Print summary
                print(f"\n📊 Audit Summary for {scenario_name}:")
                print(f"   Scenario ID: {audit_data['scenario_id']}")
                print(f"   Steps captured: {len(audit_data['steps'])}")
                if audit_data['steps']:
                    first_step = audit_data['steps'][0]
                    last_step = audit_data['steps'][-1]
                    print(f"   Initial timestep: {first_step['timestep']}")
                    print(f"   Final timestep: {last_step['timestep']}")
                    print(f"   Countries tracked: {list(first_step['state']['countries'].keys())}")
                
        except Exception as e:
            print(f"❌ Error capturing {scenario_name}: {e}")
        
        print("-" * 40)
    
    print("\n✅ Audit capture complete!")


if __name__ == "__main__":
    asyncio.run(main())
