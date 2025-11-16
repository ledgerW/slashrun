# Phase 3: Agent Service Integration [IF NEEDED]

**Purpose:** Add or update AI agent capabilities for the new feature

**Prerequisites:**
- Phase 0 complete with approved FEATURE_PLAN.md
- Agent service exists from get-started workflow Phase 8
- FEATURE_PLAN.md Section 5 documents agent changes

**Execute this phase if:** Feature requires new agent tools, prompt updates, or agent behavior changes

**Skip this phase if:** Feature doesn't involve AI capabilities

**References:**
- `.clinefiles/langchain/patterns/middleware-centric.md` - **CRITICAL:** Middleware composition pattern
- `.clinefiles/langchain/patterns/agent-folder-organization.md` - Standard agent code structure
- `.clinefiles/langchain/patterns/middleware-tools.md` - Tools middleware pattern
- `.clinefiles/langchain/core/tools.md` - Custom tool creation
- `.clinefiles/langchain/patterns/custom-subagents.md` - Multi-agent patterns
- `.clinefiles/langchain/reference-implementations/` - Production-ready code examples

---

## Overview

Phase 3 adds AI capabilities:

1. **Tools Created** - New @tool functions
2. **Prompts Updated** - System messages and instructions
3. **Tested in Studio** - LangGraph Studio verification
4. **Frontend Integration** - Next.js client calls
5. **Error Handling** - Graceful failures

---

## Step 1: Review Agent Design from FEATURE_PLAN.md

### Extract Agent Requirements

From FEATURE_PLAN.md Section 5:
- New tools needed
- Tool parameters and return types
- Prompt updates required
- Middleware changes
- Integration with existing tools

---

## Step 2: Create New Tools

### Basic Tool Pattern

```python
# agent-service/tools/feature_tools.py
from langchain_core.tools import tool
from typing import Optional

@tool
def feature_tool_name(
    param1: str,
    param2: Optional[int] = None
) -> dict:
    """
    Tool description for the AI agent.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2 (optional)
    
    Returns:
        Dict with result and metadata
    """
    try:
        # Tool implementation
        result = perform_action(param1, param2)
        
        return {
            "success": True,
            "result": result,
            "metadata": {"param1": param1}
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### Tool with Database Access

```python
from langchain_core.tools import tool
from supabase import create_client
import os

