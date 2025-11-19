# Agent State Schemas

**CRITICAL GUIDE** - Correct patterns for defining agent state schemas in LangGraph

## Overview

Agent state schemas define the data structure that flows through your agent's execution. Understanding the correct patterns is essential for avoiding common pitfalls and errors.

## ⚠️ Critical Pattern: Extend AgentState

**The correct pattern is to extend `AgentState`, NOT use `add_messages`.**

### ❌ WRONG: Using add_messages

```python
from typing_extensions import TypedDict, Annotated
from langchain_core.messages import AnyMessage, add_messages

# ❌ DON'T DO THIS
class MyAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    custom_field: str
```

**Problems:**
- `add_messages` is an older pattern that's no longer recommended
- More verbose and error-prone
- Harder to understand and maintain

### ✅ CORRECT: Extend AgentState

```python
from typing import NotRequired
from langchain.agents import AgentState

# ✅ DO THIS
class MyAgentState(AgentState):
    """State that evolves during agent execution.
    
    Extends AgentState which already includes messages field.
    """
    custom_field: NotRequired[str]
    another_field: NotRequired[dict]
```

**Benefits:**
- `messages` field automatically included from `AgentState`
- Cleaner, more concise code
- Better type support
- Follows current LangChain best practices

## State vs Context

Understanding the difference between state and context is crucial:

### State (First Parameter)

**State evolves during agent execution.**

```python
from langchain.agents import AgentState
from typing import NotRequired

class NationAgentState(AgentState):
    """State that changes as the agent runs."""
    current_action: NotRequired[str]          # Updated during execution
    diplomatic_relations: NotRequired[dict]   # Modified by tools
    military_readiness: NotRequired[float]    # Changes over time
```

- Passed as first parameter to `submit()`
- Updates accumulated through agent execution
- Persisted in checkpoints
- Accessed/modified by tools and middleware

### Context (Options Parameter)

**Context is static during a single invocation.**

```python
from dataclasses import dataclass

@dataclass
class NationAgentContext:
    """Static runtime context for agent invocation."""
    user_id: str          # Who owns the scenario
    scenario_id: int      # Which simulation
    actor_id: int         # This actor's ID
    simulation_step: int  # Current timestep
```

- Passed via `context` in options (second parameter)
- Immutable during execution
- Used for dependency injection
- Accessed via `runtime.context` in tools/middleware

### Usage Example

```python
# State evolves
agent.submit(
    {"messages": [{"role": "user", "content": "Hello"}]},  # Initial state
    {
        "context": NationAgentContext(  # Static context
            user_id="user123",
            scenario_id=42,
            actor_id=7,
            simulation_step=10
        )
    }
)
```

## Complete Implementation Pattern

### 1. Define State Schema

```python
# agents/nation_agent/models/state.py
from typing import NotRequired, Any
from langchain.agents import AgentState

class NationAgentState(AgentState):
    """State that evolves during agent execution.
    
    Extends AgentState which already includes messages.
    Use NotRequired for fields that may not always be present.
    """
    current_action: NotRequired[str]
    diplomatic_relations: NotRequired[dict[str, Any]]
    military_readiness: NotRequired[float]
    resource_stockpiles: NotRequired[dict[str, int]]
    pending_decisions: NotRequired[list[str]]
```

### 2. Define Context Schema

```python
# agents/nation_agent/models/context.py
from dataclasses import dataclass

@dataclass
class NationAgentContext:
    """Static runtime context for agent invocation."""
    user_id: str
    scenario_id: int
    actor_id: int
    simulation_step: int
```

### 3. Export Schemas

```python
# agents/nation_agent/models/__init__.py
from .context import NationAgentContext
from .state import NationAgentState

__all__ = ["NationAgentContext", "NationAgentState"]
```

### 4. Use in Agent

```python
# agents/nation_agent/agent.py
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from agents.nation_agent.models import NationAgentState, NationAgentContext

def create_nation_agent():
    model = ChatOpenAI(model="gpt-5.1")
    
    return create_agent(
        model=model,
        state_schema=NationAgentState,      # Evolving state
        context_schema=NationAgentContext,  # Static context
        middleware=[...],
    )
```

## Accessing State and Context

### In Tools

```python
from langchain_core.tools import tool, ToolRuntime

@tool
async def update_diplomatic_stance(
    target_nation: str,
    stance: str,
    runtime: ToolRuntime[NationAgentContext]
) -> str:
    """Update diplomatic stance toward another nation."""
    
    # Access context (static, immutable)
    actor_id = runtime.context.actor_id
    scenario_id = runtime.context.scenario_id
    
    # Access state (evolving)
    current_state = runtime.state
    current_relations = current_state.get("diplomatic_relations", {})
    
    # Update state
    new_relations = {**current_relations, target_nation: stance}
    
    # Return updates via state
    return json.dumps({
        "diplomatic_relations": new_relations
    })
```

### In Middleware

```python
from langchain.agents.middleware import AgentMiddleware

class StatusMiddleware(AgentMiddleware):
    def before_agent(self, state: NationAgentState, runtime) -> dict | None:
        """Access state before agent execution."""
        
        # Read from state
        current_action = state.get("current_action")
        
        # Access context
        context = runtime.context
        actor_id = context.actor_id
        
        # Return state updates
        return {
            "current_action": "preparing_response"
        }
```

