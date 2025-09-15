"""Trigger action application logic."""

from typing import List, Dict, Any, Set, Optional
from ..models.state import (
    GlobalState, Trigger, TriggerCondition, TriggerAction,
    PolicyPatch, ReducerOverride, NetworkRewrite, EventInject,
    AuditCapture
)


def apply_policy_patch(state: GlobalState, patch: PolicyPatch, audit: AuditCapture) -> None:
    """Apply policy parameter changes to state or rules."""
    try:
        # Navigate to the target path in Pydantic model structure
        path_parts = patch.path.split('.')
        target = state
        
        # Navigate to parent object
        for part in path_parts[:-1]:
            if hasattr(target, part):
                target = getattr(target, part)
            elif isinstance(target, dict) and part in target:
                target = target[part]
            else:
                audit.add_error(f"Invalid patch path: {patch.path} (missing {part})")
                return
        
        final_field = path_parts[-1]
        
        # Get old value - try both attribute and dict access
        if hasattr(target, final_field):
            old_value = getattr(target, final_field)
        elif isinstance(target, dict) and final_field in target:
            old_value = target[final_field]
        else:
            old_value = None
        
        # Apply operation
        if patch.op == "set":
            new_value = patch.value
        elif patch.op == "add":
            new_value = (old_value or 0) + patch.value
        elif patch.op == "mul":
            new_value = (old_value or 1) * patch.value
        else:
            audit.add_error(f"Unknown patch operation: {patch.op}")
            return
        
        # Set new value - try both attribute and dict access
        if hasattr(target, final_field):
            setattr(target, final_field, new_value)
        elif isinstance(target, dict):
            target[final_field] = new_value
        else:
            audit.add_error(f"Cannot set field {final_field} on target at {patch.path}")
            return
        
        # Record audit trail
        audit.record_change(
            field_path=patch.path,
            old_value=old_value,
            new_value=new_value,
            calculation_details={
                "trigger_action": "policy_patch",
                "operation": patch.op,
                "patch_value": patch.value
            }
        )
        
    except Exception as e:
        audit.add_error(f"Failed to apply policy patch {patch.path}: {str(e)}")


def apply_reducer_override(state: GlobalState, override: ReducerOverride, audit: AuditCapture) -> None:
    """Switch reducer implementations by updating regime parameters."""
    try:
        # Store override information in rules for the reducer registry to use
        if "rules" not in state:
            state["rules"] = {}
        if "reducer_overrides" not in state["rules"]:
            state["rules"]["reducer_overrides"] = {}
        
        old_impl = state["rules"]["reducer_overrides"].get(override.target)
        state["rules"]["reducer_overrides"][override.target] = override.impl_name
        
        audit.record_change(
            field_path=f"rules.reducer_overrides.{override.target}",
            old_value=old_impl,
            new_value=override.impl_name,
            calculation_details={
                "trigger_action": "reducer_override",
                "target_reducer": override.target,
                "new_implementation": override.impl_name
            }
        )
        
    except Exception as e:
        audit.add_error(f"Failed to apply reducer override {override.target}: {str(e)}")


