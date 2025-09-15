# LangGraph Context Management

## Critical Rule: Use ContextSchema Dataclasses
**ALWAYS use dataclasses with ContextSchema for runtime context**

```python
# ✅ CORRECT - Dataclass with ContextSchema
from dataclasses import dataclass
from langgraph.context import ContextSchema

@dataclass
class MyContext(ContextSchema):
    user_name: str
    db_uri: str

# ❌ WRONG - Plain dict or class
context = {"user_name": "john", "db_uri": "..."}  # No validation
```

## Essential Patterns

### 1. Context Schema Definition
**Define context using dataclass with proper typing**
```python
from dataclasses import dataclass
from langgraph.context import ContextSchema

@dataclass
class MyContext(ContextSchema):
    user_name: str
    db_uri: str
    # Add other context fields as needed
```

### 2. Runtime Context Access in Tools
**Tools access context through get_runtime()**
```python
from langgraph.runtime import get_runtime

@tool
def get_user_email() -> str:
    """Retrieve user information based on user ID."""
    runtime = get_runtime(MyContext)
    return get_user_email_from_db(runtime.context.user_name)

@tool  
def save_to_database(data: str) -> str:
    """Save data to user's database."""
    runtime = get_runtime(MyContext)
    # Use runtime.context.db_uri for database operations
    return save_data(data, runtime.context.db_uri)
```

### 3. Context-Aware Prompt Functions
**Prompt functions can access runtime context**
```python
from langgraph.runtime import get_runtime
from langchain_core.messages import AnyMessage

def prompt(state: MyState) -> list[AnyMessage]:
    runtime = get_runtime(MyContext)
    sys_msg = f"You are a helpful assistant. Address the user as {runtime.context.user_name}."
    return [{"role": "system", "content": sys_msg}] + state["messages"]
```

### 4. Context Propagation in Agent Calls
**Always pass context when invoking or streaming agents**
```python
# ✅ CORRECT - Context passed properly
async for update in agent.astream(
    {"messages": [...], "remaining_steps": 3, "user_name": runtime_context.user_name},
    context={"user_name": runtime_context.user_name, "db_uri": runtime_context.db_uri},
    stream_mode="updates",
):
    print(update)

# ✅ ALSO CORRECT - Context object to dict
async for update in agent.astream(
    {"messages": [...], "remaining_steps": 3},
    context=runtime_context.__dict__,  # Convert dataclass to dict
    stream_mode="updates",
):
    print(update)
```

## Context Integration with Agent Creation

```python
from dataclasses import dataclass
from langgraph.context import ContextSchema
from langgraph.prebuilt import create_react_agent

@dataclass
class MyContext(ContextSchema):
    user_name: str
    db_uri: str

# Agent creation with context schema
agent = create_react_agent(
    model=llm,
    tools=[get_weather, get_user_email],
    prompt=prompt,
    context_schema=MyContext,  # Required for runtime access
    state_schema=MyState,
    checkpointer=checkpointer,
    store=store,
)
```

## Common Pitfalls

### 1. Missing Context Schema in Agent
```python
# ❌ WRONG - No context_schema specified
agent = create_react_agent(
    model="anthropic:claude-3-5-sonnet-latest",
    tools=[get_user_email],  # Tool uses get_runtime() but no schema
)

# ✅ CORRECT - Context schema specified
agent = create_react_agent(
    model=llm,
    tools=[get_user_email],
    context_schema=MyContext,  # Required!
)
```

### 2. Context Not Passed in Invocation
```python
# ❌ WRONG - Missing context in agent call
async for update in agent.astream(
    {"messages": [...], "remaining_steps": 3}
    # Missing context parameter
):
    print(update)

# ✅ CORRECT - Context included
async for update in agent.astream(
    {"messages": [...], "remaining_steps": 3},
    context={"user_name": "john", "db_uri": "..."},
):
    print(update)
```

### 3. Wrong Context Type in Tools
```python
# ❌ WRONG - Wrong context class in get_runtime()
@tool
def get_user_email() -> str:
    runtime = get_runtime(SomeOtherContext)  # Wrong type
    
# ✅ CORRECT - Matching context class
@tool
def get_user_email() -> str:
    runtime = get_runtime(MyContext)  # Matches agent's context_schema
```

### 4. Plain Dict Instead of ContextSchema
```python
# ❌ WRONG - Plain dict, no validation
context_dict = {"user_name": "john", "db_uri": "..."}

# ✅ CORRECT - ContextSchema dataclass with validation
@dataclass
class MyContext(ContextSchema):
    user_name: str
    db_uri: str

context = MyContext(user_name="john", db_uri="...")
```

## Complete Example

```python
from dataclasses import dataclass
from langgraph.context import ContextSchema
from langgraph.runtime import get_runtime
from langgraph.prebuilt import create_react_agent

@dataclass
class MyContext(ContextSchema):
    user_name: str
    db_uri: str

@tool
def get_user_data() -> str:
    """Get user-specific data."""
    runtime = get_runtime(MyContext)
    return f"Data for {runtime.context.user_name}"

def custom_prompt(state: MyState) -> list[AnyMessage]:
    runtime = get_runtime(MyContext)
    sys_msg = f"Assistant for {runtime.context.user_name}"
    return [{"role": "system", "content": sys_msg}] + state["messages"]

# Agent with context
agent = create_react_agent(
    model=llm,
    tools=[get_user_data],
    prompt=custom_prompt,
    context_schema=MyContext,
    state_schema=MyState,
)

# Usage with context
runtime_context = MyContext(user_name="Alice", db_uri="postgresql://...")
async for update in agent.astream(
    {"messages": [...], "remaining_steps": 3},
    context=runtime_context.__dict__,
):
    print(update)
```

## Quick Reference

- **Context Definition**: Use `@dataclass` with `ContextSchema`
- **Tool Access**: `runtime = get_runtime(MyContext)`
- **Agent Setup**: Include `context_schema=MyContext`
- **Agent Calls**: Always pass `context=context_dict`
- **Context Dict**: Use `context_obj.__dict__` to convert

**Memory Aid**: "Dataclass context schema, get_runtime in tools, always pass context dict to agent calls."
