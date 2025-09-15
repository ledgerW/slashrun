# Implementation Plan

## [Overview]
Build a comprehensive simulation framework API with database persistence for economic scenario modeling and time-step progression.

This implementation creates a FastAPI backend service that supports creation, management, and execution of economic simulation scenarios based on the GlobalState model described in simulation_state.md. The system will allow users to create scenarios with initial state data, step through time progressions using reducer functions, and persist every simulation state for analysis. The framework supports both minimal viable scenarios with core economic indicators and comprehensive scenarios with full data sets across macro, trade, finance, energy, security, and sentiment dimensions.

## [Types]
Define comprehensive Pydantic models for the economic simulation state, audit trail, trigger system, and supporting data structures.

**Core State Models:**
```python
# Economic state slices
class Macro(BaseModel):
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
    sfa: float = 0.0

class External(BaseModel):
    fx_rate: Optional[float] = None
    reserves_usd: Optional[float] = None
    current_account_gdp: Optional[float] = None
    net_errors_omissions_gdp: float = 0.0

class Finance(BaseModel):
    sovereign_yield: Optional[float] = None
    credit_spread: Optional[float] = None
    bank_tier1_ratio: Optional[float] = None
    leverage_target: float = 10.0

class Trade(BaseModel):
    exports_gdp: Optional[float] = None
    imports_gdp: Optional[float] = None
    tariff_mfn_avg: Optional[float] = None
    ntm_index: Optional[float] = None
    terms_of_trade: float = 1.0

class EnergyFood(BaseModel):
    energy_stock_to_use: Optional[float] = None
    food_price_index: Optional[float] = None
    energy_price_index: Optional[float] = None

class Security(BaseModel):
    milex_gdp: Optional[float] = None
    personnel: Optional[int] = None
    conflict_intensity: Optional[float] = None

class Sentiment(BaseModel):
    gdelt_tone: Optional[float] = None
    trends_salience: Optional[float] = None
    policy_pressure: Optional[float] = None
    approval: Optional[float] = None

class CountryState(BaseModel):
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
    monetary: Dict[str, Any] = Field(default_factory=lambda: {"rule":"taylor","phi_pi":0.5,"phi_y":0.5})
    fx: Dict[str, Any] = Field(default_factory=lambda: {"uip_rho_base":0.0})
    fiscal: Dict[str, Any] = Field(default_factory=lambda: {"wealth_tax_rate":0.0,"elasticity_saving":-0.3})
    trade: Dict[str, Any] = Field(default_factory=lambda: {"tariff_multiplier":1.0,"ntm_shock":0.0})
    security: Dict[str, Any] = Field(default_factory=lambda: {"mobilization_intensity":0.0})
    labor: Dict[str, Any] = Field(default_factory=lambda: {"national_service_pct":0.0})
    sentiment: Dict[str, Any] = Field(default_factory=lambda: {"propaganda_gain":0.0})

class SimulationRules(BaseModel):
    regimes: RegimeParams = Field(default_factory=RegimeParams)
    rng_seed: int = 42
    invariants: Dict[str, bool] = Field(default_factory=lambda: {"bmp6": True, "sfc_light": True})

class GlobalState(BaseModel):
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
    events: Dict[str, List[Dict[str, Any]]] = Field(default_factory=lambda: {"pending": [], "processed": []})
```

**Audit Trail Models:**
```python
class FieldChange(BaseModel):
    field_path: str  # e.g., "countries.USA.macro.policy_rate"
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    reducer_name: str  # e.g., "taylor_rule"
    reducer_params: Dict[str, Any] = Field(default_factory=dict)
    calculation_details: Dict[str, Any] = Field(default_factory=dict)  # intermediate steps

class StepAudit(BaseModel):
    scenario_id: UUID
    timestep: int
    step_start_time: datetime
    step_end_time: datetime
    reducer_sequence: List[str]  # ordered list of reducers applied
    field_changes: List[FieldChange]
    triggers_fired: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
```

