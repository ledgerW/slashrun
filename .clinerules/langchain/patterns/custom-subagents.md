# Custom Subagent Pattern (PRODUCTION RECOMMENDED)

**Using create_agent + custom handoff middleware for supervisor visibility into subagent tools**

**This is THE recommended pattern for production supervisor agents** - prefer this over DeepAgents' SubAgentMiddleware.

---

## When to Use This Pattern

Use this pattern instead of `create_deep_agent` or `SubAgentMiddleware` when you need:
- **Explicit control** over supervisor system prompts
- **Tool visibility** - list subagent tools in supervisor's prompt for better decision-making
- **Avoid heavy defaults** of SubAgentMiddleware
- **Customize handoff tool** names and descriptions
- **Full transparency** about subagent capabilities to the supervisor

---

## The Problem with SubAgentMiddleware

The built-in `SubAgentMiddleware` and `create_deep_agent` come with opinionated defaults:

```python
# What you DON'T want: Opaque subagent capabilities
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="openai:gpt-5",
    subagents=[
        {
            "name": "research-agent",
            "description": "Conducts research",
            "system_prompt": "You are a researcher",
            "tools": [web_search, analyze_data]
        }
    ]
)
# Problem: Supervisor doesn't know research-agent has web_search and analyze_data tools
# Problem: Heavy middleware stack with defaults you may not want
```

**Issues:**
- Supervisor can't see what tools subagents have
- Opinionated middleware stack (summarization, caching, etc.)
- Less control over handoff tool description
- Generic system prompts without tool listings

---

## Custom Subagent Solution

Create a custom handoff middleware that:
1. Accepts a list of `create_agent` instances
2. Creates handoff tools that list each subagent's tools
3. Provides clear names and descriptions
4. Allows explicit system prompt control

### Complete Pattern

