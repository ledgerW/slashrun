"""Comprehensive tests for simulation core modules."""

import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import datetime
from unittest.mock import Mock

# Import directly from files to avoid app initialization issues
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import all the classes and functions that tests need
from db.models.state import (
    GlobalState, CountryState, Macro, External, Trade, Finance, Security,
    StepAudit, FieldChange, AuditCapture
)
from db.models.scenario import SimulationState
from app.simulation.audit import DatabaseAuditCapture
from app.simulation.reducers import (
    monetary_policy_taylor, monetary_policy_fx_peg, update_output_gap,
    update_inflation, fiscal_update, update_debt, settle_bop, update_fx,
    trade_update, labor_supply_update, security_update, reduce_world,
    register_reducer_impl, list_reducer_implementations, get_reducer_impl,
    RegimeParams
)
from db.models.state import Trigger, TriggerCondition, TriggerAction, PolicyPatch
from app.simulation.trigger_conditions import eval_condition
from app.simulation.trigger_actions import apply_trigger
from app.simulation.triggers import process_triggers, expire_triggers

# Simple test to verify basic functionality works
def test_basic_math():
    """Basic test to verify pytest works."""
    assert 1 + 1 == 2

def test_import_basic_models():
    """Test that basic models can be imported without app startup."""
    from db.models.state import GlobalState, CountryState, Macro
    
    # Create basic instances
    macro = Macro(inflation=0.03, output_gap=0.02)
    country = CountryState(name="TEST", macro=macro)
    state = GlobalState(countries={"TEST": country})
    
    assert state.countries["TEST"].macro.inflation == 0.03
    assert country.name == "TEST"


