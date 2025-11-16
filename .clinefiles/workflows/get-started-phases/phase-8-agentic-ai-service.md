# Phase 8: Agentic AI Service [MANDATORY]

**Purpose:** Integrate LangChain agents with AI capabilities using LangGraph dev server for local development and LangSmith for production deployment.

**Prerequisites:** 
- Phase 0 completed with Agent Capabilities Assessment
- Phase 1-7 completed (database, Next.js app, UI foundation)
- LangSmith API key obtained (free at smith.langchain.com/settings)

**Time Estimate:** 2-3 hours total (split across 5 sub-phases)

---

## Overview

This phase transforms your application from a standard CRUD app into an AI-native application with intelligent agent capabilities. The implementation follows the decisions made in Phase 0's "Agentic AI Capabilities Assessment."

### What You'll Build

By the end of this phase, your application will have:

- **Separate Agent Service** - Python-based LangChain service in `langchain_/` directory
- **LangGraph Dev Server** - Local development environment simulating LangSmith cloud
- **Memory Infrastructure** - Automatic persistence via LangSmith (checkpointer + store)
- **Streaming Responses** - Real-time agent output in Next.js UI
- **Custom Tools** - Domain-specific capabilities defined in Phase 0
- **LangSmith Features** - Human-in-the-loop, background runs, cron jobs, etc. (as needed)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Your Application                        │
├──────────────────┬──────────────────┬──────────────────────┤
│   nextjs_/       │   supabase_/     │   langchain_/        │
│   (Next.js UI)   │   (Database)     │   (LangChain)        │
├──────────────────┴──────────────────┴──────────────────────┤
│                                                              │
│  Next.js ←→ LangGraph Dev (port 2024) ←→ Supabase          │
│             ↓                                                │
│         LangSmith Memory                                     │
│         (automatic)                                          │
└─────────────────────────────────────────────────────────────┘
```

**Key Principle:** LangSmith handles ALL infrastructure (checkpointer, store) - you just use it via `thread_id` and `runtime.store`.

---

## Phase 8 Sub-Phases

### Phase 8.1: Agent Service Setup
**📄 [Full Guide: phase-8-1-agent-setup.md](./phase-8-1-agent-setup.md)**

**Time:** 15-20 minutes

**Purpose:** Create the agent service directory structure and initialize LangGraph development environment

**Key Steps:**
- Create `langchain_/` directory as peer to `nextjs_/` and `supabase_/`
- Initialize Python project with `uv` (per project rules)
- Install core dependencies: langchain, langchain-openai, langchain-anthropic, deepagents, langgraph-sdk, langgraph-cli[inmem]
- Create `langgraph.json` configuration file
- Set up `.env` with LangSmith API key
- Start `langgraph dev` server - memory infrastructure automatically available

**Verification:**
- `langgraph dev` runs successfully on port 2024
- API docs accessible at http://localhost:2024/docs
- Studio UI accessible via LangSmith

---

### Phase 8.2: Agent Implementation
**📄 [Full Guide: phase-8-2-agent-implementation.md](./phase-8-2-agent-implementation.md)**

**Time:** 30-40 minutes

**Purpose:** Implement agent(s) based on Phase 0 assessment using middleware-centric pattern

**Key References:**
- `.clinefiles/langchain/core/agents.md` - Agent creation fundamentals
- `.clinefiles/langchain/patterns/middleware-centric.md` - **CRITICAL:** Middleware composition pattern
- `.clinefiles/langchain/patterns/agent-folder-organization.md` - Standard agent code structure
- `.clinefiles/langchain/patterns/middleware-tools.md` - Production middleware-tools pattern
- `.clinefiles/langchain/core/tools.md` - Custom tool creation
- `.clinefiles/langchain/reference-implementations/` - Production-ready code examples

**Key Steps:**
- Implement agent(s) - can be multiple types (supervisor, simple, specialized)
- Use middleware-centric pattern for production-ready architecture
- Add middleware stack from Phase 0 assessment
- Create custom tools from Phase 0 requirements
- Configure streaming (default, already enabled via LangSmith)

**Verification:**
- Agent responds to test inputs via API
- Middleware stack executing correctly
- Custom tools working as expected
- Streaming responses visible in logs

---

### Phase 8.3: LangSmith Features Integration
**📄 [Full Guide: phase-8-3-langsmith-features.md](./phase-8-3-langsmith-features.md)**

**Time:** 20-30 minutes

**Purpose:** Integrate LangSmith features identified in Phase 0 assessment

**Key References:**
- `.clinefiles/langchain/langsmith/next-js-integration/` folder - All Next.js patterns
- `.clinefiles/langchain/core/human-in-the-loop.md` - Approval workflows
- `.clinefiles/langchain/core/retrieval.md` - RAG implementation (if needed)

**Key Steps:**
- Implement thread management (always required)
- Add human-in-the-loop flows (if Phase 0 determined needed)
- Configure background runs (if Phase 0 determined needed)
- Set up cron jobs for scheduled tasks (if Phase 0 determined needed)
- Implement RAG for document search (if Phase 0 determined needed)
- Add any other features from Phase 0 assessment

**Memory Note:** 
- Short-term (checkpointer) and long-term (store) memory are AUTOMATIC via LangSmith
- Simply use `thread_id` for persistence - no manual configuration needed
- Access store via `runtime.store` in tools/middleware

**Verification:**
- Selected features working correctly
- Memory persisting across conversations (test with thread_id)
- Background/cron jobs executing on schedule (if applicable)
- RAG returning relevant results (if applicable)

---

### Phase 8.4: Next.js Integration
**📄 [Full Guide: phase-8-4-nextjs-integration.md](./phase-8-4-nextjs-integration.md)**

**Time:** 25-35 minutes

**Purpose:** Connect Next.js frontend to agent service using LangGraph SDK

**Key References:**
- `.clinefiles/langchain/langsmith/next-js-integration/core.md` - useStream() patterns
- `.clinefiles/langchain/langsmith/next-js-integration/streaming.md` - Streaming implementation
- `.clinefiles/langchain/langsmith/next-js-integration/threads.md` - Thread management

**Key Steps:**
- Add `NEXT_PUBLIC_AGENT_API_URL=http://localhost:2024` to `.env.local`
- Install `@langchain/langgraph-sdk` in Next.js app
- Implement `useStream()` hook for agent interaction
- Create agent UI components (chat interface, streaming display)
- Add thread management and conversation history
- Test end-to-end flows from UI

