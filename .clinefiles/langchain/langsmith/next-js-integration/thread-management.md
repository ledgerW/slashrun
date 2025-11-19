# Thread Management for Next.js Integration

**CRITICAL GUIDE** - Thread ID requirements and patterns for Next.js ↔ LangChain integration

## Overview

When integrating Next.js with LangGraph agents deployed on LangSmith, proper thread management is essential. This guide covers the critical requirements and patterns for handling thread IDs, creation, and persistence.

## ⚠️ Critical Requirements

### 1. Thread IDs MUST Be UUIDs

**LangChain/LangSmith requires thread IDs to be valid UUIDs.**

```typescript
// ❌ DON'T: Use semantic keys as thread IDs
const threadId = `actor_${actorId}_scenario_${scenarioId}_sim`;
// Results in: HTTP 422 "Invalid thread ID: must be a UUID"

// ✅ DO: Use actual UUIDs
import { v4 as uuidv4 } from 'uuid';
const threadId = uuidv4(); // "123e4567-e89b-12d3-a456-426614174000"
```

### 2. Threads MUST Be Created Before Use

**You cannot use a thread ID that doesn't exist in LangSmith.**

```typescript
// ❌ DON'T: Just generate UUID and use it
const threadId = uuidv4();
await client.runs.stream(threadId, ...);
// Results in: HTTP 404 "Thread not found"

// ✅ DO: Create thread in LangSmith first
const thread = await client.threads.create({
  metadata: { actor_id, scenario_id }
});
const threadId = thread.thread_id; // Now safe to use
```

## AgentThreadManager Pattern

For applications with semantic organization (e.g., simulation scenarios), use this pattern to maintain both semantic keys (for your database) and UUIDs (for LangSmith).

### Implementation

```typescript
// lib/agent-threads.ts
import { Client as LangGraphClient } from '@langchain/langgraph-sdk';
import { v4 as uuidv4 } from 'uuid';
import { createClient as createSupabaseClient } from '@/lib/supabase/client';

export class AgentThreadManager {
  private static getLangGraphClient(): LangGraphClient {
    return new LangGraphClient({ 
      apiUrl: process.env.NEXT_PUBLIC_AGENT_API_URL 
    });
  }

  /**
   * Get or create UUID thread ID for simulation
   * 
   * Pattern:
   * 1. Generate semantic key for database storage
   * 2. Check if UUID already exists for this key
   * 3. If not, create thread in LangSmith and store UUID
   * 4. Return UUID for use with LangGraph SDK
   */
  static async getOrCreateSimulationThreadId(
    scenarioId: number,
    actorId: number
  ): Promise<string> {
    const supabase = createSupabaseClient();
    
    // Semantic key for our database
    const threadKey = `actor_${actorId}_scenario_${scenarioId}_sim`;

    // Check if thread already exists
    const { data: scenario } = await supabase
      .from('scenarios')
      .select('actor_threads')
      .eq('id', scenarioId)
      .single();

    const actorThreads = scenario?.actor_threads || {};
    
    // Return existing UUID if found
    if (actorThreads[threadKey]) {
      return actorThreads[threadKey];
    }

    // Create new thread in LangSmith
    const client = this.getLangGraphClient();
    const thread = await client.threads.create({
      metadata: {
        actor_id: actorId,
        scenario_id: scenarioId,
        thread_type: 'simulation',
        thread_key: threadKey, // Store semantic key in metadata
      }
    });

    const threadId = thread.thread_id; // UUID from LangSmith
    actorThreads[threadKey] = threadId;

    // Store mapping in database
    await supabase
      .from('scenarios')
      .update({ actor_threads: actorThreads })
      .eq('id', scenarioId);

    return threadId;
  }

  /**
   * Get or create UUID thread ID for meta chat
   * 
   * For ephemeral conversations, always create fresh thread
   */
  static async getOrCreateMetaChatThreadId(
    actorId: number,
    userId: string
  ): Promise<string> {
    const client = this.getLangGraphClient();
    
    // Create new thread in LangSmith
    const thread = await client.threads.create({
      metadata: {
        actor_id: actorId,
        user_id: userId,
        thread_type: 'meta-chat',
        created_at: new Date().toISOString(),
      }
    });

    return thread.thread_id;
  }
}
```

### Integration with useAgent Hook

```typescript
// hooks/use-agent.ts
import { useStream } from "@langchain/langgraph-sdk/react";
import { useState, useEffect } from "react";
import { AgentThreadManager } from "@/lib/agent-threads";

export function useAgent(options: {
  actorId: number;
  userId: string;
  scenarioId?: number;
  threadType: 'simulation' | 'meta-chat';
}) {
  const [threadId, setThreadId] = useState<string | undefined>();

  // Get or create UUID thread ID asynchronously
  useEffect(() => {
    let cancelled = false;

    async function getThreadId() {
      try {
        let id: string;
        
        if (options.threadType === 'simulation' && options.scenarioId) {
          id = await AgentThreadManager.getOrCreateSimulationThreadId(
            options.scenarioId,
            options.actorId
          );
        } else {
          id = await AgentThreadManager.getOrCreateMetaChatThreadId(
            options.actorId,
            options.userId
          );
        }

        if (!cancelled) {
          setThreadId(id);
        }
      } catch (error) {
        console.error('Failed to get thread ID:', error);
      }
    }

    getThreadId();

    return () => {
      cancelled = true;
    };
  }, [options.actorId, options.scenarioId, options.threadType, options.userId]);

  const stream = useStream({
    apiUrl: process.env.NEXT_PUBLIC_AGENT_API_URL!,
    assistantId: "agent",
    threadId: threadId, // UUID from LangSmith
    messagesKey: "messages",
    reconnectOnMount: true,
  });

  return stream;
}
```

