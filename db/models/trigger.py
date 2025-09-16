from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column, JSON, Relationship
from sqlalchemy import Text, Index


class ScenarioTrigger(SQLModel, table=True):
    """Database model for scenario triggers that manage policy changes."""
    
    __tablename__ = "scenario_triggers"
    
    # Primary key and relationships
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(foreign_key="scenarios.id", index=True)
    
    # Trigger identification
    name: str = Field(max_length=200, index=True)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Trigger condition (stored as JSON for flexibility)
    condition_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Trigger action (stored as JSON containing all action types)
    action_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Trigger configuration
    once_only: bool = Field(default=True)
    expires_after_turns: Optional[int] = Field(default=None)
    
    # State tracking
    has_fired: bool = Field(default=False, index=True)
    times_fired: int = Field(default=0)
    last_fired_at_turn: Optional[int] = Field(default=None, index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationships
    scenario: "Scenario" = Relationship(back_populates="scenario_triggers")
    trigger_logs: List["TriggerLog"] = Relationship(back_populates="scenario_trigger")
    
    __table_args__ = (
        Index("ix_scenario_triggers_scenario_name", "scenario_id", "name"),
        Index("ix_scenario_triggers_scenario_fired", "scenario_id", "has_fired"),
        Index("ix_scenario_triggers_last_fired", "last_fired_at_turn"),
    )


class PolicyPatch(SQLModel, table=True):
    """Database model for individual policy patches within triggers."""
    
    __tablename__ = "policy_patches"
    
    # Primary key and relationships
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_trigger_id: UUID = Field(foreign_key="scenario_triggers.id", index=True)
    
    # Patch details
    target_path: str = Field(max_length=500, index=True)  # dotpath into state/rules
    operation: str = Field(max_length=10, index=True)  # "set", "add", "mul"
    patch_value: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Application tracking
    applied_count: int = Field(default=0)
    last_applied_at_turn: Optional[int] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_policy_patches_trigger_path", "scenario_trigger_id", "target_path"),
    )


class ReducerOverride(SQLModel, table=True):
    """Database model for reducer implementation overrides."""
    
    __tablename__ = "reducer_overrides"
    
    # Primary key and relationships
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_trigger_id: UUID = Field(foreign_key="scenario_triggers.id", index=True)
    
    # Override details
    target_reducer: str = Field(max_length=100, index=True)  # e.g., "monetary_policy"
    override_impl: str = Field(max_length=100, index=True)  # e.g., "fx_peg_v1"
    
    # Configuration
    override_params: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Application tracking
    applied_count: int = Field(default=0)
    last_applied_at_turn: Optional[int] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_reducer_overrides_trigger_target", "scenario_trigger_id", "target_reducer"),
        Index("ix_reducer_overrides_impl", "override_impl"),
    )


class NetworkRewrite(SQLModel, table=True):
    """Database model for network/matrix modifications."""
    
    __tablename__ = "network_rewrites"
    
    # Primary key and relationships
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_trigger_id: UUID = Field(foreign_key="scenario_triggers.id", index=True)
    
    # Network modification details
    target_layer: str = Field(max_length=20, index=True)  # "trade", "alliances", "sanctions", "interbank", "energy"
    network_edits: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))  # list of edge modifications
    
    # Application tracking
    applied_count: int = Field(default=0)
    last_applied_at_turn: Optional[int] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_network_rewrites_trigger_layer", "scenario_trigger_id", "target_layer"),
    )


class EventInject(SQLModel, table=True):
    """Database model for event injections."""
    
    __tablename__ = "event_injections"
    
    # Primary key and relationships
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_trigger_id: UUID = Field(foreign_key="scenario_triggers.id", index=True)
    
    # Event details
    event_kind: str = Field(max_length=20, index=True)  # "conflict", "disaster", "strike", "embargo", "mobilization"
    event_payload: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Application tracking
    applied_count: int = Field(default=0)
    last_applied_at_turn: Optional[int] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_event_injections_trigger_kind", "scenario_trigger_id", "event_kind"),
        Index("ix_event_injections_kind", "event_kind"),
    )


# Create model init file to ensure imports work correctly
