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
- `.clinefiles/ui/drawer-chat-pattern.md` - **Recommended default UI pattern**
- `.clinefiles/langchain/patterns/multi-thread-actor.md` - Multi-thread management (if using actors)

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

## Step 3: Choose UI Pattern

**Default Recommendation: Drawer Pattern**

For most applications, use the **collapsible side drawer pattern** (shadcn Sheet):
- Non-intrusive, doesn't take over the page
- Allows contextual chat alongside main content
- Professional, modern UX
- Supports entity selection (e.g., multiple actors)

**Alternative: Full-Page Chat**

Use full-page only if:
- Chat is the primary/sole interface
- No other content needs to be visible
- Simple single-agent conversation

**Reference:** `.clinefiles/ui/drawer-chat-pattern.md`

---

## Step 4: Create Agent Client Hook

Create reusable hook following Phase 8.3 thread strategy:

```typescript
// hooks/use-agent.ts
"use client";

import { useStream } from "@langchain/langgraph-sdk/react";
import type { Message } from "@langchain/langgraph-sdk";

interface AgentState {
  messages: Message[];
  // Add custom state fields from Phase 8.2
}

interface UseAgentOptions {
  assistantId: string;
  threadId?: string | null;
  // Add context fields from Phase 8.2
  userId?: string;
  // Additional context as needed
}

export function useAgent(options: UseAgentOptions) {
  const { assistantId, threadId, userId, ...context } = options;

  const stream = useStream<AgentState>({
    apiUrl: process.env.NEXT_PUBLIC_AGENT_API_URL!,
    assistantId,
    threadId: threadId ?? undefined,
    messagesKey: "messages",
    reconnectOnMount: true,
  });

  // Helper to submit with context
  const submitWithContext = (input: string, additionalContext?: any) => {
    stream.submit(
      {
        messages: [{ role: "user", content: input }],
      },
      {
        context: {
          userId,
          ...context,
          ...additionalContext,
        },
      }
    );
  };

  return {
    ...stream,
    submitWithContext,
  };
}
```

**Reference:** `.clinefiles/langchain/langsmith/next-js-integration/core.md`

---

## Step 5: Implement Chat UI (Drawer Pattern - Recommended)

### Step 5.1: Install shadcn Sheet Component

```bash
npx shadcn@latest add sheet
```

### Step 5.2: Create Chat Interface Component

```typescript
// components/agent-chat-interface.tsx
"use client";

import { useState, useRef, useEffect } from "react";
import { useAgent } from "@/hooks/use-agent";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";

interface AgentChatInterfaceProps {
  assistantId: string;
  threadId?: string | null;
  userId: string;
  // Add context fields from Phase 8.2
}

export function AgentChatInterface({
  assistantId,
  threadId,
  userId,
}: AgentChatInterfaceProps) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const agent = useAgent({
    assistantId,
    threadId,
    userId,
  });

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [agent.messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    agent.submitWithContext(input);
    setInput("");
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {agent.messages.map((msg) => (
            <div
              key={msg.id}
              className={msg.type === "human" ? "text-right" : "text-left"}
            >
              <div className="inline-block p-3 rounded-lg bg-muted max-w-[80%]">
                {msg.content as string}
              </div>
            </div>
          ))}
          {agent.isLoading && (
            <div className="text-left">
              <div className="inline-block p-3 rounded-lg bg-muted">
                Thinking...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

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

### Step 5.3: Create Drawer Wrapper

```typescript
// components/agent-chat-drawer.tsx
"use client";

import { useState } from "react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { MessageSquare } from "lucide-react";
import { AgentChatInterface } from "./agent-chat-interface";

interface AgentChatDrawerProps {
  assistantId: string;
  userId: string;
  triggerLabel?: string;
}

export function AgentChatDrawer({
  assistantId,
  userId,
  triggerLabel = "Chat with Agent",
}: AgentChatDrawerProps) {
  const [threadId, setThreadId] = useState<string | null>(null);

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline" size="sm">
          <MessageSquare className="h-4 w-4 mr-2" />
          {triggerLabel}
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="w-[500px] sm:w-[600px] flex flex-col">
        <SheetHeader>
          <SheetTitle>Agent Assistant</SheetTitle>
        </SheetHeader>
        <div className="flex-1 overflow-hidden">
          <AgentChatInterface
            assistantId={assistantId}
            threadId={threadId}
            userId={userId}
          />
        </div>
      </SheetContent>
    </Sheet>
  );
}
```

### Step 5.4: Add to Page

```typescript
// app/dashboard/page.tsx (or any page)
import { AgentChatDrawer } from "@/components/agent-chat-drawer";

export default async function DashboardPage() {
  const user = await getCurrentUser(); // Your auth logic

  return (
    <div>
      {/* Your page content */}
      
      {/* Chat drawer in corner */}
      <div className="fixed bottom-4 right-4">
        <AgentChatDrawer
          assistantId="my-agent"
          userId={user.id}
        />
      </div>
    </div>
  );
}
```

**Reference:** `.clinefiles/ui/drawer-chat-pattern.md`

---

## Alternative: Full-Page Chat (If Needed)

If chat is the primary interface:

```typescript
// app/chat/page.tsx
"use client";

import { AgentChatInterface } from "@/components/agent-chat-interface";
import { useSearchParams } from "next/navigation";

