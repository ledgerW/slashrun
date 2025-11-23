# Phase 3: Agent Service Integration [IF NEEDED]

**Purpose:** Add or update AI agent capabilities for the new feature

**Prerequisites:**
- Phase 0 complete with approved FEATURE_PLAN.md
- Agent service exists from get-started workflow Phase 8
- FEATURE_PLAN.md Section 5 documents agent changes

**Execute this phase if:** Feature requires new agent tools, prompt updates, or agent behavior changes

**Skip this phase if:** Feature doesn't involve AI capabilities

**Critical References:**
- `.clinefiles/langchain/patterns/middleware-centric.md` - **REQUIRED READING** - Middleware composition pattern
- `.clinefiles/langchain/patterns/middleware-tools.md` - Tools organization pattern
- `.clinefiles/langchain/core/tools.md` - Tool creation fundamentals
- `.clinefiles/tavily/capabilities-and-integration.md` - Web search integration (if needed)
- `.clinefiles/langchain/reference-implementations/` - Production code examples

---

## Overview

Phase 3 follows this workflow:

1. **Review Requirements** → Extract from FEATURE_PLAN.md
2. **Create Tools** → Implement new @tool functions
3. **Update Agent** → Add via ToolsMiddleware (middleware-centric pattern)
4. **Update Prompts** → Separate identity (core_prompt.py) from tool guidance (tools_prompt.py)
5. **Add Web Search** → Tavily integration if needed
6. **Test in Studio** → Verify with LangGraph Studio
7. **Integrate Frontend** → Connect Next.js components
8. **Handle Errors** → Comprehensive error handling

---

## Step 1: Review Agent Design from FEATURE_PLAN.md

Extract from **FEATURE_PLAN.md Section 5: Agent Service Changes:**

**Identify:**
- [ ] New tools required (name, purpose, parameters)
- [ ] Tool guidance needed (when to use each tool)
- [ ] Core identity changes (rare - only if agent role changes)
- [ ] Web search needs (Tavily integration)
- [ ] Middleware additions (new capabilities)
- [ ] Context/state requirements (what data tools need)

---

## Step 2: Create New Tools

**Read:** `.clinefiles/langchain/core/tools.md` for complete tool creation patterns

**Tool Organization:**
```
agent-service/
├── tools/
│   ├── feature_tools.py    # New feature-specific tools
│   └── __init__.py
```

**Key Patterns to Follow:**

1. **Basic tool with @tool decorator**
2. **Tool with database access** (Supabase client pattern)
3. **Tool with runtime context** (InjectedToolRuntime)
4. **Tool returning Command** (for state updates)

**Example Tool Structure:**
```python
from langchain_core.tools import tool

@tool
def feature_tool_name(param1: str) -> dict:
    """Clear description for AI agent."""
    try:
        result = perform_action(param1)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

**See:** `.clinefiles/langchain/reference-implementations/tools-middleware-example.py` for production examples

---

## Step 3: Add Tools to Agent (Middleware-Centric Pattern)

**Read:** `.clinefiles/langchain/patterns/middleware-centric.md` - **CRITICAL GUIDE**

### Pattern Overview

**DO NOT** use old pattern:
```python
# ❌ OLD WAY - Don't do this
agent = create_agent(model=model, tools=[tool1, tool2])
```

**DO** use middleware-centric pattern:
```python
# ✅ NEW WAY - Middleware composition
from rapid_ai.agents.middleware.custom import ToolsMiddleware

agent = create_agent(
    model=model,
    middleware=[
        core_prompt,              # Identity (unchanged)
        ToolsMiddleware(          # Tools with guidance
            tools=[new_tool, existing_tool],
            system_prompt=AGENT_TOOLS_PROMPT
        ),
        # ... other middleware
    ]
)
```

### Update Tools Guidance (tools_prompt.py)

**File:** `agent-service/agents/my_agent/middleware/tools_prompt.py`

```python
AGENT_TOOLS_PROMPT = """
=== Available Tools ===

{tools_list}

**Tool Usage Guidelines:**
- Use new_tool when [describe scenario]
- Use existing_tool when [describe scenario]

**Guidelines:**
[Add feature-specific guidance]
"""
```

**Key Points:**
- Use `{tools_list}` placeholder - **auto-populated** with tool descriptions
- Add guidance on **WHEN** to use new tools
- Keep this separate from core_prompt.py

### Update Agent Configuration (agent.py)

**File:** `agent-service/agents/my_agent/agent.py`

```python
from tools.feature_tools import new_tool
from .middleware.tools_prompt import AGENT_TOOLS_PROMPT