```python
from langchain.agents import create_agent, AgentMiddleware
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

class CustomSubagentMiddleware(AgentMiddleware):
    """Custom subagent middleware with explicit tool listings and system prompt injection."""
    
    def __init__(self, subagents: list[dict]):
        """Initialize with list of subagent configurations.
        
        Args:
            subagents: List of dicts with keys:
                - agent: CompiledStateGraph (from create_agent)
                - description: str (what the subagent does)
        
        The middleware extracts tool names and agent name from the agent itself.
        """
        super().__init__()
        self.handoff_tools = []
        self.subagent_info = []  # Store info for system prompt
        
        for subagent_config in subagents:
            agent = subagent_config["agent"]
            description = subagent_config["description"]
            
            # Extract agent name and tools from the agent itself
            # Agent name from graph configuration
            name = getattr(agent, 'name', 'subagent')
            
            # Tool names from agent's tool configuration
            tool_names = [tool.name for tool in getattr(agent, 'tools', [])]
            
            # Store info for system prompt
            self.subagent_info.append({
                "name": name,
                "description": description,
                "tools": tool_names
            })
            
            # Create handoff tool with tool listing
            handoff_tool = self._create_handoff_tool(
                agent=agent,
                name=name,
                description=description,
                tool_names=tool_names
            )
            self.handoff_tools.append(handoff_tool)
        
        self.tools = self.handoff_tools
    
    def _create_handoff_tool(
        self,
        agent: CompiledStateGraph,
        name: str,
        description: str,
        tool_names: list[str]
    ):
        """Create a handoff tool for a subagent."""
        
        # Include tool listing in description
        tool_list = ", ".join(tool_names)
        full_description = f"{description}\n\nAvailable tools: {tool_list}"
        
        @tool(name, description=full_description)
        def handoff_to_subagent(task: str) -> str:
            """Delegate task to specialized subagent."""
            result = agent.invoke({
                "messages": [HumanMessage(content=task)]
            })
            return result["messages"][-1].content
        
        return handoff_to_subagent
    
    def _generate_subagent_prompt(self) -> str:
        """Generate system prompt section describing available subagents."""
        if not self.subagent_info:
            return ""
        
        prompt_lines = ["\n## Available Subagents\n"]
        prompt_lines.append("You can delegate work to the following specialized agents:\n")
        
        for i, info in enumerate(self.subagent_info, 1):
            tool_list = ", ".join(info["tools"]) if info["tools"] else "No specific tools"
            prompt_lines.append(f"{i}. **{info['name']}** (delegate_to_{info['name']})")
            prompt_lines.append(f"   - Description: {info['description']}")
            prompt_lines.append(f"   - Available tools: {tool_list}")
            prompt_lines.append("")
        
        prompt_lines.append("Use these subagents when their specialized capabilities match the task requirements.\n")
        return "\n".join(prompt_lines)
    
    def wrap_model_call(self, request, handler):
        """Inject subagent information into system prompt."""
        subagent_prompt = self._generate_subagent_prompt()
        request.system_prompt = (
            request.system_prompt + subagent_prompt
            if request.system_prompt
            else subagent_prompt
        )
        return handler(request)
    
    async def awrap_model_call(self, request, handler):
        """Inject subagent information into system prompt (async version)."""
        subagent_prompt = self._generate_subagent_prompt()
        request.system_prompt = (
            request.system_prompt + subagent_prompt
            if request.system_prompt
            else subagent_prompt
        )
        return await handler(request)

# Usage Example
from langchain.tools import tool

# Define tools
@tool
def web_search(query: str) -> str:
    """Search the web for information."""
    return f"Search results for: {query}"

@tool
def analyze_data(data: str) -> str:
    """Analyze structured data."""
    return f"Analysis of: {data}"

@tool
def query_database(sql: str) -> str:
    """Query the database."""
    return f"Query results for: {sql}"

# Create specialized subagents (use fast Haiku for subagents)
research_agent = create_agent(
    model="anthropic:claude-4-5-haiku-20251029",
    tools=[web_search, analyze_data],
    system_prompt="""You are a research specialist.

Available tools:
- web_search: Search the internet for information
- analyze_data: Analyze data and extract insights

Use these tools to conduct thorough research."""
)

data_agent = create_agent(
    model="anthropic:claude-4-5-haiku-20251029",
    tools=[query_database, analyze_data],
    system_prompt="""You are a data specialist.

Available tools:
- query_database: Execute SQL queries
- analyze_data: Analyze and interpret data

Use these tools to work with databases and data."""
)

# Create supervisor with custom subagent middleware (use Sonnet for supervisor)
supervisor = create_agent(
    model="anthropic:claude-sonnet-4-5-20250929",
    tools=[],  # No direct tools, only handoffs
    middleware=[
        CustomSubagentMiddleware(
            subagents=[
                {
                    "agent": research_agent,
                    "description": "Delegate research tasks requiring web search or data analysis"
                },
                {
                    "agent": data_agent,
                    "description": "Delegate data tasks requiring database queries or analysis"
                }
            ]
        )
    ],
    system_prompt="""You are a supervisor agent coordinating specialized subagents.

Your subagents:

1. Research Agent (delegate_to_research_agent)
   - Handles: Web research, information gathering, data analysis
   - Tools: web_search, analyze_data
   - Use when: Need to find information online or analyze research data

2. Data Agent (delegate_to_data_agent)
   - Handles: Database operations, SQL queries, data analysis
   - Tools: query_database, analyze_data
   - Use when: Need to query databases or work with structured data

Delegation strategy:
- Choose the right subagent based on task requirements
- Provide clear, specific instructions to subagents
- Synthesize results from multiple subagents if needed"""
)

# Use supervisor
result = supervisor.invoke({
    "messages": [{"role": "user", "content": "Research the latest AI trends and analyze the data"}]
})
```

---

## Key Advantages

### 1. Explicit Tool Listings

```python
# Good: Supervisor knows what each subagent can do
system_prompt="""Your subagents:

1. Research Agent
   - Tools: web_search, analyze_data
   - Use when: Need internet research or analysis

2. Data Agent
   - Tools: query_database, analyze_data
   - Use when: Need database access"""
```