**Trigger System Models:**
```python
class PolicyPatch(BaseModel):
    path: str  # dotpath into state or rules, e.g. "rules.regimes.trade.tariff_multiplier"
    op: Literal["set", "add", "mul"]
    value: Any

class ReducerOverride(BaseModel):
    target: str  # e.g., "monetary_policy", "fx_drift", "trade_update"
    impl_name: str  # e.g., "taylor_rule_v1" -> "fx_peg_v1"

class NetworkRewrite(BaseModel):
    layer: Literal["trade", "alliances", "sanctions", "interbank", "energy"]
    edits: List[Tuple[str, str, float]]  # e.g., [("USA","CHN", 0.9)] set weight/intensity

class EventInject(BaseModel):
    kind: Literal["conflict", "disaster", "strike", "embargo", "mobilization"]
    payload: Dict[str, Any]  # free-form payload consumed by events reducer

class TriggerCondition(BaseModel):
    when: Optional[str] = None  # simple DSL: "date>=2026-01-01 && country('USA').macro.inflation>0.05"
    once: bool = True

class TriggerAction(BaseModel):
    patches: List[PolicyPatch] = Field(default_factory=list)
    overrides: List[ReducerOverride] = Field(default_factory=list)
    network_rewrites: List[NetworkRewrite] = Field(default_factory=list)
    events: List[EventInject] = Field(default_factory=list)

class Trigger(BaseModel):
    name: str
    condition: TriggerCondition
    action: TriggerAction
    expires_after_turns: Optional[int] = None  # policies sunset
    description: Optional[str] = None

class TriggerLog(BaseModel):
    fired_at_turn: int
    trigger_name: str
    actions_applied: Dict[str, int]  # counts by action kind
```

**API Request/Response Models:**
```python
class ScenarioCreate(BaseModel):
    name: str
    description: Optional[str] = None
    initial_state: GlobalState
    triggers: List[Trigger] = Field(default_factory=list)
    
class ScenarioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    triggers: Optional[List[Trigger]] = None
    
class ScenarioResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    user_id: UUID
    current_timestep: int
    created_at: datetime
    updated_at: datetime
    triggers_count: int
    
class SimulationStepResponse(BaseModel):
    id: UUID
    scenario_id: UUID
    timestep: int
    state: GlobalState
    audit: StepAudit
    created_at: datetime

class AuditQueryResponse(BaseModel):
    scenario_id: UUID
    timestep_range: Tuple[int, int]
    field_changes: List[FieldChange]
    summary: Dict[str, Any]  # aggregated stats
```

## [Files]
Create new files for simulation models, API endpoints, and database schemas.

**New Files:**
- `app/models/simulation.py` - SQLModel database models for scenarios and simulation states
- `app/models/audit.py` - SQLModel database models for audit trail and step auditing
- `app/models/trigger.py` - SQLModel database models for triggers and trigger logs
- `app/models/user.py` - Move user models from backend/api/auth.py to proper location
- `app/api/simulation.py` - FastAPI endpoints for scenario management and simulation execution
- `app/api/audit.py` - FastAPI endpoints for audit trail queries and analysis
- `app/api/trigger.py` - FastAPI endpoints for trigger management
- `app/core/config.py` - Application configuration settings
- `app/core/database.py` - Database connection and session management
- `app/simulation/state.py` - GlobalState model and country state definitions
- `app/simulation/reducers.py` - Regime-aware reducer functions for state transitions
- `app/simulation/audit.py` - Audit trail capture and field change tracking
- `app/simulation/triggers.py` - Trigger engine for policy changes and regime switches
- `app/main.py` - FastAPI application entry point
- `alembic/versions/001_initial_migration.py` - Database migration for initial schema
- `alembic.ini` - Alembic configuration
- `alembic/env.py` - Alembic environment setup
- `data/triggers/examples/` - Example trigger configurations (US tariff shock, wealth tax, etc.)

**Modified Files:**
- `backend/api/auth.py` - Update imports to use new model locations
- `docker-compose.yml` - Add database initialization script reference
- `pyproject.toml` - Add alembic dependency if not present

**File Structure:**
```
app/
├── main.py
├── api/
│   ├── __init__.py
│   ├── auth.py (moved from backend/api/auth.py)
│   └── simulation.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   └── database.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── simulation.py
└── simulation/
    ├── __init__.py
    ├── state.py
    └── reducers.py
alembic/
├── env.py
├── versions/
└── alembic.ini
db/
└── init.sql
```

