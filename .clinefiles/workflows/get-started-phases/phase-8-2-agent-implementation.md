# Phase 8.2: Agent Implementation

**Time Estimate:** 30-40 minutes

**Purpose:** Implement agent(s) based on Phase 0 assessment using middleware-centric production pattern

**Prerequisites:**
- Phase 8.1 completed with `langgraph dev` running
- PROJECT_REQUIREMENTS.md documenting Phase 0 agent decisions
- Understanding of agent architecture from Phase 0 (supervisor/simple/both)

**Key References:**
- **`.clinefiles/langchain/patterns/agent-folder-organization.md`** - ⚠️ **CRITICAL: MUST READ FIRST**
- `.clinefiles/langchain/patterns/middleware-centric.md` - Middleware composition pattern
- `.clinefiles/langchain/patterns/middleware-tools.md` - Production middleware-tools pattern
- `.clinefiles/langchain/core/agents.md` - Agent fundamentals
- `.clinefiles/langchain/core/tools.md` - Custom tool creation

---

## ⚠️ CRITICAL: Step 0 - Set Up Proper Folder Structure

**READ THIS FIRST:** `.clinefiles/langchain/patterns/agent-folder-organization.md`

**This step is MANDATORY and must be completed BEFORE any agent implementation.**

### Why This Matters

The folder structure is not just organization - it's the foundation for:
- ✅ **Scalability** - Support multiple agents in one codebase
- ✅ **Reusability** - Share middleware across agents
- ✅ **Maintainability** - Know where everything lives
- ✅ **Clarity** - Separate manager vs worker concerns
- ✅ **Production-Ready** - Follow established patterns

### Required Structure

```
langchain_/src/
├── agents/                      # All agents live here
│   ├── my_agent/               # Your first agent (worker pattern)
│   │   ├── __init__.py         # Exports get_my_agent()
│   │   ├── agent.py            # Factory function
│   │   ├── README.md           # Agent documentation
│   │   ├── middleware/         # Agent-specific middleware
│   │   │   ├── __init__.py
│   │   │   ├── core_prompt.py  # @dynamic_prompt (identity ONLY)
│   │   │   └── tools_prompt.py # Tool guidance (separate from identity)
│   │   ├── models/             # Data models
│   │   │   ├── __init__.py
│   │   │   ├── context.py      # Runtime context
│   │   │   ├── state.py        # Agent state
│   │   │   └── structured_output.py  # I/O models
│   │   └── tools/              # Agent-specific tools
│   │       ├── __init__.py
│   │       └── my_tools.py
│   │
│   └── other_agent/            # Additional agents (if needed)
│       └── ... (same structure)
│
└── middleware/                  # ⚠️ SHARED middleware (reusable)
    ├── __init__.py
    ├── tools_middleware.py      # Generalizable ToolsMiddleware
    ├── guardrails_middleware.py # Generalizable GuardrailsMiddleware
    ├── specialist_middleware.py # For manager agents
    └── ... (other reusable middleware)
```

### Key Principles

1. **`agents/` folder** - All agents at same level
   - Multiple agents supported: `agents/my_agent/`, `agents/other_agent/`
   - Each agent is self-contained

2. **`middleware/` folder** - Shared, reusable middleware
   - Same level as `agents/`
   - NOT inside agent folders
   - Generalizable implementations (accept config in __init__)

3. **Agent-specific middleware** - Inside `agents/my_agent/middleware/`
   - Configured instances of shared middleware
   - Agent-specific prompts and configurations

4. **Separation of concerns:**
   - `core_prompt.py` - Agent identity ONLY
   - `tools_prompt.py` - Tool guidance (uses {tools_list} placeholder)
   - NEVER mix identity with tool guidance

### Step 0.1: Create Base Structure

```bash
cd langchain_/src

# Create agents directory (all agents live here)
mkdir -p agents

# Create shared middleware directory (reusable middleware)
mkdir -p middleware
touch middleware/__init__.py
```

### Step 0.2: Create Your First Agent Folder