**Benefit**: Supervisor makes better delegation decisions because it knows subagent capabilities.

### 2. Custom Handoff Tool Descriptions

```python
# Include tool listing in description
full_description = f"{description}\n\nAvailable tools: {tool_list}"

@tool(name=name, description=full_description)
def handoff_to_subagent(task: str) -> str:
    """Delegate task to specialized subagent."""
    # ...
```

**Benefit**: LLM sees tool capabilities when deciding whether to call handoff.

### 3. Lightweight Middleware Stack

```python
# You control the middleware
supervisor = create_agent(
    model="anthropic:claude-sonnet-4-5-20250929",
    middleware=[
        CustomSubagentMiddleware(subagents=[...]),
        # Add only the middleware YOU want
        SummarizationMiddleware(),
        LoggingMiddleware()
    ]
)

# create_deep_agent includes heavy defaults
# TodoListMiddleware, FilesystemMiddleware, SubAgentMiddleware,
# SummarizationMiddleware, AnthropicPromptCachingMiddleware, etc.
```

---

## Advanced Patterns

### Multiple Subagent Tiers

```python
# Tier 1: Specialized agents
research_agent = create_agent(...)
data_agent = create_agent(...)

# Tier 2: Domain coordinators
tech_coordinator = create_agent(
    model="anthropic:claude-sonnet-4-5-20250929",
    middleware=[
        CustomSubagentMiddleware(
            subagents=[
                {"agent": research_agent, "description": "Research specialist"},
                {"agent": data_agent, "description": "Data specialist"}
            ]
        )
    ],
    system_prompt="Coordinate tech research and data tasks"
)

# Tier 3: Top-level supervisor
supervisor = create_agent(
    model="openai:gpt-5",
    middleware=[
        CustomSubagentMiddleware(
            subagents=[
                {"agent": tech_coordinator, "name": "tech_team", ...}
            ]
        )
    ],
    system_prompt="Coordinate all teams"
)
```

### Conditional Subagent Access

```python
class ConditionalSubagentMiddleware(AgentMiddleware):
    """Only expose subagents based on runtime context."""
    
    def __init__(self, subagents: list[dict]):
        super().__init__()
        self.subagent_configs = subagents
        self.tools = []  # Populated dynamically
    
    def wrap_model_call(self, request, handler):
        """Add subagents based on user permissions."""
        permissions = request.runtime.context.permissions
        
        # Build tools list based on permissions
        available_tools = []
        for config in self.subagent_configs:
            if config.get("required_permission") in permissions:
                tool = self._create_handoff_tool(...)
                available_tools.append(tool)
        
        # Update request with filtered tools
        request.tools = request.tools + available_tools
        return handler(request)
```

### Shared State Across Subagents

```python
from langchain.agents import AgentState

class SharedState(AgentState):
    research_findings: list[str]
    database_results: list[dict]

# All agents use same state schema (use Haiku for subagents, Sonnet for supervisor)
research_agent = create_agent(
    model="anthropic:claude-4-5-haiku-20251029",
    tools=[web_search],
    state_schema=SharedState
)

data_agent = create_agent(
    model="anthropic:claude-4-5-haiku-20251029",
    tools=[query_database],
    state_schema=SharedState
)

supervisor = create_agent(
    model="anthropic:claude-sonnet-4-5-20250929",
    middleware=[CustomSubagentMiddleware(...)],
    state_schema=SharedState
)

# State persists across subagent invocations
```

---

## Implementation Variations

### Variation 1: Direct Agent Return

```python
def _create_handoff_tool(self, agent, name, description, tool_names):
    """Return full agent response instead of just content."""
    
    @tool(name=name, description=description)
    def handoff(task: str) -> dict:
        """Delegate to subagent and return full response."""
        result = agent.invoke({"messages": [HumanMessage(content=task)]})
        return {
            "content": result["messages"][-1].content,
            "tool_calls": len([m for m in result["messages"] if hasattr(m, "tool_calls")]),
            "message_count": len(result["messages"])
        }
    
    return handoff
```

