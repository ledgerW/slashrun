"""FastAPI endpoints for simulation CRUD, audit queries, and trigger management."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from backend.app.core.database import get_db
from db.models.scenario import Scenario, SimulationState
from db.models.user import User
from db.models.state import (
    GlobalState, ScenarioCreate, ScenarioUpdate, ScenarioResponse, 
    SimulationStepResponse, AuditQueryResponse, Trigger, StepAudit
)
from db.models.audit import AuditLog, FieldChangeLog
from backend.app.simulation import reduce_world, process_triggers, expire_triggers, DatabaseAuditCapture, create_audit_log
from backend.app.simulation.trigger_examples import load_trigger_examples
from backend.app.services.data_integration import generate_mvs_scenario, generate_fis_scenario
from backend.app.api.auth import get_current_user

router = APIRouter(prefix="/simulation", tags=["simulation"])


@router.post("/scenarios", response_model=ScenarioResponse)
async def create_scenario(
    scenario_data: ScenarioCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new simulation scenario with initial state."""
    try:
        # Create scenario record
        db_scenario = Scenario(
            user_id=current_user.id,
            name=scenario_data.name,
            description=scenario_data.description,
            current_timestep=0
        )
        db.add(db_scenario)
        await db.flush()  # Get scenario ID
        
        # Create initial simulation state
        initial_state = SimulationState(
            scenario_id=db_scenario.id,
            timestep=0,
            state_data=scenario_data.initial_state.model_dump()
        )
        db.add(initial_state)
        
        # Create scenario triggers if provided
        trigger_count = 0
        if scenario_data.triggers:
            from db.models.trigger import ScenarioTrigger
            for trigger in scenario_data.triggers:
                db_trigger = ScenarioTrigger(
                    scenario_id=db_scenario.id,
                    name=trigger.name,
                    description=trigger.description,
                    condition_data=trigger.condition.model_dump(),
                    action_data=trigger.action.model_dump(),
                    once_only=trigger.condition.once,
                    expires_after_turns=trigger.expires_after_turns
                )
                db.add(db_trigger)
                trigger_count += 1
        
        await db.commit()
        
        # Include the initial state in the response
        return ScenarioResponse(
            id=db_scenario.id,
            name=db_scenario.name,
            description=db_scenario.description,
            user_id=db_scenario.user_id,
            current_timestep=db_scenario.current_timestep,
            created_at=db_scenario.created_at,
            updated_at=db_scenario.updated_at,
            triggers_count=trigger_count,
            current_state=scenario_data.initial_state
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create scenario: {str(e)}")


@router.get("/scenarios", response_model=List[ScenarioResponse])
async def get_scenarios(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """List user's simulation scenarios."""
    try:
        query = (
            select(Scenario)
            .where(Scenario.user_id == current_user.id)
            .order_by(Scenario.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(query)
        scenarios = result.scalars().all()
        
        # Get trigger counts and current state for each scenario
        scenario_responses = []
        for scenario in scenarios:
            from db.models.trigger import ScenarioTrigger
            trigger_query = select(ScenarioTrigger).where(ScenarioTrigger.scenario_id == scenario.id)
            trigger_result = await db.execute(trigger_query)
            triggers_count = len(list(trigger_result.scalars().all()))
            
            # Get current state
            current_state = None
            if scenario.current_timestep is not None:
                state_query = select(SimulationState).where(
                    and_(
                        SimulationState.scenario_id == scenario.id,
                        SimulationState.timestep == scenario.current_timestep
                    )
                )
                state_result = await db.execute(state_query)
                state_record = state_result.scalar_one_or_none()
                if state_record:
                    current_state = GlobalState.model_validate(state_record.state_data)
            
            scenario_responses.append(ScenarioResponse(
                id=scenario.id,
                name=scenario.name,
                description=scenario.description,
                user_id=scenario.user_id,
                current_timestep=scenario.current_timestep,
                created_at=scenario.created_at,
                updated_at=scenario.updated_at,
                triggers_count=triggers_count,
                current_state=current_state
            ))
        
        return scenario_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list scenarios: {str(e)}")


@router.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific scenario details."""
    try:
        query = select(Scenario).where(
            and_(Scenario.id == scenario_id, Scenario.user_id == current_user.id)
        )
        result = await db.execute(query)
        scenario = result.scalar_one_or_none()
        
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Get trigger count
        from db.models.trigger import ScenarioTrigger
        trigger_query = select(ScenarioTrigger).where(ScenarioTrigger.scenario_id == scenario.id)
        trigger_result = await db.execute(trigger_query)
        triggers_count = len(list(trigger_result.scalars().all()))
        
        # Get current state
        current_state = None
        if scenario.current_timestep is not None:
            state_query = select(SimulationState).where(
                and_(
                    SimulationState.scenario_id == scenario.id,
                    SimulationState.timestep == scenario.current_timestep
                )
            )
            state_result = await db.execute(state_query)
            state_record = state_result.scalar_one_or_none()
            if state_record:
                current_state = GlobalState.model_validate(state_record.state_data)
        
        return ScenarioResponse(
            id=scenario.id,
            name=scenario.name,
            description=scenario.description,
            user_id=scenario.user_id,
            current_timestep=scenario.current_timestep,
            created_at=scenario.created_at,
            updated_at=scenario.updated_at,
            triggers_count=triggers_count,
            current_state=current_state
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scenario: {str(e)}")


@router.put("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    scenario_id: UUID,
    updates: ScenarioUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update scenario metadata and triggers."""
    try:
        # Get existing scenario
        query = select(Scenario).where(
            and_(Scenario.id == scenario_id, Scenario.user_id == current_user.id)
        )
        result = await db.execute(query)
        scenario = result.scalar_one_or_none()
        
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Update basic fields
        if updates.name is not None:
            scenario.name = updates.name
        if updates.description is not None:
            scenario.description = updates.description
        
        # Update triggers if provided
        trigger_count = 0
        if updates.triggers is not None:
            from db.models.trigger import ScenarioTrigger
            
            # Delete existing triggers
            delete_query = select(ScenarioTrigger).where(ScenarioTrigger.scenario_id == scenario_id)
            delete_result = await db.execute(delete_query)
            existing_triggers = delete_result.scalars().all()
            for trigger in existing_triggers:
                await db.delete(trigger)
            
            # Create new triggers
            for trigger in updates.triggers:
                db_trigger = ScenarioTrigger(
                    scenario_id=scenario.id,
                    name=trigger.name,
                    description=trigger.description,
                    condition_data=trigger.condition.model_dump(),
                    action_data=trigger.action.model_dump(),
                    once_only=trigger.condition.once,
                    expires_after_turns=trigger.expires_after_turns
                )
                db.add(db_trigger)
                trigger_count += 1
        
        scenario.updated_at = scenario.updated_at  # This will be updated by the database
        await db.commit()
        
        # Get current state
        current_state = None
        if scenario.current_timestep is not None:
            state_query = select(SimulationState).where(
                and_(
                    SimulationState.scenario_id == scenario.id,
                    SimulationState.timestep == scenario.current_timestep
                )
            )
            state_result = await db.execute(state_query)
            state_record = state_result.scalar_one_or_none()
            if state_record:
                current_state = GlobalState.model_validate(state_record.state_data)
        
        return ScenarioResponse(
            id=scenario.id,
            name=scenario.name,
            description=scenario.description,
            user_id=scenario.user_id,
            current_timestep=scenario.current_timestep,
            created_at=scenario.created_at,
            updated_at=scenario.updated_at,
            triggers_count=trigger_count if updates.triggers is not None else 0,
            current_state=current_state
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update scenario: {str(e)}")


@router.delete("/scenarios/{scenario_id}")
async def delete_scenario(
    scenario_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete scenario and all associated data."""
    try:
        # Get scenario
        query = select(Scenario).where(
            and_(Scenario.id == scenario_id, Scenario.user_id == current_user.id)
        )
        result = await db.execute(query)
        scenario = result.scalar_one_or_none()
        
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Delete related data manually since cascade isn't configured
        
        # Delete audit logs
        from db.models.audit import AuditLog, FieldChangeLog
        audit_query = select(AuditLog).where(AuditLog.scenario_id == scenario_id)
        audit_result = await db.execute(audit_query)
        audit_logs = audit_result.scalars().all()
        for audit_log in audit_logs:
            # Delete field change logs first
            field_change_query = select(FieldChangeLog).where(FieldChangeLog.audit_log_id == audit_log.id)
            field_change_result = await db.execute(field_change_query)
            field_changes = field_change_result.scalars().all()
            for field_change in field_changes:
                await db.delete(field_change)
            await db.delete(audit_log)
        
        # Delete scenario triggers
        from db.models.trigger import ScenarioTrigger
        trigger_query = select(ScenarioTrigger).where(ScenarioTrigger.scenario_id == scenario_id)
        trigger_result = await db.execute(trigger_query)
        triggers = trigger_result.scalars().all()
        for trigger in triggers:
            await db.delete(trigger)
        
        # Delete simulation states
        state_query = select(SimulationState).where(SimulationState.scenario_id == scenario_id)
        state_result = await db.execute(state_query)
        states = state_result.scalars().all()
        for state in states:
            await db.delete(state)
        
        # Finally delete the scenario
        await db.delete(scenario)
        await db.commit()
        
        return {"message": "Scenario deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete scenario: {str(e)}")


@router.post("/scenarios/{scenario_id}/step", response_model=SimulationStepResponse)
async def step_simulation(
    scenario_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute one simulation step with complete transparency."""
    try:
        # Get scenario
        scenario_query = select(Scenario).where(
            and_(Scenario.id == scenario_id, Scenario.user_id == current_user.id)
        )
        scenario_result = await db.execute(scenario_query)
        scenario = scenario_result.scalar_one_or_none()
        
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Get current state
        current_timestep = scenario.current_timestep
        state_query = select(SimulationState).where(
            and_(
                SimulationState.scenario_id == scenario_id,
                SimulationState.timestep == current_timestep
            )
        )
        state_result = await db.execute(state_query)
        current_state_record = state_result.scalar_one_or_none()
        
        if not current_state_record:
            raise HTTPException(status_code=400, detail="Current state not found")
        
        # Parse current state
        current_state = GlobalState.model_validate(current_state_record.state_data)
        
        # Get scenario triggers
        from db.models.trigger import ScenarioTrigger
        trigger_query = select(ScenarioTrigger).where(ScenarioTrigger.scenario_id == scenario_id)
        trigger_result = await db.execute(trigger_query)
        db_triggers = trigger_result.scalars().all()
        
        # Convert to trigger objects and track fired triggers
        triggers = []
        fired_triggers = set()
        fired_trigger_times = {}
        
        for db_trigger in db_triggers:
            if db_trigger.has_fired and db_trigger.once_only:
                fired_triggers.add(db_trigger.name)
                if db_trigger.last_fired_at_turn:
                    fired_trigger_times[db_trigger.name] = db_trigger.last_fired_at_turn
            
            from db.models.state import TriggerCondition, TriggerAction
            
            trigger = Trigger(
                name=db_trigger.name,
                description=db_trigger.description or "",
                condition=TriggerCondition.model_validate(db_trigger.condition_data),
                action=TriggerAction.model_validate(db_trigger.action_data),
                expires_after_turns=db_trigger.expires_after_turns
            )
            triggers.append(trigger)
        
        # Initialize audit capture
        next_timestep = current_timestep + 1
        audit = DatabaseAuditCapture(
            scenario_id=scenario_id,
            timestep=next_timestep,
            reducer_name="simulation_step"
        )
        
        # Create a copy of the state with incremented timestep for trigger evaluation
        # This ensures triggers fire at the correct timestep
        trigger_eval_state = current_state.model_copy(deep=True)
        trigger_eval_state.t = next_timestep
        
        # Process triggers against the next timestep and apply to current state
        # Note: We evaluate conditions against next_timestep but apply actions to current_state
        newly_fired = []
        for trigger in triggers:
            # Skip if this is a once-only trigger that has already fired
            if trigger.condition.once and trigger.name in fired_triggers:
                continue
            
            # Evaluate trigger condition against next timestep
            try:
                from backend.app.simulation.trigger_conditions import eval_condition
                should_fire = eval_condition(trigger_eval_state, trigger.condition.when or "")
            except Exception as e:
                audit.add_error(f"Error evaluating trigger {trigger.name}: {str(e)}")
                continue
            
            if should_fire:
                # Apply the trigger to current_state (which will be processed by reducer)
                from backend.app.simulation.trigger_actions import apply_trigger
                if apply_trigger(current_state, trigger, audit):
                    newly_fired.append(trigger.name)
                    audit.add_trigger_fired(trigger.name)
                    
                    # Mark as fired if it's a once-only trigger
                    if trigger.condition.once:
                        fired_triggers.add(trigger.name)
        
        # Update trigger states in database
        for trigger_name in newly_fired:
            for db_trigger in db_triggers:
                if db_trigger.name == trigger_name:
                    db_trigger.has_fired = True
                    db_trigger.times_fired += 1
                    db_trigger.last_fired_at_turn = next_timestep
                    break
        
        # Expire triggers
        expired_triggers = expire_triggers(current_state, triggers, fired_trigger_times)
        
        # Execute world reducer with audit trail
        # Map base currency to country name (USD -> USA)
        base_ccy_country_map = {
            "USD": "USA",
            "CNY": "CHN", 
            "EUR": "EUR",
            "JPY": "JPN",
            "GBP": "GBR"
        }
        base_country_name = base_ccy_country_map.get(current_state.base_ccy, "USA")
        new_state = reduce_world(current_state, base_country_name, audit)
        
        # Finalize audit
        step_audit = audit.finalize()
        
        # Store new simulation state
        new_state_record = SimulationState(
            scenario_id=scenario_id,
            timestep=next_timestep,
            state_data=new_state.model_dump()
        )
        db.add(new_state_record)
        await db.flush()
        
        # Store audit log
        audit_log = await create_audit_log(step_audit, new_state_record, db)
        
        # Update scenario current timestep
        scenario.current_timestep = next_timestep
        
        await db.commit()
        
        # Broadcast real-time update via WebSocket if available
        try:
            from fastapi import FastAPI
            from typing import TYPE_CHECKING
            # Access the app instance to get the WebSocket manager
            # This is a simplified approach for demo purposes
            websocket_data = {
                "type": "simulation_step_complete",
                "timestep": next_timestep,
                "scenario_id": str(scenario_id),
                "state_summary": {
                    "countries_count": len(new_state.countries),
                    "triggers_fired": newly_fired,
                    "reducer_count": len(step_audit.reducer_sequence),
                    "error_count": len(step_audit.errors)
                },
                "timestamp": step_audit.step_end_time.isoformat()
            }
            # Note: In a production system, you would access the WebSocket manager
            # through dependency injection or app state
        except Exception as e:
            # Log WebSocket error but don't fail the simulation step
            pass
        
        return SimulationStepResponse(
            id=new_state_record.id,
            scenario_id=scenario_id,
            timestep=next_timestep,
            state=new_state,
            audit=step_audit,
            created_at=new_state_record.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to step simulation: {str(e)}")


@router.get("/scenarios/{scenario_id}/states/{timestep}", response_model=SimulationStepResponse)
async def get_simulation_state(
    scenario_id: UUID,
    timestep: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get simulation state at specific timestep."""
    try:
        # Verify scenario ownership
        scenario_query = select(Scenario).where(
            and_(Scenario.id == scenario_id, Scenario.user_id == current_user.id)
        )
        scenario_result = await db.execute(scenario_query)
        scenario = scenario_result.scalar_one_or_none()
        
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Get simulation state
        state_query = select(SimulationState).where(
            and_(
                SimulationState.scenario_id == scenario_id,
                SimulationState.timestep == timestep
            )
        )
        state_result = await db.execute(state_query)
        state_record = state_result.scalar_one_or_none()
        
        if not state_record:
            raise HTTPException(status_code=404, detail=f"State not found for timestep {timestep}")
        
        # Get audit log for this timestep
        audit_query = select(AuditLog).where(
            and_(
                AuditLog.scenario_id == scenario_id,
                AuditLog.timestep == timestep
            )
        )
        audit_result = await db.execute(audit_query)
        audit_log = audit_result.scalar_one_or_none()
        
        # Parse state and audit
        state = GlobalState.model_validate(state_record.state_data)
        
        if audit_log:
            step_audit = StepAudit(
                scenario_id=scenario_id,
                timestep=timestep,
                step_start_time=audit_log.step_start_time,
                step_end_time=audit_log.step_end_time,
                reducer_sequence=audit_log.reducer_sequence,
                field_changes=[],  # Would need to fetch from FieldChangeLog
                triggers_fired=audit_log.triggers_fired,
                errors=audit_log.errors
            )
        else:
            # Create minimal audit for initial state
            from datetime import datetime
            step_audit = StepAudit(
                scenario_id=scenario_id,
                timestep=timestep,
                step_start_time=datetime.utcnow(),
                step_end_time=datetime.utcnow(),
                reducer_sequence=[],
                field_changes=[],
                triggers_fired=[],
                errors=[]
            )
        
        return SimulationStepResponse(
            id=state_record.id,
            scenario_id=scenario_id,
            timestep=timestep,
            state=state,
            audit=step_audit,
            created_at=state_record.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get simulation state: {str(e)}")


@router.get("/scenarios/{scenario_id}/history", response_model=List[SimulationStepResponse])
async def get_simulation_history(
    scenario_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    start_timestep: Optional[int] = Query(None, ge=0),
    end_timestep: Optional[int] = Query(None, ge=0)
):
    """Get simulation history for scenario."""
    try:
        # Verify scenario ownership
        scenario_query = select(Scenario).where(
            and_(Scenario.id == scenario_id, Scenario.user_id == current_user.id)
        )
        scenario_result = await db.execute(scenario_query)
        scenario = scenario_result.scalar_one_or_none()
        
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Build query for simulation states
        query = select(SimulationState).where(SimulationState.scenario_id == scenario_id)
        
        if start_timestep is not None:
            query = query.where(SimulationState.timestep >= start_timestep)
        if end_timestep is not None:
            query = query.where(SimulationState.timestep <= end_timestep)
        
        query = query.order_by(SimulationState.timestep)
        
        result = await db.execute(query)
        states = result.scalars().all()
        
        # Get corresponding audit logs
        audit_query = select(AuditLog).where(AuditLog.scenario_id == scenario_id)
        if start_timestep is not None:
            audit_query = audit_query.where(AuditLog.timestep >= start_timestep)
        if end_timestep is not None:
            audit_query = audit_query.where(AuditLog.timestep <= end_timestep)
        
        audit_result = await db.execute(audit_query)
        audit_logs = {log.timestep: log for log in audit_result.scalars().all()}
        
        # Build response
        history = []
        for state_record in states:
            state = GlobalState.model_validate(state_record.state_data)
            
            audit_log = audit_logs.get(state_record.timestep)
            if audit_log:
                step_audit = StepAudit(
                    scenario_id=scenario_id,
                    timestep=state_record.timestep,
                    step_start_time=audit_log.step_start_time,
                    step_end_time=audit_log.step_end_time,
                    reducer_sequence=audit_log.reducer_sequence,
                    field_changes=[],  # Simplified for performance
                    triggers_fired=audit_log.triggers_fired,
                    errors=audit_log.errors
                )
            else:
                from datetime import datetime
                step_audit = StepAudit(
                    scenario_id=scenario_id,
                    timestep=state_record.timestep,
                    step_start_time=datetime.utcnow(),
                    step_end_time=datetime.utcnow(),
                    reducer_sequence=[],
                    field_changes=[],
                    triggers_fired=[],
                    errors=[]
                )
            
            history.append(SimulationStepResponse(
                id=state_record.id,
                scenario_id=scenario_id,
                timestep=state_record.timestep,
                state=state,
                audit=step_audit,
                created_at=state_record.created_at
            ))
        
        return history
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get simulation history: {str(e)}")


# Template endpoints
@router.post("/templates/mvs", response_model=Dict[str, Any])
async def generate_mvs_template():
    """Generate Minimum Viable Scenario template with real data."""
    try:
        template = await generate_mvs_scenario()
        return {
            "template_type": "MVS",
            "description": "Minimum Viable Scenario with 10 major economies",
            "countries_count": len(template.countries),
            "state": template.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate MVS template: {str(e)}")


@router.post("/templates/fis", response_model=Dict[str, Any])
async def generate_fis_template():
    """Generate Full Information Scenario template with comprehensive data."""
    try:
        template = await generate_fis_scenario()
        return {
            "template_type": "FIS",
            "description": "Full Information Scenario with 30+ economies and comprehensive data",
            "countries_count": len(template.countries),
            "state": template.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate FIS template: {str(e)}")


@router.get("/triggers/examples", response_model=Dict[str, Trigger])
async def get_trigger_examples():
    """Get example trigger configurations for policy scenarios."""
    try:
        examples = load_trigger_examples()
        return examples
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load trigger examples: {str(e)}")
