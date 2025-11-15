# Agent Folder Organization

## Overview

Standard folder structure for organizing agents using the middleware-centric pattern. This structure promotes clarity, maintainability, and consistency across all agents in the codebase.

## Standard Agent Structure

```
agents/
└── my_agent/
    ├── __init__.py              # Exports get_my_agent() factory
    ├── agent.py                 # Agent factory function
    ├── README.md                # Agent-specific documentation
    ├── utils.py                 # Helper functions (optional)
    ├── middleware/              # Agent-specific middleware
    │   ├── __init__.py          # Exports middleware & prompts
    │   ├── core_prompt.py       # @dynamic_prompt for agent
    │   ├── tools_prompt.py      # Tool guidance (if tools used)
    │   └── my_guardrails.py     # Configured middleware instances
    ├── models/                  # Data models
    │   ├── __init__.py
    │   ├── context.py           # Runtime context schema
    │   ├── state.py             # Agent state schema
    │   ├── structured_output.py # Response format
    │   └── guardrails.py        # Validation schemas (optional)
    ├── tools/                   # Agent-specific tools
    │   ├── __init__.py
    │   └── my_tool.py           # Custom tool implementations
    └── specialists/             # For manager agents only
        ├── __init__.py
        ├── definitions.py       # Specialist configurations
        ├── factory.py           # Specialist creation
        └── middleware/          # Specialist middleware
            ├── __init__.py
            ├── core_prompt.py
            └── tools_prompt.py
```

## File Purposes

### Root Files

**`__init__.py`**
- Exports the main factory function: `get_my_agent()`
- Minimal, just for public API exposure

**`agent.py`**
- Contains the main factory function
- Composes middleware stack
- Creates and configures the agent
- Example:
```python
def get_my_agent(llm, checkpointer=None):
    """Create configured agent."""
    return create_agent(
        model=llm,
        middleware=[
            core_prompt,
            ToolsMiddleware(tools),
            StatusInjectionMiddleware(),
            PatchToolCallsMiddleware()
        ],
        context_schema=MyContext,
        state_schema=MyState,
        response_format=MyOutput,
        checkpointer=checkpointer
    )
```

**`README.md`**
- Agent overview and purpose
- Middleware stack explanation
- Usage examples
- Configuration options

**`utils.py`** (optional)
- Helper functions specific to this agent
- Data transformations
- Validation logic

### `/middleware` Folder

Contains agent-specific middleware configurations.

**`core_prompt.py`**
- `@dynamic_prompt` function for agent identity
- Accesses runtime context and state
- **IMPORTANT**: Should contain only agent identity, NOT tool guidance
- Example:
```python
@dynamic_prompt
def my_agent_prompt(request: ModelRequest) -> str:
    context = request.runtime.context
    return f"You are {context.persona}..."
```

**`tools_prompt.py`** (if agent uses tools)
- Tool usage guidance as a string constant
- Uses `{tools_list}` placeholder for automatic tool listing
- **IMPORTANT**: Separate from core identity prompt
- Example:
```python
MY_AGENT_TOOLS_PROMPT = """
=== Available Tools ===

{tools_list}

**Tool Usage Guidelines:**
- Use tool_name for X purpose
- Use other_tool for Y purpose
"""
```

**Agent-specific middleware instances**
- Configured versions of reusable middleware
- Example: `my_guardrails.py`

**`__init__.py`**
- Exports middleware and prompts
- Imports from `rapid_ai.agents.middleware.custom`

### `/models` Folder

Contains all Pydantic models and schemas.

**`context.py`**
- Runtime context schema (extends base Context)
- Immutable configuration passed to agent
- Example:
```python
@dataclass
class MyAgentContext:
    """Runtime context for MyAgent."""
    user_id: str
    persona: str
    entity_id: str
```

**`state.py`**
- Agent state schema (extends AgentState)
- Tracks conversation and custom fields
- Example:
```python
class MyAgentState(AgentState):
    """Extended state for MyAgent."""
    custom_field: NotRequired[str]
```

**`structured_output.py`**
- Input and output models
- Response format definitions
- Example:
```python
class MyAgentOutput(BaseModel):
    """Structured output from MyAgent."""
    result: str
    confidence: float
```

**`guardrails.py`** (optional)
- Validation schemas for guardrails middleware
- Output filtering models

### `/tools` Folder