## Database Schema

Store thread mappings in your database:

```sql
-- Add actor_threads column to scenarios table
ALTER TABLE scenarios 
ADD COLUMN actor_threads JSONB DEFAULT '{}';

-- Example data structure:
{
  "actor_42_scenario_123_sim": "123e4567-e89b-12d3-a456-426614174000",
  "actor_43_scenario_123_sim": "987fcdeb-51a2-43d7-b890-123456789abc"
}
```

## Flow Diagram

```
User Opens Chat
      ↓
useAgent Hook Initializes
      ↓
getOrCreateSimulationThreadId(scenarioId, actorId)
      ↓
Check Database for Semantic Key
      ↓
   Exists? ──Yes─→ Return Stored UUID
      ↓ No
Create Thread in LangSmith
      ↓
LangSmith Returns UUID
      ↓
Store UUID with Semantic Key
      ↓
Return UUID to useAgent
      ↓
useStream Connects to LangSmith
      ↓
Chat Works ✓
```

## Common Errors and Solutions

### HTTP 422: Invalid thread ID: must be a UUID

**Cause:** Passing semantic key instead of UUID to LangGraph SDK

**Solution:** Use AgentThreadManager to get UUID

```typescript
// ❌ Wrong
const threadId = `actor_${actorId}_scenario_${scenarioId}`;
stream.submit({ messages }, { threadId });

// ✅ Correct
const threadId = await AgentThreadManager.getOrCreateSimulationThreadId(
  scenarioId, actorId
);
stream.submit({ messages }, { threadId });
```

### HTTP 404: Thread not found

**Cause:** UUID generated but thread not created in LangSmith

**Solution:** Create thread before use

```typescript
// ❌ Wrong
const threadId = uuidv4();
await client.runs.stream(threadId, ...);

// ✅ Correct
const thread = await client.threads.create({ metadata: {...} });
await client.runs.stream(thread.thread_id, ...);
```

### 'dict' object has no attribute 'thread_id'

**Cause:** Using semantic key instead of UUID in database lookups

**Solution:** Always store UUIDs, use semantic keys only as database keys

```typescript
// ✅ Correct storage pattern
const mapping = {
  [semanticKey]: uuid  // Key is semantic, value is UUID
};
```

## Best Practices

### 1. Separate Concerns

- **Semantic Keys**: Internal organization (database keys, human-readable)
- **UUIDs**: External integration (LangSmith threads)

### 2. Always Create Before Use

```typescript
// Pattern for new conversations
const thread = await client.threads.create({
  metadata: { /* app-specific data */ }
});
const threadId = thread.thread_id; // Use this UUID
```

### 3. Cache Thread Mappings

```typescript
// Check cache first
const cachedThreadId = await getFromCache(semanticKey);
if (cachedThreadId) return cachedThreadId;

// Create if needed
const thread = await client.threads.create({...});
await saveToCache(semanticKey, thread.thread_id);
return thread.thread_id;
```

### 4. Include Metadata

```typescript
// Store semantic information in thread metadata
await client.threads.create({
  metadata: {
    actor_id: 42,
    scenario_id: 123,
    thread_key: "actor_42_scenario_123_sim", // For reference
    created_by: userId,
    app_version: "1.0.0"
  }
});
```

## Testing

```typescript
describe('AgentThreadManager', () => {
  test('generates valid UUIDs', async () => {
    const threadId = await AgentThreadManager.getOrCreateSimulationThreadId(
      123, 42
    );
    
    // Should be valid UUID
    expect(threadId).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
    );
  });

  test('reuses existing threads', async () => {
    const id1 = await AgentThreadManager.getOrCreateSimulationThreadId(
      123, 42
    );
    const id2 = await AgentThreadManager.getOrCreateSimulationThreadId(
      123, 42
    );
    
    // Should return same UUID
    expect(id1).toBe(id2);
  });

  test('creates threads in LangSmith', async () => {
    const threadId = await AgentThreadManager.getOrCreateSimulationThreadId(
      123, 42
    );
    
    // Should exist in LangSmith
    const client = new LangGraphClient({ apiUrl: '...' });
    const thread = await client.threads.get(threadId);
    expect(thread).toBeDefined();
  });
});
```

## Related Documentation

- [Core Integration Guide](./ core.md) - Basic useStream setup
- [Threads API](./threads.md) - LangGraph SDK thread operations
- [Multi-Thread Actor Pattern](../../patterns/multi-thread-actor.md) - Advanced patterns

## Summary

**Critical Points:**
1. ✅ Thread IDs **MUST** be UUIDs
2. ✅ Threads **MUST** be created before use
3. ✅ Use AgentThreadManager pattern for semantic organization
4. ✅ Store UUID ↔ semantic key mappings in database
5. ✅ Always create threads via LangGraph SDK

Following these patterns ensures error-free integration between Next.js and LangChain agents.