### Variation 2: Streaming Support

```python
def _create_handoff_tool(self, agent, name, description, tool_names):
    """Support streaming from subagent."""
    
    @tool(name=name, description=description)
    def handoff(task: str, runtime: ToolRuntime) -> str:
        """Delegate with progress updates."""
        writer = runtime.stream_writer
        
        writer(f"Delegating to {name}...")
        
        result = agent.invoke({"messages": [HumanMessage(content=task)]})
        
        writer(f"{name} completed task")
        
        return result["messages"][-1].content
    
    return handoff
```

### Variation 3: Context Passing

```python
def _create_handoff_tool(self, agent, name, description, tool_names):
    """Pass supervisor context to subagent."""
    
    @tool(name=name, description=description)
    def handoff(task: str, runtime: ToolRuntime) -> str:
        """Delegate with context propagation."""
        # Pass supervisor's context to subagent
        result = agent.invoke(
            {"messages": [HumanMessage(content=task)]},
            context=runtime.context  # Propagate user_id, session_id, etc.
        )
        return result["messages"][-1].content
    
    return handoff
```

---

## Comparison: Custom vs SubAgentMiddleware

| Feature | Custom Pattern | SubAgentMiddleware |
|---------|---------------|-------------------|
| **Tool Visibility** | Explicit in prompts | Opaque to supervisor |
| **System Prompt Control** | Full control | Limited customization |
| **Middleware Stack** | Choose what you need | Heavy defaults |
| **Handoff Tool Names** | Custom names | Generic "task" tool |
| **Setup Complexity** | More code | Quick setup |
| **Flexibility** | High | Lower |
| **Best For** | Production, custom needs | Prototyping, simple cases |

---

## LangGraph Dev Server Integration

**Recommended Approach**: Use LangGraph dev server (local) and LangSmith platform (production) instead of FastAPI.

```python
# agents/main_agent.py
from langgraph.prebuilt import create_agent
from middleware.subagents import CustomSubagentMiddleware

# Initialize subagents
research_agent = create_agent(
    model="anthropic:claude-4-5-haiku-20251029",  # Fast subagent
    tools=[web_search],
    system_prompt="Research specialist"
)

data_agent = create_agent(
    model="anthropic:claude-4-5-haiku-20251029",
    tools=[query_database],
    system_prompt="Data specialist"
)

# Create supervisor with CustomSubagentMiddleware
supervisor = create_agent(
    model="anthropic:claude-sonnet-4-5-20250929",  # Latest Claude 4.5 Sonnet
    middleware=[
        CustomSubagentMiddleware(
            subagents=[
                {
                    "agent": research_agent,
                    "name": "research_agent",
                    "description": "Research specialist",
                    "tools": ["web_search"]
                },
                {
                    "agent": data_agent,
                    "name": "data_agent",
                    "description": "Data specialist",
                    "tools": ["query_database"]
                }
            ]
        )
    ],
    system_prompt="You coordinate specialized agents..."
)

# Export for LangGraph server
graph = supervisor
```

**langgraph.json**:
```json
{
  "dependencies": ["."],
  "graphs": {
    "main_agent": "./agents/main_agent.py:graph"
  },
  "env": ".env"
}
```

**Start server**:
```bash
langgraph dev
```

**Endpoints auto-generated**:
- `POST /agents/main_agent/invoke` - Single invocation
- `POST /agents/main_agent/stream` - Streaming
- `GET /agents/main_agent/state/{thread_id}` - Get state

**Next.js Integration**:
```typescript
// lib/agent-client.ts
export async function invokeAgent(
  messages: AgentMessage[],
  threadId: string,
  context: AgentContext
) {
  const response = await fetch('http://localhost:8123/agents/main_agent/invoke', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      input: { messages },
      config: { configurable: { thread_id: threadId } },
      context
    })
  });
  
  const data = await response.json();
  return data.output.messages;
}
```

See `.clinerules/workflows/phases/phase-8-agentic-ai-service.md` for complete setup.

