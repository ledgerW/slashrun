#!/usr/bin/env python3
"""
Enhanced Scenario Runner with detailed state and reducer tracking.
Loads structured YAML scenario definitions and executes with comprehensive audit capture.
"""

import asyncio
import json
import yaml
import httpx
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import sys
import os

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent / "backend"))

@dataclass
class ScenarioResult:
    """Results from scenario execution."""
    scenario_name: str
    scenario_id: str
    success: bool
    timesteps_completed: int
    execution_time: float
    audit_trail: List[Dict[str, Any]]
    validation_results: Dict[str, Any]
    error_message: Optional[str] = None

@dataclass
class ValidationResult:
    """Results from economic relationship validation."""
    check_name: str
    description: str
    passed: bool
    details: Dict[str, Any]
    error_message: Optional[str] = None

class EconomicValidator:
    """Validates economic relationships and realism."""
    
    def __init__(self):
        self.tolerance = 0.001
    
    def validate_relationship(self, check_name: str, description: str, 
                            audit_trail: List[Dict], initial_state: Dict) -> ValidationResult:
        """Validate a specific economic relationship."""
        try:
            if check_name == "policy_rate_adjusts_for_inflation":
                return self._validate_taylor_rule_response(audit_trail, initial_state)
            elif check_name == "inflation_changes_over_time":
                return self._validate_inflation_evolution(audit_trail, initial_state)
            elif check_name == "trigger_fires_on_schedule":
                return self._validate_trigger_timing(audit_trail, description)
            elif check_name == "tariffs_increase_over_time":
                return self._validate_tariff_escalation(audit_trail)
            elif check_name == "fx_rate_increases_in_crisis":
                return self._validate_currency_devaluation(audit_trail)
            elif check_name == "credit_spreads_widen_with_bank_stress":
                return self._validate_credit_spread_widening(audit_trail)
            else:
                return ValidationResult(
                    check_name=check_name,
                    description=description,
                    passed=False,
                    details={},
                    error_message=f"Unknown validation check: {check_name}"
                )
        except Exception as e:
            return ValidationResult(
                check_name=check_name,
                description=description, 
                passed=False,
                details={},
                error_message=f"Validation error: {str(e)}"
            )
    
    def _validate_taylor_rule_response(self, audit_trail: List[Dict], initial_state: Dict) -> ValidationResult:
        """Validate that policy rate responds to inflation gap."""
        if len(audit_trail) < 2:
            return ValidationResult("policy_rate_adjusts_for_inflation", "Taylor rule response", False, 
                                  {}, "Insufficient timesteps for validation")
        
        initial_inflation = initial_state["countries"]["USA"]["macro"]["inflation"]
        initial_rate = initial_state["countries"]["USA"]["macro"]["policy_rate"]
        target_inflation = initial_state["countries"]["USA"]["macro"].get("inflation_target", 0.02)
        
        final_step = audit_trail[-1]
        final_inflation = final_step["state"]["countries"]["USA"]["macro"]["inflation"]
        final_rate = final_step["state"]["countries"]["USA"]["macro"]["policy_rate"]
        
        initial_gap = initial_inflation - target_inflation
        final_gap = final_inflation - target_inflation
        
        # Check if rate moved in correct direction
        if initial_gap > 0:  # Above target inflation
            rate_should_increase = final_rate > initial_rate - self.tolerance
        else:  # Below target inflation
            rate_should_increase = final_rate < initial_rate + self.tolerance
        
        return ValidationResult(
            check_name="policy_rate_adjusts_for_inflation",
            description="Taylor rule response",
            passed=rate_should_increase,
            details={
                "initial_inflation": initial_inflation,
                "final_inflation": final_inflation,
                "initial_rate": initial_rate,
                "final_rate": final_rate,
                "initial_gap": initial_gap,
                "final_gap": final_gap,
                "target_inflation": target_inflation
            }
        )
    
    def _validate_inflation_evolution(self, audit_trail: List[Dict], initial_state: Dict) -> ValidationResult:
        """Validate that inflation changes over time."""
        if len(audit_trail) < 2:
            return ValidationResult("inflation_changes_over_time", "Inflation evolution", False,
                                  {}, "Insufficient timesteps for validation")
        
        initial_inflation = initial_state["countries"]["USA"]["macro"]["inflation"]
        final_inflation = audit_trail[-1]["state"]["countries"]["USA"]["macro"]["inflation"]
        
        changed = abs(final_inflation - initial_inflation) > self.tolerance
        
        return ValidationResult(
            check_name="inflation_changes_over_time",
            description="Inflation evolution",
            passed=changed,
            details={
                "initial_inflation": initial_inflation,
                "final_inflation": final_inflation,
                "change": final_inflation - initial_inflation
            }
        )
    
    def _validate_trigger_timing(self, audit_trail: List[Dict], description: str) -> ValidationResult:
        """Validate that trigger fires at expected time."""
        trigger_fired = False
        fire_timestep = None
        
        for step in audit_trail:
            if step["audit"]["triggers_fired"]:
                trigger_fired = True
                fire_timestep = step["timestep"]
                break
        
        return ValidationResult(
            check_name="trigger_fires_on_schedule",
            description=description,
            passed=trigger_fired,
            details={
                "trigger_fired": trigger_fired,
                "fire_timestep": fire_timestep,
                "expected_timestep": "varies by scenario"
            }
        )
    
    def _validate_tariff_escalation(self, audit_trail: List[Dict]) -> ValidationResult:
        """Validate tariff escalation pattern."""
        us_tariffs = []
        chn_tariffs = []
        
        for step in audit_trail:
            state = step["state"]
            if "USA" in state["countries"] and "trade" in state["countries"]["USA"]:
                us_tariffs.append(state["countries"]["USA"]["trade"]["tariff_mfn_avg"])
            if "CHN" in state["countries"] and "trade" in state["countries"]["CHN"]:
                chn_tariffs.append(state["countries"]["CHN"]["trade"]["tariff_mfn_avg"])
        
        us_escalated = len(us_tariffs) > 1 and max(us_tariffs) > min(us_tariffs) + 0.1
        chn_escalated = len(chn_tariffs) > 1 and max(chn_tariffs) > min(chn_tariffs) + 0.1
        
        return ValidationResult(
            check_name="tariffs_increase_over_time",
            description="Tariff escalation",
            passed=us_escalated or chn_escalated,
            details={
                "us_tariff_range": (min(us_tariffs), max(us_tariffs)) if us_tariffs else None,
                "chn_tariff_range": (min(chn_tariffs), max(chn_tariffs)) if chn_tariffs else None,
                "us_escalated": us_escalated,
                "chn_escalated": chn_escalated
            }
        )
    
    def _validate_currency_devaluation(self, audit_trail: List[Dict]) -> ValidationResult:
        """Validate currency devaluation during crisis."""
        fx_rates = []
        
        for step in audit_trail:
            state = step["state"]
            for country_code, country_data in state["countries"].items():
                if "external" in country_data and "fx_rate" in country_data["external"]:
                    fx_rate = country_data["external"]["fx_rate"]
                    if country_code != "USA":  # Non-USD currencies
                        fx_rates.append((step["timestep"], country_code, fx_rate))
        
        # Look for significant devaluation (FX rate increase for non-USD)
        devaluation_found = False
        for i in range(1, len(fx_rates)):
            if fx_rates[i][2] > fx_rates[0][2] * 1.1:  # 10%+ devaluation
                devaluation_found = True
                break
        
        return ValidationResult(
            check_name="fx_rate_increases_in_crisis",
            description="Currency devaluation",
            passed=devaluation_found,
            details={
                "fx_rate_series": fx_rates,
                "devaluation_found": devaluation_found
            }
        )
    
    def _validate_credit_spread_widening(self, audit_trail: List[Dict]) -> ValidationResult:
        """Validate credit spread widening during financial stress."""
        spreads = []
        
        for step in audit_trail:
            state = step["state"]
            for country_code, country_data in state["countries"].items():
                if "finance" in country_data and "credit_spread" in country_data["finance"]:
                    spread = country_data["finance"]["credit_spread"]
                    spreads.append((step["timestep"], country_code, spread))
        
        # Look for significant spread widening
        widening_found = False
        if len(spreads) > 1:
            max_spread = max(spreads, key=lambda x: x[2])
            min_spread = min(spreads, key=lambda x: x[2])
            if max_spread[2] > min_spread[2] * 1.5:  # 50%+ widening
                widening_found = True
        
        return ValidationResult(
            check_name="credit_spreads_widen_with_bank_stress",
            description="Credit spread widening",
            passed=widening_found,
            details={
                "spread_series": spreads,
                "widening_found": widening_found,
                "max_spread": max(spreads, key=lambda x: x[2]) if spreads else None,
                "min_spread": min(spreads, key=lambda x: x[2]) if spreads else None
            }
        )