```bash
# Replace my_agent with your agent name (e.g., customer_support, data_analyst)
mkdir -p agents/my_agent
cd agents/my_agent

# Create agent files
touch __init__.py agent.py README.md

# Create middleware folder (agent-specific)
mkdir -p middleware
touch middleware/__init__.py
touch middleware/core_prompt.py
touch middleware/tools_prompt.py  # If agent uses tools

# Create models folder
mkdir -p models
touch models/__init__.py
touch models/context.py
touch models/state.py
touch models/structured_output.py

# Create tools folder (if agent needs custom tools)
mkdir -p tools
touch tools/__init__.py
touch tools/my_tools.py
```

### Step 0.3: Update langgraph.json

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/agents/my_agent/agent.py:graph"
  },
  "env": ".env"
}
```

**Note:** If you have multiple agents, add them to the graphs object:

```json
{
  "graphs": {
    "my_agent": "./src/agents/my_agent/agent.py:graph",
    "other_agent": "./src/agents/other_agent/agent.py:graph"
  }
}
```

### Step 0.4: Verification Checklist

Before proceeding to Step 1, verify:

- [ ] `agents/` directory created at `langchain_/src/agents/`
- [ ] `middleware/` directory created at `langchain_/src/middleware/` (NOT inside agents/)
- [ ] Agent folder created: `agents/my_agent/`
- [ ] Agent has: `__init__.py`, `agent.py`, `README.md`
- [ ] Agent has `middleware/` subfolder with `core_prompt.py` and `tools_prompt.py`
- [ ] Agent has `models/` subfolder with `context.py`, `state.py`, `structured_output.py`
- [ ] Agent has `tools/` subfolder (if needed)
- [ ] `langgraph.json` points to `./src/agents/my_agent/agent.py:graph`
- [ ] Read `.clinefiles/langchain/patterns/agent-folder-organization.md` thoroughly

**⚠️ DO NOT proceed to Step 1 without completing this structure.**

---

## Step 0.5: Define Interface Specifications (REQUIRED)

**⚠️ CRITICAL: Interface-First Development**

Before writing ANY implementation code, you MUST define the interface specifications in the agent's README.md.

**Reference:** `project/service-interfaces/README.md` - Interface-first methodology

### Why This Step is Mandatory

From `project/service-interfaces/README.md`:
```
❌ WRONG: Implement → Document
✅ RIGHT: Document → Implement → Validate
```

**If you implement before documenting:**
1. ❌ Multiple sources of truth emerge
2. ❌ TypeScript/Python types diverge
3. ❌ Integration failures occur
4. ❌ No spec to validate against

### Step 0.5.1: Create Agent README with Interface Specifications

Create `src/agents/my_agent/README.md` with this structure:

```markdown
# [Agent Name] Agent