## [Functions]
Implement core simulation logic, database operations, and API endpoints.

**Core Regime-Aware Reducer Functions (app/simulation/reducers.py):**
- `taylor_rule(m: Macro, regimes: RegimeParams, phi_pi: float = 0.5, phi_y: float = 0.5) -> float` - Federal Reserve Taylor rule with regime parameters
- `monetary_policy_taylor(country: CountryState, regimes: RegimeParams, audit: AuditCapture) -> None` - Taylor rule monetary policy implementation
- `monetary_policy_fx_peg(country: CountryState, regimes: RegimeParams, audit: AuditCapture) -> None` - FX peg monetary policy implementation
- `update_output_gap(country: CountryState, regimes: RegimeParams, audit: AuditCapture, demand_shock_pct: float = 0.0) -> None` - Calculate output gap changes with audit trail
- `update_inflation(country: CountryState, regimes: RegimeParams, audit: AuditCapture, kappa: float = 0.1, beta: float = 0.6) -> None` - New-Keynesian Phillips Curve inflation dynamics with audit
- `fiscal_update(country: CountryState, regimes: RegimeParams, audit: AuditCapture) -> None` - Government finances including wealth tax and elasticities  
- `update_debt(country: CountryState, regimes: RegimeParams, audit: AuditCapture) -> None` - IMF debt dynamics calculations with audit
- `settle_bop(country: CountryState, audit: AuditCapture) -> None` - Balance of payments identity closure with audit
- `update_fx(dom: CountryState, base: CountryState, regimes: RegimeParams, audit: AuditCapture, rho: float = 0.0) -> None` - Uncovered Interest Parity FX updates
- `trade_update(state: GlobalState, regimes: RegimeParams, audit: AuditCapture) -> None` - Trade flows with tariff/NTM regime parameters
- `fire_sale_step(state: GlobalState, regimes: RegimeParams, audit: AuditCapture, price_impact: float = 0.05) -> None` - Financial contagion modeling
- `interbank_loss_step(state: GlobalState, regimes: RegimeParams, audit: AuditCapture, default_threshold: float = 0.06) -> None` - Banking sector stress propagation
- `social_belief_step(state: GlobalState, regimes: RegimeParams, audit: AuditCapture, alpha_tone=0.02, alpha_trend=0.01, decay=0.9) -> None` - DeGroot belief updating
- `unrest_hazard_step(state: GlobalState, regimes: RegimeParams, audit: AuditCapture, a=0.5, b=0.8, c=0.6, decay=0.8) -> None` - Hawkes process for conflict dynamics
- `energy_food_step(ctry: CountryState, regimes: RegimeParams, audit: AuditCapture) -> None` - Commodity price and inventory updates
- `labor_supply_update(country: CountryState, regimes: RegimeParams, audit: AuditCapture) -> None` - Labor supply effects from national service
- `security_update(country: CountryState, regimes: RegimeParams, audit: AuditCapture) -> None` - Military expenditure and mobilization effects
- `reduce_world(state: GlobalState, base_ccy_country: str, audit: AuditCapture) -> GlobalState` - Master world-level turn reducer with audit trail

**Audit Trail Functions (app/simulation/audit.py):**
- `AuditCapture.__init__(scenario_id: UUID, timestep: int)` - Initialize audit capture for simulation step
- `AuditCapture.capture_field_change(field_path: str, old_value: Any, new_value: Any, reducer_name: str, params: Dict, details: Dict) -> None` - Record field change with calculation details
- `AuditCapture.add_reducer(reducer_name: str) -> None` - Add reducer to execution sequence
- `AuditCapture.add_trigger_fired(trigger_name: str) -> None` - Record trigger activation
- `AuditCapture.add_error(error_msg: str) -> None` - Record error during step execution
- `AuditCapture.finalize() -> StepAudit` - Complete audit trail and return StepAudit object
- `create_audit_log(audit: StepAudit, db: AsyncSession) -> AuditLog` - Store audit trail in database