def apply_network_rewrite(state: GlobalState, rewrite: NetworkRewrite, audit: AuditCapture) -> None:
    """Modify network layer weights/connections."""
    try:
        # Get target network matrix using dictionary access
        matrix = None
        if rewrite.layer == "trade":
            matrix = state.get("trade_matrix", {})
        elif rewrite.layer == "alliances":
            matrix = state.get("alliance_graph", {})
        elif rewrite.layer == "sanctions":
            matrix = state.get("sanctions", {})
        elif rewrite.layer == "interbank":
            matrix = state.get("interbank_matrix", {})
        elif rewrite.layer == "energy":
            # Energy network might need to be created
            if "io_coefficients" not in state:
                state["io_coefficients"] = {}
            if "energy_network" not in state["io_coefficients"]:
                state["io_coefficients"]["energy_network"] = {}
            matrix = state["io_coefficients"]["energy_network"]
        else:
            audit.add_error(f"Unknown network layer: {rewrite.layer}")
            return
        
        if matrix is None:
            audit.add_error(f"Could not access matrix for layer: {rewrite.layer}")
            return
        
        changes_applied = 0
        
        # Apply each edge edit
        for edge_data in rewrite.network_edits:
            if len(edge_data) >= 3:
                from_node = edge_data["from"] if isinstance(edge_data, dict) else edge_data[0]
                to_node = edge_data["to"] if isinstance(edge_data, dict) else edge_data[1]
                weight = edge_data["weight"] if isinstance(edge_data, dict) else edge_data[2]
                
                # Ensure nodes exist in matrix
                if from_node not in matrix:
                    matrix[from_node] = {}
                
                old_weight = matrix[from_node].get(to_node)
                matrix[from_node][to_node] = weight
                changes_applied += 1
                
                # Record individual edge change
                audit.record_change(
                    field_path=f"{rewrite.layer}_matrix.{from_node}.{to_node}",
                    old_value=old_weight,
                    new_value=weight,
                    calculation_details={
                        "trigger_action": "network_rewrite",
                        "network_layer": rewrite.layer,
                        "edge": f"{from_node}->{to_node}"
                    }
                )
        
        if changes_applied == 0:
            audit.add_error(f"No valid network edits applied for layer {rewrite.layer}")
            
    except Exception as e:
        audit.add_error(f"Failed to apply network rewrite for {rewrite.layer}: {str(e)}")


def inject_event(state: GlobalState, event: EventInject, audit: AuditCapture) -> None:
    """Add event to pending queue for processing by event reducers."""
    try:
        # Ensure events structure exists
        if "events" not in state:
            state["events"] = {"pending": []}
        if "pending" not in state["events"]:
            state["events"]["pending"] = []
        
        # Create event object
        event_obj = {
            "kind": event.kind,
            "payload": event.payload,
            "injected_at_timestep": state.get("t", 0),
            "status": "pending"
        }
        
        # Add to pending events
        old_length = len(state["events"]["pending"])
        state["events"]["pending"].append(event_obj)
        
        audit.record_change(
            field_path="events.pending",
            old_value=old_length,
            new_value=len(state["events"]["pending"]),
            calculation_details={
                "trigger_action": "event_inject",
                "event_kind": event.kind,
                "event_payload": event.payload,
                "injected_at_timestep": state.get("t", 0)
            }
        )
        
    except Exception as e:
        audit.add_error(f"Failed to inject event {event.kind}: {str(e)}")


def apply_trigger(state: GlobalState, trigger: Trigger, audit: AuditCapture) -> bool:
    """
    Execute all trigger actions.
    
    Returns:
        bool: True if trigger was successfully applied, False otherwise
    """
    success = True
    actions_applied = {
        "patches": 0,
        "overrides": 0,
        "network_rewrites": 0,
        "events": 0
    }
    
    try:
        # Apply policy patches
        for patch in trigger.action.patches:
            apply_policy_patch(state, patch, audit)
            actions_applied["patches"] += 1
        
        # Apply reducer overrides
        for override in trigger.action.overrides:
            apply_reducer_override(state, override, audit)
            actions_applied["overrides"] += 1
        
        # Apply network rewrites
        for rewrite in trigger.action.network_rewrites:
            apply_network_rewrite(state, rewrite, audit)
            actions_applied["network_rewrites"] += 1
        
        # Inject events
        for event in trigger.action.events:
            inject_event(state, event, audit)
            actions_applied["events"] += 1
        
        # Record overall trigger application
        audit.add_calculation_detail(f"trigger_{trigger.name}_actions", actions_applied)
        
    except Exception as e:
        audit.add_error(f"Failed to apply trigger {trigger.name}: {str(e)}")
        success = False
    
    return success
