from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column, JSON, Relationship
from sqlalchemy import Text, Index


class AuditLog(SQLModel, table=True):
    """Database model for simulation step audit logs."""
    
    __tablename__ = "audit_logs"
    
    # Primary key and relationships
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(foreign_key="scenarios.id", index=True)
    simulation_state_id: UUID = Field(foreign_key="simulation_states.id", unique=True)
    
    # Step information
    timestep: int = Field(index=True)
    step_start_time: datetime = Field(index=True)
    step_end_time: datetime
    
    # Reducer execution details
    reducer_sequence: List[str] = Field(sa_column=Column(JSON))
    triggers_fired: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    errors: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Performance metrics
    execution_time_ms: Optional[float] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationships
    scenario: "Scenario" = Relationship(back_populates="audit_logs")
    simulation_state: "SimulationState" = Relationship(back_populates="audit_log")
    field_change_logs: List["FieldChangeLog"] = Relationship(back_populates="audit_log")
    trigger_logs: List["TriggerLog"] = Relationship(back_populates="audit_log")
    
    __table_args__ = (
        Index("ix_audit_logs_scenario_timestep", "scenario_id", "timestep"),
        Index("ix_audit_logs_scenario_created", "scenario_id", "created_at"),
        Index("ix_audit_logs_execution_time", "execution_time_ms"),
    )


class FieldChangeLog(SQLModel, table=True):
    """Database model for individual field changes during simulation steps."""
    
    __tablename__ = "field_change_logs"
    
    # Primary key and relationships
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    audit_log_id: UUID = Field(foreign_key="audit_logs.id", index=True)
    
    # Field change details
    field_path: str = Field(max_length=500, index=True)  # e.g., "countries.USA.macro.policy_rate"
    old_value: Optional[Any] = Field(default=None, sa_column=Column(JSON))
    new_value: Optional[Any] = Field(default=None, sa_column=Column(JSON))
    
    # Reducer attribution
    reducer_name: str = Field(max_length=100, index=True)  # e.g., "taylor_rule"
    reducer_params: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    calculation_details: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Metadata
    change_order: int = Field(index=True)  # order of changes within the step
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationships
    audit_log: AuditLog = Relationship(back_populates="field_change_logs")
    
    __table_args__ = (
        Index("ix_field_changes_audit_order", "audit_log_id", "change_order"),
        Index("ix_field_changes_field_path", "field_path"),
        Index("ix_field_changes_reducer", "reducer_name"),
        Index("ix_field_changes_audit_reducer", "audit_log_id", "reducer_name"),
    )


class TriggerLog(SQLModel, table=True):
    """Database model for trigger execution logs."""
    
    __tablename__ = "trigger_logs"
    
    # Primary key and relationships
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    audit_log_id: UUID = Field(foreign_key="audit_logs.id", index=True)
    scenario_trigger_id: UUID = Field(foreign_key="scenario_triggers.id", index=True)
    
    # Trigger execution details
    fired_at_turn: int = Field(index=True)
    trigger_name: str = Field(max_length=200, index=True)
    
    # Action counts and results
    actions_applied: Dict[str, int] = Field(sa_column=Column(JSON))  # e.g., {"patches": 2, "overrides": 1}
    execution_result: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationships
    audit_log: AuditLog = Relationship(back_populates="trigger_logs")
    scenario_trigger: "ScenarioTrigger" = Relationship(back_populates="trigger_logs")
    
    __table_args__ = (
        Index("ix_trigger_logs_audit_trigger", "audit_log_id", "scenario_trigger_id"),
        Index("ix_trigger_logs_fired_turn", "fired_at_turn"),
    )