**Trigger Engine Functions (app/simulation/triggers.py):**
- `eval_condition(state: GlobalState, condition: str) -> bool` - Evaluate trigger condition using simple DSL
- `apply_policy_patch(state: GlobalState, patch: PolicyPatch, audit: AuditCapture) -> None` - Apply policy parameter changes
- `apply_reducer_override(state: GlobalState, override: ReducerOverride, audit: AuditCapture) -> None` - Switch reducer implementations  
- `apply_network_rewrite(state: GlobalState, rewrite: NetworkRewrite, audit: AuditCapture) -> None` - Modify network layer weights/connections
- `inject_event(state: GlobalState, event: EventInject, audit: AuditCapture) -> None` - Add event to pending queue
- `apply_trigger(state: GlobalState, trigger: Trigger, audit: AuditCapture) -> bool` - Execute all trigger actions, return success
- `process_triggers(state: GlobalState, triggers: List[Trigger], fired_triggers: Set[str], audit: AuditCapture) -> List[str]` - Process all triggers, return newly fired trigger names
- `expire_triggers(state: GlobalState, triggers: List[Trigger], fired_triggers: Dict[str, int]) -> List[str]` - Remove expired triggers, return expired trigger names
- `load_trigger_examples() -> Dict[str, Trigger]` - Load example trigger configurations from data/triggers/examples/

**Reducer Registry Functions (app/simulation/reducers.py):**
- `get_reducer_impl(reducer_type: str, impl_name: Optional[str] = None) -> Callable` - Get reducer implementation by type and name
- `register_reducer_impl(reducer_type: str, impl_name: str, impl_func: Callable) -> None` - Register new reducer implementation
- `list_reducer_implementations(reducer_type: str) -> List[str]` - List available implementations for reducer type

**API Endpoint Functions (app/api/simulation.py):**
- `create_scenario(scenario_data: ScenarioCreate, current_user: User, db: AsyncSession) -> ScenarioResponse` - Create new simulation scenario
- `get_scenarios(current_user: User, db: AsyncSession) -> List[ScenarioResponse]` - List user's scenarios
- `get_scenario(scenario_id: UUID, current_user: User, db: AsyncSession) -> ScenarioResponse` - Get specific scenario
- `update_scenario(scenario_id: UUID, updates: ScenarioUpdate, current_user: User, db: AsyncSession) -> ScenarioResponse` - Update scenario metadata
- `delete_scenario(scenario_id: UUID, current_user: User, db: AsyncSession) -> Dict[str, str]` - Delete scenario and all states
- `step_simulation(scenario_id: UUID, current_user: User, db: AsyncSession) -> SimulationStepResponse` - Execute one simulation step
- `get_simulation_state(scenario_id: UUID, timestep: int, current_user: User, db: AsyncSession) -> SimulationStepResponse` - Get state at specific timestep
- `get_simulation_history(scenario_id: UUID, current_user: User, db: AsyncSession) -> List[SimulationStepResponse]` - Get all simulation states for scenario

**Database Helper Functions (app/models/simulation.py):**
- `get_latest_state(scenario_id: UUID, db: AsyncSession) -> Optional[SimulationState]` - Get most recent state for scenario
- `create_simulation_state(scenario_id: UUID, timestep: int, state_data: GlobalState, db: AsyncSession) -> SimulationState` - Store new simulation state

## [Classes]
Define SQLModel classes for database persistence and API models.

**Database Models (app/models/simulation.py):**
```python
class Scenario(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=200, index=True)
    description: Optional[str] = Field(default=None, max_length=2000)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    current_timestep: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    states: List["SimulationState"] = Relationship(back_populates="scenario", cascade_delete=True)
    audit_logs: List["AuditLog"] = Relationship(back_populates="scenario", cascade_delete=True)
    triggers: List["ScenarioTrigger"] = Relationship(back_populates="scenario", cascade_delete=True)
    user: "User" = Relationship(back_populates="scenarios")

class SimulationState(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(foreign_key="scenario.id", index=True)
    timestep: int = Field(index=True)
    state_data: Dict[str, Any] = Field(sa_column=Column(JSON))  # Stored as JSON
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    scenario: Scenario = Relationship(back_populates="states")
    audit_log: Optional["AuditLog"] = Relationship(back_populates="simulation_state")
    
    # Composite unique constraint on scenario_id + timestep
    __table_args__ = (UniqueConstraint("scenario_id", "timestep"),)
```