# Expand tools list
tools = [
    # ... existing tools
    new_tool,  # Add new tool
]

# Update ToolsMiddleware
middleware = [
    core_prompt,  # Keep identity unchanged
    ToolsMiddleware(
        tools=tools,
        system_prompt=AGENT_TOOLS_PROMPT
    ),
    # ... rest of middleware stack
]
```

**See:** `.clinefiles/langchain/patterns/middleware-tools.md` for complete organization pattern

---

## Step 4: Update Prompts (Only If Needed)

**Read:** `.clinefiles/langchain/patterns/middleware-centric.md` - Sections on prompt separation

### Core Identity (Rare)

**Update `core_prompt.py` ONLY if agent's core identity/role changes**

Example: If agent becomes a "research assistant" instead of "general assistant"

**Otherwise:** Leave core_prompt.py unchanged

### Tool Guidance (Common)

**Update `tools_prompt.py` when adding tools** (this is normal)

Add guidance on:
- When to use new tool
- Expected parameters
- Use case examples

**Key Principle:** Separate identity from tool guidance

---

## Step 5: Add Web Search Integration (If Feature Needs It)

**Read:** `.clinefiles/tavily/capabilities-and-integration.md` for complete integration guide

### When to Add Tavily

If FEATURE_PLAN.md identified need for:
- Real-time web search
- Content extraction from URLs
- News monitoring
- Research capabilities

### Integration Pattern

**1. Install Package:**
```bash
cd agent-service
uv add langchain-tavily
```

**IMPORTANT:** Use `langchain-tavily`, NOT `langchain_community`

**2. Add Tavily Tools:**
```python
from langchain_tavily import TavilySearchResults, TavilyExtract

# Add to tools list
tools = [
    # ... existing tools
    TavilySearchResults(max_results=5),
    TavilyExtract(),
]
```

**3. Update Tool Guidance:**
```python
AGENT_TOOLS_PROMPT = """
=== Available Tools ===

{tools_list}

**Web Search Guidelines:**
- Use tavily_search_results_json when user asks about current events
- Use tavily_extract when given URLs to analyze
- Search query should be specific and focused
"""
```

**See:** `.clinefiles/tavily/capabilities-and-integration.md` for:
- LangChain integration details
- Search vs extract vs crawl vs map
- Best practices and credit optimization
- MCP server options

---

## Step 6: Test in LangGraph Studio

**Read:** `.clinefiles/langchain/langsmith/local-development.md` for local testing patterns

### Start Development Server

```bash
cd agent-service
langgraph dev
```

Server starts on: `http://localhost:2024`  
Studio opens at: `http://localhost:2024`

### Test New Tools

1. **Navigate to Studio** (opens automatically)
2. **Select your agent** from list
3. **Run test queries:**
   ```json
   {
     "messages": [{
       "role": "user",
       "content": "Test the new feature capability"
     }]
   }
   ```
4. **Verify:**
   - Tool appears in available tools list
   - Tool is called with correct parameters
   - Tool returns expected results
   - Errors handled gracefully

### Check Tool Execution

- View tool calls in Studio execution graph
- Inspect tool input/output
- Verify context passed correctly
- Test error scenarios

---

## Step 7: Frontend Integration

**Read:** `.clinefiles/langchain/langsmith/next-js-integration/core.md` for integration patterns

### Integration Options

Depending on feature needs:

**Simple Invocation:**
- Read: `.clinefiles/langchain/langsmith/next-js-integration/core.md`
- Use: `useStream()` hook for streaming responses
- Pattern: Button click → agent invocation → display result

**Thread-Based Chat:**
- Read: `.clinefiles/langchain/langsmith/next-js-integration/threads.md`
- Use: Thread management for conversation history
- Pattern: Chat interface with persistent threads

**Drawer Chat UI (Recommended):**
- Read: `.clinefiles/ui/drawer-chat-pattern.md`
- Use: Collapsible drawer for agent interaction
- Best for: Feature-specific agent access

### Basic Integration Pattern

**Client Component:**
```typescript
// components/feature-agent.tsx
'use client'

import { useStream } from '@/lib/agent-hooks'
import { Button } from '@/components/ui/button'

export function FeatureAgent({ userId }: { userId: string }) {
  const { stream, isLoading } = useStream({
    agentId: 'main_agent',
    threadId: `user_${userId}_feature`
  })

  async function handleSubmit(query: string) {
    await stream({ messages: [{ role: 'user', content: query }] })
  }

  // ... UI implementation
}
```

**See complete patterns in referenced guides above**

---

## Step 8: Error Handling

**Key Principle:** Tools should **never break agent execution**

### Tool-Level Error Handling

