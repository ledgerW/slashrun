# Phase 8.4: Next.js Integration

**Time Estimate:** 25-35 minutes

**Purpose:** Connect Next.js frontend to agent service using LangGraph SDK

**Prerequisites:**
- Phase 8.3 completed with agent service features working
- Next.js app from Phase 2 running
- PROJECT_REQUIREMENTS.md documenting thread management strategy

**Key References:**
- `.clinefiles/langchain/langsmith/next-js-integration/core.md` - useStream() fundamentals
- `.clinefiles/langchain/langsmith/next-js-integration/streaming.md` - Streaming patterns
- `.clinefiles/langchain/langsmith/next-js-integration/threads.md` - Thread management

---

## Step 1: Configure Environment

Add agent API URL to Next.js environment:

```bash
# In your-nextjs-app/.env.local
NEXT_PUBLIC_AGENT_API_URL=http://localhost:2024
```

**Why NEXT_PUBLIC_?** Client-side React components need access to this URL.

---

## Step 2: Install LangGraph SDK

```bash
# From Next.js app directory
cd your-nextjs-app
npm install @langchain/langgraph-sdk @langchain/core
```

---

## Step 3: Create Agent Client Hook

Create reusable hook following Phase 8.3 thread strategy:

```typescript
// lib/use-agent.ts
"use client";

import { useStream } from "@langchain/langgraph-sdk/react";
import type { Message } from "@langchain/langgraph-sdk";

interface AgentState {
  messages: Message[];
  // Add custom state fields from Phase 8.2
}

export function useAgent(threadId?: string | null) {
  return useStream<AgentState>({
    apiUrl: process.env.NEXT_PUBLIC_AGENT_API_URL!,
    assistantId: "agent",
    threadId: threadId ?? undefined,
    messagesKey: "messages",
    reconnectOnMount: true, // Resume after page refresh
  });
}
```

**Reference:** `.clinefiles/langchain/langsmith/next-js-integration/core.md`

---

## Step 4: Create Chat Component

```typescript
// components/agent-chat.tsx
"use client";

import { useState } from "react";
import { useAgent } from "@/lib/use-agent";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function AgentChat({ 
  threadId, 
  onThreadIdChange 
}: { 
  threadId?: string | null;
  onThreadIdChange?: (id: string) => void;
}) {
  const [input, setInput] = useState("");
  const agent = useAgent(threadId);

  // Notify parent when thread created
  if (!threadId && agent.threadId && onThreadIdChange) {
    onThreadIdChange(agent.threadId);
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    agent.submit({
      messages: [{ role: "user", content: input }]
    });
    setInput("");
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {agent.messages.map((msg) => (
          <div key={msg.id} className={msg.type === "human" ? "text-right" : "text-left"}>
            <div className="inline-block p-3 rounded-lg bg-muted">
              {msg.content as string}
            </div>
          </div>
        ))}
        {agent.isLoading && <div>Agent is thinking...</div>}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask the agent..."
            disabled={agent.isLoading}
          />
          <Button type="submit" disabled={agent.isLoading}>
            Send
          </Button>
        </div>
      </form>
    </div>
  );
}
```

---

## Step 5: Implement Thread Management

Based on Phase 8.3 strategy, implement thread persistence:

### Option A: URL-based threads (Recommended)

```typescript
// app/chat/page.tsx
"use client";

import { AgentChat } from "@/components/agent-chat";
import { useSearchParams, useRouter } from "next/navigation";

export default function ChatPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const threadId = searchParams.get("thread");

  const handleThreadChange = (newThreadId: string) => {
    router.push(`/chat?thread=${newThreadId}`);
  };

  return (
    <div className="h-screen">
      <AgentChat 
        threadId={threadId}
        onThreadIdChange={handleThreadChange}
      />
    </div>
  );
}
```

### Option B: Session storage

```typescript
// Alternative: Use session storage for threads
const [threadId, setThreadId] = useState(() => 
  sessionStorage.getItem("agent-thread") || null
);

const handleThreadChange = (id: string) => {
  sessionStorage.setItem("agent-thread", id);
  setThreadId(id);
};
```

**Reference:** `.clinefiles/langchain/langsmith/next-js-integration/threads.md`

---

## Step 6: Add Human-in-the-Loop UI (If Implemented)

If Phase 8.3 implemented human-in-the-loop:

```typescript
// Update AgentChat component
if (agent.interrupt) {
  return (
    <div className="p-4 border rounded-lg">
      <p>Agent requires approval:</p>
      <pre>{JSON.stringify(agent.interrupt.value, null, 2)}</pre>
      <div className="flex gap-2 mt-4">
        <Button onClick={() => agent.submit(undefined, { command: { resume: true } })}>
          Approve
        </Button>
        <Button variant="outline" onClick={() => agent.submit(undefined, { command: { resume: false } })}>
          Reject
        </Button>
      </div>
    </div>
  );
}
```