Agent-specific tool implementations.

**Tool files**
- Custom tools not in common tools library
- Domain-specific functionality
- Use `@tool` decorator or BaseTool class

### `/specialists` Folder (Manager Agents Only)

For agents using the manager-worker pattern.

**`definitions.py`**
- Specialist tool configurations
- Specialist descriptions for delegation
- Example:
```python
SPECIALIST_DESCRIPTIONS = {
    "specialist_1": "Handles task type A...",
    "specialist_2": "Handles task type B..."
}

specialized_agent_tools = {
    "specialist_1": [tool1, tool2],
    "specialist_2": [tool3, tool4]
}
```

**`factory.py`**
- Function to create specialist agents
- Applies worker middleware stack
- Example:
```python
def create_specialist_agent(llm, specialist_name, tools):
    return create_agent(
        model=llm,
        middleware=[worker_prompt, ToolsMiddleware(tools), ...],
        ...
    )
```

**`/specialists/middleware/`**
- Specialist-specific middleware
- Worker prompts and configurations

## Manager vs Worker Organization

### Manager Agent

```
my_manager_agent/
├── agent.py                    # Manager factory
├── middleware/
│   ├── core_prompt.py          # Manager prompt
│   └── manager_guardrails.py
├── models/
│   ├── context.py              # ManagerContext
│   ├── state.py                # ManagerState (with specialist_histories)
│   └── structured_output.py
└── specialists/                # Specialist configuration
    ├── definitions.py
    ├── factory.py
    └── middleware/
        ├── core_prompt.py      # Worker prompt
        └── tools_prompt.py
```

**Key Features:**
- Uses `SpecialistAgentsMiddleware`
- State includes `specialist_histories`
- Has `specialists/` folder
- Manager delegates to workers

### Worker Agent

```
my_worker_agent/
├── agent.py                    # Worker factory
├── middleware/
│   ├── core_prompt.py          # Worker identity
│   └── tools_prompt.py         # Tool guidance
├── models/
│   ├── context.py              # WorkerContext
│   ├── state.py                # WorkerState
│   └── structured_output.py
└── tools/                      # Domain tools
    └── my_tools.py
```

**Key Features:**
- Uses `ToolsMiddleware` for domain tools
- Separates identity (core_prompt.py) from tool guidance (tools_prompt.py)
- No `specialists/` folder
- Focused on execution, not delegation
- Typically has more tools

## Import Patterns

### Good Import Structure

```python
# agent.py
from .middleware import core_prompt, my_guardrails
from .models import MyContext, MyState, MyOutput
from rapid_ai.agents.middleware.custom import (
    StatusInjectionMiddleware,
    ToolsMiddleware
)

# middleware/__init__.py
from rapid_ai.agents.middleware.custom.guardrails import GuardrailsMiddleware
from .core_prompt import my_agent_prompt as core_prompt
from .my_guardrails import my_guardrails_instance

# models/__init__.py
from .context import MyContext
from .state import MyState
from .structured_output import MyInput, MyOutput
```

### Avoiding Circular Imports

**Problem:**
```python
# models/structured_output.py imports from models/state.py
# models/state.py imports from models/structured_output.py
```

**Solution:**
```python
# Use TYPE_CHECKING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .state import MyState

# Or restructure to avoid circular dependency
```

## Naming Conventions

### Files
- `snake_case` for all Python files
- `core_prompt.py` for main agent prompt (identity only)
- `tools_prompt.py` for tool guidance (if agent uses tools)
- `{feature}_middleware.py` for middleware configs
- `context.py`, `state.py`, `structured_output.py` for models

### Functions
- `get_{agent_name}()` for factory functions
- `create_{specialist}_agent()` for specialist factories
- `{agent_name}_prompt` for `@dynamic_prompt` functions

### Classes
- `PascalCase` for all classes
- `{Agent}Context` for context schemas
- `{Agent}State` for state schemas
- `{Agent}Input` / `{Agent}Output` for I/O models
- `{Feature}Middleware` for middleware classes

### Variables
- `snake_case` for variables
- `{agent}_core_prompt` for prompt instances
- `{agent}_guardrails` for configured middleware

## Best Practices

### Do ✓