class TestBasicFunctionality:
    """Test basic functionality without complex imports."""
    
    def test_simple_calculation(self):
        """Test simple economic calculation."""
        # Simple Taylor rule calculation
        inflation = 0.03
        target = 0.02
        neutral_rate = 0.025
        output_gap = 0.01
        
        # Taylor rule: r = r* + π + φ_π(π - π*) + φ_y(y)  
        phi_pi = 0.5
        phi_y = 0.5
        
        rate = neutral_rate + inflation + phi_pi * (inflation - target) + phi_y * output_gap
        
        expected = 0.025 + 0.03 + 0.5 * (0.03 - 0.02) + 0.5 * 0.01
        assert abs(rate - expected) < 0.001
    
    def test_monetary_policy_taylor(self):
        """Test Taylor rule monetary policy implementation."""
        country = CountryState(
            name="USA",
            macro=Macro(
                policy_rate=0.05,
                inflation=0.03,
                output_gap=0.01,
                neutral_rate=0.025,
                inflation_target=0.02
            )
        )
        regimes = RegimeParams()
        audit = AuditCapture("test")
        
        old_rate = country.macro.policy_rate
        monetary_policy_taylor(country, regimes, audit)
        
        assert country.macro.policy_rate != old_rate
        assert len(audit.field_changes) == 1
        assert audit.field_changes[0].field_path == "countries.USA.macro.policy_rate"
    
    def test_monetary_policy_fx_peg(self):
        """Test FX peg monetary policy implementation."""
        country = CountryState(
            name="USA",
            macro=Macro(policy_rate=0.05),
            external=External(fx_rate=1.2)
        )
        regimes = RegimeParams()
        regimes.monetary["peg_target"] = 1.0
        regimes.monetary["peg_strength"] = 2.0
        audit = AuditCapture("test")
        
        old_rate = country.macro.policy_rate
        monetary_policy_fx_peg(country, regimes, audit)
        
        # Rate should increase to defend the peg (fx_rate > target)
        assert country.macro.policy_rate > old_rate
        assert len(audit.field_changes) == 1
    
    def test_update_output_gap(self):
        """Test output gap calculation."""
        country = CountryState(
            name="USA",
            macro=Macro(
                gdp=1000000,
                potential_gdp=950000,
                output_gap=0.0
            )
        )
        regimes = RegimeParams()
        audit = AuditCapture("test")
        
        update_output_gap(country, regimes, audit, demand_shock_pct=2.0)
        
        # Expected gap: (1000000 * 1.02 - 950000) / 950000 = 0.073...
        assert abs(country.macro.output_gap - 0.0737) < 0.001
        assert len(audit.field_changes) == 1
    
    def test_update_inflation(self):
        """Test Phillips curve inflation update."""
        country = CountryState(
            name="USA",
            macro=Macro(
                inflation=0.025,
                output_gap=0.02,
                inflation_target=0.02
            )
        )
        regimes = RegimeParams()
        audit = AuditCapture("test")
        
        old_inflation = country.macro.inflation
        update_inflation(country, regimes, audit, kappa=0.1, beta=0.6)
        
        # Phillips curve target: 0.6*0.02 + 0.1*0.02 = 0.014
        # With dynamics: 0.025 + 0.1 * (0.014 - 0.025) = 0.0239
        assert abs(country.macro.inflation - 0.0239) < 0.001
        assert country.macro.inflation != old_inflation
        assert len(audit.field_changes) == 1
    
    def test_fiscal_update(self):
        """Test fiscal policy update with wealth tax."""
        country = CountryState(
            name="USA",
            macro=Macro(
                gdp=1000000,
                primary_balance=-0.03
            )
        )
        regimes = RegimeParams()
        regimes.fiscal["wealth_tax_rate"] = 0.02
        regimes.fiscal["elasticity_saving"] = -0.3
        audit = AuditCapture("test")
        
        old_balance = country.macro.primary_balance
        fiscal_update(country, regimes, audit)
        
        # Wealth tax should improve primary balance
        assert country.macro.primary_balance > old_balance
        assert len(audit.field_changes) == 1
    
    def test_update_debt(self):
        """Test debt dynamics calculation."""
        country = CountryState(
            name="USA",
            macro=Macro(
                debt_gdp=0.95,
                primary_balance=-0.03,
                gdp=1000000,
                potential_gdp=950000,
                inflation=0.02,
                sfa=0.01
            ),
            finance=Finance(sovereign_yield=0.045)
        )
        regimes = RegimeParams()
        audit = AuditCapture("test")
        
        old_debt = country.macro.debt_gdp
        update_debt(country, regimes, audit)
        
        # Debt should increase (negative primary balance, positive real rate)
        assert country.macro.debt_gdp != old_debt
        assert len(audit.field_changes) == 1
    
    def test_settle_bop(self):
        """Test balance of payments settlement."""
        country = CountryState(
            name="USA",
            macro=Macro(gdp=1000000),
            external=External(
                current_account_gdp=-0.025,
                reserves_usd=150000
            )
        )
        audit = AuditCapture("test")
        
        old_reserves = country.external.reserves_usd
        settle_bop(country, audit)
        
        # Reserves should change based on current account
        assert country.external.reserves_usd != old_reserves
        assert len(audit.field_changes) == 1
    
    def test_update_fx(self):
        """Test FX rate update via UIP."""
        dom_country = CountryState(
            name="CHN",
            macro=Macro(policy_rate=0.035),
            external=External(fx_rate=6.8)
        )
        base_country = CountryState(
            name="USA",
            macro=Macro(policy_rate=0.05)
        )
        regimes = RegimeParams()
        audit = AuditCapture("test")
        
        old_fx = dom_country.external.fx_rate
        update_fx(dom_country, base_country, regimes, audit)
        
        # FX should appreciate (negative interest differential)
        assert dom_country.external.fx_rate < old_fx
        assert len(audit.field_changes) == 1
    
    def test_trade_update(self):
        """Test trade flow updates with tariffs."""
        state = GlobalState(
            base_ccy="USD",
            countries={
                "USA": CountryState(
                    name="USA",
                    trade=Trade(
                        exports_gdp=0.12,
                        imports_gdp=0.15,
                        tariff_mfn_avg=0.05
                    )
                )
            }
        )
        regimes = RegimeParams()
        regimes.trade["tariff_multiplier"] = 2.0
        audit = AuditCapture("test")
        
        old_exports = state.countries["USA"].trade.exports_gdp
        old_imports = state.countries["USA"].trade.imports_gdp
        
        trade_update(state, regimes, audit)
        
        # Trade should decrease due to higher effective tariffs
        assert state.countries["USA"].trade.exports_gdp < old_exports
        assert state.countries["USA"].trade.imports_gdp < old_imports
        assert len(audit.field_changes) == 2
    
    def test_labor_supply_update(self):
        """Test labor supply effects from national service."""
        country = CountryState(
            name="USA",
            macro=Macro(unemployment=0.04)
        )
        regimes = RegimeParams()
        regimes.labor["national_service_pct"] = 2.0
        audit = AuditCapture("test")
        
        old_unemployment = country.macro.unemployment
        labor_supply_update(country, regimes, audit)
        
        # Unemployment should decrease due to national service
        assert country.macro.unemployment < old_unemployment
        assert len(audit.field_changes) == 1
    
    def test_security_update(self):
        """Test military expenditure mobilization effects."""
        country = CountryState(
            name="USA",
            security=Security(milex_gdp=0.035, personnel=1400000)
        )
        regimes = RegimeParams()
        regimes.security["mobilization_intensity"] = 1.5
        audit = AuditCapture("test")
        
        old_milex = country.security.milex_gdp
        old_personnel = country.security.personnel
        
        security_update(country, regimes, audit)
        
        # Both should increase
        assert country.security.milex_gdp > old_milex
        assert country.security.personnel > old_personnel
        assert len(audit.field_changes) == 2
    
    def test_reducer_registry(self):
        """Test reducer implementation registry."""
        def dummy_impl(country, regimes, audit):
            pass
        
        # Test registration
        register_reducer_impl("test_reducer", "dummy", dummy_impl)
        
        # Test listing
        implementations = list_reducer_implementations("test_reducer")
        assert "dummy" in implementations
        
        # Test retrieval
        retrieved = get_reducer_impl("test_reducer", "dummy")
        assert retrieved == dummy_impl
        
        # Test default retrieval
        default = get_reducer_impl("test_reducer")
        assert default == dummy_impl
    
    def test_reduce_world(self):
        """Test complete world reduction."""
        state = GlobalState(
            t=0,
            base_ccy="USD",
            countries={
                "USA": CountryState(
                    name="USA",
                    macro=Macro(
                        gdp=1000000,
                        potential_gdp=950000,
                        inflation=0.025,
                        unemployment=0.04,
                        output_gap=0.053,
                        policy_rate=0.05,
                        neutral_rate=0.025,
                        debt_gdp=0.95,
                        primary_balance=-0.03,
                        inflation_target=0.02
                    ),
                    external=External(
                        fx_rate=1.0,
                        reserves_usd=150000,
                        current_account_gdp=-0.025
                    ),
                    trade=Trade(
                        exports_gdp=0.12,
                        imports_gdp=0.15,
                        tariff_mfn_avg=0.05
                    ),
                    finance=Finance(sovereign_yield=0.045)
                )
            }
        )
        audit = AuditCapture("world_test")
        
        new_state = reduce_world(state, "USA", audit)
        
        # Time should advance
        assert new_state.t == 1
        
        # Should have field changes from multiple reducers
        assert len(audit.field_changes) > 5
        
        # Should have executed multiple reducers
        assert len(audit.reducer_sequence) > 5
        assert "monetary_policy" in audit.reducer_sequence
        assert "fiscal_update" in audit.reducer_sequence