export default function ChatPage() {
  const searchParams = useSearchParams();
  const threadId = searchParams.get("thread");

  return (
    <div className="h-screen">
      <AgentChatInterface
        assistantId="my-agent"
        threadId={threadId}
        userId="user-123" // From auth
      />
    </div>
  );
}
```

---

## Step 6: Implement Thread Management

Thread persistence strategy depends on your use case:

### Strategy A: Per-Session Threads (Most Common)

New thread per drawer open, persists within session:

```typescript
// In AgentChatDrawer component
const [threadId, setThreadId] = useState<string | null>(null);

// Thread created on first message, persists until drawer closed
```

### Strategy B: Entity-Bound Threads (For Multi-Actor/Item Systems)

Thread tied to specific entity (actor, document, etc.):

```typescript
// See .clinefiles/langchain/patterns/multi-thread-actor.md for full pattern

// hooks/use-agent.ts - Auto-generate thread IDs
const threadId = useMemo(() => {
  if (entityType === 'actor' && scenarioId) {
    // Simulation thread
    return `actor_${actorId}_scenario_${scenarioId}_sim`;
  } else {
    // Meta-chat thread
    return `actor_${actorId}_chat_${userId}_${timestamp}`;
  }
}, [entityType, actorId, scenarioId, userId]);
```

### Strategy C: URL-Based Threads (For Full-Page Chat)

Thread ID in URL for bookmarking/sharing:

```typescript
const searchParams = useSearchParams();
const router = useRouter();
const threadId = searchParams.get("thread");

const handleThreadCreate = (newThreadId: string) => {
  router.push(`/chat?thread=${newThreadId}`);
};
```

**References:**
- `.clinefiles/langchain/langsmith/next-js-integration/threads.md`
- `.clinefiles/langchain/patterns/multi-thread-actor.md` (for entity-bound threads)

---

## Step 7: Add Human-in-the-Loop UI (If Implemented)

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

## Step 8: Add Background Runs (If Needed)

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

## Step 9: Validate Against Interface Specifications (REQUIRED)

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

## Step 10: Test Integration

### Test 1: Basic Drawer Interaction

1. Start agent service: `langgraph dev` (in agent-service/)
2. Start Next.js: `npm run dev` (in Next.js app/)
3. Navigate to page with drawer
4. Click drawer trigger button
5. Drawer should slide in from right
6. Send message, verify response streams
7. Close and reopen drawer, verify thread persists (if Strategy A)

### Test 2: Thread Management

**For Strategy A (Per-Session):**
1. Open drawer, send messages
2. Close drawer, reopen
3. Verify conversation persists

**For Strategy B (Entity-Bound):**
1. Select entity (actor, etc.)
2. Send messages
3. Select different entity
4. Return to first entity
5. Verify conversation persists per entity

**For Strategy C (URL-Based):**
1. Send several messages
2. Note thread ID in URL
3. Refresh page
4. Verify conversation history loads

### Test 3: Multiple Simultaneous Threads

1. Open drawer for Entity A
2. Send messages
3. Switch to Entity B (or open different drawer)
4. Send different messages
5. Return to Entity A
6. Verify correct thread loaded with correct history

### Test 4: Mobile Responsiveness

1. Open DevTools, switch to mobile view
2. Trigger drawer
3. Verify proper width/positioning
4. Test scrolling in message area
5. Verify input accessible

---

## Phase 8.4 Completion Checklist

Before proceeding to Phase 8.5:

**Environment & Dependencies:**
- [ ] `NEXT_PUBLIC_AGENT_API_URL` added to `.env.local`
- [ ] `@langchain/langgraph-sdk` installed
- [ ] shadcn Sheet component installed

**Core Implementation:**
- [ ] `useAgent` hook created with context support
- [ ] `AgentChatInterface` component implemented
- [ ] `AgentChatDrawer` component implemented
- [ ] Drawer integrated into relevant pages
- [ ] Thread management strategy from Phase 8.3 implemented

**Interface Validation (CRITICAL):**
- [ ] TypeScript types match Python schemas exactly
- [ ] Context passed via options parameter (not state, not config)
- [ ] State fields match AgentState schema
- [ ] Service interface docs updated to 🟢 IMPLEMENTED
- [ ] Cross-references verified (clickable links work)

**Feature Implementation:**
- [ ] Human-in-the-loop UI added (if Phase 8.3 implemented it)
- [ ] Background runs implemented (if Phase 0 determined needed)
- [ ] Entity selection working (if multi-entity system)

**Testing:**
- [ ] Basic drawer interaction test passes
- [ ] Thread persistence test passes (per strategy)
- [ ] Multiple threads test passes (if applicable)
- [ ] Mobile responsiveness verified
- [ ] Streaming responses display token-by-token
- [ ] No CORS errors in browser console
- [ ] Drawer positioning correct (doesn't obstruct content)

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

### Issue: Drawer not opening

**Check:**
- shadcn Sheet component installed
- SheetTrigger wrapped in asChild
- Sheet state not controlled incorrectly
- No z-index conflicts with other UI elements

### Issue: Thread not persisting between drawer opens

**Check:**
- Thread ID stored correctly per your strategy
- useAgent receives same thread ID on reopen
- reconnectOnMount: true in useStream config

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
