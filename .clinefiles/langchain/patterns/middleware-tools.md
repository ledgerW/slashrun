# Middleware-Centric Tools Pattern

**Last Updated:** 2025-01-11

## Overview

This guide documents the recommended pattern for adding custom tools to LangGraph agents using middleware rather than passing tools directly to `create_agent()`. This approach provides better modularity, reusability, and organization of agent capabilities.

## Why Middleware-Centric?

### Traditional Approach (Avoid)
```python
# ❌ DON'T: Passing tools directly
agent = create_agent(
    model=model,
    tools=[tool1, tool2, tool3, ...],  # Tools passed directly
    system_prompt=PROMPT,
    middleware=[...],
)
```

### Middleware-Centric Approach (Recommended)
```python
# ✅ DO: Tools wrapped in middleware
agent = create_agent(
    model=model,
    # No tools parameter - provided by middleware instead
    system_prompt=PROMPT,
    middleware=[
        TodoListMiddleware(),
        FilesystemMiddleware(),
        ToolsMiddleware(),  # Custom tools via middleware
        CustomSubagentMiddleware(),
        # ...
    ],
)
```

### Benefits

1. **Modularity**: Tools are bundled into logical groups
2. **Reusability**: Same middleware can be used across multiple agents
3. **Versioning**: Middleware can evolve independently
4. **Organization**: Clear separation of concerns
5. **Testability**: Easier to test tool groups in isolation
6. **Runtime Control**: Middleware can conditionally enable/disable tools

## Implementation Pattern

### Step 1: Create Tools Module

Create tools with real implementations (not mock data):

```python
# tools/database_tools.py
from langchain_core.tools import tool
from langchain_core.tools import ToolRuntime
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field
import asyncpg

# Import context schema
from ..schemas.context import SimulationContext

# Structured output schemas
class InfluenceAnalysis(BaseModel):
    """Structured output for influence calculations."""
    influence_score: int = Field(description="Overall influence score from 0-100")
    diplomatic_power: int = Field(description="Diplomatic capability score 0-100")
    # ... more fields

@tool
async def query_scenario_state(
    scenario_id: int,
    runtime: ToolRuntime[SimulationContext]
) -> str:
    """Get current state of a simulation scenario.
    
    Args:
        scenario_id: The ID of the scenario to query
        runtime: Runtime context with user information
    
    Returns:
        JSON string with scenario details
    """
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Real database query
        scenario = await conn.fetchrow(
            """
            SELECT id, name, description, status, current_timestep
            FROM scenarios
            WHERE id = $1 AND user_id = $2
            """,
            scenario_id,
            runtime.context.get("user_id")
        )
        
        # Return structured data
        return json.dumps(dict(scenario), indent=2, default=str)
    finally:
        await conn.close()

@tool
async def calculate_influence(
    actor_id: int,
    runtime: ToolRuntime[SimulationContext]
) -> str:
    """Calculate actor influence using AI analysis.
    
    Uses LLM with structured output for analysis.
    """
    # Get actor data from database
    conn = await asyncpg.connect(DATABASE_URL)
    actor = await conn.fetchrow("SELECT * FROM actors WHERE id = $1", actor_id)
    await conn.close()
    
    # Use LLM with structured output
    llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.3)
    structured_llm = llm.with_structured_output(InfluenceAnalysis)
    
    prompt = f"""Analyze the influence and power of this actor:
    
    Actor: {actor['name']}
    Type: {actor['actor_type']}
    Resources: {json.dumps(actor['resources'], indent=2)}
    
    Provide comprehensive influence analysis..."""
    
    analysis = await structured_llm.ainvoke(prompt)
    return json.dumps(analysis.model_dump(), indent=2)
```

### Step 2: Create Tools Middleware

Create a **generalizable** middleware that accepts a list of tools and an optional prompt explaining the tool group's purpose:

**⚠️ CRITICAL:** All custom middleware MUST extend `AgentMiddleware` base class and call `super().__init__()`. Failing to do this will cause `AttributeError: type object 'ToolsMiddleware' has no attribute 'wrap_tool_call'` errors.