class TestAudit:
    """Test audit system functionality."""
    
    def test_database_audit_capture(self):
        """Test DatabaseAuditCapture functionality."""
        scenario_id = uuid4()
        audit = DatabaseAuditCapture(scenario_id, 1, "test_reducer")
        
        # Test basic properties
        assert audit.scenario_id == scenario_id
        assert audit.timestep == 1
        assert audit.reducer_name == "test_reducer"
        
        # Test adding reducers and triggers
        audit.add_reducer("test_reducer_1")
        audit.add_reducer("test_reducer_2")
        audit.add_trigger_fired("test_trigger")
        audit.add_error("test error")
        
        # Test recording changes
        audit.record_change("test.field", "old", "new", {"detail": "test"})
        
        # Test finalization
        step_audit = audit.finalize()
        
        assert step_audit.scenario_id == scenario_id
        assert step_audit.timestep == 1
        assert len(step_audit.reducer_sequence) == 2
        assert len(step_audit.field_changes) == 1
        assert len(step_audit.triggers_fired) == 1
        assert len(step_audit.errors) == 1
        assert step_audit.step_end_time is not None
    
    @pytest_asyncio.fixture
    async def mock_db_session(self):
        """Mock database session for audit tests."""
        from unittest.mock import AsyncMock
        mock_session = AsyncMock()
        mock_session.add = Mock()
        mock_session.flush = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.execute = AsyncMock()
        return mock_session
    
    async def test_create_audit_log(self, mock_db_session):
        """Test audit log creation in database."""
        from app.simulation.audit import create_audit_log
        from db.models.state import StepAudit, FieldChange
        
        # Create test data
        scenario_id = uuid4()
        step_audit = StepAudit(
            scenario_id=scenario_id,
            timestep=1,
            step_start_time=datetime.utcnow(),
            step_end_time=datetime.utcnow(),
            reducer_sequence=["test_reducer"],
            field_changes=[
                FieldChange(
                    field_path="test.field",
                    old_value="old",
                    new_value="new",
                    reducer_name="test_reducer"
                )
            ],
            triggers_fired=["test_trigger"],
            errors=["test_error"]
        )
        
        simulation_state = SimulationState(
            id=uuid4(),
            scenario_id=scenario_id,
            timestep=1,
            state_data={}
        )
        
        # Mock the audit log ID
        mock_audit_log = Mock()
        mock_audit_log.id = uuid4()
        mock_db_session.add.side_effect = lambda obj: setattr(obj, 'id', uuid4()) if hasattr(obj, 'id') else None
        
        # Test creation
        result = await create_audit_log(step_audit, simulation_state, mock_db_session)
        
        # Verify database interactions
        assert mock_db_session.add.call_count >= 2  # AuditLog + FieldChangeLog
        mock_db_session.flush.assert_called_once()
        mock_db_session.commit.assert_called_once()