**Audit Trail Database Models (app/models/audit.py):**
```python
class AuditLog(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(foreign_key="scenario.id", index=True)
    timestep: int = Field(index=True)
    step_start_time: datetime = Field(default_factory=datetime.utcnow)
    step_end_time: datetime = Field(default_factory=datetime.utcnow)
    reducer_sequence: List[str] = Field(sa_column=Column(JSON))
    triggers_fired: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    errors: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    scenario: Scenario = Relationship(back_populates="audit_logs")
    simulation_state: Optional["SimulationState"] = Relationship(back_populates="audit_log")
    field_changes: List["FieldChangeLog"] = Relationship(back_populates="audit_log", cascade_delete=True)
    
    # Composite unique constraint on scenario_id + timestep
    __table_args__ = (UniqueConstraint("scenario_id", "timestep"),)

class FieldChangeLog(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    audit_log_id: UUID = Field(foreign_key="auditlog.id", index=True)
    field_path: str = Field(max_length=500, index=True)
    old_value: Optional[str] = Field(default=None)  # JSON serialized
    new_value: Optional[str] = Field(default=None)  # JSON serialized
    reducer_name: str = Field(max_length=100, index=True)
    reducer_params: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    calculation_details: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    audit_log: AuditLog = Relationship(back_populates="field_changes")
```

**Trigger Database Models (app/models/trigger.py):**
```python
class ScenarioTrigger(SQLModel, table=True):
    __tablename__ = "scenario_trigger"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(foreign_key="scenario.id", index=True)
    name: str = Field(max_length=200, index=True)
    description: Optional[str] = Field(default=None, max_length=2000)
    condition_when: Optional[str] = Field(default=None, max_length=1000)
    condition_once: bool = Field(default=True)
    expires_after_turns: Optional[int] = Field(default=None)
    
    # Trigger actions stored as JSON
    patches: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    overrides: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    network_rewrites: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    events: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    scenario: Scenario = Relationship(back_populates="triggers")
    trigger_logs: List["TriggerLog"] = Relationship(back_populates="trigger", cascade_delete=True)

class TriggerLog(SQLModel, table=True):
    __tablename__ = "trigger_log"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    trigger_id: UUID = Field(foreign_key="scenario_trigger.id", index=True)
    scenario_id: UUID = Field(foreign_key="scenario.id", index=True)
    fired_at_turn: int = Field(index=True)
    actions_applied: Dict[str, int] = Field(sa_column=Column(JSON))  # counts by action kind
    success: bool = Field(default=True)
    error_message: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships  
    trigger: ScenarioTrigger = Relationship(back_populates="trigger_logs")
    scenario: Scenario = Relationship()
    
    # Composite unique constraint on trigger_id + fired_at_turn for once-only triggers
    __table_args__ = (Index("idx_trigger_turn", "trigger_id", "fired_at_turn"),)
```

**User Model Updates (app/models/user.py):**
```python
class User(SQLModel, table=True):
    # ... existing fields ...
    
    # Add relationship to scenarios
    scenarios: List["Scenario"] = Relationship(back_populates="user")
```

