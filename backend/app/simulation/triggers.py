"""Trigger engine for policy management, regime switches, and event injection."""

from typing import List, Dict, Any, Set, Optional

from db.models.state import GlobalState, Trigger, AuditCapture
from .trigger_conditions import eval_condition
from .trigger_actions import apply_trigger
from .trigger_examples import load_trigger_examples


def process_triggers(
    state: GlobalState, 
    triggers: List[Trigger], 
    fired_triggers: Set[str], 
    audit: AuditCapture
) -> List[str]:
    """
    Process all triggers, return newly fired trigger names.
    
    Args:
        state: Current simulation state
        triggers: List of all triggers to evaluate
        fired_triggers: Set of already fired trigger names (for once-only triggers)
        audit: Audit capture object
    
    Returns:
        List[str]: Names of triggers that fired this timestep
    """
    newly_fired = []
    
    for trigger in triggers:
        # Skip if this is a once-only trigger that has already fired
        if trigger.condition.once and trigger.name in fired_triggers:
            continue
        
        # Evaluate trigger condition
        try:
            should_fire = eval_condition(state, trigger.condition.when or "")
        except Exception as e:
            audit.add_error(f"Error evaluating trigger {trigger.name}: {str(e)}")
            continue
        
        if should_fire:
            # Apply the trigger
            if apply_trigger(state, trigger, audit):
                newly_fired.append(trigger.name)
                audit.add_trigger_fired(trigger.name)
                
                # Mark as fired if it's a once-only trigger
                if trigger.condition.once:
                    fired_triggers.add(trigger.name)
    
    return newly_fired


def expire_triggers(
    state: GlobalState, 
    triggers: List[Trigger], 
    fired_triggers: Dict[str, int]
) -> List[str]:
    """
    Remove expired triggers based on expires_after_turns.
    
    Args:
        state: Current simulation state
        triggers: List of all triggers
        fired_triggers: Dict mapping trigger name to timestep when first fired
    
    Returns:
        List[str]: Names of triggers that expired this timestep
    """
    expired = []
    
    for trigger in triggers:
        if (trigger.expires_after_turns is not None and 
            trigger.name in fired_triggers):
            
            turns_since_fired = state.t - fired_triggers[trigger.name]
            if turns_since_fired >= trigger.expires_after_turns:
                expired.append(trigger.name)
    
    # Remove expired triggers from fired_triggers
    for expired_trigger in expired:
        fired_triggers.pop(expired_trigger, None)
    
    return expired


# Create trigger engine package
__all__ = [
    "process_triggers",
    "expire_triggers",
    "load_trigger_examples"
]