[Brief description of agent's purpose]

---

## Interface Specifications

### State Schema (AgentState)

The state that changes during agent execution:

\`\`\`python
from typing import TypedDict, Annotated, Any
from langchain_core.messages import AnyMessage, add_messages

class MyAgentState(TypedDict):
    """State that evolves during agent execution."""
    messages: Annotated[list[AnyMessage], add_messages]
    # Add your state fields based on Phase 0 requirements
    field1: str
    field2: dict[str, Any]
\`\`\`

**Field Descriptions:**
- `messages`: Conversation history (managed by LangChain)
- `field1`: [Description of what this field stores]
- `field2`: [Description of what this field stores]

### Context Schema (Runtime)

Static context provided at invocation time:

\`\`\`python
from dataclasses import dataclass

@dataclass
class MyAgentContext:
    """Static runtime context for agent invocation."""
    user_id: str          # User who owns the data
    # Add context fields based on Phase 0 requirements
    context_field1: int
    context_field2: str
\`\`\`

**Usage:** Context accessed via `runtime.context` in tools and middleware

### Invocation Example

From Next.js using `useStream()` hook:

\`\`\`typescript
import { useStream } from "@langchain/langgraph-sdk/react";

const thread = useStream<MyAgentState>({
  apiUrl: process.env.NEXT_PUBLIC_AGENT_API_URL,
  assistantId: "my-agent",
  threadId: threadId,
  messagesKey: "messages",
});

// Submit with state and context
thread.submit(
  // Input State
  {
    messages: [{ role: "user", content: "User message" }],
    field1: "initial value",
    field2: {}
  },
  // Options with context
  {
    context: {
      user_id: "uuid-here",
      context_field1: 123,
      context_field2: "value"
    }
  }
);
\`\`\`

### Output Structure

After agent execution, state is updated:

\`\`\`python
{
    "messages": [
        # All conversation messages including agent responses
    ],
    "field1": "updated value",
    "field2": {
        "key": "value"
    }
}
\`\`\`

### Integration Points

**Next.js Frontend:**
- Documentation: [nextjs-langchain-interface.md](../../../project/service-interfaces/nextjs-langchain-interface.md#my-agent)
- TypeScript types match Python schemas
- Uses `useStream()` hook pattern

**Supabase Database:**
- Documentation: [langchain-supabase-interface.md](../../../project/service-interfaces/langchain-supabase-interface.md#my-agent-tools)
- Tools access specific tables
- Service role key for elevated access

---

[Rest of README with architecture, tools, etc.]
```

### Step 0.5.2: Update Service Interface Documents

Mark agent as PLANNED in service interface documents:

#### Update nextjs-langchain-interface.md

Add agent section to `project/service-interfaces/nextjs-langchain-interface.md`:

```markdown
## My Agent

### Status
🔵 PLANNED

### Agent Details
**Location**: `langchain_/src/agents/my_agent/`
**README**: [my_agent/README.md](../../langchain_/src/agents/my_agent/README.md#interface-specifications)

### TypeScript Types

\`\`\`typescript
// State schema (matches Python TypedDict)
interface MyAgentState {
  messages: Message[];
  field1: string;
  field2: Record<string, any>;
}

// Context schema (matches Python dataclass)
interface MyAgentContext {
  user_id: string;
  context_field1: number;
  context_field2: string;
}
\`\`\`

### References

**Python Schemas**: [my_agent/README.md](../../langchain_/src/agents/my_agent/README.md#interface-specifications)
**Supabase Operations**: [langchain-supabase-interface.md#my-agent-tools](./langchain-supabase-interface.md#my-agent-tools)
```

#### Update langchain-supabase-interface.md

Add tool section to `project/service-interfaces/langchain-supabase-interface.md`:

```markdown
## My Agent Tools

### Status
🔵 PLANNED

### Agent Location
**Agent**: `langchain_/src/agents/my_agent/`
**Tools**: `langchain_/src/agents/my_agent/tools/my_tools.py`
**README**: [my_agent/README.md](../../langchain_/src/agents/my_agent/README.md#interface-specifications)

### Tool: [tool_name]

**Purpose**: [What this tool does]

**Context Used**:
\`\`\`python
@dataclass
class MyAgentContext:
    user_id: str
    context_field1: int
\`\`\`

**Database Operations**:
\`\`\`python
@tool
def tool_name(runtime: ToolRuntime[MyAgentContext]) -> dict:
    # Access context
    user_id = runtime.context.user_id
    
    # Query database
    result = supabase.table('table_name').select('*').execute()
    
    return result.data
\`\`\`

**Tables Accessed**:
- `table_name` (SELECT)

**Migrations Referenced**:
- `20250110000001_create_tables.sql`
```

### Step 0.5.3: Validation Checklist

Before proceeding to implementation, verify:

- [ ] Agent README created with complete Interface Specifications section
- [ ] State Schema (TypedDict) documented with all fields
- [ ] Context Schema (dataclass) documented with all fields
- [ ] Invocation example shows correct useStream() pattern
- [ ] Output structure documented
- [ ] Integration points referenced (NextJS & Supabase docs)
- [ ] nextjs-langchain-interface.md updated with agent section (marked 🔵 PLANNED)
- [ ] langchain-supabase-interface.md updated with tool section (marked 🔵 PLANNED)
- [ ] TypeScript types match Python schemas exactly
- [ ] All team members reviewed and approved interface contract

**⚠️ DO NOT implement until interface specifications are complete and approved.**

### Why This Matters

This interface documentation is:
1. **The Contract** - Between frontend, backend, and database
2. **The Source of Truth** - All code must match these specs
3. **The Validation Target** - You'll verify implementation against this
4. **The Onboarding Doc** - New developers learn the system from this

**Reference:** See `langchain_/src/agents/nation_agent/README.md` for a complete example.

---

## Step 1: Review Phase 0 Agent Decisions

**Before writing code, review your Phase 0 assessment in PROJECT_REQUIREMENTS.md:**

1. **Agent Architecture:** What type(s) of agents did you decide to build?
   - Supervisor agent (complex tasks, planning, delegation)
   - Simple agent (direct tool calling, Q&A)
   - Both (different use cases)

2. **Middleware Stack:** Which middleware did Phase 0 determine you need?
   - TodoListMiddleware (planning)
   - FilesystemMiddleware (file operations)
   - CustomSubagentMiddleware (delegation)
   - SummarizationMiddleware (context management)
   - Error handling middleware

3. **Custom Tools:** What domain-specific tools did Phase 0 identify?
   - Database queries
   - API calls
   - Business logic
   - File operations

4. **Memory Requirements:** How should threads be organized?
   - Per conversation, per project, per user session?

---

## Step 2: Define Agent State

**Replace the minimal state from Phase 8.1 with your actual state schema.**

All agents need at least a messages list. Add additional state fields as needed:

```python
# src/agent/graph.py
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class State(TypedDict):
    """
    Agent state schema.
    Reference: .clinefiles/langchain/core/agents.md
    """
    # Messages are REQUIRED for all agents
    messages: Annotated[list, add_messages]
    
    # Add application-specific state based on Phase 0 requirements
    # Examples:
    # context: str  # Additional context from database
    # task_list: list[str]  # If using TodoListMiddleware
    # files: dict  # If using FilesystemMiddleware
    # user_id: str  # For user-specific operations
```

**State Design Principles:**
- Keep state minimal - only what's needed across nodes
- Use clear, descriptive names
- Document purpose of each field
- Reference Phase 0 requirements

---

## Step 3: Choose Agent Pattern

### Option A: Simple Agent (Direct Tool Calling)

**Use when:** Single-step tasks, no planning needed, straightforward Q&A

```python
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Initialize model
model = ChatOpenAI(model="gpt-4o-mini", streaming=True)

# Define tools (see Step 4)
tools = [
    # your custom tools here
]

# Create agent using prebuilt pattern
graph = create_react_agent(
    model,
    tools=tools,
    state_schema=State,
)
```

**Reference:** `.clinefiles/langchain/core/agents.md` for simple agent patterns

### Option B: Supervisor Agent (Planning & Delegation)

**Use when:** Complex multi-step tasks, research, delegation to subagents

```python
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END

# Initialize model
model = ChatAnthropic(model="claude-3-5-sonnet-20241022", streaming=True)

# Build graph with nodes and edges
builder = StateGraph(State)

# Add nodes (defined in Step 5)
builder.add_node("planner", planner_node)
builder.add_node("executor", executor_node)
builder.add_node("reviewer", reviewer_node)

# Define flow
builder.add_edge(START, "planner")
builder.add_conditional_edges(
    "planner",
    route_after_planning,
    {"execute": "executor", "done": END}
)
builder.add_edge("executor", "reviewer")
builder.add_conditional_edges(
    "reviewer",
    route_after_review,
    {"continue": "executor", "done": END}
)

graph = builder.compile()
```

**Reference:** `.clinefiles/langchain/patterns/custom-subagents.md` for supervisor patterns

### Option C: Multiple Agents (Both Types)

**Use when:** App needs both quick Q&A AND complex tasks

Create separate graph files:
- `src/agent/simple_agent.py` - Quick responses
- `src/agent/supervisor_agent.py` - Complex tasks

Update `langgraph.json`:
```json
{
  "graphs": {
    "simple": "./src/agent/simple_agent.py:graph",
    "supervisor": "./src/agent/supervisor_agent.py:graph"
  }
}
```

---

## Step 4: Implement Custom Tools (Middleware-First Pattern)

**Critical Pattern:** Tools should be organized in **middleware**, not passed directly to `create_agent()`.

**Reference:** `.clinefiles/langchain/patterns/middleware-tools.md` for complete pattern.

### Step 4.1: Define Tools

Create `src/agent/tools/database_tools.py`:

```python
"""
Database tools for agent.
Reference: .clinefiles/langchain/core/tools.md
"""
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from typing import Annotated


@tool
def query_database(
    query: str,
    state: Annotated[dict, InjectedState],
) -> str:
    """
    Query the application database.
    
    Args:
        query: Natural language description of what to find
        state: Injected agent state (has user context)
    
    Returns:
        Query results as formatted string
    """
    # Access user_id from state for user-specific queries
    user_id = state.get("user_id")
    
    # Implement database query logic
    # Connect to Supabase, run query, return results
    
    return "Query results here"


@tool
def call_external_api(
    endpoint: str,
    params: dict,
) -> str:
    """
    Call external API for additional data.
    
    Args:
        endpoint: API endpoint to call
        params: Request parameters
    
    Returns:
        API response data
    """
    # Implement API call logic
    
    return "API response here"
```

### Step 4.2: Create Tool Prompts (Tool + Prompt Pairing)

**Important:** Every tool should come with system prompt guidance.

Create `src/agent/prompts/tool_prompts.py`:

```python
"""
System prompts paired with tools.
Each tool group gets guidance on when and how to use the tools.
"""

DATABASE_TOOLS_PROMPT = """
## Database Tools

You have access to database query tools for retrieving application data.

Available tools:
- query_database: Query the application database using natural language
- call_external_api: Call external APIs for additional data

When to use:
- Use query_database when you need information stored in the application database
- Use call_external_api when you need data from external services

Best practices:
- Be specific in your queries
- Check for empty results before proceeding
- Handle errors gracefully
"""
```

### Step 4.3: Create Generalizable Tools Middleware

**This is the key pattern:** Middleware that accepts tools and prompt as init parameters.

Create `src/agent/middleware/tools.py`:

```python
"""
Generalizable tools middleware.
Accepts any list of tools and optional prompt guidance.
Reference: .clinefiles/langchain/patterns/middleware-tools.md
"""
from langgraph.prebuilt.chat_agent_executor import AgentMiddleware
from typing import Callable, Optional


class ToolsMiddleware(AgentMiddleware):
    """Generalizable middleware for providing custom tools.
    
    This middleware-centric approach:
    - Accepts any list of tools (developer groups them logically)
    - Accepts optional prompt explaining the tool group's purpose
    - Automatically adds tool descriptions to system prompts
    - Is reusable across different agents and use cases
    """
    
    def __init__(self, tools: list, prompt: Optional[str] = None):
        """Initialize with tools and optional guidance.
        
        Args:
            tools: List of tool functions to provide to the agent
            prompt: Optional prompt explaining tool group purpose and usage
        """
        super().__init__()
        self.tools = tools
        self.group_prompt = prompt
    
    def wrap_model_call(self, request, handler: Callable) -> any:
        """Add tool guidance to system prompt before model call."""
        # Build tool information
        tool_info = "\n\n"
        
        # Add group context if provided
        if self.group_prompt:
            tool_info += f"{self.group_prompt}\n\n"
        
        # Add tool descriptions
        tool_info += "## Available Tools\n"
        for tool in self.tools:
            tool_info += f"- **{tool.name}**: {tool.description}\n"
        
        # Append to system prompt
        request.system_prompt = request.system_prompt + tool_info
        
        return handler(request)
    
    async def awrap_model_call(self, request, handler: Callable) -> any:
        """Add tool guidance to system prompt (async version)."""
        # Build tool information
        tool_info = "\n\n"
        
        # Add group context if provided
        if self.group_prompt:
            tool_info += f"{self.group_prompt}\n\n"
        
        # Add tool descriptions
        tool_info += "## Available Tools\n"
        for tool in self.tools:
            tool_info += f"- **{tool.name}**: {tool.description}\n"
        
        # Append to system prompt
        request.system_prompt = request.system_prompt + tool_info
        
        return await handler(request)
```

**Tool Design Guidelines:**
- One tool per clear function
- Descriptive names and docstrings (agent reads these)
- Use `InjectedState` to access agent state/context
- Return strings (easiest for LLM to process)
- Handle errors gracefully
- **Always pair tools with system prompt guidance**

**Reference:** `.clinefiles/langchain/patterns/middleware-tools.md` for complete patterns

---

## Step 5: Add Middleware (If Using)

**Per `.clinefiles/langchain/patterns/middleware-tools.md`, middleware is the PRIMARY way to add capabilities.**

### Example: Adding TodoListMiddleware (Planning)

```python
from langgraph.prebuilt import TodoListMiddleware

# Create middleware instance
todo_middleware = TodoListMiddleware()

# Wrap model with middleware
model_with_middleware = todo_middleware.wrap_model(model)

# Use wrapped model in agent
graph = create_react_agent(
    model_with_middleware,
    tools=tools,
    state_schema=State,
)
```

### Example: Adding FilesystemMiddleware (File Operations)

```python
from deepagents import FilesystemMiddleware

# Create filesystem middleware
fs_middleware = FilesystemMiddleware(
    base_dir="./workspace",  # Where agent can read/write files
    allowed_extensions=[".txt", ".md", ".json"],
)

# Wrap model
model_with_fs = fs_middleware.wrap_model(model)
```

### Example: Multiple Middleware (Stack)

```python
from langgraph.prebuilt import TodoListMiddleware, SummarizationMiddleware
from deepagents import FilesystemMiddleware, PatchToolCallsMiddleware

# Create middleware instances
todo = TodoListMiddleware()
fs = FilesystemMiddleware(base_dir="./workspace")
summarize = SummarizationMiddleware(trigger_token_count=170_000)
patch = PatchToolCallsMiddleware()  # Error handling

# Wrap model with all middleware (order matters - innermost first)
model_with_middleware = patch.wrap_model(
    summarize.wrap_model(
        fs.wrap_model(
            todo.wrap_model(model)
        )
    )
)
```

**Middleware Order:**
1. Core capabilities (Todo, Filesystem) - innermost
2. Context management (Summarization)
3. Error handling (Patch) - outermost

**Reference:** `.clinefiles/langchain/core/middleware.md` for middleware concepts

---

## Step 6: Implement Agent Nodes (Supervisor Pattern Only)

**Skip this if using simple agent pattern (prebuilt handles it).**

For supervisor agents, define node functions:

```python
def planner_node(state: State):
    """
    Planning node - breaks down task into steps.
    Reference: .clinefiles/langchain/patterns/custom-subagents.md
    """
    messages = state["messages"]
    
    # Use model to generate plan
    response = model.invoke([
        {"role": "system", "content": "You are a planner. Break down the user's request into clear steps."},
        *messages
    ])
    
    return {"messages": [response]}


def executor_node(state: State):
    """
    Execution node - performs work using tools.
    """
    messages = state["messages"]
    
    # Agent decides which tools to call
    response = model_with_tools.invoke(messages)
    
    return {"messages": [response]}


def reviewer_node(state: State):
    """
    Review node - checks if work is complete.
    """
    messages = state["messages"]
    
    response = model.invoke([
        {"role": "system", "content": "Review the work and determine if the task is complete."},
        *messages
    ])
    
    return {"messages": [response]}
```

**Node Design Principles:**
- Each node has single responsibility
- Return updates to state (messages, context, etc.)
- Use clear system prompts
- Keep logic simple - complexity in graph structure

---

## Step 7: Configure Streaming (Default Enabled)

**Streaming is automatic when running `langgraph dev` - no configuration needed.**

Verify streaming is working:

```python
# Streaming is enabled by default via model initialization
model = ChatOpenAI(
    model="gpt-4o-mini",
    streaming=True,  # Default behavior
)
```

**That's it!** LangSmith handles the streaming infrastructure automatically.

**Reference:** `.clinefiles/langchain/core/streaming.md` for streaming patterns

---

## Step 8: Update graph.py with Complete Implementation

**Replace the minimal agent from Phase 8.1 with your complete implementation:**

```python
"""
[Your App Name] Agent
Implements [supervisor/simple/both] architecture per Phase 0 assessment.

References:
- .clinefiles/langchain/core/agents.md
- .clinefiles/langchain/patterns/middleware-tools.md
"""
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI  # or ChatAnthropic
from langgraph.prebuilt import create_react_agent  # or StateGraph

# Import your tools
from .tools import tools


class State(TypedDict):
    """Agent state per Phase 0 requirements"""
    messages: Annotated[list, add_messages]
    # Add your custom state fields


# Initialize model with streaming
model = ChatOpenAI(
    model="gpt-4o-mini",
    streaming=True,
    temperature=0.7,
)

# Add middleware if Phase 0 determined needed
# model = middleware.wrap_model(model)

# Build graph
graph = create_react_agent(
    model,
    tools=tools,
    state_schema=State,
)

# Export for langgraph.json
# graph = builder.compile()  # if custom StateGraph
```

---

## Step 9: Test Agent Locally

### Test 1: Basic Conversation

```bash
curl -X POST http://localhost:2024/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "agent",
    "input": {
      "messages": [{"role": "user", "content": "Hello, test the agent"}]
    },
    "stream_mode": "values"
  }'
```

Should see agent response streaming back.

### Test 2: Tool Calling

Send a message that should trigger tool use:

```bash
curl -X POST http://localhost:2024/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "agent",
    "input": {
      "messages": [{"role": "user", "content": "[Query that requires your custom tool]"}]
    },
    "stream_mode": "values"
  }'
```

Verify tool is called and returns results.

### Test 3: Thread Persistence

Create a thread and send multiple messages:

```bash
# Create thread
curl -X POST http://localhost:2024/threads \
  -H "Content-Type: application/json"
# Note the thread_id from response

# Send message 1
curl -X POST http://localhost:2024/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "[your-thread-id]",
    "assistant_id": "agent",
    "input": {
      "messages": [{"role": "user", "content": "My name is Alice"}]
    }
  }'

# Send message 2 (should remember context)
curl -X POST http://localhost:2024/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "[your-thread-id]",
    "assistant_id": "agent",
    "input": {
      "messages": [{"role": "user", "content": "What is my name?"}]
    }
  }'
```

Agent should remember "Alice" - this verifies automatic memory is working.

---

## Phase 8.2 Completion Checklist

Before proceeding to Phase 8.3, verify:

- [ ] Reviewed Phase 0 agent decisions in PROJECT_REQUIREMENTS.md
- [ ] Agent state schema defined with required fields
- [ ] Agent architecture implemented (supervisor/simple/both)
- [ ] Custom tools created for Phase 0 requirements
- [ ] Tools use clear names and docstrings
- [ ] Middleware stack added (if Phase 0 determined needed)
- [ ] Middleware wrap model in correct order
- [ ] Streaming enabled (verify model has `streaming=True`)
- [ ] Agent nodes implemented (if supervisor pattern)
- [ ] Complete agent in `src/agent/graph.py`
- [ ] `langgraph dev` reloaded with new code (hot reload)
- [ ] Basic conversation test passes
- [ ] Tool calling test works
- [ ] Thread persistence test shows memory working
- [ ] No errors in langgraph dev terminal

---

## Troubleshooting

### Issue: Agent doesn't call tools

**Check:**
- Tool docstrings are clear and descriptive
- Tool names are intuitive
- System prompt doesn't discourage tool use
- Model supports tool calling (gpt-4, claude-3+)

### Issue: Middleware not executing

**Check:**
- Middleware wraps model correctly
- Middleware order (innermost to outermost)
- Import paths correct

### Issue: Streaming not working

**Check:**
- Model initialized with `streaming=True`
- Using stream endpoints in curl tests
- LangSmith dev server running

### Issue: Memory not persisting

**Check:**
- Using `thread_id` in requests
- Thread ID is valid UUID
- LangSmith automatic memory enabled (it is by default)

### Issue: Import errors

**Check:**
- Ran `uv pip install -e .` to install in editable mode
- All dependencies installed via `uv add`
- __init__.py files in place

---

## Important Notes

### Context Engineering (CRITICAL)

**Agent reliability depends 90% on context.**

Per `.clinefiles/langchain/core/context-engineering.md`:
- Clear tool descriptions are essential
- Provide examples in docstrings
- System prompts set expectations
- State includes necessary context

### Production Best Practices

From `.clinefiles/langchain/patterns/middleware-tools.md`:
- ✅ Use middleware-centric pattern
- ✅ Organize tools separately from graph
- ✅ Add error handling middleware
- ✅ Keep nodes focused and simple

### Memory Usage

Remember: Memory is AUTOMATIC via LangSmith
- ✅ Use `thread_id` for persistence
- ✅ Access via `state` in tools
- ❌ Don't manually configure checkpointer

---

## Next Steps

**Proceed to:** [Phase 8.3: LangSmith Features Integration](./phase-8-3-langsmith-features.md)

**With:** Working agent(s) that respond to messages, call tools, and persist conversations across threads.
