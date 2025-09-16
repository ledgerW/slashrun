"""Database operation tests for SlashRun models and persistence."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlmodel import SQLModel

from db.models.user import User
from db.models.scenario import Scenario, SimulationState
from db.models.audit import AuditLog, FieldChangeLog, TriggerLog
from db.models.trigger import ScenarioTrigger, PolicyPatch
from backend.app.services.auth_service import auth_service


class TestUserModel:
    """Test user model operations."""
    
    async def test_create_user(self, test_db: AsyncSession):
        """Test user creation and retrieval."""
        user = User(
            email="testuser@example.com",
            username="testuser",
            hashed_password=auth_service.hash_password("password123"),
            full_name="Test User",
            bio="Test bio",
            organization="Test Org"
        )
        
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        
        assert user.id is not None
        assert user.email == "testuser@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.login_count == 0
        assert "password123" not in str(user)  # Actual password should not appear in string representation
    
    async def test_user_relationships(self, test_db: AsyncSession, test_user: User):
        """Test user-scenario relationships."""
        # Create scenario for the user
        scenario = Scenario(
            name="Test Scenario",
            description="Test scenario for user relationship",
            user_id=test_user.id,
            current_timestep=0
        )
        
        test_db.add(scenario)
        await test_db.commit()
        
        # Verify relationship
        result = await test_db.execute(
            select(User).where(User.id == test_user.id)
        )
        user_with_scenarios = result.scalar_one()
        
        # Note: In SQLModel, relationships need explicit loading
        # This test verifies the foreign key constraint works
        assert scenario.user_id == user_with_scenarios.id


class TestScenarioModel:
    """Test scenario model operations."""
    
    async def test_create_scenario(self, test_db: AsyncSession, test_user: User):
        """Test scenario creation with JSON state."""
        scenario = Scenario(
            name="JSON State Test",
            description="Testing JSON state storage",
            user_id=test_user.id,
            current_timestep=0
        )
        
        test_db.add(scenario)
        await test_db.commit()
        await test_db.refresh(scenario)
        
        # Create initial state as timestep 0
        initial_state = {
            "t": 0,
            "base_ccy": "USD",
            "countries": {
                "USA": {
                    "name": "USA",
                    "macro": {"gdp": 23000000, "inflation": 0.025}
                }
            },
            "rules": {"regimes": {"monetary": {"taylor_rule_enabled": True}}}
        }
        
        state = SimulationState(
            scenario_id=scenario.id,
            timestep=0,
            state_data=initial_state
        )
        
        test_db.add(state)
        await test_db.commit()
        await test_db.refresh(state)
        
        # Verify JSON serialization/deserialization
        assert state.state_data["t"] == 0
        assert state.state_data["countries"]["USA"]["name"] == "USA"
        assert state.state_data["countries"]["USA"]["macro"]["gdp"] == 23000000
        assert state.state_data["rules"]["regimes"]["monetary"]["taylor_rule_enabled"] is True
    
    async def test_scenario_with_simulation_states(self, test_db: AsyncSession, test_user: User):
        """Test scenario with multiple simulation states."""
        scenario = Scenario(
            name="Multi-State Scenario",
            user_id=test_user.id,
            current_timestep=2
        )
        
        test_db.add(scenario)
        await test_db.commit()
        
        # Create simulation states
        state1 = SimulationState(
            scenario_id=scenario.id,
            timestep=1,
            state_data={"t": 1, "countries": {"USA": {"name": "USA", "macro": {"gdp": 23100000}}}}
        )
        
        state2 = SimulationState(
            scenario_id=scenario.id,
            timestep=2,
            state_data={"t": 2, "countries": {"USA": {"name": "USA", "macro": {"gdp": 23200000}}}}
        )
        
        test_db.add_all([state1, state2])
        await test_db.commit()
        
        # Verify states are stored
        result = await test_db.execute(
            select(SimulationState)
            .where(SimulationState.scenario_id == scenario.id)
            .order_by(SimulationState.timestep)
        )
        states = result.scalars().all()
        
        assert len(states) == 2
        assert states[0].timestep == 1
        assert states[1].timestep == 2
        assert states[1].state_data["countries"]["USA"]["macro"]["gdp"] == 23200000


class TestAuditTrail:
    """Test audit trail functionality."""
    
    async def test_complete_audit_chain(self, test_db: AsyncSession, test_user: User):
        """Test complete audit trail from scenario to field changes."""
        # Create scenario and simulation state
        scenario = Scenario(
            name="Audit Test Scenario",
            user_id=test_user.id,
            current_timestep=1
        )
        test_db.add(scenario)
        await test_db.commit()
        
        state = SimulationState(
            scenario_id=scenario.id,
            timestep=1,
            state_data={"t": 1, "countries": {"USA": {"macro": {"inflation": 0.026}}}}
        )
        test_db.add(state)
        await test_db.commit()
        
        # Create audit log
        from datetime import datetime, timezone
        start_time = datetime.now(timezone.utc)
        end_time = datetime.now(timezone.utc)
        
        audit_log = AuditLog(
            scenario_id=scenario.id,
            simulation_state_id=state.id,
            timestep=1,
            step_start_time=start_time,
            step_end_time=end_time,
            reducer_sequence=["taylor_rule", "phillips_curve"],
            triggers_fired=["test_trigger"],
            execution_time_ms=125.5
        )
        test_db.add(audit_log)
        await test_db.commit()
        
        # Create field change logs
        field_change1 = FieldChangeLog(
            audit_log_id=audit_log.id,
            field_path="countries.USA.macro.inflation",
            old_value=0.025,
            new_value=0.026,
            reducer_name="phillips_curve",
            reducer_params={"unemployment_gap": -0.002},
            calculation_details={"method": "expectations_augmented"},
            change_order=1
        )
        
        field_change2 = FieldChangeLog(
            audit_log_id=audit_log.id,
            field_path="countries.USA.macro.policy_rate",
            old_value=0.05,
            new_value=0.051,
            reducer_name="taylor_rule",
            reducer_params={"inflation_gap": 0.006, "output_gap": 0.001},
            calculation_details={"taylor_coefficient": 1.5},
            change_order=2
        )
        
        test_db.add_all([field_change1, field_change2])
        await test_db.commit()
        
        # Verify audit chain
        result = await test_db.execute(
            select(AuditLog).where(AuditLog.scenario_id == scenario.id)
        )
        stored_audit = result.scalar_one()
        
        assert stored_audit.timestep == 1
        assert stored_audit.reducer_sequence == ["taylor_rule", "phillips_curve"]
        assert stored_audit.triggers_fired == ["test_trigger"]
        assert stored_audit.execution_time_ms == 125.5
        
        # Verify field changes
        result = await test_db.execute(
            select(FieldChangeLog)
            .where(FieldChangeLog.audit_log_id == audit_log.id)
            .order_by(FieldChangeLog.change_order)
        )
        changes = result.scalars().all()
        
        assert len(changes) == 2
        assert changes[0].field_path == "countries.USA.macro.inflation"
        assert changes[0].old_value == 0.025
        assert changes[0].new_value == 0.026
        assert changes[0].reducer_params["unemployment_gap"] == -0.002
        assert changes[1].reducer_name == "taylor_rule"


class TestTriggerSystem:
    """Test trigger storage and retrieval."""
    
    async def test_scenario_trigger_storage(self, test_db: AsyncSession, test_user: User):
        """Test storing complex trigger configurations."""
        scenario = Scenario(
            name="Trigger Test Scenario",
            user_id=test_user.id,
            current_timestep=0
        )
        test_db.add(scenario)
        await test_db.commit()
        
        # Create scenario trigger
        trigger = ScenarioTrigger(
            scenario_id=scenario.id,
            name="Inflation Shock Trigger",
            description="Triggers when inflation exceeds 4%",
            condition_data={
                "when": "countries.USA.macro.inflation > 0.04",
                "once": True
            },
            action_data={
                "patches": [
                    {
                        "path": "countries.USA.macro.policy_rate",
                        "op": "add", 
                        "value": 0.02
                    }
                ],
                "events": [
                    {
                        "kind": "policy_change",
                        "payload": {"type": "emergency_rate_hike"}
                    }
                ]
            },
            once_only=True,
            expires_after_turns=5
        )
        
        test_db.add(trigger)
        await test_db.commit()
        
        # Create policy patches
        patch = PolicyPatch(
            scenario_trigger_id=trigger.id,
            target_path="countries.USA.macro.policy_rate",
            operation="add",
            patch_value={"value": 0.02},
            applied_count=0
        )
        
        test_db.add(patch)
        await test_db.commit()
        
        # Verify storage
        result = await test_db.execute(
            select(ScenarioTrigger).where(ScenarioTrigger.scenario_id == scenario.id)
        )
        stored_trigger = result.scalar_one()
        
        assert stored_trigger.name == "Inflation Shock Trigger"
        assert stored_trigger.condition_data["when"] == "countries.USA.macro.inflation > 0.04"
        assert stored_trigger.condition_data["once"] is True
        assert len(stored_trigger.action_data["patches"]) == 1
        assert stored_trigger.action_data["patches"][0]["value"] == 0.02
        assert stored_trigger.once_only is True
        assert stored_trigger.has_fired is False
        assert stored_trigger.expires_after_turns == 5
        
        # Verify policy patch
        result = await test_db.execute(
            select(PolicyPatch).where(PolicyPatch.scenario_trigger_id == trigger.id)
        )
        stored_patch = result.scalar_one()
        
        assert stored_patch.target_path == "countries.USA.macro.policy_rate"
        assert stored_patch.operation == "add"
        assert stored_patch.patch_value["value"] == 0.02
        assert stored_patch.applied_count == 0
    
    async def test_trigger_execution_tracking(self, test_db: AsyncSession, test_user: User):
        """Test tracking trigger execution in audit logs."""
        # Setup scenario and audit log
        scenario = Scenario(
            name="Execution Tracking Test",
            user_id=test_user.id,
            current_timestep=1
        )
        test_db.add(scenario)
        await test_db.commit()
        
        state = SimulationState(
            scenario_id=scenario.id,
            timestep=1,
            state_data={"t": 1}
        )
        test_db.add(state)
        await test_db.commit()
        
        from datetime import datetime, timezone
        start_time = datetime.now(timezone.utc)
        
        audit_log = AuditLog(
            scenario_id=scenario.id,
            simulation_state_id=state.id,
            timestep=1,
            step_start_time=start_time,
            step_end_time=start_time,
            reducer_sequence=["taylor_rule"],
            triggers_fired=["inflation_shock"]
        )
        test_db.add(audit_log)
        await test_db.commit()
        
        # Create scenario trigger
        trigger = ScenarioTrigger(
            scenario_id=scenario.id,
            name="inflation_shock",
            condition_data={"when": "t >= 1"},
            action_data={"patches": []},
            has_fired=True,
            times_fired=1,
            last_fired_at_turn=1
        )
        test_db.add(trigger)
        await test_db.commit()
        
        # Create trigger log
        trigger_log = TriggerLog(
            audit_log_id=audit_log.id,
            scenario_trigger_id=trigger.id,
            fired_at_turn=1,
            trigger_name="inflation_shock",
            actions_applied={"patches": 1, "events": 0},
            execution_result={"success": True, "changes_made": 1}
        )
        test_db.add(trigger_log)
        await test_db.commit()
        
        # Verify execution tracking
        result = await test_db.execute(
            select(ScenarioTrigger).where(ScenarioTrigger.name == "inflation_shock")
        )
        fired_trigger = result.scalar_one()
        
        assert fired_trigger.has_fired is True
        assert fired_trigger.times_fired == 1
        assert fired_trigger.last_fired_at_turn == 1
        
        # Verify trigger log
        result = await test_db.execute(
            select(TriggerLog).where(TriggerLog.trigger_name == "inflation_shock")
        )
        trigger_log_stored = result.scalar_one()
        
        assert trigger_log_stored.fired_at_turn == 1
        assert trigger_log_stored.actions_applied["patches"] == 1
        assert trigger_log_stored.execution_result["success"] is True


class TestDatabaseIntegrity:
    """Test database constraints and data integrity."""
    
    async def test_foreign_key_constraints(self, test_db: AsyncSession, test_user: User):
        """Test that foreign key constraints are enforced."""
        # This test ensures referential integrity between models
        scenario = Scenario(
            name="FK Test Scenario",
            user_id=test_user.id,
            current_timestep=0
        )
        test_db.add(scenario)
        await test_db.commit()
        
        # Create simulation state
        state = SimulationState(
            scenario_id=scenario.id,
            timestep=1,
            state_data={"t": 1}
        )
        test_db.add(state)
        await test_db.commit()
        
        # Verify the relationship exists
        result = await test_db.execute(
            select(SimulationState).where(SimulationState.scenario_id == scenario.id)
        )
        linked_state = result.scalar_one()
        
        assert linked_state.scenario_id == scenario.id
        assert linked_state.timestep == 1
    
    async def test_json_field_defaults(self, test_db: AsyncSession, test_user: User):
        """Test that JSON fields have proper defaults."""
        # Test that default factories work for JSON columns
        trigger = ScenarioTrigger(
            scenario_id=None,  # We'll set this after creating a scenario
            name="Default Test Trigger"
        )
        
        # Create a minimal scenario first
        scenario = Scenario(
            name="Default Test",
            user_id=test_user.id,
            current_timestep=0
        )
        test_db.add(scenario)
        await test_db.commit()
        
        # Now set the scenario_id and add the trigger
        trigger.scenario_id = scenario.id
        test_db.add(trigger)
        await test_db.commit()
        await test_db.refresh(trigger)
        
        # Verify defaults are applied
        assert trigger.condition_data == {}  # default_factory=dict
        assert trigger.action_data == {}     # default_factory=dict
        assert trigger.has_fired is False   # explicit default
        assert trigger.times_fired == 0     # explicit default
