# LangGraph Prebuilt Agents

## Critical Rule: Use Prebuilt Library
**ALWAYS use prebuilt agents (`create_react_agent`, `create_supervisor`) instead of manual `StateGraph` construction**

### 1. Model Initialization
**Use init_chat_model for consistent model setup**
```python
from langgraph.chat_models import init_chat_model

# ✅ CORRECT - Centralized model init
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(temperature=0.1, model="gpt-4.1")
```

```python
# ✅ CORRECT - Prebuilt agent
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model=llm,
    tools=[get_weather, get_user_email],
    prompt=prompt,
    checkpointer=checkpointer,
    store=store,
)

# ❌ WRONG - Manual graph construction
from langgraph.graph import StateGraph
builder = StateGraph(MessagesState)  # Avoid manual construction
```

## Essential Patterns

### 2. React Agent Creation
**Standard prebuilt agent with all configuration**
```python
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from pydantic import BaseModel

class WeatherResponse(BaseModel):
    location: str
    temperature: float
    description: str

class MyState(AgentState):
    messages: list
    remaining_steps: int
    user_name: str

agent = create_react_agent(
    model=llm,
    tools=[get_weather, get_user_email],
    prompt=prompt,                    # Custom prompt function
    response_format=WeatherResponse,  # Structured output
    context_schema=MyContext,         # Runtime context
    state_schema=MyState,            # Custom state
    checkpointer=checkpointer,       # Async checkpointer
    store=store,                     # Async store
)
```

### 3. Streaming Responses
**Always use async streaming for real-time responses**
```python
# ✅ CORRECT - Async streaming
async for update in agent.astream(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}], 
     "remaining_steps": 3, 
     "user_name": runtime_context.user_name},
    context={"user_name": runtime_context.user_name, "db_uri": runtime_context.db_uri},
    stream_mode="updates",  # or "messages", "values"
):
    print(update)
```

### 4. Structured Output with Response Format
**Use response_format for structured Pydantic model outputs**
```python
from pydantic import BaseModel

class WeatherReport(BaseModel):
    location: str
    temperature: float
    description: str
    humidity: int
    recommendations: list[str]

class TaskResult(BaseModel):
    task_completed: bool
    summary: str
    next_steps: list[str]

agent = create_react_agent(
    model=llm,
    tools=[get_weather, get_user_email],
    response_format=WeatherReport,  # Structured Pydantic output
    context_schema=MyContext,
    state_schema=MyState,
    checkpointer=checkpointer,
)
```

### 5. Custom State Schema
**Extend AgentState for additional fields**
```python
from langgraph.prebuilt.chat_agent_executor import AgentState

class MyState(AgentState):
    messages: list          # Required from AgentState
    remaining_steps: int    # Custom field
    user_name: str         # Custom field
    structured_output: dict # Required for response_format
    # Add other custom fields as needed
```

## Stream Modes

| Mode | Use Case | Output |
|------|----------|---------|
| `"updates"` | Step-by-step progress | Individual node updates |
| `"messages"` | Message-focused apps | Just message updates |
| `"values"` | Full state tracking | Complete state snapshots |

## Common Pitfalls

### 1. Manual Graph Construction
```python
# ❌ WRONG - Manual StateGraph
builder = StateGraph(MessagesState)
builder.add_node(call_model)
graph = builder.compile()

# ✅ CORRECT - Prebuilt agent
agent = create_react_agent(model, tools)
```

### 2. Missing Async Context
```python
# ❌ WRONG - Sync streaming
for update in agent.stream():  # Blocking

# ✅ CORRECT - Async streaming  
async for update in agent.astream():  # Non-blocking
```

### 3. Incorrect State Schema
```python
# ❌ WRONG - Wrong base class
class MyState(MessagesState):  # For manual graphs only

# ✅ CORRECT - For prebuilt agents
class MyState(AgentState):     # For create_react_agent
```

### 4. Missing Required Fields
```python
# ❌ WRONG - Missing messages in state
{"remaining_steps": 3, "user_name": "john"}

# ✅ CORRECT - Always include messages
{"messages": [...], "remaining_steps": 3, "user_name": "john"}
```

## Tool Integration

### 1. Context-Aware Tools
**Tools can access runtime context**
```python
from langgraph.runtime import get_runtime

@tool
def get_user_email() -> str:
    """Retrieve user information based on user ID."""
    runtime = get_runtime(MyContext)
    return get_user_email_from_db(runtime.context.user_name)
```

### 2. State-Accessing Tools
**Tools can access state using InjectedState**
```python
from typing import Annotated, NotRequired
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from langgraph.prebuilt.chat_agent_executor import AgentState

class CustomState(AgentState):
    # The user_name field in short-term state
    user_name: NotRequired[str]

@tool
def get_user_name(
    state: Annotated[CustomState, InjectedState]
) -> str:
    """Retrieve the current user-name from state."""
    # Return stored name or a default if not set
    return state.get("user_name", "Unknown user")
```

### 3. State-Updating Tools
**Tools can update state using Command objects**
```python
from typing import Annotated
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool, InjectedToolCallId

@tool
def update_user_name(
    new_name: str,
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Update user-name in short-term memory."""
    return Command(update={
        "user_name": new_name,
        "messages": [
            ToolMessage(f"Updated user name to {new_name}", tool_call_id=tool_call_id)
        ]
    })
```