class TestTriggerConditions:
    """Test trigger condition evaluation."""
    
    def test_evaluate_simple_condition(self):
        """Test simple condition evaluation."""
        state = GlobalState(
            t=5,
            countries={
                "USA": CountryState(
                    name="USA",
                    macro=Macro(inflation=0.035)
                )
            }
        )
        
        # Test time-based condition
        assert eval_condition(state, "state.t >= 3") == True
        assert eval_condition(state, "state.t < 3") == False
        
        # Test country-based condition
        assert eval_condition(state, "country('USA').macro.inflation > 0.03") == True
        assert eval_condition(state, "country('USA').macro.inflation < 0.03") == False
    
    def test_evaluate_complex_condition(self):
        """Test complex condition with logical operators."""
        state = GlobalState(
            t=5,
            countries={
                "USA": CountryState(
                    name="USA",
                    macro=Macro(inflation=0.035, unemployment=0.08)
                )
            }
        )
        
        # Test AND condition
        condition = "state.t >= 3 && country('USA').macro.inflation > 0.03"
        assert eval_condition(state, condition) == True
        
        # Test OR condition
        condition = "state.t < 3 || country('USA').macro.unemployment > 0.07"
        assert eval_condition(state, condition) == True
    
    def test_evaluate_invalid_condition(self):
        """Test invalid condition handling."""
        state = GlobalState(t=5)
        
        # Invalid syntax should return False
        assert eval_condition(state, "invalid syntax") == False
        assert eval_condition(state, "country('INVALID').macro.gdp > 0") == False