**Reference:** `.clinefiles/langchain/langsmith/next-js-integration/human-in-the-loop.md`

---

## Step 7: Add Background Runs (If Needed)

If Phase 0 determined background runs needed:

```typescript
// lib/use-background-agent.ts
import { Client } from "@langchain/langgraph-sdk";

export async function startBackgroundRun(input: any) {
  const client = new Client({ 
    apiUrl: process.env.NEXT_PUBLIC_AGENT_API_URL! 
  });
  
  // Create run without waiting
  const run = await client.runs.create(
    null, // threadless or provide thread_id
    "agent",
    { input, multitaskStrategy: "enqueue" }
  );
  
  return run.run_id;
}

// Poll for status
export async function checkRunStatus(runId: string) {
  const client = new Client({ 
    apiUrl: process.env.NEXT_PUBLIC_AGENT_API_URL! 
  });
  
  return await client.runs.get(null, runId);
}
```

**Reference:** `.clinefiles/langchain/langsmith/next-js-integration/background-runs.md`

---

## Step 7.5: Validate Against Interface Specifications (REQUIRED)

**⚠️ CRITICAL: Verify Implementation Matches Interface Contract**

Before testing, you MUST validate that your implementation matches the interface specifications defined in Phase 8.2.

**Reference:** `project/service-interfaces/README.md` - Validation checklist

### Step 7.5.1: Validate TypeScript Types

Compare your TypeScript types against the schemas documented in interface docs:

**Check Agent README:**
- Open: `langchain_/src/agents/my_agent/README.md#interface-specifications`
- Note the Python schemas (State and Context)

**Check Interface Doc:**
- Open: `project/service-interfaces/nextjs-langchain-interface.md#my-agent`
- Verify TypeScript types match Python schemas exactly

**Example Validation:**

```typescript
// Python Schema (from agent README)
class MyAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    current_action: str | None
    data_field: dict[str, Any]

// TypeScript Type (in your code) - MUST MATCH
interface MyAgentState {
  messages: Message[];
  current_action: string | null;  // ✅ Matches Python str | None
  data_field: Record<string, any>; // ✅ Matches Python dict[str, Any]
}
```

**Common Mismatches to Fix:**
- `str` → `string`
- `int` → `number`
- `dict` → `Record<string, any>` or object type
- `list` → `Array<T>` or `T[]`
- `None` → `null`
- `Optional[T]` → `T | null`

### Step 7.5.2: Validate Invocation Pattern

Verify you're using the correct invocation pattern documented in interface specs:

```typescript
// From interface doc - MUST use this exact pattern
thread.submit(
  // Input State (matches AgentState schema)
  {
    messages: [{ role: "user", content: input }],
    current_action: null,
    data_field: {}
  },
  // Options with context (NOT in state, NOT in config.configurable)
  {
    context: {
      user_id: userId,
      field1: value1
    }
  }
);
```

**Validation Checklist:**
- [ ] Context passed via `options` parameter (second argument)
- [ ] Context NOT in state object (first argument)
- [ ] Context NOT in `config.configurable`
- [ ] State fields match AgentState schema exactly
- [ ] Using `useStream()` hook (not Client directly)

### Step 7.5.3: Update Service Interface Documents

Mark implementation as complete:

#### Update nextjs-langchain-interface.md

Change status from 🔵 PLANNED to 🟢 IMPLEMENTED:

```markdown
## My Agent

### Status
🟢 IMPLEMENTED
```

Verify all sections are accurate:
- [ ] TypeScript types match Python schemas
- [ ] Usage example matches your implementation
- [ ] References point to correct files

#### Update langchain-supabase-interface.md

If agent uses database tools, mark those as implemented:

```markdown
## My Agent Tools

### Status
🟢 IMPLEMENTED
```

### Step 7.5.4: Cross-Reference Validation

Ensure bidirectional references work:

**From Next.js code → Interface Doc:**
```typescript
// In your component, add reference comment
/**
 * Agent integration following interface specification:
 * @see project/service-interfaces/nextjs-langchain-interface.md#my-agent
 */
const thread = useStream<MyAgentState>({...});
```

**From Interface Doc → Agent README:**
- Verify link works: Click the README link in interface doc
- Should jump to Interface Specifications section

**From Interface Doc → Supabase Doc:**
- Verify tool operations documented match actual tool code

### Step 7.5.5: Validation Checklist

Before proceeding to testing, verify:

**Type Validation:**
- [ ] TypeScript State interface matches Python TypedDict exactly
- [ ] TypeScript Context interface matches Python dataclass exactly
- [ ] All field types converted correctly (str→string, dict→Record, etc.)
- [ ] Optional fields use `| null` or `?` correctly
- [ ] No extra or missing fields

**Pattern Validation:**
- [ ] Using `useStream()` hook
- [ ] Context passed via options (second parameter)
- [ ] State passed as first parameter
- [ ] Thread management follows documented pattern
- [ ] Error handling follows best practices

