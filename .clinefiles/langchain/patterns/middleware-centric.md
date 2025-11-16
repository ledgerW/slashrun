# Middleware-Centric Agent Pattern

## Overview

Build LangChain agents by composing reusable middleware instead of writing monolithic agent code. This pattern provides better separation of concerns, reusability, and maintainability.

## Core Concept

```python
# Traditional approach - monolithic
agent = create_agent(
    model=llm,
    tools=[tool1, tool2, tool3],
    system_prompt=long_complex_prompt
)

# Middleware-centric approach - composable
agent = create_agent(
    model=llm,
    middleware=[
        CorePromptMiddleware(),      # Dynamic prompts
        ToolsMiddleware(tools=tools), # Tool injection
        GuardrailsMiddleware(...),   # Safety checks
        StatusInjectionMiddleware(), # Context awareness
        PatchToolCallsMiddleware()   # Must be last
    ]
)
```

## Why Use This Pattern?

1. **Reusability**: Write middleware once, use across many agents
2. **Composition**: Mix and match capabilities as needed
3. **Separation of Concerns**: Each middleware handles one responsibility
4. **Testability**: Test middleware independently
5. **Maintainability**: Update middleware without touching agent code
6. **Clarity**: Clear middleware stack shows what the agent does

## Key Principles

### 1. Middleware Extends AgentMiddleware

```python
from langchain.agents.middleware import AgentMiddleware

class MyMiddleware(AgentMiddleware):
    """Brief description of what this does."""
    
    def __init__(self, **config):
        super().__init__()
        self.config = config
    
    # Implement hooks as needed
    def wrap_model_call(self, request, handler):
        # Modify request before model call
        request.system_prompt = "Custom: " + request.system_prompt
        return handler(request)
```

### 2. Dynamic Prompts Over Static Strings

```python
from langchain.agents.middleware import dynamic_prompt, ModelRequest

@dynamic_prompt
def my_core_prompt(request: ModelRequest) -> str:
    """Context-aware prompt that adapts at runtime."""
    context = request.runtime.context
    return f"You are {context.persona}. Entity: {context.entity_id}"

# Use in agent
agent = create_agent(
    model=llm,
    middleware=[my_core_prompt, ...]
)
```

### 3. State Schema Extension

Middleware can extend agent state with custom fields:

```python
from typing_extensions import TypedDict, NotRequired
from langchain.agents.middleware import AgentState

class MyExtendedState(AgentState):
    """Extended state with custom tracking."""
    custom_field: NotRequired[str]
    specialist_histories: NotRequired[dict]

class MyMiddleware(AgentMiddleware):
    state_schema = MyExtendedState
    
    def before_agent(self, state, runtime):
        return {"custom_field": "initialized"}
```

### 4. Tool Injection via Middleware

**IMPORTANT**: Always separate core agent identity from tool usage guidance. Core prompts define who the agent is; tool prompts explain how to use tools.

```python
# middleware/core_prompt.py - Agent identity ONLY
@dynamic_prompt
def chatbot_prompt(request: ModelRequest) -> str:
    """Core identity - NO tool guidance here."""
    return """You are a helpful assistant..."""

# middleware/tools_prompt.py - Tool guidance ONLY
CHATBOT_TOOLS_PROMPT = """
=== Tools Available ===

You have access to the following specialized tools:
{tools_list}

**Tool Usage Guidelines:**
- Use search_content when user asks about X
- Use retrieve_document when user needs Y
"""

# agent.py - Compose with ToolsMiddleware
from rapid_ai.agents.middleware.custom import ToolsMiddleware

agent = create_agent(
    model=llm,
    middleware=[
        core_prompt,  # Identity first
        ToolsMiddleware(
            tools=[search_tool, retrieve_tool],
            system_prompt=CHATBOT_TOOLS_PROMPT  # Guidance second
        ),
        ...
    ]
)
```

**The `{tools_list}` placeholder** is automatically replaced with formatted tool descriptions at runtime. This ensures:
- Tool descriptions stay in sync with actual tools
- Agent sees up-to-date tool signatures
- No manual maintenance of tool lists

## ⚠️ Critical Requirements for Custom Middleware

**All custom middleware MUST:**

1. **Extend `AgentMiddleware` base class**
   ```python
   from langchain.agents.middleware import AgentMiddleware
   
   class MyMiddleware(AgentMiddleware):  # MUST extend
   ```

2. **Call `super().__init__()` in constructor**
   ```python
   def __init__(self, **config):
       super().__init__()  # CRITICAL: Must call this
       self.config = config
   ```

**Failure to follow these requirements will cause:**
- `AttributeError: type object 'YourMiddleware' has no attribute 'wrap_tool_call'`
- Middleware not being recognized by `create_agent()`
- Agent initialization failures