```python
@tool
def safe_feature_tool(param: str) -> dict:
    """Tool with comprehensive error handling."""
    try:
        # Validate inputs
        if not param:
            return {"success": False, "error": "Parameter required"}
        
        # Perform operation
        result = risky_operation(param)
        return {"success": True, "result": result}
        
    except ValueError as e:
        return {"success": False, "error": f"Invalid input: {str(e)}"}
    except Exception as e:
        logging.error(f"Tool error: {str(e)}")
        return {"success": False, "error": "An error occurred"}
```

**Pattern:** Always return dict with success/error fields

### Frontend Error Handling

```typescript
try {
  const result = await invokeAgent(query)
  // Handle success
} catch (error) {
  console.error('Agent error:', error)
  toast.error('Failed to process request')
}
```

---

## Common Issues and Solutions

### Issue 1: Tool not appearing in agent

**Symptom:** Tool not listed in Studio

**Solutions:**
- Verify tool imported in agent.py
- Verify tool added to tools list
- Check ToolsMiddleware initialized correctly
- Restart langgraph dev server

### Issue 2: {tools_list} not populated

**Symptom:** Literal `{tools_list}` text appears in prompt

**Solution:** Ensure using ToolsMiddleware - it handles placeholder replacement

### Issue 3: Runtime context not available in tools

**Symptom:** `context` is None or missing attributes

**Solutions:**
- Pass context from frontend in invocation request
- Use InjectedToolRuntime parameter in tool
- Check context_schema defined in agent

### Issue 4: Database permissions

**Symptom:** RLS blocks agent queries

**Solutions:**
- Use service_role_key (not anon_key) in tools
- Add RLS policy for service role if needed
- Verify environment variables set correctly

### Issue 5: Tavily tools not working

**Symptom:** Search/extract tools fail

**Solutions:**
- Verify `langchain-tavily` installed (NOT langchain_community)
- Check TAVILY_API_KEY environment variable
- Verify API key has credits available
- Review `.clinefiles/tavily/capabilities-and-integration.md`

---

## Phase 3 Completion Checklist

### Tool Implementation
- [ ] New tools created following `.clinefiles/langchain/core/tools.md` patterns
- [ ] Tools organized in `tools/feature_tools.py`
- [ ] Tools handle errors gracefully (never break execution)
- [ ] Tools return structured data (success/error pattern)

### Agent Integration (Middleware-Centric)
- [ ] Tools added via ToolsMiddleware (not direct tools array)
- [ ] Tool guidance added to tools_prompt.py
- [ ] {tools_list} placeholder used correctly
- [ ] Core identity unchanged (unless role changed)
- [ ] Followed `.clinefiles/langchain/patterns/middleware-centric.md`

### Web Search (If Applicable)
- [ ] Tavily integration added if needed
- [ ] Used `langchain-tavily` package (not langchain_community)
- [ ] Search/extract tools configured correctly
- [ ] Tool guidance explains when to use web search

### Testing
- [ ] Tested in LangGraph Studio (`langgraph dev`)
- [ ] Tools appear in available tools list
- [ ] Tools execute successfully with test inputs
- [ ] Error handling verified (invalid inputs, failures)
- [ ] Context passing works correctly

### Frontend Integration
- [ ] Agent client can invoke agent with new tools
- [ ] Frontend receives responses correctly
- [ ] Streaming works (if applicable)
- [ ] Error handling implemented

### Documentation
- [ ] FEATURE_PLAN.md updated with implementation details
- [ ] Tool usage documented
- [ ] Integration points documented

---

## Next Phase

**Proceed to:** [Phase 4: Integration Testing](./phase-4-integration-testing.md)

**With:**
- [ ] Agent tools working in LangGraph Studio
- [ ] Frontend successfully invokes agent
- [ ] All tools tested individually
- [ ] Ready for end-to-end integration testing

---

## Additional Resources

**Must Read Before Implementation:**
- `.clinefiles/langchain/patterns/middleware-centric.md` - Core pattern
- `.clinefiles/langchain/patterns/middleware-tools.md` - Tool organization
- `.clinefiles/langchain/core/tools.md` - Tool creation

**Read If Applicable:**
- `.clinefiles/tavily/capabilities-and-integration.md` - Web search integration
- `.clinefiles/ui/drawer-chat-pattern.md` - Agent chat UI
- `.clinefiles/langchain/patterns/multi-thread-actor.md` - Multi-context agents

**Reference Examples:**
- `.clinefiles/langchain/reference-implementations/tools-middleware-example.py`
- `.clinefiles/langchain/reference-implementations/guardrails-middleware-example.py`