**Documentation Validation:**
- [ ] nextjs-langchain-interface.md updated with 🟢 IMPLEMENTED
- [ ] langchain-supabase-interface.md updated if applicable
- [ ] All cross-references work (clickable links)
- [ ] Usage examples match actual implementation
- [ ] Integration points documented

**Code Quality:**
- [ ] Added reference comments linking to interface doc
- [ ] Component properly typed with TypeScript
- [ ] No `any` types where specific types available
- [ ] Followed documented error handling patterns

### Why This Matters

Per `project/service-interfaces/README.md`:

> **If you implement without validating against interface specs:**
> 1. ❌ Runtime errors due to type mismatches
> 2. ❌ Integration failures between services
> 3. ❌ Debugging nightmare (no clear contract)
> 4. ❌ Breaking changes go unnoticed

**This validation step prevents all of these issues.**

### Example: Complete Validation Flow

```typescript
// 1. Check agent README for schemas
// langchain_/src/agents/my_agent/README.md#interface-specifications

// 2. Import and define matching TypeScript types
import type { Message } from "@langchain/langgraph-sdk";

// Matches Python TypedDict exactly
interface MyAgentState {
  messages: Message[];
  current_action: string | null;
  field1: string;
}

// Matches Python dataclass exactly
interface MyAgentContext {
  user_id: string;
  context_field: number;
}

// 3. Use in component with correct pattern
export function MyAgentChat({ userId, contextValue }: Props) {
  const thread = useStream<MyAgentState>({
    apiUrl: process.env.NEXT_PUBLIC_AGENT_API_URL!,
    assistantId: "my-agent",
    threadId: threadId,
    messagesKey: "messages",
  });

  const handleSubmit = (input: string) => {
    // Correct pattern: state + context
    thread.submit(
      {
        messages: [{ role: "user", content: input }],
        current_action: null,
        field1: "value"
      },
      {
        context: {
          user_id: userId,
          context_field: contextValue
        }
      }
    );
  };

  // 4. Verify in interface doc
  // project/service-interfaces/nextjs-langchain-interface.md#my-agent
  // Types should match exactly ✅
}
```

---

## Step 8: Test Integration

### Test 1: Basic Chat

1. Start agent service: `langgraph dev` (in agent-service/)
2. Start Next.js: `npm run dev` (in Next.js app/)
3. Navigate to chat page
4. Send message, verify response streams

### Test 2: Thread Persistence

1. Send several messages
2. Note thread ID in URL
3. Refresh page
4. Verify conversation history loads

### Test 3: New Conversation

1. Clear thread ID from URL (or start new session)
2. Send message
3. Verify new thread created
4. Check URL updates with new thread ID

---

## Phase 8.4 Completion Checklist

Before proceeding to Phase 8.5:

- [ ] `NEXT_PUBLIC_AGENT_API_URL` added to `.env.local`
- [ ] `@langchain/langgraph-sdk` installed
- [ ] `useAgent` hook created
- [ ] Chat UI component implemented
- [ ] Thread management strategy from Phase 8.3 implemented
- [ ] Thread persistence working (URL or session storage)
- [ ] Human-in-the-loop UI added (if Phase 8.3 implemented it)
- [ ] Background runs implemented (if Phase 0 determined needed)
- [ ] Basic chat test passes
- [ ] Thread persistence test passes
- [ ] New conversation test passes
- [ ] Streaming responses display token-by-token
- [ ] No CORS errors in browser console

---

## Troubleshooting

### Issue: CORS errors

**Solution:** LangGraph dev server should handle CORS automatically. If issues persist:
- Verify agent service running on port 2024
- Check `NEXT_PUBLIC_AGENT_API_URL` is correct
- Try restarting both servers

### Issue: useStream() not updating

**Check:**
- Component is client component ("use client")
- apiUrl environment variable set correctly
- Agent service responding (test with curl)

### Issue: Thread not persisting

**Check:**
- Thread ID in URL/storage
- `reconnectOnMount: true` in useStream config
- Thread ID valid UUID format

### Issue: Messages not streaming

**Check:**
- Model has `streaming=True` in agent service
- Using correct stream mode
- Browser DevTools network tab shows SSE connection

---

## Important Notes

### Streaming is Default

Per Phase 8.2, streaming is enabled by default:
- Responses appear token-by-token automatically
- No additional configuration needed
- `useStream()` hook handles all streaming logic

### Memory Automatic

Thread persistence handled by LangSmith:
- Just use `thread_id` parameter
- History loads automatically
- No manual checkpointer configuration

### Error Handling

Add error boundaries and toast notifications:
- Catch network errors
- Display user-friendly messages
- Retry failed requests

---

## Next Steps

**Proceed to:** [Phase 8.5: Testing & Documentation](./phase-8-5-testing-docs.md)

**With:** Working Next.js integration where users can chat with agent, threads persist, and all features from Phase 8.3 are accessible via UI.