## Common Patterns

### Pattern: Optional Fields with NotRequired

Use `NotRequired` for fields that may not always be present:

```python
from typing import NotRequired
from langchain.agents import AgentState

class MyState(AgentState):
    # Always present
    user_preferences: dict
    
    # May not be present
    current_task: NotRequired[str]
    analysis_results: NotRequired[dict]
```

### Pattern: Complex Nested Types

```python
from typing import NotRequired, Any
from langchain.agents import AgentState

class SimulationState(AgentState):
    # Nested structures
    actor_states: NotRequired[dict[int, dict[str, Any]]]
    event_history: NotRequired[list[dict[str, Any]]]
    relationships: NotRequired[dict[tuple[int, int], float]]
```

### Pattern: Enum Fields

```python
from typing import NotRequired
from enum import Enum
from langchain.agents import AgentState

class DecisionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DecisionState(AgentState):
    status: NotRequired[DecisionStatus]
    decision_type: NotRequired[str]
```

## Migration from add_messages

If you have existing code using `add_messages`:

### Before (Old Pattern)

```python
from typing_extensions import TypedDict, Annotated
from langchain_core.messages import AnyMessage, add_messages

class OldState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    custom_field: str
```

### After (New Pattern)

```python
from typing import NotRequired
from langchain.agents import AgentState

class NewState(AgentState):  # Extends AgentState
    custom_field: NotRequired[str]  # messages already included
```

## Common Errors and Solutions

### Error: AttributeError 'dict' has no attribute 'system_prompt'

**Cause:** Using wrong hook signature in middleware

**Solution:** Use correct middleware hooks:
```python
# ❌ Wrong - before_model receives (state, runtime) as dict
def before_model(self, request: ModelRequest):
    request.system_prompt = "..."  # Error!

# ✅ Correct - wrap_model_call receives ModelRequest
@wrap_model_call
def wrap_model_call(self, request: ModelRequest, handler):
    request.system_prompt = "..."  # Works!
    return handler(request)
```

### Error: Messages not in state

**Cause:** Not extending AgentState

**Solution:** Extend AgentState:
```python
# ❌ Wrong
class MyState(TypedDict):
    custom_field: str
    # messages missing!

# ✅ Correct
class MyState(AgentState):  # messages included automatically
    custom_field: NotRequired[str]
```

### Error: Context fields not accessible

**Cause:** Passing context as state instead of options

**Solution:** Pass context correctly:
```python
# ❌ Wrong
agent.submit({"messages": [...], "user_id": "123"})

# ✅ Correct  
agent.submit(
    {"messages": [...]},
    {"context": {"user_id": "123", ...}}
)
```

## Best Practices

### 1. Separate State and Context Files

```
agents/my_agent/models/
├── __init__.py
├── state.py     # State schema
└── context.py   # Context schema
```

### 2. Document Field Purposes

```python
class MyAgentState(AgentState):
    """State for my agent.
    
    Fields:
        current_task: The task being executed
        task_history: List of completed tasks
        analysis_cache: Cached analysis results
    """
    current_task: NotRequired[str]
    task_history: NotRequired[list[str]]
    analysis_cache: NotRequired[dict]
```

### 3. Use Type Hints Consistently

```python
from typing import NotRequired, Any

class MyState(AgentState):
    # Good: Specific types
    scores: NotRequired[dict[str, float]]
    items: NotRequired[list[str]]
    
    # Avoid: Too generic
    data: NotRequired[Any]  # What kind of data?
```

### 4. Validate State Updates

```python
def update_state(new_values: dict) -> dict:
    """Validate state updates before returning."""
    # Validate
    if "score" in new_values:
        assert 0 <= new_values["score"] <= 100
    
    return new_values
```

## Testing State Schemas

```python
import pytest
from agents.nation_agent.models import NationAgentState, NationAgentContext

def test_state_has_messages():
    """AgentState should include messages automatically."""
    state = NationAgentState()
    assert "messages" in state.__annotations__

def test_context_immutable():
    """Context should be immutable dataclass."""
    context = NationAgentContext(
        user_id="test",
        scenario_id=1,
        actor_id=1,
        simulation_step=0
    )
    
    # Dataclass is immutable
    with pytest.raises(AttributeError):
        context.user_id = "different"

def test_state_optional_fields():
    """Optional fields should use NotRequired."""
    import inspect
    hints = inspect.get_annotations(NationAgentState)
    
    # Custom fields should be NotRequired
    assert "NotRequired" in str(hints.get("current_action"))
```

## Related Documentation

- [Agents Guide](./agents.md) - Creating agents with state schemas
- [Runtime Guide](./runtime.md) - Accessing state and context
- [Tools Guide](./tools.md) - Using state in tools
- [Middleware Guide](./middleware.md) - State manipulation in middleware

## Summary

**Critical Points:**

1. ✅ **Extend `AgentState`** - Don't use `add_messages`
2. ✅ **Use `NotRequired`** - For optional fields
3. ✅ **Separate State and Context** - Different purposes
4. ✅ **Messages Included** - Automatically from AgentState
5. ✅ **TypedDict Not Dataclass** - State is TypedDict, Context is dataclass

Following these patterns ensures type-safe, maintainable agent implementations.
