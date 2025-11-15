# Phase 8.3: LangSmith Features Integration

**Time Estimate:** 20-30 minutes

**Purpose:** Integrate LangSmith features identified in Phase 0 assessment

**Prerequisites:**
- Phase 8.2 completed with working agent(s)
- PROJECT_REQUIREMENTS.md documenting Phase 0 LangSmith features assessment
- `langgraph dev` running

**Key References:**
- `.clinerules/langchain/langsmith/next-js-integration/` folder - All Next.js integration patterns
- `.clinerules/langchain/core/human-in-the-loop.md` - Approval workflows
- `.clinerules/langchain/core/retrieval.md` - RAG implementation

---

## Step 1: Review Phase 0 LangSmith Features Assessment

**Check PROJECT_REQUIREMENTS.md for which features you determined you need:**

- [ ] **Threads** - Thread management (ALWAYS required)
- [ ] **Streaming** - Real-time responses (Default enabled)
- [ ] **Assistants** - Multiple agent configurations
- [ ] **Human-in-the-loop** - Approval workflows
- [ ] **Background runs** - Async processing
- [ ] **Cron jobs** - Scheduled tasks
- [ ] **Generative UI** - Dynamic UI from agent
- [ ] **Multiple agents same thread** - Multi-agent conversations
- [ ] **Time travel** - Conversation branching

**This phase implements ONLY the features you checked in Phase 0.**

---

## Step 2: Thread Management (ALWAYS REQUIRED)

Thread management is the foundation - all agents need it for conversation persistence.

### Memory is Automatic

**Critical understanding:** LangSmith handles ALL memory infrastructure automatically.

When using `thread_id`:
- ✅ **Checkpointer (short-term memory)** - Conversation history automatically saved
- ✅ **Store (long-term memory)** - Cross-thread data automatically available
- ❌ **NO configuration needed** - Just use `thread_id` parameter

**Reference:** `.clinerules/langchain/core/short-term-memory.md` and `.clinerules/langchain/core/long-term-memory.md`

### Thread Organization Strategy

**From Phase 0, how did you decide to organize threads?**

**Option A: One thread per conversation**
```python
# Next.js creates new thread for each chat session
# Good for: Chat apps, support tickets, isolated conversations
```

**Option B: One thread per project/entity**
```python
# Thread tied to project ID or entity ID
# Good for: Project-based work, document editing, persistent context
```

**Option C: One thread per user session**
```python
# Thread persists across page refreshes in same session
# Good for: Single ongoing conversation, research tasks
```

**Document your choice** - it will guide Phase 8.4 Next.js implementation.

**Reference:** `.clinerules/langchain/langsmith/next-js-integration/threads.md`

---

## Step 3: Human-in-the-Loop (If Phase 0 Determined Needed)

**Skip if Phase 0 determined NOT needed.**

Human-in-the-loop allows agents to pause and request user approval before taking actions.

### Implementation Pattern

```python
# src/agent/graph.py
from langgraph.types import interrupt


def tool_approval_node(state: State):
    """Node that requires human approval before executing tool"""
    
    # Prepare action for approval
    proposed_action = {
        "tool": "delete_database_record",
        "args": {"record_id": "123"}
    }
    
    # Interrupt and wait for human decision
    approval = interrupt(proposed_action)
    
    # If approved, execute
    if approval:
        # Execute the tool
        result = execute_tool(proposed_action)
        return {"messages": [{"role": "assistant", "content": result}]}
    else:
        return {"messages": [{"role": "assistant", "content": "Action cancelled by user"}]}
```

### When to Use

- Destructive operations (delete, modify critical data)
- Financial transactions
- External API calls with cost
- Sending emails/notifications
- Any action requiring user confirmation

**Reference:** `.clinerules/langchain/core/human-in-the-loop.md` and `.clinerules/langchain/langsmith/next-js-integration/human-in-the-loop.md`

---

## Step 4: Background Runs (If Phase 0 Determined Needed)

**Skip if Phase 0 determined NOT needed.**

Background runs allow agents to process long-running tasks asynchronously without blocking UI.

### Use Cases

- Long research tasks (10+ minutes)
- Batch processing
- Report generation
- Data analysis
- Any task where user doesn't need to wait

### Implementation

Background runs are handled on the Next.js side (Phase 8.4). On agent side, no special configuration needed - just build agent normally.

**Reference:** `.clinerules/langchain/langsmith/next-js-integration/background-runs.md`

---

## Step 5: Cron Jobs (If Phase 0 Determined Needed)

**Skip if Phase 0 determined NOT needed.**

Cron jobs schedule agents to run automatically on a schedule.

### Use Cases

- Daily reports
- Periodic data sync
- Scheduled notifications
- Monitoring tasks
- Cleanup operations

### Configuration

Update `langgraph.json` to define cron schedule:

```json
{
  "graphs": {
    "agent": "./src/agent/graph.py:graph"
  },
  "crons": [
    {
      "schedule": "0 9 * * *",
      "assistant_id": "agent",
      "input": {
        "messages": [{"role": "user", "content": "Generate daily report"}]
      }
    }
  ]
}
```

**Schedule format:** Cron syntax (minute hour day month weekday)
- `"0 9 * * *"` - Daily at 9 AM
- `"0 */4 * * *"` - Every 4 hours
- `"0 0 * * 0"` - Weekly on Sunday midnight