class TestTriggerActions:
    """Test trigger action application."""
    
    def test_apply_policy_patch(self):
        """Test policy patch application."""
        state = GlobalState(
            countries={
                "USA": CountryState(
                    name="USA",
                    macro=Macro(policy_rate=0.05)
                )
            }
        )
        
        action = TriggerAction(
            patches=[
                PolicyPatch(
                    path="countries.USA.macro.policy_rate",
                    op="set",
                    value=0.02
                )
            ]
        )
        audit = AuditCapture("trigger_test")
        
        # Create a trigger to use the apply_trigger function
        trigger = Trigger(
            name="test_trigger",
            condition=TriggerCondition(when="state.t >= 0", once=False),
            action=action
        )
        
        apply_trigger(state, trigger, audit)
        
        assert state.countries["USA"].macro.policy_rate == 0.02
        assert len(audit.field_changes) > 0
    
    def test_apply_add_operation(self):
        """Test addition operation in policy patch."""
        state = GlobalState(
            countries={
                "USA": CountryState(
                    name="USA",
                    macro=Macro(policy_rate=0.05)
                )
            }
        )
        
        action = TriggerAction(
            patches=[
                PolicyPatch(
                    path="countries.USA.macro.policy_rate",
                    op="add",
                    value=0.01
                )
            ]
        )
        audit = AuditCapture("trigger_test")
        
        # Create a trigger to use the apply_trigger function
        trigger = Trigger(
            name="test_trigger",
            condition=TriggerCondition(when="state.t >= 0", once=False),
            action=action
        )
        
        apply_trigger(state, trigger, audit)
        
        assert abs(state.countries["USA"].macro.policy_rate - 0.06) < 0.001
    
    def test_apply_mul_operation(self):
        """Test multiplication operation in policy patch."""
        state = GlobalState(
            countries={
                "USA": CountryState(
                    name="USA",
                    macro=Macro(policy_rate=0.05)
                )
            }
        )
        
        action = TriggerAction(
            patches=[
                PolicyPatch(
                    path="countries.USA.macro.policy_rate",
                    op="mul",
                    value=2.0
                )
            ]
        )
        audit = AuditCapture("trigger_test")
        
        # Create a trigger to use the apply_trigger function
        trigger = Trigger(
            name="test_trigger",
            condition=TriggerCondition(when="state.t >= 0", once=False),
            action=action
        )
        
        apply_trigger(state, trigger, audit)
        
        assert abs(state.countries["USA"].macro.policy_rate - 0.1) < 0.001


class TestTriggerProcessing:
    """Test trigger processing system."""
    
    def test_process_triggers_basic(self):
        """Test basic trigger processing."""
        state = GlobalState(
            t=5,
            countries={
                "USA": CountryState(
                    name="USA",
                    macro=Macro(inflation=0.035)
                )
            }
        )
        
        triggers = [
            Trigger(
                name="inflation_shock",
                condition=TriggerCondition(when="t >= 3", once=True),
                action=TriggerAction(
                    patches=[
                        PolicyPatch(
                            path="countries.USA.macro.policy_rate",
                            op="set",
                            value=0.06
                        )
                    ]
                )
            )
        ]
        
        fired_triggers = set()
        audit = AuditCapture("trigger_test")
        
        newly_fired = process_triggers(state, triggers, fired_triggers, audit)
        
        assert "inflation_shock" in newly_fired
        assert len(newly_fired) == 1
    
    def test_process_triggers_once_only(self):
        """Test once-only trigger behavior."""
        state = GlobalState(t=5)
        
        triggers = [
            Trigger(
                name="once_trigger",
                condition=TriggerCondition(when="t >= 3", once=True),
                action=TriggerAction(patches=[])
            )
        ]
        
        fired_triggers = {"once_trigger"}
        audit = AuditCapture("trigger_test")
        
        newly_fired = process_triggers(state, triggers, fired_triggers, audit)
        
        # Should not fire again
        assert len(newly_fired) == 0
    
    def test_expire_triggers(self):
        """Test trigger expiration."""
        state = GlobalState(t=10)
        
        triggers = [
            Trigger(
                name="expiring_trigger",
                condition=TriggerCondition(when="t >= 3", once=True),
                action=TriggerAction(patches=[]),
                expires_after_turns=5
            )
        ]
        
        fired_trigger_times = {"expiring_trigger": 5}  # Fired at turn 5
        
        expired = expire_triggers(state, triggers, fired_trigger_times)
        
        # Should be expired (current turn 10, fired at 5, expires after 5 turns)
        assert "expiring_trigger" in expired
