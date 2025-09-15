"""Audit trail capture system with database persistence."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.state import FieldChange, StepAudit, AuditCapture
from ..models.audit import AuditLog, FieldChangeLog, TriggerLog
from ..models.scenario import SimulationState


class DatabaseAuditCapture(AuditCapture):
    """Enhanced AuditCapture that supports database persistence."""
    
    def __init__(self, scenario_id: UUID, timestep: int, reducer_name: str = "simulation_step", reducer_params: Dict[str, Any] = None):
        super().__init__(reducer_name, reducer_params)
        self.scenario_id = scenario_id
        self.timestep = timestep
        self.step_start_time = datetime.utcnow()
        self.step_end_time: Optional[datetime] = None
        self.reducer_sequence: List[str] = []
        self.triggers_fired: List[str] = []
        self.errors: List[str] = []
    
    def add_reducer(self, reducer_name: str) -> None:
        """Add reducer to execution sequence."""
        if reducer_name not in self.reducer_sequence:
            self.reducer_sequence.append(reducer_name)
    
    def add_trigger_fired(self, trigger_name: str) -> None:
        """Record trigger activation."""
        if trigger_name not in self.triggers_fired:
            self.triggers_fired.append(trigger_name)
    
    def add_error(self, error_msg: str) -> None:
        """Record error during step execution."""
        self.errors.append(error_msg)
    
    def finalize(self) -> StepAudit:
        """Complete audit trail and return StepAudit object."""
        self.step_end_time = datetime.utcnow()
        
        return StepAudit(
            scenario_id=self.scenario_id,
            timestep=self.timestep,
            step_start_time=self.step_start_time,
            step_end_time=self.step_end_time,
            reducer_sequence=self.reducer_sequence,
            field_changes=self.field_changes,
            triggers_fired=self.triggers_fired,
            errors=self.errors
        )


async def create_audit_log(
    audit: StepAudit, 
    simulation_state: SimulationState,
    db: AsyncSession
) -> AuditLog:
    """Store audit trail in database with complete field change tracking."""
    
    # Calculate execution time
    execution_time_ms = None
    if audit.step_end_time and audit.step_start_time:
        execution_time_ms = (audit.step_end_time - audit.step_start_time).total_seconds() * 1000
    
    # Create main audit log
    db_audit_log = AuditLog(
        scenario_id=audit.scenario_id,
        simulation_state_id=simulation_state.id,
        timestep=audit.timestep,
        step_start_time=audit.step_start_time,
        step_end_time=audit.step_end_time,
        reducer_sequence=audit.reducer_sequence,
        triggers_fired=audit.triggers_fired,
        errors=audit.errors,
        execution_time_ms=execution_time_ms
    )
    
    db.add(db_audit_log)
    await db.flush()  # Get the ID
    
    # Create field change logs
    field_change_logs = []
    for i, field_change in enumerate(audit.field_changes):
        db_field_change = FieldChangeLog(
            audit_log_id=db_audit_log.id,
            field_path=field_change.field_path,
            old_value=field_change.old_value,
            new_value=field_change.new_value,
            reducer_name=field_change.reducer_name,
            reducer_params=field_change.reducer_params,
            calculation_details=field_change.calculation_details,
            change_order=i
        )
        field_change_logs.append(db_field_change)
        db.add(db_field_change)
    
    await db.commit()
    return db_audit_log


async def get_audit_history(
    scenario_id: UUID,
    db: AsyncSession,
    timestep_start: Optional[int] = None,
    timestep_end: Optional[int] = None,
    reducer_filter: Optional[str] = None,
    field_path_filter: Optional[str] = None
) -> List[AuditLog]:
    """Query audit history with filters."""
    from sqlalchemy import select
    
    query = select(AuditLog).where(AuditLog.scenario_id == scenario_id)
    
    if timestep_start is not None:
        query = query.where(AuditLog.timestep >= timestep_start)
    
    if timestep_end is not None:
        query = query.where(AuditLog.timestep <= timestep_end)
    
    result = await db.execute(query)
    audit_logs = result.scalars().all()
    
    # Apply additional filters if needed
    if reducer_filter or field_path_filter:
        filtered_logs = []
        for log in audit_logs:
            if reducer_filter and reducer_filter not in log.reducer_sequence:
                continue
            
            if field_path_filter:
                # Check if any field changes match the path filter
                field_query = select(FieldChangeLog).where(
                    FieldChangeLog.audit_log_id == log.id,
                    FieldChangeLog.field_path.like(f"%{field_path_filter}%")
                )
                field_result = await db.execute(field_query)
                field_changes = field_result.scalars().all()
                if not field_changes:
                    continue
            
            filtered_logs.append(log)
        
        return filtered_logs
    
    return list(audit_logs)


async def get_field_change_history(
    scenario_id: UUID,
    field_path: str,
    db: AsyncSession,
    timestep_start: Optional[int] = None,
    timestep_end: Optional[int] = None
) -> List[FieldChangeLog]:
    """Get complete change history for a specific field."""
    from sqlalchemy import select, join
    
    query = (
        select(FieldChangeLog)
        .join(AuditLog)
        .where(
            AuditLog.scenario_id == scenario_id,
            FieldChangeLog.field_path == field_path
        )
        .order_by(AuditLog.timestep, FieldChangeLog.change_order)
    )
    
    if timestep_start is not None:
        query = query.where(AuditLog.timestep >= timestep_start)
    
    if timestep_end is not None:
        query = query.where(AuditLog.timestep <= timestep_end)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_reducer_performance_stats(
    scenario_id: UUID,
    db: AsyncSession,
    reducer_name: Optional[str] = None
) -> Dict[str, Any]:
    """Get performance statistics for reducers."""
    from sqlalchemy import select, func
    
    query = select(
        AuditLog.reducer_sequence,
        func.avg(AuditLog.execution_time_ms).label("avg_execution_time"),
        func.min(AuditLog.execution_time_ms).label("min_execution_time"),
        func.max(AuditLog.execution_time_ms).label("max_execution_time"),
        func.count().label("execution_count")
    ).where(AuditLog.scenario_id == scenario_id)
    
    if reducer_name:
        query = query.where(AuditLog.reducer_sequence.contains([reducer_name]))
    
    query = query.group_by(AuditLog.reducer_sequence)
    
    result = await db.execute(query)
    stats = {}
    
    for row in result:
        sequence_key = ",".join(row.reducer_sequence)
        stats[sequence_key] = {
            "avg_execution_time_ms": float(row.avg_execution_time) if row.avg_execution_time else None,
            "min_execution_time_ms": float(row.min_execution_time) if row.min_execution_time else None,
            "max_execution_time_ms": float(row.max_execution_time) if row.max_execution_time else None,
            "execution_count": row.execution_count
        }
    
    return stats


async def get_error_summary(
    scenario_id: UUID,
    db: AsyncSession,
    timestep_start: Optional[int] = None,
    timestep_end: Optional[int] = None
) -> Dict[str, Any]:
    """Get summary of errors encountered during simulation."""
    from sqlalchemy import select, func
    
    query = select(AuditLog).where(
        AuditLog.scenario_id == scenario_id,
        func.array_length(AuditLog.errors, 1) > 0
    )
    
    if timestep_start is not None:
        query = query.where(AuditLog.timestep >= timestep_start)
    
    if timestep_end is not None:
        query = query.where(AuditLog.timestep <= timestep_end)
    
    result = await db.execute(query)
    error_logs = result.scalars().all()
    
    # Aggregate error information
    error_counts = {}
    error_by_reducer = {}
    total_errors = 0
    
    for log in error_logs:
        for error in log.errors:
            total_errors += 1
            error_counts[error] = error_counts.get(error, 0) + 1
            
            # Track which reducers generated errors
            for reducer in log.reducer_sequence:
                if reducer not in error_by_reducer:
                    error_by_reducer[reducer] = []
                if error not in error_by_reducer[reducer]:
                    error_by_reducer[reducer].append(error)
    
    return {
        "total_errors": total_errors,
        "error_counts": error_counts,
        "errors_by_reducer": error_by_reducer,
        "affected_timesteps": [log.timestep for log in error_logs]
    }


async def get_transparency_report(
    scenario_id: UUID,
    timestep: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """Generate comprehensive transparency report for a specific timestep."""
    from sqlalchemy import select
    
    # Get audit log for the timestep
    audit_query = select(AuditLog).where(
        AuditLog.scenario_id == scenario_id,
        AuditLog.timestep == timestep
    )
    
    audit_result = await db.execute(audit_query)
    audit_log = audit_result.scalar_one_or_none()
    
    if not audit_log:
        return {"error": f"No audit log found for timestep {timestep}"}
    
    # Get all field changes
    field_changes_query = select(FieldChangeLog).where(
        FieldChangeLog.audit_log_id == audit_log.id
    ).order_by(FieldChangeLog.change_order)
    
    field_result = await db.execute(field_changes_query)
    field_changes = list(field_result.scalars().all())
    
    # Get trigger logs
    trigger_query = select(TriggerLog).where(
        TriggerLog.audit_log_id == audit_log.id
    )
    
    trigger_result = await db.execute(trigger_query)
    trigger_logs = list(trigger_result.scalars().all())
    
    # Build comprehensive report
    report = {
        "scenario_id": str(scenario_id),
        "timestep": timestep,
        "execution_summary": {
            "start_time": audit_log.step_start_time.isoformat(),
            "end_time": audit_log.step_end_time.isoformat(),
            "execution_time_ms": audit_log.execution_time_ms,
            "reducer_sequence": audit_log.reducer_sequence,
            "triggers_fired": audit_log.triggers_fired,
            "error_count": len(audit_log.errors),
            "errors": audit_log.errors
        },
        "field_changes": {
            "total_changes": len(field_changes),
            "changes_by_reducer": {},
            "changes_by_field": {},
            "detailed_changes": []
        },
        "triggers": {
            "total_fired": len(trigger_logs),
            "trigger_details": []
        }
    }
    
    # Analyze field changes
    for change in field_changes:
        # Group by reducer
        if change.reducer_name not in report["field_changes"]["changes_by_reducer"]:
            report["field_changes"]["changes_by_reducer"][change.reducer_name] = 0
        report["field_changes"]["changes_by_reducer"][change.reducer_name] += 1
        
        # Group by field
        if change.field_path not in report["field_changes"]["changes_by_field"]:
            report["field_changes"]["changes_by_field"][change.field_path] = 0
        report["field_changes"]["changes_by_field"][change.field_path] += 1
        
        # Add detailed change
        report["field_changes"]["detailed_changes"].append({
            "field_path": change.field_path,
            "old_value": change.old_value,
            "new_value": change.new_value,
            "reducer_name": change.reducer_name,
            "reducer_params": change.reducer_params,
            "calculation_details": change.calculation_details,
            "change_order": change.change_order
        })
    
    # Analyze trigger logs
    for trigger_log in trigger_logs:
        report["triggers"]["trigger_details"].append({
            "trigger_name": trigger_log.trigger_name,
            "fired_at_turn": trigger_log.fired_at_turn,
            "actions_applied": trigger_log.actions_applied,
            "execution_result": trigger_log.execution_result
        })
    
    return report


# Initialize audit capture for simulation package
__all__ = [
    "DatabaseAuditCapture",
    "create_audit_log",
    "get_audit_history",
    "get_field_change_history",
    "get_reducer_performance_stats",
    "get_error_summary",
    "get_transparency_report"
]
