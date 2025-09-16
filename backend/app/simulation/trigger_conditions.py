"""Trigger condition evaluation logic."""

import re
from typing import Any

from db.models.state import GlobalState


def eval_condition(state: GlobalState, condition: str) -> bool:
    """
    Evaluate trigger condition using simple DSL.
    
    Supported syntax:
    - date>=2026-01-01 (timestep comparison)
    - country('USA').macro.inflation>0.05 (field access)
    - t >= 3 (timestep comparison)
    - && (AND operator)
    - || (OR operator)
    """
    if not condition.strip():
        return True
    
    # Replace date comparisons with timestep comparisons
    # For simplicity, assume each timestep = 1 quarter, starting from 2025-Q1
    date_pattern = r'date([><=!]+)(\d{4}-\d{2}-\d{2})'
    
    def date_replacement(match):
        operator = match.group(1)
        date_str = match.group(2)
        year = int(date_str[:4])
        # Simplified: each year = 4 timesteps, starting from 2025
        target_timestep = (year - 2025) * 4
        return f"state.t{operator}{target_timestep}"
    
    condition = re.sub(date_pattern, date_replacement, condition)
    
    # Replace country access pattern with safe attribute access
    country_pattern = r"country\('([^']+)'\)\.([a-zA-Z_][a-zA-Z0-9_.]*)"
    
    def country_replacement(match):
        country_name = match.group(1)
        field_path = match.group(2)
        # Build safe nested attribute access using getattr
        return f"safe_getattr(state.countries.get('{country_name}'), '{field_path}')"
    
    condition = re.sub(country_pattern, country_replacement, condition)
    
    # Replace simple timestep access - avoid double replacement
    condition = re.sub(r'(?<!state\.)\bt\b', 'state.t', condition)
    
    # Replace logical operators
    condition = condition.replace("&&", " and ").replace("||", " or ")
    
    # Helper function for safe nested attribute access
    def safe_getattr(obj, path, default=None):
        """Safely get nested attribute, returning None if any part is missing."""
        if obj is None:
            return default
        try:
            for part in path.split('.'):
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                else:
                    return default
            return obj
        except (AttributeError, TypeError):
            return default
    
    # Create safe evaluation context
    eval_context = {
        "state": state,
        "safe_getattr": safe_getattr,
        "__builtins__": {},  # Disable built-in functions for security
    }
    
    try:
        result = eval(condition, eval_context)
        return bool(result) if result is not None else False
    except Exception as e:
        # If evaluation fails, don't trigger
        print(f"Condition evaluation failed for '{condition}': {e}")
        return False