class EnhancedScenarioRunner:
    """Enhanced scenario runner with comprehensive audit capture."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = {}
        self.validator = EconomicValidator()
        
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
    
    def load_scenario_definition(self, scenario_path: Path) -> Dict[str, Any]:
        """Load scenario definition from YAML file."""
        with open(scenario_path, 'r') as f:
            return yaml.safe_load(f)
    
    async def execute_scenario(self, scenario_def: Dict[str, Any]) -> ScenarioResult:
        """Execute a scenario with comprehensive tracking."""
        scenario_name = scenario_def["name"]
        start_time = datetime.utcnow()
        
        print(f"\n🔄 Executing scenario: {scenario_name}")
        print(f"   Description: {scenario_def['description']}")
        print(f"   Complexity: {scenario_def['complexity']}")
        print(f"   Expected duration: {scenario_def['expected_duration']} timesteps")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Create scenario
                create_data = {
                    "name": scenario_name,
                    "description": scenario_def["description"],
                    "initial_state": scenario_def["initial_state"],
                    "triggers": scenario_def.get("triggers", [])
                }
                
                create_response = await client.post(
                    f"{self.base_url}/api/v1/simulation/scenarios",
                    json=create_data,
                    headers=self.headers
                )
                
                if create_response.status_code != 200:
                    return ScenarioResult(
                        scenario_name=scenario_name,
                        scenario_id="",
                        success=False,
                        timesteps_completed=0,
                        execution_time=0,
                        audit_trail=[],
                        validation_results={},
                        error_message=f"Failed to create scenario: {create_response.status_code} - {create_response.text}"
                    )
                
                scenario = create_response.json()
                scenario_id = scenario["id"]
                print(f"✅ Created scenario: {scenario_id}")
                
                # Execute timesteps with detailed tracking
                audit_trail = []
                timesteps = scenario_def.get("test_parameters", {}).get("timesteps", scenario_def["expected_duration"])
                
                for timestep in range(timesteps):
                    print(f"   Step {timestep + 1}/{timesteps}")
                    
                    step_response = await client.post(
                        f"{self.base_url}/api/v1/simulation/scenarios/{scenario_id}/step",
                        headers=self.headers
                    )
                    
                    if step_response.status_code == 200:
                        step_data = step_response.json()
                        audit_trail.append(step_data)
                        
                        # Print step summary
                        triggers_fired = step_data["audit"]["triggers_fired"]
                        field_changes = len(step_data["audit"]["field_changes"])
                        reducer_sequence = step_data["audit"]["reducer_sequence"]
                        
                        print(f"     ✅ Timestep {step_data['timestep']}: {field_changes} changes, {len(reducer_sequence)} reducers")
                        if triggers_fired:
                            print(f"     🔥 Triggers fired: {triggers_fired}")
                    else:
                        return ScenarioResult(
                            scenario_name=scenario_name,
                            scenario_id=scenario_id,
                            success=False,
                            timesteps_completed=timestep,
                            execution_time=(datetime.utcnow() - start_time).total_seconds(),
                            audit_trail=audit_trail,
                            validation_results={},
                            error_message=f"Step {timestep + 1} failed: {step_response.status_code}"
                        )
                
                # Perform validation
                validation_results = await self.validate_scenario(scenario_def, audit_trail)
                
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                return ScenarioResult(
                    scenario_name=scenario_name,
                    scenario_id=scenario_id,
                    success=True,
                    timesteps_completed=len(audit_trail),
                    execution_time=execution_time,
                    audit_trail=audit_trail,
                    validation_results=validation_results
                )
                
        except Exception as e:
            return ScenarioResult(
                scenario_name=scenario_name,
                scenario_id="",
                success=False,
                timesteps_completed=0,
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                audit_trail=[],
                validation_results={},
                error_message=f"Execution error: {str(e)}"
            )
    
    async def validate_scenario(self, scenario_def: Dict[str, Any], audit_trail: List[Dict]) -> Dict[str, Any]:
        """Validate scenario results against expected outcomes."""
        validation_config = scenario_def.get("validation", {})
        results = {
            "economic_relationships": [],
            "expected_outcomes": [],
            "overall_passed": True
        }
        
        # Validate economic relationships
        relationships = validation_config.get("economic_relationships", [])
        for relationship in relationships:
            check_name = relationship["check"]
            description = relationship["description"]
            
            validation_result = self.validator.validate_relationship(
                check_name, description, audit_trail, scenario_def["initial_state"]
            )
            
            results["economic_relationships"].append(asdict(validation_result))
            if not validation_result.passed:
                results["overall_passed"] = False
        
        # Validate expected outcomes
        outcomes = validation_config.get("expected_outcomes", [])
        for outcome in outcomes:
            outcome_result = self.validate_expected_outcome(outcome, audit_trail, scenario_def["initial_state"])
            results["expected_outcomes"].append(outcome_result)
            if not outcome_result["passed"]:
                results["overall_passed"] = False
        
        return results
    
    def validate_expected_outcome(self, outcome: Dict[str, Any], audit_trail: List[Dict], initial_state: Dict) -> Dict[str, Any]:
        """Validate a specific expected outcome."""
        field_path = outcome["field"]
        should = outcome["should"]
        
        try:
            # Extract field values over time
            field_values = []
            for step in audit_trail:
                value = self.extract_field_value(step, field_path)
                if value is not None:
                    field_values.append((step["timestep"], value))
            
            # Get initial value
            initial_value = self.extract_field_value({"state": initial_state}, field_path)
            
            # Validate based on expectation
            if should == "change":
                tolerance = outcome.get("tolerance", 0.001)
                final_value = field_values[-1][1] if field_values else initial_value
                passed = abs(final_value - initial_value) > tolerance
            elif should == "equal":
                expected_value = outcome["value"]
                after_timestep = outcome.get("after_timestep", field_values[-1][0] if field_values else 0)
                
                relevant_values = [v for t, v in field_values if t >= after_timestep]
                passed = any(abs(v - expected_value) < 0.001 for v in relevant_values)
            elif should == "increase":
                by_amount = outcome.get("by", 0)
                by_percent = outcome.get("by_percent", 0)
                final_value = field_values[-1][1] if field_values else initial_value
                
                if by_amount > 0:
                    passed = final_value >= initial_value + by_amount * 0.9  # 90% tolerance
                elif by_percent > 0:
                    expected_final = initial_value * (1 + by_percent / 100)
                    passed = final_value >= expected_final * 0.9  # 90% tolerance
                else:
                    passed = final_value > initial_value
            elif should == "decrease":
                by_percent = outcome.get("by_percent", 0)
                final_value = field_values[-1][1] if field_values else initial_value
                
                if by_percent > 0:
                    expected_final = initial_value * (1 - by_percent / 100)
                    passed = final_value <= expected_final * 1.1  # 110% tolerance
                else:
                    passed = final_value < initial_value
            else:
                passed = False
            
            return {
                "field": field_path,
                "description": outcome["description"],
                "should": should,
                "passed": passed,
                "initial_value": initial_value,
                "final_value": field_values[-1][1] if field_values else None,
                "field_trajectory": field_values[-5:] if len(field_values) > 5 else field_values
            }
            
        except Exception as e:
            return {
                "field": field_path,
                "description": outcome["description"],
                "should": should,
                "passed": False,
                "error": str(e)
            }
    
    def extract_field_value(self, step_data: Dict, field_path: str) -> Any:
        """Extract a field value from step data using dot notation."""
        try:
            # Handle audit fields
            if field_path.startswith("audit."):
                audit_field = field_path[6:]  # Remove "audit."
                return step_data["audit"].get(audit_field)
            
            # Handle state fields
            parts = field_path.split(".")
            current = step_data["state"]
            
            for part in parts:
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    return None
            
            return current
        except:
            return None
    
    async def save_results(self, result: ScenarioResult, output_dir: Path):
        """Save scenario results to files."""
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed audit trail
        audit_file = output_dir / f"audit_{result.scenario_name.lower().replace(' ', '_')}_{timestamp}.json"
        with open(audit_file, 'w') as f:
            json.dump({
                "scenario_name": result.scenario_name,
                "scenario_id": result.scenario_id,
                "execution_time": result.execution_time,
                "timesteps_completed": result.timesteps_completed,
                "audit_trail": result.audit_trail,
                "captured_at": datetime.utcnow().isoformat()
            }, f, indent=2, default=str)
        
        # Save validation report
        validation_file = output_dir / f"validation_{result.scenario_name.lower().replace(' ', '_')}_{timestamp}.json"
        with open(validation_file, 'w') as f:
            json.dump({
                "scenario_name": result.scenario_name,
                "success": result.success,
                "validation_results": result.validation_results,
                "error_message": result.error_message,
                "execution_summary": {
                    "timesteps_completed": result.timesteps_completed,
                    "execution_time": result.execution_time
                }
            }, f, indent=2, default=str)
        
        print(f"💾 Results saved:")
        print(f"   Audit trail: {audit_file}")
        print(f"   Validation report: {validation_file}")
        
        return audit_file, validation_file

async def main():
    """Main execution function."""
    if len(sys.argv) > 1:
        scenario_filter = sys.argv[1].lower()
    else:
        scenario_filter = "all"
    
    print("🚀 Enhanced SlashRun Scenario Runner")
    print("=" * 50)
    
    runner = EnhancedScenarioRunner()
    
    # Login
    if not await runner.login():
        print("❌ Failed to authenticate")
        return
    
    # Find scenario files
    definitions_dir = Path(__file__).parent / "definitions"
    scenario_files = []
    
    for complexity in ["simple", "medium", "complex"]:
        complexity_dir = definitions_dir / complexity
        if complexity_dir.exists():
            if scenario_filter == "all" or scenario_filter == complexity:
                scenario_files.extend(list(complexity_dir.glob("*.yaml")))
    
    if not scenario_files:
        print(f"❌ No scenario files found for filter: {scenario_filter}")
        return
    
    print(f"📋 Found {len(scenario_files)} scenarios to execute")
    
    # Execute scenarios
    results = []
    for scenario_file in scenario_files:
        try:
            scenario_def = runner.load_scenario_definition(scenario_file)
            result = await runner.execute_scenario(scenario_def)
            results.append(result)
            
            # Save results
            reports_dir = Path(__file__).parent / "reports"
            await runner.save_results(result, reports_dir)
            
            # Print summary
            print(f"\n📊 Scenario Summary: {result.scenario_name}")
            print(f"   Success: {'✅' if result.success else '❌'}")
            print(f"   Timesteps: {result.timesteps_completed}")
            print(f"   Execution time: {result.execution_time:.2f}s")
            if result.validation_results:
                overall_passed = result.validation_results.get("overall_passed", False)
                print(f"   Validation: {'✅' if overall_passed else '❌'}")
                
                # Show failed validations
                for rel in result.validation_results.get("economic_relationships", []):
                    if not rel["passed"]:
                        print(f"     ❌ {rel['check_name']}: {rel.get('error_message', 'Failed')}")
                
                for outcome in result.validation_results.get("expected_outcomes", []):
                    if not outcome["passed"]:
                        print(f"     ❌ {outcome['field']}: Expected {outcome['should']}")
            
            if result.error_message:
                print(f"   Error: {result.error_message}")
            
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ Error executing {scenario_file.name}: {e}")
    
    # Final summary
    successful_scenarios = [r for r in results if r.success]
    print(f"\n✅ Execution complete!")
    print(f"   Total scenarios: {len(results)}")
    print(f"   Successful: {len(successful_scenarios)}")
    print(f"   Failed: {len(results) - len(successful_scenarios)}")

if __name__ == "__main__":
    asyncio.run(main())