**Verification:**
- Agent chat UI functional in Next.js app
- Streaming responses displaying token-by-token
- Thread persistence working (refresh page, conversation retained)
- Error handling graceful

---

### Phase 8.5: Testing & Documentation
**📄 [Full Guide: phase-8-5-testing-docs.md](./phase-8-5-testing-docs.md)**

**Time:** 20-25 minutes

**Purpose:** Comprehensive testing and documentation of agent capabilities

**Key Steps:**
- Test all agent features from Phase 0 requirements
- Verify memory persistence (short-term and long-term)
- Test error scenarios and edge cases
- Document agent capabilities in README
- Create troubleshooting guide for common issues
- Prepare for LangSmith cloud deployment

**Verification:**
- All Phase 0 agent features working end-to-end
- Documentation complete and clear
- Deployment preparation checklist complete

---

## Critical References

Throughout Phase 8, you MUST reference ONLY these docs:

### Core LangChain Patterns
- `.clinefiles/langchain/core/agents.md`
- `.clinefiles/langchain/core/tools.md`
- `.clinefiles/langchain/core/middleware.md`
- `.clinefiles/langchain/core/context-engineering.md`
- `.clinefiles/langchain/patterns/middleware-centric.md` - **CRITICAL PATTERN**
- `.clinefiles/langchain/patterns/agent-folder-organization.md` - Standard structure

### Memory & Persistence
- `.clinefiles/langchain/core/short-term-memory.md`
- `.clinefiles/langchain/core/long-term-memory.md`
- `.clinefiles/langchain/langsmith/local-development.md`

### Production Patterns
- `.clinefiles/langchain/patterns/middleware-centric.md` - **CRITICAL:** Middleware composition
- `.clinefiles/langchain/patterns/agent-folder-organization.md` - Code organization
- `.clinefiles/langchain/patterns/middleware-tools.md` - Tools middleware pattern
- `.clinefiles/langchain/patterns/custom-subagents.md` - Multi-agent patterns
- `.clinefiles/langchain/reference-implementations/` - Working code examples

