"""Pydantic models for economic simulation state and audit trail."""

from typing import Optional, Dict, Any, List, Literal, Tuple
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# Economic state slices
class Macro(BaseModel):
    """Macroeconomic indicators for a country."""
    gdp: Optional[float] = None
    potential_gdp: Optional[float] = None
    inflation: Optional[float] = None
    unemployment: Optional[float] = None
    output_gap: Optional[float] = None
    primary_balance: Optional[float] = None
    debt_gdp: Optional[float] = None
    neutral_rate: Optional[float] = None
    policy_rate: Optional[float] = None
    inflation_target: float = 0.02
    sfa: float = 0.0  # Stock-flow adjustment


class External(BaseModel):
    """External sector indicators for a country."""
    fx_rate: Optional[float] = None
    reserves_usd: Optional[float] = None
    current_account_gdp: Optional[float] = None
    net_errors_omissions_gdp: float = 0.0


class Finance(BaseModel):
    """Financial sector indicators for a country."""
    sovereign_yield: Optional[float] = None
    credit_spread: Optional[float] = None
    bank_tier1_ratio: Optional[float] = None
    leverage_target: float = 10.0


class Trade(BaseModel):
    """Trade sector indicators for a country."""
    exports_gdp: Optional[float] = None
    imports_gdp: Optional[float] = None
    tariff_mfn_avg: Optional[float] = None
    ntm_index: Optional[float] = None
    terms_of_trade: float = 1.0


class EnergyFood(BaseModel):
    """Energy and food sector indicators for a country."""
    energy_stock_to_use: Optional[float] = None
    food_price_index: Optional[float] = None
    energy_price_index: Optional[float] = None


class Security(BaseModel):
    """Security and defense indicators for a country."""
    milex_gdp: Optional[float] = None
    personnel: Optional[int] = None
    conflict_intensity: Optional[float] = None


class Sentiment(BaseModel):
    """Sentiment and social indicators for a country."""
    gdelt_tone: Optional[float] = None
    trends_salience: Optional[float] = None
    policy_pressure: Optional[float] = None
    approval: Optional[float] = None


class CountryState(BaseModel):
    """Complete state for a single country across all economic domains."""
    name: str
    macro: Macro = Field(default_factory=Macro)
    external: External = Field(default_factory=External)
    finance: Finance = Field(default_factory=Finance)
    trade: Trade = Field(default_factory=Trade)
    energy: EnergyFood = Field(default_factory=EnergyFood)
    security: Security = Field(default_factory=Security)
    sentiment: Sentiment = Field(default_factory=Sentiment)


# Cross-country matrices stored as JSON
Matrix = Dict[str, Dict[str, float]]


# Regime parameters for policy-aware reducers
class RegimeParams(BaseModel):
    """Policy regime parameters that control reducer behavior."""
    monetary: Dict[str, Any] = Field(
        default_factory=lambda: {"rule": "taylor", "phi_pi": 0.5, "phi_y": 0.5}
    )
    fx: Dict[str, Any] = Field(
        default_factory=lambda: {"uip_rho_base": 0.0}
    )
    fiscal: Dict[str, Any] = Field(
        default_factory=lambda: {"wealth_tax_rate": 0.0, "elasticity_saving": -0.3}
    )
    trade: Dict[str, Any] = Field(
        default_factory=lambda: {"tariff_multiplier": 1.0, "ntm_shock": 0.0}
    )
    security: Dict[str, Any] = Field(
        default_factory=lambda: {"mobilization_intensity": 0.0}
    )
    labor: Dict[str, Any] = Field(
        default_factory=lambda: {"national_service_pct": 0.0}
    )
    sentiment: Dict[str, Any] = Field(
        default_factory=lambda: {"propaganda_gain": 0.0}
    )


class SimulationRules(BaseModel):
    """Simulation rules and configuration parameters."""
    regimes: RegimeParams = Field(default_factory=RegimeParams)
    rng_seed: int = 42
    invariants: Dict[str, bool] = Field(
        default_factory=lambda: {"bmp6": True, "sfc_light": True}
    )


class GlobalState(BaseModel):
    """Complete global economic simulation state."""
    model_config = ConfigDict(extra='allow')
    
    t: int = 0
    base_ccy: str = "USD"
    countries: Dict[str, CountryState] = Field(default_factory=dict)
    trade_matrix: Matrix = Field(default_factory=dict)
    interbank_matrix: Matrix = Field(default_factory=dict)
    alliance_graph: Matrix = Field(default_factory=dict)
    sanctions: Matrix = Field(default_factory=dict)
    io_coefficients: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    commodity_prices: Dict[str, float] = Field(default_factory=dict)
    rules: SimulationRules = Field(default_factory=SimulationRules)
    events: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=lambda: {"pending": [], "processed": []}
    )


# Audit trail models
class FieldChange(BaseModel):
    """Record of a single field change during simulation step."""
    field_path: str  # e.g., "countries.USA.macro.policy_rate"
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    reducer_name: str  # e.g., "taylor_rule"
    reducer_params: Dict[str, Any] = Field(default_factory=dict)
    calculation_details: Dict[str, Any] = Field(default_factory=dict)  # intermediate steps