## Common Middleware Stack Patterns

### Manager Agent Stack

Manager coordinates specialists or handles high-level tasks:

```python
manager = create_agent(
    model=llm,
    middleware=[
        manager_core_prompt,                    # Manager identity & goals
        SpecialistAgentsMiddleware(specialists),# Delegation capability
        StatusInjectionMiddleware(),            # Work awareness
        GuardrailsMiddleware(...),              # Quality control
        AnthropicPromptCachingMiddleware(),     # Performance
        PatchToolCallsMiddleware()              # Must be last
    ],
    context_schema=ManagerContext,
    state_schema=ManagerState,
    response_format=ManagerOutput
)
```

### Worker Agent Stack

Worker executes tools and performs specific tasks:

```python
worker = create_agent(
    model=llm,
    middleware=[
        worker_core_prompt,                     # Worker identity
        ToolsMiddleware(tools=worker_tools),    # Domain tools
        InjectConfigMiddleware(),               # Config injection
        JMESPathMapMiddleware(),                # Large data handling
        FilesystemMiddleware(...),              # File operations
        StatusInjectionMiddleware(),            # Task awareness
        AnthropicPromptCachingMiddleware(),     # Performance
        PatchToolCallsMiddleware()              # Must be last
    ],
    context_schema=WorkerContext,
    state_schema=WorkerState,
    response_format=WorkerOutput
)
```

## Middleware Ordering Matters

```python
middleware=[
    # 1. Core prompts first - establish identity/goals
    core_prompt,
    
    # 2. Feature middleware - add capabilities
    ToolsMiddleware(tools),
    SpecialistAgentsMiddleware(specialists),
    
    # 3. Data handling middleware
    InjectConfigMiddleware(),
    JMESPathMapMiddleware(),
    FilesystemMiddleware(...),
    
    # 4. Context/status awareness
    StatusInjectionMiddleware(),
    
    # 5. Quality control
    GuardrailsMiddleware(...),
    
    # 6. Performance optimizations
    AnthropicPromptCachingMiddleware(),
    
    # 7. Fixes/patches MUST BE LAST
    PatchToolCallsMiddleware()
]
```

**Why?**
- Prompts establish context for later middleware
- Feature middleware builds on core identity
- Data handling needs to come before status tracking
- Guardrails validate final outputs
- Patches fix issues without being modified by other middleware

## Creating Reusable Middleware

### Design for Configuration

```python
class GuardrailsMiddleware(AgentMiddleware):
    """Reusable guardrails - configure per agent."""
    
    def __init__(
        self,
        *,
        system_prompt_rules: str,
        output_filter_system_prompt: Optional[str] = None,
        output_filter_user_prompt: Optional[str] = None,
        output_schema: Optional[Type[BaseModel]] = None,
        validation_model: Optional[BaseChatModel] = None
    ):
        super().__init__()
        self.system_prompt_rules = system_prompt_rules
        self.output_filter_system_prompt = output_filter_system_prompt
        # ... store config
```

### Agent-Specific Instances

Create configured instances in agent middleware folders:

```
agents/my_agent/middleware/
├── __init__.py
├── core_prompt.py           # Agent-specific prompt
└── my_guardrails.py         # Configured instance

# my_guardrails.py
from rapid_ai.agents.middleware.custom.guardrails import GuardrailsMiddleware
from ..prompts.guardrails import my_rules

my_guardrails = GuardrailsMiddleware(
    system_prompt_rules=my_rules,
    validation_model=get_llm("gpt-4o-mini")
)
```

### Document Assumptions

Always document what your middleware expects:

```python
class MyMiddleware(AgentMiddleware):
    """
    Brief description.
    
    ## Assumptions
    
    ### Context Schema:
    - Requires `context.entity_id` field
    - Optional `context.persona` field
    
    ### State Schema:
    - Reads `state.messages` for history
    - Writes `state.custom_field` for tracking
    
    ### Message Format:
    - Expects ToolMessage to have `name` attribute
    - AI messages may have `tool_calls` list
    """
```

## Common Patterns

### Pattern: Dynamic Prompt

```python
@dynamic_prompt
def my_prompt(request: ModelRequest) -> str:
    """Dynamic prompt accesses context and state."""
    context = request.runtime.context
    state = request.runtime.state
    
    # Build prompt based on runtime data
    prompt = f"You are {context.persona}."
    
    # Add context-aware information
    if state.get("reference_context"):
        prompt += f"\n\nContext: {state['reference_context']}"
    
    return prompt
```

### Pattern: Tool Guidance with {tools_list}