```python
# middleware/tools.py
from langchain.agents.middleware import AgentMiddleware
from typing import Callable, Optional

class ToolsMiddleware(AgentMiddleware):  # MUST extend AgentMiddleware
    """Generalizable middleware for providing custom tools to agents.
    
    This middleware-centric approach:
    - Accepts any list of tools (developer groups them logically)
    - Accepts optional prompt explaining the tool group's purpose
    - Automatically adds tool descriptions to system prompts
    - Uses standard runtime context (not "middleware context")
    - Is reusable across different agents and use cases
    """
    
    def __init__(self, tools: list, prompt: Optional[str] = None):
        """Initialize the tools middleware with a group of related tools.
        
        Args:
            tools: List of tool functions to provide to the agent
            prompt: Optional prompt explaining the purpose and usage of this tool group
        """
        super().__init__()  # CRITICAL: Must call super().__init__()
        self.tools = tools
        self.group_prompt = prompt
    
    def wrap_model_call(self, request, handler: Callable) -> any:
        """Add tool group context and descriptions to system prompt.
        
        This is the middleware-centric pattern:
        1. Add optional group context prompt
        2. Add tool descriptions to system prompt
        3. Call handler with enhanced request
        
        Args:
            request: ModelRequest with standard runtime context
            handler: Function to call with the request
            
        Returns:
            ModelResponse from the handler
        """
        # Build tool information section
        tool_info = "\n\n"
        
        # Add group context if provided
        if self.group_prompt:
            tool_info += f"## Tool Group Context\n{self.group_prompt}\n\n"
        
        # Add tool descriptions
        tool_info += "## Available Tools\n"
        for tool in self.tools:
            tool_info += f"- **{tool.name}**: {tool.description}\n"
        
        # Append to system prompt
        request.system_prompt = request.system_prompt + tool_info
        
        # Call handler with enhanced request
        return handler(request)
    
    async def awrap_model_call(self, request, handler: Callable) -> any:
        """Add tool group context and descriptions to system prompt (async).
        
        Args:
            request: ModelRequest with standard runtime context
            handler: Async function to call with the request
            
        Returns:
            ModelResponse from the handler
        """
        # Build tool information section
        tool_info = "\n\n"
        
        # Add group context if provided
        if self.group_prompt:
            tool_info += f"## Tool Group Context\n{self.group_prompt}\n\n"
        
        # Add tool descriptions
        tool_info += "## Available Tools\n"
        for tool in self.tools:
            tool_info += f"- **{tool.name}**: {tool.description}\n"
        
        # Append to system prompt
        request.system_prompt = request.system_prompt + tool_info
        
        # Call handler with enhanced request
        return await handler(request)
```

### Step 3: Use in Agent

Use the generalizable middleware pattern by passing tools and optional context prompt:

```python
# agents/supervisor/agent.py
from middleware.tools import ToolsMiddleware
from tools.database_tools import (
    query_scenario_state,
    get_actor_relationships,
    get_timestep_history,
    update_actor_resources,
    create_actor_message,
    calculate_influence,
    evaluate_policy,
    advance_simulation
)

# Build middleware stack
middleware_stack = [
    TodoListMiddleware(),
    FilesystemMiddleware(backend=backend),
    
    # Generalizable ToolsMiddleware - pass tools list and context prompt
    ToolsMiddleware(
        tools=[
            query_scenario_state,
            get_actor_relationships,
            get_timestep_history,
            update_actor_resources,
            create_actor_message,
            calculate_influence,
            evaluate_policy,
            advance_simulation
        ],
        prompt="Database and analysis tools for managing simulation state. These tools allow querying scenario information, analyzing actor relationships and influence, managing resources and messages, evaluating policy impacts, and advancing the simulation timestep. Use these tools to gather information before making decisions or delegating to specialist subagents."
    ),
    
    CustomSubagentMiddleware(subagents=[...]),
    SummarizationMiddleware(model=model),
    AnthropicPromptCachingMiddleware(),
    PatchToolCallsMiddleware(),
]

# Create agent
agent = create_agent(
    model=model,
    system_prompt=SUPERVISOR_SYSTEM_PROMPT,
    middleware=middleware_stack,  # Tools provided via middleware
    context_schema=SimulationContext,
    state_schema=SimulationState,
    checkpointer=checkpointer,
    store=store
)
```

**Key Benefits of This Approach:**
- **Logical Grouping**: Developer organizes related tools into meaningful groups
- **Context-Rich**: Optional prompt explains the tool group's purpose and usage guidelines
- **Reusable**: Same ToolsMiddleware class works for any set of tools
- **Multiple Instances**: Can use multiple ToolsMiddleware instances for different tool groups

## Tool Implementation Best Practices

### 1. Real Database Operations

Tools should perform actual operations, not return mock data:

```python
# ❌ DON'T: Mock data
@tool
def get_actor(actor_id: int) -> str:
    return f"Actor {actor_id}: Mock data"

# ✅ DO: Real database query
@tool
async def get_actor(actor_id: int, runtime: ToolRuntime[Context]) -> str:
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        actor = await conn.fetchrow(
            "SELECT * FROM actors WHERE id = $1",
            actor_id
        )
        return json.dumps(dict(actor), indent=2, default=str)
    finally:
        await conn.close()
```

### 2. LLM Calls for Analysis

Use LLMs with structured output for analysis tools:

