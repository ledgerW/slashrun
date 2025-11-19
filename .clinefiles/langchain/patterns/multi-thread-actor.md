# Multi-Thread Actor Pattern

**Purpose:** Enable AI actors to maintain separate conversation threads for different contexts - simulation threads tied to scenarios and meta-chat threads for interviewing actors about their decisions.

**Related Patterns:**
- [Middleware-Centric Architecture](./middleware-centric.md)
- [Agent Folder Organization](./agent-folder-organization.md)
- [Drawer Chat Pattern](../../ui/drawer-chat-pattern.md)

---

## Overview

The Multi-Thread Actor Pattern enables AI agents (actors) to maintain multiple, contextually-separate conversation threads:

1. **Simulation Threads**: One thread per actor per scenario for in-character simulation
2. **Meta-Chat Threads**: Separate threads for out-of-character interviews about actor decisions

This pattern is essential for applications where agents need to:
- Participate in multiple concurrent scenarios without context bleed
- Provide explanations of their reasoning in a separate conversation
- Load historical context from one thread type into another

---

## Core Concepts

### Thread Types

```typescript
type ThreadType = 'simulation' | 'meta-chat';

interface ThreadContext {
  actorId: number;
  userId: string;
  scenarioId?: number;  // Required for simulation, optional for meta-chat
  threadType: ThreadType;
}
```

### Thread Naming Conventions

**Simulation Threads** (scenario-bound):
```
actor_{actorId}_scenario_{scenarioId}_sim
Example: actor_42_scenario_123_sim
```

**Meta-Chat Threads** (user-bound):
```
actor_{actorId}_chat_{userId}_{timestamp}
Example: actor_42_chat_user123_1699564800
```

### Single Source of Truth

**LangSmith** is the single source of truth for all thread data:
- Thread messages stored in LangSmith checkpointers
- Thread state managed by LangSmith
- No manual checkpointer instantiation needed

**Supabase** stores only thread references:
```sql
-- scenarios.actor_threads JSONB column
{
  "actor_42_scenario_123_sim": "thread-uuid-from-langsmith",
  "actor_43_scenario_123_sim": "thread-uuid-from-langsmith"
}
```

---

## Implementation Pattern

### 1. Thread Management Utility

Create a centralized thread manager:

```typescript
// lib/agent-threads.ts
import { createClient } from '@/lib/supabase/client';

export class AgentThreadManager {
  private supabase = createClient();

  /**
   * Generate simulation thread key
   */
  getSimulationThreadKey(actorId: number, scenarioId: number): string {
    return `actor_${actorId}_scenario_${scenarioId}_sim`;
  }

  /**
   * Generate meta-chat thread key
   */
  getMetaChatThreadKey(actorId: number, userId: string): string {
    const timestamp = Date.now();
    return `actor_${actorId}_chat_${userId}_${timestamp}`;
  }

  /**
   * Save simulation thread reference to scenario
   */
  async saveSimulationThread(
    scenarioId: number,
    actorId: number,
    threadId: string
  ): Promise<void> {
    const key = this.getSimulationThreadKey(actorId, scenarioId);
    
    const { data: scenario } = await this.supabase
      .from('scenarios')
      .select('actor_threads')
      .eq('id', scenarioId)
      .single();

    const actorThreads = scenario?.actor_threads || {};
    actorThreads[key] = threadId;

    await this.supabase
      .from('scenarios')
      .update({ actor_threads: actorThreads })
      .eq('id', scenarioId);
  }

  /**
   * Retrieve simulation thread ID
   */
  async getSimulationThread(
    scenarioId: number,
    actorId: number
  ): Promise<string | null> {
    const key = this.getSimulationThreadKey(actorId, scenarioId);
    
    const { data } = await this.supabase
      .from('scenarios')
      .select('actor_threads')
      .eq('id', scenarioId)
      .single();

    return data?.actor_threads?.[key] || null;
  }

  /**
   * Load complete thread history from LangSmith
   */
  async loadThreadHistory(threadId: string): Promise<any[]> {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_LANGCHAIN_API_URL}/threads/${threadId}/history`,
      {
        headers: {
          'X-API-Key': process.env.NEXT_PUBLIC_LANGCHAIN_API_KEY!,
        },
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to load thread history');
    }
    
    const data = await response.json();
    return data.values || [];
  }

  /**
   * Get scenarios where actor has simulation threads
   */
  async getActorScenarios(actorId: number): Promise<any[]> {
    const { data: scenarios } = await this.supabase
      .from('scenarios')
      .select('id, name, description, actor_threads')
      .not('actor_threads', 'is', null);

    return (scenarios || []).filter(scenario => {
      const key = this.getSimulationThreadKey(actorId, scenario.id);
      return scenario.actor_threads?.[key];
    });
  }

  /**
   * Create a new thread with prepopulated context messages
   */
  async createThreadWithContext(
    threadId: string,
    contextMessages: any[]
  ): Promise<void> {
    // Create thread with initial context
    await fetch(
      `${process.env.NEXT_PUBLIC_LANGCHAIN_API_URL}/threads/${threadId}/create`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_LANGCHAIN_API_KEY!,
        },
        body: JSON.stringify({
          messages: contextMessages,
        }),
      }
    );
  }
}
```

### 2. React Hook Integration

Create a multi-thread aware hook:

```typescript
// hooks/use-agent.ts
import { useStream } from '@langchain/langgraph-sdk/react';
import { AgentThreadManager } from '@/lib/agent-threads';