class StepAudit(BaseModel):
    """Complete audit record for a simulation step."""
    scenario_id: UUID
    timestep: int
    step_start_time: datetime
    step_end_time: datetime
    reducer_sequence: List[str]  # ordered list of reducers applied
    field_changes: List[FieldChange]
    triggers_fired: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


# Trigger system models
class PolicyPatch(BaseModel):
    """Policy parameter modification."""
    path: str  # dotpath into state or rules, e.g. "rules.regimes.trade.tariff_multiplier"
    op: Literal["set", "add", "mul"]
    value: Any


class ReducerOverride(BaseModel):
    """Reducer implementation override."""
    target: str  # e.g., "monetary_policy", "fx_drift", "trade_update"
    impl_name: str  # e.g., "taylor_rule_v1" -> "fx_peg_v1"


class NetworkRewrite(BaseModel):
    """Network/matrix modification."""
    layer: Literal["trade", "alliances", "sanctions", "interbank", "energy"]
    edits: List[Tuple[str, str, float]]  # e.g., [("USA","CHN", 0.9)] set weight/intensity


class EventInject(BaseModel):
    """Event injection for scenario dynamics."""
    kind: Literal["conflict", "disaster", "strike", "embargo", "mobilization"]
    payload: Dict[str, Any]  # free-form payload consumed by events reducer


class TriggerCondition(BaseModel):
    """Condition for trigger activation."""
    when: Optional[str] = None  # simple DSL: "date>=2026-01-01 && country('USA').macro.inflation>0.05"
    once: bool = True


class TriggerAction(BaseModel):
    """Actions to execute when trigger fires."""
    patches: List[PolicyPatch] = Field(default_factory=list)
    overrides: List[ReducerOverride] = Field(default_factory=list)
    network_rewrites: List[NetworkRewrite] = Field(default_factory=list)
    events: List[EventInject] = Field(default_factory=list)


class Trigger(BaseModel):
    """Complete trigger definition."""
    name: str
    condition: TriggerCondition
    action: TriggerAction
    expires_after_turns: Optional[int] = None  # policies sunset
    description: Optional[str] = None


class TriggerLog(BaseModel):
    """Log record of trigger execution."""
    fired_at_turn: int
    trigger_name: str
    actions_applied: Dict[str, int]  # counts by action kind


# API Request/Response models
class ScenarioCreate(BaseModel):
    """Request model for creating a new scenario."""
    name: str
    description: Optional[str] = None
    initial_state: GlobalState
    triggers: List[Trigger] = Field(default_factory=list)


class ScenarioUpdate(BaseModel):
    """Request model for updating an existing scenario."""
    name: Optional[str] = None
    description: Optional[str] = None
    triggers: Optional[List[Trigger]] = None


class ScenarioResponse(BaseModel):
    """Response model for scenario information."""
    id: UUID
    name: str
    description: Optional[str]
    user_id: UUID
    current_timestep: int
    created_at: datetime
    updated_at: datetime
    triggers_count: int
    current_state: Optional[GlobalState] = None


class SimulationStepResponse(BaseModel):
    """Response model for simulation step results."""
    id: UUID
    scenario_id: UUID
    timestep: int
    state: GlobalState
    audit: StepAudit
    created_at: datetime


class AuditQueryResponse(BaseModel):
    """Response model for audit queries."""
    scenario_id: UUID
    timestep_range: Tuple[int, int]
    field_changes: List[FieldChange]
    summary: Dict[str, Any]  # aggregated stats


# Audit capture context for reducers
class AuditCapture:
    """Context manager for capturing field changes during reducer execution."""
    
    def __init__(self, reducer_name: str, reducer_params: Dict[str, Any] = None):
        self.reducer_name = reducer_name
        self.reducer_params = reducer_params or {}
        self.field_changes: List[FieldChange] = []
        self.calculation_details: Dict[str, Any] = {}
        self.reducer_sequence: List[str] = []
        self.triggers_fired: List[str] = []
        self.errors: List[str] = []
    
    def record_change(
        self,
        field_path: str,
        old_value: Any,
        new_value: Any,
        calculation_details: Dict[str, Any] = None
    ):
        """Record a field change with audit information."""
        change = FieldChange(
            field_path=field_path,
            old_value=old_value,
            new_value=new_value,
            reducer_name=self.reducer_name,
            reducer_params=self.reducer_params.copy(),
            calculation_details=calculation_details or {}
        )
        self.field_changes.append(change)
    
    def add_calculation_detail(self, key: str, value: Any):
        """Add calculation detail for transparency."""
        self.calculation_details[key] = value
    
    def add_reducer(self, reducer_name: str):
        """Add a reducer to the execution sequence."""
        self.reducer_sequence.append(reducer_name)
    
    def add_trigger_fired(self, trigger_name: str):
        """Record that a trigger was fired."""
        self.triggers_fired.append(trigger_name)
    
    def add_error(self, error_message: str):
        """Record an error during execution."""
        self.errors.append(error_message)
    
    def get_changes(self) -> List[FieldChange]:
        """Get all recorded field changes."""
        return self.field_changes.copy()