**Audit Capture Helper Class (app/simulation/audit.py):**
```python
class AuditCapture:
    def __init__(self, scenario_id: UUID, timestep: int):
        self.scenario_id = scenario_id
        self.timestep = timestep
        self.step_start_time = datetime.utcnow()
        self.reducer_sequence: List[str] = []
        self.field_changes: List[FieldChange] = []
        self.triggers_fired: List[str] = []
        self.errors: List[str] = []
    
    def capture_field_change(
        self, 
        field_path: str, 
        old_value: Any, 
        new_value: Any, 
        reducer_name: str, 
        params: Dict[str, Any] = None, 
        details: Dict[str, Any] = None
    ) -> None:
        change = FieldChange(
            field_path=field_path,
            old_value=old_value,
            new_value=new_value,
            reducer_name=reducer_name,
            reducer_params=params or {},
            calculation_details=details or {}
        )
        self.field_changes.append(change)
    
    def add_reducer(self, reducer_name: str) -> None:
        self.reducer_sequence.append(reducer_name)
    
    def add_trigger_fired(self, trigger_name: str) -> None:
        self.triggers_fired.append(trigger_name)
    
    def add_error(self, error_msg: str) -> None:
        self.errors.append(error_msg)
    
    def finalize(self) -> StepAudit:
        return StepAudit(
            scenario_id=self.scenario_id,
            timestep=self.timestep,
            step_start_time=self.step_start_time,
            step_end_time=datetime.utcnow(),
            reducer_sequence=self.reducer_sequence,
            field_changes=self.field_changes,
            triggers_fired=self.triggers_fired,
            errors=self.errors
        )
```