interface UseAgentOptions {
  assistantId: string;
  actorId: number;
  userId: string;
  scenarioId?: number;
  threadType: 'simulation' | 'meta-chat';
  explicitThreadId?: string;
  sourceThreadId?: string;  // For loading context
}

export function useAgent(options: UseAgentOptions) {
  const threadManager = new AgentThreadManager();
  const [contextMessages, setContextMessages] = useState<any[]>([]);
  const [contextSource, setContextSource] = useState<string | null>(null);
  const [isLoadingContext, setIsLoadingContext] = useState(false);

  // Auto-generate thread ID based on type
  const threadId = useMemo(() => {
    if (options.explicitThreadId) {
      return options.explicitThreadId;
    }

    if (options.threadType === 'simulation') {
      if (!options.scenarioId) {
        throw new Error('scenarioId required for simulation threads');
      }
      return threadManager.getSimulationThreadKey(
        options.actorId,
        options.scenarioId
      );
    } else {
      return threadManager.getMetaChatThreadKey(
        options.actorId,
        options.userId
      );
    }
  }, [options]);

  // Load context from source thread if specified
  useEffect(() => {
    if (options.sourceThreadId) {
      loadScenarioContext(options.sourceThreadId);
    }
  }, [options.sourceThreadId]);

  const loadScenarioContext = async (sourceThreadId: string) => {
    setIsLoadingContext(true);
    try {
      const history = await threadManager.loadThreadHistory(sourceThreadId);
      setContextMessages(history);
      setContextSource(sourceThreadId);
    } catch (error) {
      console.error('Failed to load context:', error);
    } finally {
      setIsLoadingContext(false);
    }
  };

  // LangGraph SDK stream hook
  const streamResult = useStream({
    url: process.env.NEXT_PUBLIC_LANGCHAIN_API_URL!,
    apiKey: process.env.NEXT_PUBLIC_LANGCHAIN_API_KEY!,
    assistantId: options.assistantId,
    threadId,
  });

  return {
    ...streamResult,
    threadId,
    contextMessages,
    contextSource,
    isLoadingContext,
    loadScenarioContext,
  };
}
```

### 3. Context Loading Component

Enable loading simulation context into meta-chat:

```typescript
// components/scenario-context-loader.tsx
export function ScenarioContextLoader({
  actorId,
  onContextLoaded,
}: {
  actorId: number;
  onContextLoaded: (threadId: string, messageCount: number) => void;
}) {
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadScenarios = async () => {
      const manager = new AgentThreadManager();
      const actorScenarios = await manager.getActorScenarios(actorId);
      setScenarios(actorScenarios);
    };
    loadScenarios();
  }, [actorId]);

  const handleLoadContext = async (scenarioId: number) => {
    setLoading(true);
    const manager = new AgentThreadManager();
    const threadId = await manager.getSimulationThread(scenarioId, actorId);
    
    if (threadId) {
      const history = await manager.loadThreadHistory(threadId);
      onContextLoaded(threadId, history.length);
    }
    setLoading(false);
  };

  return (
    <Select onValueChange={(value) => handleLoadContext(Number(value))}>
      <SelectTrigger>
        <SelectValue placeholder="Load scenario context..." />
      </SelectTrigger>
      <SelectContent>
        {scenarios.map((scenario) => (
          <SelectItem key={scenario.id} value={scenario.id.toString()}>
            {scenario.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
```

---

## State and Context Passing

### Required State Parameters

When calling the agent, always pass:

```typescript
const state = {
  // Core identifiers
  actorId: number,
  userId: string,
  scenarioId?: number,  // Required for simulation
  
  // Actor context (from database)
  actorName: string,
  actorPersona: string,
  actorGoals: string[],
  
  // Scenario context (from database, if simulation)
  scenarioDescription?: string,
  scenarioState?: any,
  scenarioRules?: string[],
  
  // Current message
  message: string,
  
  // Optional: Loaded context from another thread
  contextMessages?: any[],
};

await agent.invoke({
  input: state.message,
  config: {
    configurable: {
      thread_id: threadId,
      actorId: state.actorId,
      scenarioId: state.scenarioId,
      // ... other state fields
    }
  }
});
```

### Agent Access to State

Agents access this state through runtime:

```python
# langchain_/src/agents/nation_agent/middleware/context.py
from langchain.agents import runtime

class ContextMiddleware:
    @before_agent
    async def load_context(self, state: dict):
        # Access state via runtime
        actor_id = runtime.get("actorId")
        scenario_id = runtime.get("scenarioId")
        
        # Access short-term memory (current thread)
        thread_state = runtime.thread_state.get("key")
        
        # Access long-term memory (persistent store)
        memories = await runtime.store.search(
            namespace=("actors", str(actor_id)),
            query="relevant context"
        )
        
        return state
```

---

## Database Schema

### Scenario Thread References

```sql
-- Migration: supabase_/supabase/migrations/YYYYMMDDHHMMSS_add_actor_threads.sql
ALTER TABLE scenarios 
ADD COLUMN actor_threads JSONB DEFAULT '{}'::jsonb;

CREATE INDEX idx_scenarios_actor_threads 
ON scenarios USING gin (actor_threads);

COMMENT ON COLUMN scenarios.actor_threads IS 
'Maps actor simulation thread keys to LangSmith thread UUIDs. 
Example: {"actor_42_scenario_123_sim": "thread-uuid"}';
```

### Thread Reference Query Patterns

```sql
-- Find all scenarios where an actor has threads
SELECT s.* 
FROM scenarios s
WHERE s.actor_threads ? 'actor_42_scenario_%';

-- Get specific actor thread from scenario
SELECT s.actor_threads->>'actor_42_scenario_123_sim' as thread_id
FROM scenarios s
WHERE s.id = 123;
```

---

## UI Integration: Drawer Pattern

Use the [Drawer Chat Pattern](../../ui/drawer-chat-pattern.md) for all chat interfaces:

```typescript
// components/actor-chat-drawer.tsx
export function ActorChatDrawer({ actors, scenarioId }: Props) {
  const [selectedActorId, setSelectedActorId] = useState<number | null>(null);
  const [sourceThreadId, setSourceThreadId] = useState<string | null>(null);

  const handleContextLoaded = (threadId: string) => {
    setSourceThreadId(threadId);
  };

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button>Chat with Actors</Button>
      </SheetTrigger>
      <SheetContent side="right" className="w-[500px]">
        {/* Actor Selection */}
        <Select onValueChange={(v) => setSelectedActorId(Number(v))}>
          <SelectTrigger>
            <SelectValue placeholder="Select an actor" />
          </SelectTrigger>
          <SelectContent>
            {actors.map((actor) => (
              <SelectItem key={actor.id} value={actor.id.toString()}>
                {actor.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {selectedActorId && (
          <>
            {/* Optional: Load scenario context */}
            <ScenarioContextLoader
              actorId={selectedActorId}
              onContextLoaded={handleContextLoaded}
            />

            {/* Chat Interface */}
            <ActorChatInterface
              actorId={selectedActorId}
              scenarioId={scenarioId}
              threadType={scenarioId ? 'simulation' : 'meta-chat'}
              sourceThreadId={sourceThreadId}
            />
          </>
        )}
      </SheetContent>
    </Sheet>
  );
}
```

---

## Common Patterns

### Pattern 1: In-Scenario Simulation

Actor participates in scenario with persistent thread:

```typescript
// On scenario page
<ActorChatDrawer
  actors={scenario.actors}
  scenarioId={scenario.id}  // Enables simulation mode
/>
```

Agent receives:
- `threadType: 'simulation'`
- `scenarioId: 123`
- Thread key: `actor_42_scenario_123_sim`
- Full scenario context in state

### Pattern 2: Meta-Chat Without Context

Interview actor outside of any scenario:

```typescript
// On actor detail page
<ActorChatDrawer
  actors={[actor]}
  scenarioId={null}  // Meta-chat mode
/>
```

Agent receives:
- `threadType: 'meta-chat'`
- `scenarioId: undefined`
- Thread key: `actor_42_chat_user123_1699564800`
- Only actor context in state

### Pattern 3: Meta-Chat With Scenario Context

Interview actor about specific scenario decisions:

```typescript
// User selects scenario context
const handleContextLoaded = (threadId: string) => {
  setSourceThreadId(threadId);
};

// useAgent hook automatically loads history
const { contextMessages } = useAgent({
  actorId,
  threadType: 'meta-chat',
  sourceThreadId,  // Loads simulation history
});
```

Agent receives:
- `threadType: 'meta-chat'` (new conversation)
- `contextMessages: [...]` (from simulation)
- Can reference simulation without affecting it

---

## Agent Implementation

### Thread-Aware Prompts

```python
# core_prompt.py
CORE_IDENTITY = """
You are {actor_name}, participating in: {context_type}

{context_description}

{loaded_context_note}
"""

def build_system_prompt(state: dict) -> str:
    is_simulation = "scenarioId" in state
    context_type = "simulation" if is_simulation else "meta-conversation"
    
    context_desc = ""
    if is_simulation:
        context_desc = f"Scenario: {state['scenarioDescription']}"
    else:
        context_desc = "You are being interviewed about your decisions."
    
    loaded_note = ""
    if state.get("contextMessages"):
        loaded_note = (
            "The user has loaded context from a previous simulation. "
            "You can reference those events when answering."
        )
    
    return CORE_IDENTITY.format(
        actor_name=state['actorName'],
        context_type=context_type,
        context_description=context_desc,
        loaded_context_note=loaded_note
    )
```

### Context-Aware Tools

```python
@tool
async def recall_decision(query: str) -> str:
    """Search your memory for past decisions and reasoning."""
    actor_id = runtime.get("actorId")
    
    # Search long-term memory
    memories = await runtime.store.search(
        namespace=("actors", str(actor_id)),
        query=query
    )
    
    # Also check loaded context if present
    context_messages = runtime.get("contextMessages", [])
    if context_messages:
        # Search through loaded simulation history
        relevant = [m for m in context_messages if query.lower() in m['content'].lower()]
        return format_memories(memories, relevant)
    
    return format_memories(memories)
```

---

## Testing Checklist

- [ ] Simulation threads persist across page reloads
- [ ] Meta-chat threads generate unique IDs per session
- [ ] Thread references save to Supabase correctly
- [ ] Context loading displays message count
- [ ] Loaded context doesn't pollute current thread
- [ ] Actor selection resets context when changed
- [ ] Empty state shows when no actor selected
- [ ] Thread IDs follow naming conventions
- [ ] State parameters pass through hook correctly
- [ ] Agent can access both thread and loaded context

---

## Common Pitfalls

### ❌ Don't: Manually instantiate checkpointers

```python
# WRONG - LangSmith handles this
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver(...)
```

### ✅ Do: Use thread_id only

```python
# CORRECT - Let LangSmith handle checkpointing
graph.compile(checkpointer=True)
result = await agent.invoke(input, config={"thread_id": thread_id})
```

### ❌ Don't: Store thread messages in Supabase

```sql
-- WRONG - Messages belong in LangSmith
CREATE TABLE thread_messages (
  thread_id uuid,
  content text,
  ...
);
```

### ✅ Do: Store only thread references

```sql
-- CORRECT - Reference to LangSmith thread
ALTER TABLE scenarios 
ADD COLUMN actor_threads JSONB;
-- Stores: {"actor_42_scenario_123_sim": "langsmith-uuid"}
```

### ❌ Don't: Mix simulation and meta-chat in same thread

```typescript
// WRONG - Context bleed
const threadId = `actor_${actorId}`;  // Same thread for everything
```

### ✅ Do: Use separate threads per context

```typescript
// CORRECT - Separate threads
const simThreadId = `actor_${actorId}_scenario_${scenarioId}_sim`;
const chatThreadId = `actor_${actorId}_chat_${userId}_${timestamp}`;
```

---

## Related Documentation

- [Short-Term Memory](../core/short-term-memory.md) - Thread-level state management
- [Long-Term Memory](../core/long-term-memory.md) - Cross-thread persistent storage
- [Middleware-Centric](./middleware-centric.md) - Agent architecture pattern
- [Drawer Chat Pattern](../../ui/drawer-chat-pattern.md) - UI implementation
- [Local Development](../langsmith/local-development.md) - Testing with langgraph dev

---

## Summary

The Multi-Thread Actor Pattern enables:
1. **Context Separation**: Actors maintain distinct threads per scenario
2. **Meta-Analysis**: Interview actors about decisions without polluting simulation
3. **Context Loading**: Reference simulation history in meta-conversations
4. **Single Source of Truth**: LangSmith handles all thread storage automatically
5. **Clean Architecture**: Thread references in Supabase, messages in LangSmith

**Key Principle**: Never manually manage checkpointers or stores. Use thread_id conventions and let LangSmith handle the infrastructure.