---

## Best Practices

### 1. List Tools in System Prompts

```python
# Good: Explicit tool listing
system_prompt="""You coordinate these agents:

Research Agent (delegate_to_research_agent):
- Tools: web_search, analyze_data
- Use for: Internet research, data analysis

Data Agent (delegate_to_data_agent):
- Tools: query_database, analyze_data
- Use for: Database queries, data processing"""

# Bad: Vague descriptions
system_prompt="You have research and data agents"
```

### 2. Use Descriptive Handoff Names

```python
# Good: Clear, specific
"delegate_to_research_agent"
"handoff_to_data_specialist"

# Bad: Generic
"task"
"subagent"
```

### 3. Keep Subagent Scope Focused

```python
# Good: Specialized subagents
research_agent = create_agent(
    tools=[web_search],
    system_prompt="You are a web research specialist"
)

# Bad: Do-everything subagent
mega_agent = create_agent(
    tools=[web_search, db_query, email, file_ops, calculations],
    system_prompt="You do everything"
)
```

### 4. Document Handoff Strategy

```python
system_prompt="""Delegation strategy:

1. Identify task requirements
2. Match requirements to subagent capabilities
3. Choose most specialized subagent
4. Provide clear, specific instructions
5. Synthesize results if using multiple subagents

Example:
Task: "Research AI trends and store in database"
-> First: delegate_to_research_agent (web_search)
-> Then: delegate_to_data_agent (query_database)
-> Finally: Synthesize and present results"""
```

### 5. Test Individually Then Together

```python
# Test subagents independently first
research_result = research_agent.invoke({"messages": [...]})
data_result = data_agent.invoke({"messages": [...]})

# Then test supervisor coordination
supervisor_result = supervisor.invoke({"messages": [...]})
```

---

## Common Patterns

### Research + Analysis Workflow

```python
# Research agent: Gather information (use Haiku for focused subagent tasks)
research_agent = create_agent(
    model="anthropic:claude-4-5-haiku-20251029",
    tools=[web_search, fetch_documents],
    system_prompt="Gather comprehensive research data"
)

# Analysis agent: Process findings
analysis_agent = create_agent(
    model="anthropic:claude-4-5-haiku-20251029",
    tools=[analyze_data, create_report],
    system_prompt="Analyze research data and create reports"
)

# Supervisor: Orchestrate workflow (use Sonnet for coordination)
supervisor = create_agent(
    model="anthropic:claude-sonnet-4-5-20250929",
    middleware=[CustomSubagentMiddleware(...)],
    system_prompt="""Workflow:
    1. Use research_agent to gather information
    2. Use analysis_agent to process findings
    3. Synthesize final report"""
)
```

### Domain-Specific Teams

```python
# Marketing team
marketing_agent = create_agent(tools=[social_media, analytics])

# Sales team  
sales_agent = create_agent(tools=[crm, email])

# Support team
support_agent = create_agent(tools=[ticketing, knowledge_base])

# Department head
supervisor = create_agent(
    middleware=[CustomSubagentMiddleware(
        subagents=[
            {"agent": marketing_agent, ...},
            {"agent": sales_agent, ...},
            {"agent": support_agent, ...}
        ]
    )]
)
```

---

## Next Steps

- **Middleware Pattern**: See [middleware-centric.md](./middleware-centric.md) for bundling capabilities
- **Long-term Memory**: Enable cross-agent persistence with [long-term-memory.md](../core/long-term-memory.md)
- **Streaming**: Stream updates from subagents with [streaming.md](../core/streaming.md)
- **Agents**: Core agent patterns in [agents.md](../core/agents.md)

---

## References

- [LangChain create_agent](https://docs.langchain.com/oss/python/langchain/agents)
- [DeepAgents Harness](https://docs.langchain.com/oss/python/deepagents/harness)
- `.clinerules/langchain/patterns/middleware-centric.md` - Middleware pattern
- `.clinerules/langchain/core/middleware.md` - Middleware fundamentals