1. **Keep agent.py focused** - Just factory and middleware composition
2. **Use models/ for all schemas** - One place for data structures
3. **Configure middleware in middleware/** - Agent-specific instances
4. **Separate core identity from tool guidance** - Use core_prompt.py and tools_prompt.py
5. **Use {tools_list} placeholder** - In tools_prompt.py for automatic tool listing
6. **Document assumptions** - In READMEs and docstrings
7. **Export through __init__** - Clean public API
8. **Separate manager and worker** - Different patterns, different structures
9. **Use @dynamic_prompt** - For context-aware prompts

### Don't ✗

1. **Don't put business logic in agent.py** - Use middleware or tools
2. **Don't mix tool guidance with core identity** - Separate into different files
3. **Don't manually list tools** - Use {tools_list} placeholder
4. **Don't hardcode prompts** - Use @dynamic_prompt or constants
5. **Don't create circular imports** - Use TYPE_CHECKING
6. **Don't mix manager and worker patterns** - Choose one
7. **Don't duplicate middleware** - Create reusable versions in custom/
8. **Don't forget __init__.py files** - Python needs them
9. **Don't skip documentation** - Future you will thank you

## Common Patterns

### Pattern: Simple Worker Agent

```
simple_worker/
├── __init__.py
├── agent.py
├── middleware/
│   ├── __init__.py
│   ├── core_prompt.py
│   └── tools_prompt.py      # If tools used
├── models/
│   ├── __init__.py
│   ├── context.py
│   ├── state.py
│   └── structured_output.py
└── tools/
    └── my_tools.py
```

### Pattern: Complex Manager Agent

```
complex_manager/
├── __init__.py
├── agent.py
├── README.md
├── middleware/
│   ├── __init__.py
│   ├── core_prompt.py
│   └── manager_guardrails.py
├── models/
│   ├── __init__.py
│   ├── context.py
│   ├── state.py
│   ├── structured_output.py
│   ├── criteria.py
│   └── guardrails.py
└── specialists/
    ├── __init__.py
    ├── definitions.py
    ├── factory.py
    ├── formatter.py
    └── middleware/
        ├── __init__.py
        ├── core_prompt.py
        └── tools_prompt.py
```

### Pattern: Shared Utilities

For code shared across multiple agents, use the common middleware location:

```
rapid_ai/agents/middleware/custom/
├── guardrails/
│   ├── __init__.py
│   └── middleware.py
├── tools/
│   ├── __init__.py
│   └── middleware.py
└── status_injection/
    ├── __init__.py
    └── middleware.py
```

## Migration Guide

### Refactoring to This Structure

1. **Identify agent type** - Manager or worker?
2. **Extract middleware** - Move to middleware/
3. **Organize models** - Consolidate in models/
4. **Create factory** - Simple get_agent() function
5. **Add documentation** - README with examples
6. **Update imports** - Use clean import patterns
7. **Test thoroughly** - Ensure nothing broke

## Example: Real Box Agent Structure

```
box/
├── __init__.py                          # Exports get_box_agent
├── agent.py                             # Manager factory
├── README.md                            # Full documentation
├── utils.py                             # Helper functions
├── middleware/
│   ├── __init__.py
│   ├── core_prompt.py                   # Manager @dynamic_prompt
│   └── box_guardrails.py                # Configured guardrails
├── models/
│   ├── __init__.py
│   ├── context.py                       # BoxManagerContext
│   ├── state.py                         # ManagerState
│   ├── structured_output.py             # BoxInput, BoxOutput
│   ├── criteria.py                      # RiskCriteria
│   └── guardrails.py                    # Validation schemas
└── specialists/
    ├── __init__.py
    ├── definitions.py                   # 7 specialist configs
    ├── factory.py                       # create_specialist_agent()
    ├── formatter.py                     # Response formatting
    └── middleware/
        ├── __init__.py
        ├── core_prompt.py               # Worker @dynamic_prompt
        └── tools_prompt.py              # Tool guidance
```

This structure enables the box agent to:
- Clearly separate manager and worker concerns
- Reuse middleware across 7 specialists
- Maintain clean imports
- Scale to complex multi-agent systems

## Summary

Good folder organization:
- **Makes code discoverable** - Know where to find things
- **Reduces complexity** - Separation of concerns
- **Enables reuse** - Shared components obvious
- **Simplifies testing** - Clear boundaries
- **Aids onboarding** - Consistent patterns

Follow this structure for all agents to maintain consistency across the codebase.