```python
# middleware/tools_prompt.py
AGENT_TOOLS_PROMPT = """
=== Available Tools ===

{tools_list}

**When to Use Tools:**
- Use tool_name for purpose X
- Use another_tool for purpose Y

**Tool Guidelines:**
- Always validate inputs before calling
- Handle tool errors gracefully
"""

# agent.py
from rapid_ai.agents.middleware.custom import ToolsMiddleware
from .middleware.tools_prompt import AGENT_TOOLS_PROMPT

middleware = [
    core_prompt,
    ToolsMiddleware(tools=tools, system_prompt=AGENT_TOOLS_PROMPT),
    ...
]
```

### Pattern: Tool Wrapping

```python
class InjectConfigMiddleware(AgentMiddleware):
    """Inject config into tool calls."""
    
    async def awrap_tool_call(self, request, handler):
        tool_call = request.tool_call
        context = request.runtime.context
        
        # Inject entity_id into tool args
        if 'entity_id' not in tool_call['args']:
            tool_call['args']['entity_id'] = context.entity_id
        
        # Call handler with modified request
        return await handler(request)
```

### Pattern: Output Validation

```python
class GuardrailsMiddleware(AgentMiddleware):
    """Validate and correct outputs."""
    
    @hook_config(can_jump_to=["end"])
    def after_agent(self, state, runtime):
        last_message = state["messages"][-1]
        
        # Validate output
        if not self._is_valid(last_message):
            # Return correction
            return {
                "messages": [AIMessage(content="Corrected output")],
                "jump_to": "end"
            }
        
        return None  # No changes
```

### Pattern: State Extension

```python
class SpecialistAgentsMiddleware(AgentMiddleware):
    """Track specialist conversation histories."""
    
    # Extend state schema
    state_schema = SpecialistHistoriesState
    
    # Tools automatically update state
    @tool
    async def assign_to_specialist(task: str, runtime: ToolRuntime):
        result = await specialist_agent.ainvoke({"messages": [task]})
        
        # Return Command to update extended state
        return Command(update={
            "messages": [ToolMessage(content=result)],
            "specialist_histories": {
                f"specialist_1": result["messages"]
            }
        })
```

## Dos and Don'ts

### Do ✓

- **Compose middleware** for different agent types
- **Use @dynamic_prompt** for context-aware prompts
- **Separate tool guidance from core prompts** - Use ToolsMiddleware with tools_prompt.py
- **Use {tools_list} placeholder** - Automatic tool listing in prompts
- **Document assumptions** clearly
- **Order middleware** thoughtfully
- **Test middleware** independently
- **Configure via __init__** for reusability
- **Return Command** to update state from tools
- **Handle errors gracefully** - never break agent execution

### Don't ✗

- **Don't mix tool guidance with core identity** - Separate concerns
- **Don't manually list tools** - Use {tools_list} placeholder
- **Don't use static prompts** when context varies
- **Don't modify state directly** - return updates
- **Don't ignore middleware order** - it matters
- **Don't create monolithic middleware** - separate concerns
- **Don't forget async versions** of hooks (awrap_model_call, etc.)
- **Don't place patches before other middleware**
- **Don't break on errors** - log and continue

## Quick Reference

### Available Hooks

```python
# Model call wrapping
def wrap_model_call(request, handler) -> ModelResponse
async def awrap_model_call(request, handler) -> ModelResponse

# Tool call wrapping
def wrap_tool_call(request, handler) -> ToolMessage | Command
async def awrap_tool_call(request, handler) -> ToolMessage | Command

# Agent lifecycle
def before_agent(state, runtime) -> dict | None
async def abefore_agent(state, runtime) -> dict | None

def after_agent(state, runtime) -> dict | None
async def aafter_agent(state, runtime) -> dict | None

# Model lifecycle (less common)
def before_model(state, runtime) -> dict | None
def after_model(state, runtime) -> dict | None
```

### Creating Dynamic Prompts

```python
from langchain.agents.middleware import dynamic_prompt, ModelRequest

@dynamic_prompt
def my_prompt(request: ModelRequest) -> str:
    # Access context
    context = request.runtime.context
    # Access state  
    state = request.runtime.state
    # Build prompt
    return f"Custom prompt for {context.user_id}"
```

### Extending State

```python
from typing_extensions import TypedDict, NotRequired
from langchain.agents.middleware import AgentState

class MyState(AgentState):
    custom_field: NotRequired[str]

class MyMiddleware(AgentMiddleware):
    state_schema = MyState
```

### Adding Tools

```python
class ToolsMiddleware(AgentMiddleware):
    def __init__(self, tools: List[BaseTool]):
        super().__init__()
        self._tools = tools
    
    @property
    def tools(self):
        return self._tools
```

## Summary

The middleware-centric pattern enables:
1. **Reusable components** across agents
2. **Clear separation** of concerns
3. **Flexible composition** of capabilities
4. **Easy testing** and maintenance
5. **Consistent patterns** across the codebase

Build agents by composing middleware, not by writing monolithic code.