**Configuration Class (app/core/config.py):**
```python
class Settings(BaseSettings):
    app_name: str = "SlashRun Simulation API"
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## [Dependencies]
Add database migration tools and ensure all required packages are available.

**Add to pyproject.toml dependencies:**
- `alembic>=1.13.0` - Database migrations (if not present)

**Verify existing dependencies are sufficient:**
- `sqlmodel>=0.0.24` ✓
- `asyncpg>=0.30.0` ✓  
- `pydantic>=2.11.7` ✓
- `fastapi>=0.116.1` ✓
- `uvicorn>=0.35.0` ✓

All required dependencies are already present in pyproject.toml.

## [Testing]
Create unit tests for simulation logic and API endpoints.

**Test Files to Create:**
- `tests/test_simulation_reducers.py` - Test all reducer functions with various economic scenarios
- `tests/test_simulation_api.py` - Test API endpoints for CRUD operations and simulation stepping
- `tests/test_simulation_models.py` - Test database models and constraints
- `tests/conftest.py` - Pytest fixtures for database and authentication

**Testing Approach:**
- Unit tests for individual reducer functions using known economic data
- Integration tests for complete simulation stepping workflow  
- API tests using FastAPI TestClient with authenticated requests
- Database tests with temporary test database using pytest fixtures

## [Data Sources]
Comprehensive mapping of data sources to GlobalState fields with API endpoints and fallback strategies.

### Minimum Viable Scenario (MVS) Template
4-10 countries with essential economic indicators for basic simulation functionality:

```json
{
  "t": 0,
  "base_ccy": "USD",
  "countries": {
    "USA": {
      "name": "USA",
      "macro": {
        "gdp": 0,                 // WDI GDP current LCU (NY.GDP.MKTP.CN) or USD (NY.GDP.MKTP.CD)
        "potential_gdp": 0,       // Est: HP-filter trend of GDP; or OECD potential if available
        "inflation": 0.0,         // CPI YoY (FP.CPI.TOTL.ZG, % -> /100)
        "unemployment": 0.0,      // ILOSTAT/WDI unemployment rate (SL.UEM.TOTL.ZS -> /100)
        "output_gap": 0.0,        // Start ~0 if using potential trend; else (GDP - Pot)/Pot
        "primary_balance": 0.0,   // IMF WEO/IFS if available; else gov balance - interest (approx)
        "debt_gdp": 0.0,          // General gov gross debt % GDP (WDI or IMF WEO)
        "neutral_rate": 0.02,     // Calibrate (e.g., Laubach-Williams proxy), else 2%
        "policy_rate": 0.0,       // IFS policy/overnight; or FRED series (e.g., FEDFUNDS)
        "inflation_target": 0.02,
        "sfa": 0.0
      },
      "external": {
        "fx_rate": 1.0,           // Base currency = USD; others: FRED H.10 or IFS XR
        "reserves_usd": 0.0,      // IFS Reserves (USD bn)
        "current_account_gdp": 0.0 // CA % GDP (BPM6) via IMF Data Portal/IFS
      },
      "finance": {
        "sovereign_yield": 0.0,   // FRED (e.g., DGS10) or local MoF series
        "credit_spread": 0.0,     // Sovereign z-spread vs base; est: y10 - policy if needed
        "bank_tier1_ratio": 0.12, // Start 12% if unknown
        "leverage_target": 10.0
      },
      "trade": {
        "exports_gdp": 0.0,       // WDI NE.EXP.GNFS.ZS (% GDP -> /100)
        "imports_gdp": 0.0,       // WDI NE.IMP.GNFS.ZS (% GDP -> /100)
        "tariff_mfn_avg": 0.0,    // WITS/TRAINS MFN simple avg; fallback 3–10% by income grp
        "ntm_index": 0.2,         // Fallback 0.2 if unknown (0..1)
        "terms_of_trade": 1.0
      },
      "energy": {
        "energy_stock_to_use": 1.0,   // Est: inventories/consumption from IEA/Energy Institute aggregates
        "food_price_index": 120.0,    // FAO FFPI level (latest)
        "energy_price_index": 100.0   // World Bank/IMF commodity basket baseline if used
      },
      "security": {
        "milex_gdp": 0.0,         // SIPRI milex % GDP (or absolute, then divide by GDP)
        "personnel": 0,           // WDI or IISS (if licensed)
        "conflict_intensity": 0.0 // Start at 0–0.1; if modeling events, seed from UCDP level
      },
      "sentiment": {
        "gdelt_tone": 0.0,        // GDELT GKG tone (avg last week)
        "trends_salience": 50.0,  // Google Trends topic score (0–100)
        "policy_pressure": 0.2,   // Initialize ∈ [0,1]
        "approval": 0.5
      }
    }
  },
  "trade_matrix": {},              // UN Comtrade bilateral shares (latest year)
  "interbank_matrix": {},          // BIS CBS topology if available; else empty for MVS
  "alliance_graph": {},            // COW Formal Alliances v4.1 (to 2012) + manual updates
  "sanctions": {},                 // GSDB dyads (0..1 intensity)
  "io_coefficients": {},           // Skip in MVS (set empty)
  "commodity_prices": { "oil_brent": 85.0 } // Energy Institute / Pink Sheet baseline
}
```

### Full Information Scenario (FIS) Template
20-60 countries with comprehensive data sets for maximum realism:

```json
{
  "t": 0,
  "base_ccy": "USD",
  "countries": {
    // Same structure as MVS but extended to major economies
    // USA, CHN, EU27, JPN, IND, BRA, RUS, IDN, MEX, TUR, KOR, SAU, NGA, ZAF, etc.
  },
  "trade_matrix": {
    "CHN": {"USA": 0.18, "EU27": 0.15, "JPN": 0.06},
    "USA": {"MEX": 0.15, "CAN": 0.14, "CHN": 0.13}
  },
  "interbank_matrix": {
    "USA": {"GBR": 120.0, "JPN": 80.0},  // USD bn ultimate-risk exposures (BIS CBS)
    "GBR": {"USA": 140.0, "DEU": 60.0}
  },
  "alliance_graph": {
    "USA": {"JPN": 1.0, "KOR": 1.0, "NATO_EUR": 1.0},  // COW + manual post-2012 updates
    "RUS": {"IRN": 0.5}
  },
  "sanctions": {
    "USA": {"RUS": 0.9, "IRN": 0.8},      // GSDB dyads/intensity by type (financial/trade)
    "EU27": {"RUS": 0.85}
  },
  "io_coefficients": {
    "USA": { "Agriculture->Food": 0.15, "Refining->Transport": 0.22 }  // from ICIO/WIOD/Eora
  },
  "commodity_prices": {
    "oil_brent": 85.0, "natgas_TTF": 30.0, "wheat": 250.0, "copper": 8500.0
  }
}
```

### Data Source API Mappings

**Macro Economic Indicators:**
- **GDP, CPI, Unemployment**: World Bank WDI via Indicators API (`NY.GDP.MKTP.CD`, `FP.CPI.TOTL.ZG`, `SL.UEM.TOTL.ZS`)
- **Policy Rates**: IMF IFS money/interest or FRED API (e.g., FEDFUNDS for US)
- **Government Finances**: IMF Data Portal/WEO/IFS for debt/GDP and primary balance
- **Potential GDP**: OECD potential series or HP-filter trend computation

**External Sector:**
- **FX Rates**: FRED H.10 or IMF IFS exchange rate series
- **Reserves**: IMF IFS international liquidity data
- **Current Account**: IMF Data Portal/IFS (BPM6 methodology)

**Financial Markets:**
- **Sovereign Yields**: FRED series (DGS10) or local central bank data
- **Banking**: BIS Consolidated Banking Statistics for cross-border exposures

**Trade and Production:**
- **Trade Flows**: UN Comtrade API for bilateral trade matrices
- **Tariffs/NTMs**: WITS/UNCTAD TRAINS for MFN rates and non-tariff measures
- **Input-Output**: OECD ICIO, WIOD, or Eora MRIO for production linkages

**Energy and Commodities:**
- **Energy Balances**: IEA World Energy Balances or Energy Institute Statistical Review
- **Food Prices**: FAO Food Price Index (FFPI)
- **Commodity Prices**: World Bank Pink Sheet or IMF Primary Commodity Prices

**Security and Geopolitics:**
- **Military Expenditure**: SIPRI Military Expenditure Database
- **Conflicts**: UCDP Georeferenced Event Dataset (GED)
- **Alliances**: COW Formal Alliances v4.1 with manual post-2012 updates
- **Sanctions**: Global Sanctions Data Base (GSDB-R4)

**Information and Sentiment:**
- **News Tone**: GDELT Global Knowledge Graph (GKG) tone indicators
- **Topic Salience**: Google Trends API (alpha) for narrative interest

### Data Fallback Strategies

**Missing Primary Balance**: `primary_balance ≈ overall_balance + interest_outlays/GDP` where interest ≈ `sovereign_yield × debt/GDP`

**Missing Potential GDP**: Compute HP-filter trend (λ=100 for annual data) or rolling log-linear regression; set `output_gap = (GDP - trend)/trend`

**Missing Energy Stock-to-Use**: `SU ≈ (last_year_stocks + 0.5*production - consumption)/consumption`; default to 1.0 if no inventory data

**Missing NTM Index**: Normalize TRAINS NTM counts to [0,1] scale; fallback by income group (HIC: 0.35, UMIC: 0.30, LMIC: 0.25, LIC: 0.20)

**Missing Sanction Intensity**: Map GSDB case types to intensities {trade: 0.3, finance: 0.5, energy: 0.7, full: 0.9}

## [Implementation Order]
Sequential implementation to minimize conflicts and ensure working system at each stage.

1. **Core Infrastructure Setup**
   - Create app directory structure
   - Set up app/core/config.py and app/core/database.py
   - Move and update user models in app/models/user.py
   - Update backend/api/auth.py imports

2. **Database Schema and Models**
   - Create app/models/simulation.py with Scenario and SimulationState models
   - Set up Alembic configuration and initial migration
   - Run migration to create database tables

3. **Simulation State Framework**
   - Implement app/simulation/state.py with all Pydantic models
   - Create app/simulation/reducers.py with all economic update functions
   - Test reducer functions with sample data

4. **Data Integration Layer**
   - Create app/data/sources.py for API integrations (WDI, FRED, Comtrade, etc.)
   - Implement scenario template loaders for MVS and FIS configurations
   - Add data validation and fallback logic for missing fields

5. **API Endpoints**
   - Create app/api/simulation.py with all CRUD endpoints
   - Implement scenario management (create, read, update, delete)
   - Implement simulation stepping endpoint with state persistence
   - Add endpoints for scenario template generation from data sources

6. **Application Entry Point**
   - Create app/main.py with FastAPI app initialization
   - Include authentication and simulation routers
   - Test full application startup

7. **Database Initialization**
   - Create db/init.sql for PostgreSQL extensions and initial setup
   - Update docker-compose.yml to mount init script
   - Test full Docker Compose deployment

8. **Testing and Validation**
   - Create test suite for reducer functions with MVS/FIS data
   - Create API integration tests including data source fallbacks
   - Test end-to-end scenario creation and simulation stepping
   - Validate with both minimal and comprehensive economic scenarios