```python
@tool
async def evaluate_policy(policy_description: str, runtime: ToolRuntime) -> str:
    """Analyze policy impacts using AI."""
    llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.4)
    
    structured_llm = llm.with_structured_output(PolicyEvaluation)
    
    prompt = f"""Evaluate this policy:
    
    Policy: {policy_description}
    
    Provide comprehensive impact assessment..."""
    
    evaluation = await structured_llm.ainvoke(prompt)
    return json.dumps(evaluation.model_dump(), indent=2)
```

### 3. Use Runtime Context

Access user/session context via `ToolRuntime`:

```python
@tool
async def query_user_data(
    query: str,
    runtime: ToolRuntime[SimulationContext]
) -> str:
    """Query user-specific data."""
    user_id = runtime.context.get("user_id")
    scenario_id = runtime.context.get("scenario_id")
    
    # Use context for authorization and filtering
    conn = await asyncpg.connect(DATABASE_URL)
    data = await conn.fetchrow(
        "SELECT * FROM data WHERE user_id = $1 AND scenario_id = $2",
        user_id,
        scenario_id
    )
    await conn.close()
    
    return json.dumps(dict(data), indent=2, default=str)
```

## Code Organization

### Recommended Structure

```
agent-service/
├── schemas/
│   ├── context.py          # Runtime context schemas
│   └── state.py            # Conversation state schemas
├── middleware/
│   ├── tools.py            # Tools middleware
│   └── subagents.py        # Subagent middleware
├── tools/
│   ├── database_tools.py   # Database operation tools
│   └── analysis_tools.py   # AI analysis tools
└── agents/
    ├── main_agent.py       # Entry point
    ├── supervisor/          # Supervisor agent folder
    │   ├── agent.py        # Supervisor implementation
    │   └── prompts.py      # Supervisor prompts
    └── subagents/          # Subagents folder
        ├── nation/         # Nation agent
        │   ├── agent.py
        │   ├── prompts.py
        │   └── tools.py
        ├── organization/   # Organization agent
        │   ├── agent.py
        │   ├── prompts.py
        │   └── tools.py
        ├── individual/     # Individual agent
        │   ├── agent.py
        │   ├── prompts.py
        │   └── tools.py
        └── population/     # Population agent
            ├── agent.py
            ├── prompts.py
            └── tools.py
```

### Import Organization

```python
# agents/main_agent.py (entry point)
from agents.supervisor.agent import create_supervisor_agent
graph = create_supervisor_agent()

# agents/supervisor/agent.py
from schemas.context import SimulationContext
from schemas.state import SimulationState
from .prompts import SUPERVISOR_SYSTEM_PROMPT
from middleware.tools import ToolsMiddleware
from middleware.subagents import CustomSubagentMiddleware
from agents.subagents.nation.agent import create_nation_agent
from agents.subagents.organization.agent import create_organization_agent
# ... other subagent imports
```

## Complete Example

See the GeoSim Platform implementation:

- **Tools**: `agent-service/tools/database_tools.py`
- **Middleware**: `agent-service/middleware/tools.py`
- **Agent**: `agent-service/agents/main_agent.py`
- **Schemas**: `agent-service/schemas/`
- **Prompts**: `agent-service/prompts/`

## Migration from Direct Tools

If you have an existing agent with direct tools:

1. Create `middleware/tools.py` with `ToolsMiddleware` class
2. Move tool imports from agent to middleware
3. Remove `tools=[...]` parameter from `create_agent()`
4. Add `ToolsMiddleware()` to middleware stack
5. Verify tools are bound correctly by checking agent schema

## Testing Tools Middleware

```python
# Test that tools are properly bound
def test_tools_middleware():
    middleware = ToolsMiddleware()
    assert len(middleware.tools) > 0
    assert all(hasattr(t, '__name__') for t in middleware.tools)

# Test tool execution
async def test_tool_execution():
    result = await query_scenario_state(
        scenario_id=1,
        runtime=MockRuntime(context={"user_id": "test_user"})
    )
    assert result  # Should return data, not mock string
```

## Related Guides

- **Supervisor Pattern**: `.clinefiles/langchain/patterns/custom-subagents.md`
- **Custom Subagents**: `.clinefiles/langchain/patterns/custom-subagents.md`
- **Tools Guide**: `.clinefiles/langchain/core/tools.md`
- **Middleware Guide**: `.clinefiles/langchain/core/middleware.md`

## When to Use This Pattern

✅ **Use middleware-centric tools when:**
- Building production agents with custom capabilities
- Tools need database access or API calls
- Tools require LLM analysis with structured output
- You want modular, reusable tool groups
- Multiple agents share common tools

❌ **Direct tools may be acceptable for:**
- Quick prototypes or demos
- Single-use utility tools
- Simple agents with 1-2 tools
- Learning/tutorial contexts

## Summary

The middleware-centric tools pattern provides:
1. Better code organization
2. Improved reusability
3. Clearer separation of concerns
4. Easier testing and maintenance
5. Professional, production-ready architecture

This is the **recommended approach** for all production agent implementations.