## Pre/Post Model Hooks

### 1. Prompt Functions with Formatted Messages
**Prompt functions should return formatted message lists**
```python
from langgraph.runtime import get_runtime
from langchain_core.messages import AnyMessage

def prompt_function(state: MyState) -> list[AnyMessage]:
    """Create formatted messages for the agent."""
    runtime = get_runtime(MyContext)  # Access context
    
    # Access state directly (same as hooks)
    user_name = state.get("user_name", "User")
    
    # Format system prompt with context/state data
    system_prompt = """You are a helpful assistant for {user_name}. 
    Current context: {context_info}""".format(
        user_name=user_name,
        context_info=runtime.context.user_name
    )
    
    # Return list with different formatted message types
    return [
        ("system", system_prompt),           # System message
        ("placeholder", "{messages}"),       # Placeholder for state messages
    ]

agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=prompt_function,  # Formatted messages
    context_schema=MyContext,
    state_schema=MyState,
    checkpointer=checkpointer,
)
```

### 2. Pre-Model Hook Pattern  
**Hooks can process state before LLM calls (e.g., message trimming)**
```python
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from langgraph.runtime import get_runtime

def pre_model_hook(state: MyState):
    """Trim messages before LLM call to manage context length."""
    runtime = get_runtime(MyContext)  # Access context (same as prompts)
    
    trimmed_messages = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=384,
        start_on="human",
        end_on=("human", "tool"),
    )
    return {"llm_input_messages": trimmed_messages}

agent = create_react_agent(
    model=llm,
    tools=tools,
    pre_model_hook=pre_model_hook,  # Add hook
    context_schema=MyContext,
    checkpointer=checkpointer,
)
```

### 3. Advanced Pre-Model Hook with Summarization
**Using summarization nodes for memory management**
```python
from langchain_anthropic import ChatAnthropic
from langmem.short_term import SummarizationNode, RunningSummary
from langchain_core.messages.utils import count_tokens_approximately

class State(AgentState):
    messages: list
    # Track summary information to avoid re-summarizing
    context: dict[str, RunningSummary]

model = ChatAnthropic(model="claude-3-5-sonnet-latest")

summarization_node = SummarizationNode(
    token_counter=count_tokens_approximately,
    model=model,
    max_tokens=384,
    max_summary_tokens=128,
    output_messages_key="llm_input_messages",
)

agent = create_react_agent(
    model=model,
    tools=tools,
    pre_model_hook=summarization_node,
    state_schema=State,
    checkpointer=checkpointer,
)
```

### 4. Post-Model Hook Pattern
**Hooks can process state after LLM calls (e.g., validation, human-in-the-loop)**
```python
from langgraph.runtime import get_runtime

def post_model_hook(state):
    """Validate or process LLM response."""
    runtime = get_runtime(MyContext)  # Access context if needed
    
    # Example: Add validation logic
    last_message = state["messages"][-1]
    if "sensitive_content" in last_message.content:
        return {
            "messages": [
                *state["messages"][:-1],  # Keep all but last
                {"role": "assistant", "content": "I cannot provide that information."}
            ]
        }
    
    return {}  # No changes

agent = create_react_agent(
    model=llm,
    tools=tools,
    post_model_hook=post_model_hook,  # Add hook (version="v2" only)
    context_schema=MyContext,
    version="v2",  # Required for post_model_hook
    checkpointer=checkpointer,
)
```

## State/Context Access Patterns

| Component | State Access | Context Access | Pattern |
|-----------|--------------|----------------|---------|
| **Prompt Functions** | Direct (`state["field"]`) | `get_runtime(MyContext)` | Return formatted message list |
| **Pre/Post Hooks** | Direct (`state["field"]`) | `get_runtime(MyContext)` | Return state update dict |
| **Tools** | `InjectedState` annotation | `get_runtime(MyContext)` | Return values or Commands |

## Hook/Prompt Requirements

| Type | Required Return | Purpose |
|------|----------------|---------|
| `prompt` | `list[AnyMessage]` with formatted messages | Create agent input |
| `pre_model_hook` | `{"messages": [...]}` or `{"llm_input_messages": [...]}` | Process before LLM |
| `post_model_hook` | State update dict | Process after LLM |

## Quick Reference

```python
# Complete prebuilt agent setup with all capabilities
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.types import Command

class MyState(AgentState):
    messages: list
    custom_field: str

@tool
def state_updating_tool(
    value: str,
    state: Annotated[CustomState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    return Command(update={"custom_field": value, "messages": [ToolMessage("Updated", tool_call_id)]})

def pre_hook(state: MyState):
    return {"llm_input_messages": trim_messages(state["messages"], max_tokens=500)}

def post_hook(state: MyState):
    # Validation or processing logic
    return {}

agent = create_react_agent(
    model=llm,
    tools=[state_updating_tool],
    state_schema=MyState,
    pre_model_hook=pre_hook,
    post_model_hook=post_hook,
    context_schema=MyContext,
    version="v2",  # Required for post_model_hook
    checkpointer=async_checkpointer,
    store=async_store,
)

# Stream with all capabilities
async for update in agent.astream(
    {"messages": [...], "custom_field": "value"},
    context=context_dict,
    stream_mode="updates"
):
    process(update)
```

**Memory Aid**: "Prebuilt agents, InjectedState in tools, formatted message prompts, hooks/prompts same access pattern, always async streaming."