@tool
def query_feature_data(user_id: str, filter_criteria: str) -> dict:
    """Query feature data from database for a specific user."""
    
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Service role for agent
    )
    
    try:
        response = supabase.table("table_name")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()
        
        return {
            "success": True,
            "data": response.data,
            "count": len(response.data)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Tool with Runtime Context

```python
from langchain_core.tools import tool, InjectedToolRuntime

@tool
def context_aware_tool(
    query: str,
    runtime: InjectedToolRuntime
) -> dict:
    """Tool that accesses user context from runtime."""
    
    # Access user context passed from frontend
    user_id = runtime.context.get("user_id")
    session_id = runtime.context.get("session_id")
    
    # Use context in tool logic
    result = process_for_user(query, user_id)
    
    return {
        "result": result,
        "user_id": user_id
    }
```

---

## Step 3: Add Tool to Agent

### Update Agent Configuration (Middleware-Centric Pattern)

Following the middleware-centric pattern, add tools via ToolsMiddleware:

```python
# agent-service/agents/my_agent/middleware/tools_prompt.py
# Update tools prompt to describe new tool usage
MY_AGENT_TOOLS_PROMPT = """
=== Available Tools ===

{tools_list}

**Tool Usage Guidelines:**
- Use existing_tool for X purpose
- Use feature_tool_name for NEW CAPABILITY  # <-- Add guidance
- Use query_feature_data when user needs Y   # <-- Add guidance
"""

# agent-service/agents/my_agent/agent.py
from rapid_ai.agents.middleware.custom import ToolsMiddleware
from tools.feature_tools import feature_tool_name, query_feature_data
from .middleware.tools_prompt import MY_AGENT_TOOLS_PROMPT

# Add new tools to existing tools list
tools = [
    # ... existing tools
    feature_tool_name,
    query_feature_data,
]

# Update ToolsMiddleware with expanded tools
agent = create_agent(
    model=model,
    middleware=[
        core_prompt,  # Agent identity (unchanged)
        ToolsMiddleware(
            tools=tools,  # Expanded tools list
            system_prompt=MY_AGENT_TOOLS_PROMPT  # Updated guidance
        ),
        # ... other middleware
    ],
    # ... other config
)
```

**Key Points:**
- Separate tool guidance from core agent identity
- Use `{tools_list}` placeholder - auto-populated with tool descriptions
- Add guidance on WHEN to use new tools
- Keep core_prompt.py unchanged unless agent identity changes

---

## Step 4: Update Prompts (If Needed)

### Core Identity Updates (Rare)

Only update core_prompt.py if the agent's IDENTITY changes:

```python
# agent-service/agents/my_agent/middleware/core_prompt.py
from langchain.agents.middleware import dynamic_prompt, ModelRequest

@dynamic_prompt
def my_agent_prompt(request: ModelRequest) -> str:
    """Core agent identity - only update if role changes."""
    context = request.runtime.context
    
    return f"""You are an AI assistant specialized in {context.domain}.

Your core responsibilities:
1. {Responsibility 1}
2. {NEW RESPONSIBILITY if role changed}  # <-- Only add if identity changes
3. {Responsibility 3}

You have access to tools to help users accomplish these tasks.
"""
```

### Tool Guidance Updates (Common)

Update tools_prompt.py when adding tools (more common):

```python
# agent-service/agents/my_agent/middleware/tools_prompt.py

MY_AGENT_TOOLS_PROMPT = """
=== Available Tools ===

{tools_list}

**NEW FEATURE CAPABILITIES:**
- Use {tool_name} when users ask about {use case}
- When {scenario}, follow this pattern: {pattern}

**Tool Usage Guidelines:**
1. {Guideline 1}
2. {Guideline 2}
"""
```

**IMPORTANT:**
- Core identity (core_prompt.py) rarely changes
- Tool guidance (tools_prompt.py) changes more frequently
- Keep them separate per middleware-centric pattern

---

## Step 5: Test in LangGraph Studio

### Start Dev Server

```bash
cd agent-service
langgraph dev
```

### Test in Studio

1. Navigate to http://localhost:8123
2. Select main_agent
3. Test new tool:

```json
{
  "messages": [{
    "role": "user",
    "content": "Use the new feature to {test scenario}"
  }]
}
```

4. Verify:
   - Tool is called correctly
   - Parameters passed properly
   - Response formatted correctly
   - Errors handled gracefully

---

## Step 6: Frontend Integration

### Update Agent Client (If Needed)

```typescript
// lib/agent-client.ts

export async function invokeFeatureAgent(
  message: string,
  userId: string
) {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_AGENT_API_URL}/agents/main_agent/invoke`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input: {
          messages: [{ role: 'user', content: message }]
        },
        config: {
          configurable: { thread_id: `user_${userId}_feature` }
        },
        context: {
          user_id: userId,
          feature: 'feature_name'
        }
      })
    }
  )

  if (!response.ok) {
    throw new Error('Agent invocation failed')
  }

  return response.json()
}
```

### Feature Component with Agent

```typescript
// components/feature-agent.tsx
'use client'

import { useState } from 'react'
import { invokeFeatureAgent } from '@/lib/agent-client'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { toast } from 'sonner'

export function FeatureAgent({ userId }: { userId: string }) {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  async function handleSubmit() {
    if (!query.trim()) return

    setIsLoading(true)
    try {
      const result = await invokeFeatureAgent(query, userId)
      setResponse(result.output.messages[result.output.messages.length - 1].content)
    } catch (error) {
      console.error('Agent error:', error)
      toast.error('Failed to process request')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <Textarea
        placeholder="Ask about..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        disabled={isLoading}
      />
      <Button onClick={handleSubmit} disabled={isLoading}>
        {isLoading ? 'Processing...' : 'Submit'}
      </Button>
      {response && (
        <div className="p-4 border rounded-lg">
          {response}
        </div>
      )}
    </div>
  )
}
```

---

## Step 7: Error Handling

### Tool Error Handling

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
    except ConnectionError as e:
        return {"success": False, "error": "Service unavailable"}
    except Exception as e:
        # Log unexpected errors
        logging.error(f"Unexpected error in tool: {str(e)}")
        return {"success": False, "error": "An error occurred"}
```

---

## Common Issues and Solutions

### Issue 1: Tool not appearing in agent

**Cause:** Not added to tools list

**Solution:** Verify tool imported and added to `tools = [...]` array

### Issue 2: Runtime context not available

**Cause:** Context not passed from frontend

**Solution:** Ensure `context` object in agent invocation request

### Issue 3: Database permissions

**Cause:** RLS blocking agent service role

**Solution:** Use service_role_key or add policy for service role

---

## Phase 3 Completion Checklist

- [ ] New tools implemented
- [ ] Tools added to agent configuration
- [ ] Prompts updated (if needed)
- [ ] Tested in LangGraph Studio
- [ ] Frontend integration working
- [ ] Error handling comprehensive
- [ ] Context passing correctly
- [ ] Documentation updated

---

## Next Phase

**Proceed to:** [Phase 4: Integration Testing](./phase-4-integration-testing.md)

**With:**
- Agent tools working in Studio
- Frontend can invoke agent
- Streaming working (if applicable)
- Ready for end-to-end testing
