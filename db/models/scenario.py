from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column, JSON, Relationship
from sqlalchemy import Text, Index


class Scenario(SQLModel, table=True):
    """Database model for simulation scenarios."""
    
    __tablename__ = "scenarios"
    
    # Primary key and relationships
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    
    # Basic scenario information
    name: str = Field(max_length=200, index=True)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Current simulation state
    current_timestep: int = Field(default=0, index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationships
    simulation_states: list["SimulationState"] = Relationship(back_populates="scenario")
    audit_logs: list["AuditLog"] = Relationship(back_populates="scenario")
    scenario_triggers: list["ScenarioTrigger"] = Relationship(back_populates="scenario")
    
    __table_args__ = (
        Index("ix_scenarios_user_created", "user_id", "created_at"),
        Index("ix_scenarios_user_name", "user_id", "name"),
    )


class SimulationState(SQLModel, table=True):
    """Database model for simulation states at specific timesteps."""
    
    __tablename__ = "simulation_states"
    
    # Primary key and relationships
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    scenario_id: UUID = Field(foreign_key="scenarios.id", index=True)
    
    # State identification
    timestep: int = Field(index=True)
    
    # State data stored as JSON
    state_data: Dict[str, Any] = Field(sa_column=Column(JSON))
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationships
    scenario: Scenario = Relationship(back_populates="simulation_states")
    audit_log: Optional["AuditLog"] = Relationship(back_populates="simulation_state")
    
    __table_args__ = (
        Index("ix_simulation_states_scenario_timestep", "scenario_id", "timestep", unique=True),
        Index("ix_simulation_states_scenario_created", "scenario_id", "created_at"),
    )