**Reference:** `.clinerules/langchain/langsmith/next-js-integration/cron-jobs.md`

---

## Step 6: RAG / Retrieval (If Phase 0 Determined Needed)

**Skip if Phase 0 determined NOT needed.**

RAG (Retrieval-Augmented Generation) enables agents to search and query document collections.

### When to Use

- Document Q&A systems
- Knowledge base search
- Context-aware responses from internal docs
- FAQ systems

### Implementation Pattern

```python
# src/agent/tools.py
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings


# Initialize vector store (Supabase with pgvector)
embeddings = OpenAIEmbeddings()
vectorstore = SupabaseVectorStore(
    client=supabase_client,
    embedding=embeddings,
    table_name="documents",
    query_name="match_documents"
)


@tool
def search_documents(query: str) -> str:
    """
    Search knowledge base for relevant documents.
    
    Args:
        query: Search query
    
    Returns:
        Relevant document excerpts
    """
    docs = vectorstore.similarity_search(query, k=3)
    return "\n\n".join([doc.page_content for doc in docs])
```

### Setup Requirements

1. Enable pgvector in Supabase
2. Create documents table with vector column
3. Create match function for similarity search
4. Ingest documents into vector store

**Reference:** `.clinerules/langchain/core/retrieval.md`

---

## Step 7: Assistants (If Multiple Agent Types)

**Skip if only using single agent type.**

Assistants allow multiple agent configurations in same service.

### Implementation

Create separate graph files for each assistant:

```python
# src/agent/research_assistant.py
# Supervisor agent for deep research

# src/agent/qa_assistant.py  
# Simple agent for quick Q&A
```

Update `langgraph.json`:

```json
{
  "graphs": {
    "research": "./src/agent/research_assistant.py:graph",
    "qa": "./src/agent/qa_assistant.py:graph"
  }
}
```

Access different assistants via `assistant_id` parameter in API calls.

**Reference:** `.clinerules/langchain/langsmith/next-js-integration/assistants.md`

---

## Step 8: Verify Features

### Test Thread Persistence

```bash
# Create thread
curl -X POST http://localhost:2024/threads
# Save thread_id

# Send messages, verify conversation persists
curl -X POST http://localhost:2024/runs/stream \
  -d '{"thread_id": "[thread-id]", "assistant_id": "agent", ...}'
```

### Test Human-in-the-Loop (if implemented)

```bash
# Send message that triggers approval
# Verify agent pauses and waits for approval
# Use update endpoint to provide approval
```

### Test Cron Jobs (if configured)

Check `langgraph.json` cron syntax is valid:
- Schedule follows cron format
- Assistant ID matches graph name
- Input has required structure

### Test RAG (if implemented)

```bash
# Send query that should retrieve documents
# Verify agent searches vector store and uses context
```

---

## Phase 8.3 Completion Checklist

Before proceeding to Phase 8.4, verify:

- [ ] Reviewed Phase 0 LangSmith features in PROJECT_REQUIREMENTS.md
- [ ] Thread management strategy documented
- [ ] Memory automatic (no manual checkpointer/store config)
- [ ] Human-in-the-loop implemented (if Phase 0 determined needed)
- [ ] Background runs noted for Phase 8.4 (if Phase 0 determined needed)
- [ ] Cron jobs configured in langgraph.json (if Phase 0 determined needed)
- [ ] RAG/retrieval implemented with vector store (if Phase 0 determined needed)
- [ ] Multiple assistants configured (if Phase 0 determined needed)
- [ ] Thread persistence test passes
- [ ] Feature-specific tests pass
- [ ] `langgraph dev` runs without errors

---

## Troubleshooting

### Issue: Thread not persisting

**Check:**
- Using valid UUID for `thread_id`
- Not passing `null` instead of thread ID
- LangSmith automatic memory enabled (default)

### Issue: Human-in-the-loop not triggering

**Check:**
- Using `interrupt()` function correctly
- Interrupt value structure matches expected format
- Update endpoint called to provide approval

### Issue: Cron not executing

**Check:**
- Cron syntax valid (use crontab.guru to verify)
- Assistant ID matches graph name in langgraph.json
- Input structure correct

### Issue: RAG returning irrelevant results

**Check:**
- Documents properly embedded in vector store
- Search parameters (k value, similarity threshold)
- Query quality and specificity

---

## Important Notes

### Memory Infrastructure (CRITICAL REMINDER)

**Never configure memory manually.** LangSmith provides:
- ✅ Checkpointer via `thread_id`
- ✅ Store via `runtime.store`
- ❌ No PostgresSaver/PostgresStore setup needed

### Feature Selection

Implement ONLY features from Phase 0 assessment:
- Don't add features "just in case"
- Each feature adds complexity
- Can add more features later if needed

### Next.js Integration

Many features require Next.js implementation (Phase 8.4):
- Human-in-the-loop approval UI
- Background run status monitoring
- Thread management UI
- Feature-specific components

---

## Next Steps

**Proceed to:** [Phase 8.4: Next.js Integration](./phase-8-4-nextjs-integration.md)

**With:** Agent service running with selected LangSmith features, ready for frontend integration.