### Next.js Integration
- All files in `.clinefiles/langchain/langsmith/next-js-integration/`

---

## Phase 8 Completion Checklist

Return to main workflow and verify:

### Setup & Configuration ✓
- [ ] `langchain_/` directory created with proper Python structure
- [ ] Dependencies installed via `uv add`: langchain, langchain-openai, langchain-anthropic, deepagents, langgraph, langgraph-cli
- [ ] `langgraph.json` configuration file created
- [ ] `.env` contains `LANGSMITH_API_KEY`
- [ ] `langgraph dev` runs successfully on port 2024
- [ ] API accessible at http://localhost:2024
- [ ] Studio UI accessible via LangSmith link

### Agent Implementation ✓
- [ ] Agent architecture from Phase 0 implemented (supervisor/simple/both)
- [ ] Middleware stack from Phase 0 assessment working
- [ ] Custom tools from Phase 0 requirements functional
- [ ] Streaming enabled and responses visible
- [ ] Memory automatic via LangSmith (no manual checkpointer/store setup)

### LangSmith Features ✓
- [ ] Thread management working (conversations persist)
- [ ] Features from Phase 0 implemented:
  - [ ] Human-in-the-loop (if applicable)
  - [ ] Background runs (if applicable)
  - [ ] Cron jobs (if applicable)
  - [ ] RAG (if applicable)
  - [ ] Other features (if applicable)

### Next.js Integration ✓
- [ ] `NEXT_PUBLIC_AGENT_API_URL` in Next.js `.env.local`
- [ ] `@langchain/langgraph-sdk` installed in Next.js
- [ ] `useStream()` hook implemented
- [ ] Agent chat UI components created
- [ ] Thread management in UI working
- [ ] Streaming responses displaying token-by-token
- [ ] Error handling implemented

### Testing & Documentation ✓
- [ ] All agent features from Phase 0 tested end-to-end
- [ ] Memory persistence verified (threads, store)
- [ ] Edge cases and error scenarios tested
- [ ] README.md documents agent capabilities
- [ ] Troubleshooting guide created
- [ ] Deployment preparation complete

**Cannot proceed to Phase 9 without completing all checklist items.**

---

## Common Issues - Quick Reference

For detailed troubleshooting, see each sub-phase guide:

### Setup Issues → Phase 8.1
- Python version compatibility (requires 3.11+)
- `uv` command not found
- LangSmith API key issues
- Port 2024 already in use

### Implementation Issues → Phase 8.2
- Middleware execution order
- Tool calling failures
- Streaming not working
- Agent not following instructions

### Feature Issues → Phase 8.3
- Thread not persisting
- Store data not accessible
- Human-in-the-loop not triggering
- RAG returning irrelevant results

### Integration Issues → Phase 8.4
- CORS errors from Next.js
- useStream() hook not updating
- Thread management broken
- Token streaming choppy

### Testing Issues → Phase 8.5
- End-to-end flows failing
- Memory not persisting correctly
- Performance issues with large contexts

---

## Important Reminders

### Memory Infrastructure (CRITICAL)
- ✅ **DO:** Use `thread_id` for conversation persistence
- ✅ **DO:** Access store via `runtime.store` in tools/middleware
- ❌ **DON'T:** Manually instantiate PostgresSaver or PostgresStore
- ❌ **DON'T:** Configure checkpointer in code - LangSmith handles it

### Patterns to Follow
- ✅ Use middleware-centric pattern for production agents
- ✅ Reference `.clinefiles/langchain/` docs ONLY
- ✅ Follow patterns from Next.js integration guides exactly
- ✅ Implement streaming by default (rarely disable)

### Workflow Principles
- Stay in context by referencing docs (don't repeat content)
- Update WORKFLOW_CHECKPOINT.md after each sub-phase
- Condense context when >40-50% to continue effectively
- All patterns generalizable (not specific to current project)

---

## Next Phase

**Proceed to:** [Phase 9: System Review](./phase-9-system-review.md)

**After:** All Phase 8 checklist items verified and agent service fully integrated with Next.js application.
