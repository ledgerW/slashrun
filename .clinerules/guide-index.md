# .clinerules Guide Index

**Master reference catalog for AI coding assistant**

## Purpose

This index catalogs all available .clinerules guides (excluding workflows). Before implementing any feature, **read the relevant guides first** to ensure you follow established patterns and best practices.

## How to Use This Guide

1. **Identify your task** - What are you being asked to build or fix?
2. **Scan the relevant categories** below
3. **Read the indicated guide(s)** BEFORE writing code
4. **Multiple guides may apply** to a single task - read all relevant ones

---

## 📁 LangChain & LangGraph

### Core Concepts (.clinefiles/langchain/core/)

#### agents.md
**Read this for:** Creating and configuring LangChain agents  
**Summary:** Core agent creation patterns, configuration options, and setup basics.  
**Location:** `.clinefiles/langchain/core/agents.md`

#### short-term-memory.md
**Read this for:** Thread-level conversation history, managing message context  
**Summary:** Short-term memory (checkpointers) via LangSmith. Explains how LangSmith handles ALL checkpointer infrastructure automatically - simply use thread_id. Includes patterns for trimming, deleting, and summarizing messages.  
**Location:** `.clinefiles/langchain/core/short-term-memory.md`

#### long-term-memory.md
**Read this for:** Cross-thread memory storage, persistent user data  
**Summary:** Long-term memory (stores) via LangSmith. Explains how LangSmith handles ALL store infrastructure automatically - access via runtime.store only. Covers namespaces, semantic search, and memory organization.  
**Location:** `.clinefiles/langchain/core/long-term-memory.md`

#### tools.md
**Read this for:** Building custom tool functions, tool patterns  
**Summary:** Creating custom tools, tool runtime access, state/context access in tools, returning structured data.  
**Location:** `.clinefiles/langchain/core/tools.md`

#### middleware.md
**Read this for:** Request/response processing, intercepting model calls  
**Summary:** Middleware patterns (@before_model, @after_model, @dynamic_prompt), state manipulation, custom processing layers.  
**Location:** `.clinefiles/langchain/core/middleware.md`

#### runtime.md
**Read this for:** Accessing runtime context and state  
**Summary:** Runtime API, accessing state/context/store in tools and middleware, type-safe runtime usage.  
**Location:** `.clinefiles/langchain/core/runtime.md`

#### context-engineering.md
**Read this for:** Optimizing context for agents, prompt engineering  
**Summary:** Context is #1 factor in agent reliability. Covers context optimization strategies, prompt design, and information architecture.  
**Location:** `.clinefiles/langchain/core/context-engineering.md`

#### messages.md
**Read this for:** Working with message types, message formatting  
**Summary:** Message types (human, ai, system, tool), message manipulation, conversation history management.  
**Location:** `.clinefiles/langchain/core/messages.md`

#### streaming.md
**Read this for:** Real-time agent output streaming  
**Summary:** Streaming agent responses, token-by-token output, progress updates.  
**Location:** `.clinefiles/langchain/core/streaming.md`

#### structured-output.md
**Read this for:** Type-safe agent responses, output schemas  
**Summary:** Defining output schemas, type validation, structured data extraction from LLM responses.  
**Location:** `.clinefiles/langchain/core/structured-output.md`

#### guardrails.md
**Read this for:** Safety and validation patterns, output filtering  
**Summary:** Implementing safety checks, content filtering, validation rules, error handling.  
**Location:** `.clinefiles/langchain/core/guardrails.md`

#### human-in-the-loop.md
**Read this for:** Interactive approval workflows, user confirmation  
**Summary:** Patterns for requiring human approval, breakpoints, interrupt patterns.  
**Location:** `.clinefiles/langchain/core/human-in-the-loop.md`

#### multi-agent.md
**Read this for:** Multi-agent orchestration, agent coordination  
**Summary:** Patterns for multiple agents working together, delegation, handoffs between agents.  
**Location:** `.clinefiles/langchain/core/multi-agent.md`

#### retrieval.md
**Read this for:** RAG patterns, document retrieval  
**Summary:** Retrieval-augmented generation, document search, knowledge base integration.  
**Location:** `.clinefiles/langchain/core/retrieval.md`

#### models.md
**Read this for:** LLM model configuration  
**Summary:** Model selection, configuration, provider-specific settings.  
**Location:** `.clinefiles/langchain/core/models.md`

#### state-schemas.md
**Read this for:** Defining agent state and context schemas  
**Summary:** **CRITICAL GUIDE** - Correct pattern: extend AgentState (NOT add_messages). Covers state vs context, using NotRequired, accessing state in tools/middleware, common errors and solutions. Essential for avoiding "dict has no attribute" errors.  
**Location:** `.clinefiles/langchain/core/state-schemas.md`

### LangSmith Deployment (.clinefiles/langchain/langsmith/)

#### local-development.md
**Read this for:** Using `langgraph dev` for local testing  
**Summary:** Critical guide for local development. Explains how `langgraph dev` emulates LangSmith platform locally. Shows that checkpointers and stores are NEVER manually instantiated - LangSmith handles everything.  
**Location:** `.clinefiles/langchain/langsmith/local-development.md`

#### long-term-memory.md
**Read this for:** Configuring semantic search for stores  
**Summary:** How to configure semantic search (embeddings) in langgraph.json for store queries. Deployment-specific store configuration.  
**Location:** `.clinefiles/langchain/langsmith/long-term-memory.md`

#### monorepo-setup.md
**Read this for:** Multi-agent monorepo structure  
**Summary:** Organizing multiple agents in a single repository, shared code patterns, deployment configuration.  
**Location:** `.clinefiles/langchain/langsmith/monorepo-setup.md`

#### next-js-integration/ (folder)
**Read this for:** Next.js frontend patterns  
**Summary:** Various Next.js integration guides including core setup, streaming, human-in-the-loop, threads, assistants, background runs, cron jobs, generative UI, and more.  
**Location:** `.clinefiles/langchain/langsmith/next-js-integration/`

#### next-js-integration/thread-management.md
**Read this for:** Thread ID requirements, UUID patterns, AgentThreadManager pattern  
**Summary:** **CRITICAL GUIDE** - Thread IDs MUST be UUIDs. Thread MUST be created before use. Complete AgentThreadManager pattern for Next.js ↔ LangChain integration. Essential for avoiding 422 "Invalid thread ID" and 404 "Thread not found" errors.  
**Location:** `.clinefiles/langchain/langsmith/next-js-integration/thread-management.md`

### Production Patterns (.clinefiles/langchain/patterns/)

#### middleware-centric.md
**Read this for:** Middleware-centric architecture, composing reusable middleware  
**Summary:** **CRITICAL PATTERN** - Build agents by composing middleware instead of monolithic code. Covers {tools_list} placeholder, separation of identity vs tool guidance (core_prompt.py vs tools_prompt.py), middleware ordering, state extension, and all middleware hooks. Essential for any agent development.  
**Location:** `.clinefiles/langchain/patterns/middleware-centric.md`

#### agent-folder-organization.md
**Read this for:** Organizing agent code structure, manager vs worker patterns  
**Summary:** Standard folder structure for agents using middleware-centric pattern. Covers manager vs worker organization, naming conventions, import patterns, and best practices. Follow this for all agent projects.  
**Location:** `.clinefiles/langchain/patterns/agent-folder-organization.md`

#### middleware-tools.md
**Read this for:** Organizing custom tools in middleware  
**Summary:** Production pattern for middleware-centric tool organization, separating tool logic from agent definition.  
**Location:** `.clinefiles/langchain/patterns/middleware-tools.md`

#### custom-subagents.md
**Read this for:** Building specialized sub-agents  
**Summary:** Patterns for creating specialized agents that can be composed into larger systems.  
**Location:** `.clinefiles/langchain/patterns/custom-subagents.md`

#### guardrails-middleware.md
**Read this for:** Safety and validation middleware patterns  
**Summary:** Generalizable middleware for content safety, PII protection, domain compliance, and output validation. Shows how to accept system prompts, rules, and structured output models as init parameters for before/after-agent hooks.  
**Location:** `.clinefiles/langchain/patterns/guardrails-middleware.md`

#### multi-thread-actor.md
**Read this for:** Multi-context agent threads, actor-based systems, simulation vs meta-chat  
**Summary:** **Critical pattern for actor/entity-based systems**. Enables agents to maintain separate threads for different contexts (simulation threads per scenario, meta-chat threads for interviews). Covers thread naming conventions, state/context passing, LangSmith as single source of truth, context loading between threads, and UI integration with drawer pattern. Essential for any system where agents participate in multiple scenarios or need separate conversation contexts.  
**Location:** `.clinefiles/langchain/patterns/multi-thread-actor.md`

### Reference Implementations (.clinefiles/langchain/reference-implementations/)

**Read these for:** Complete, production-ready Python code examples  
**Summary:** Working implementations of middleware patterns including GuardrailsMiddleware, SpecialistAgentsMiddleware, ToolsMiddleware, JMESPathMapMiddleware, and more. Use as templates for your own middleware.  
**Location:** `.clinefiles/langchain/reference-implementations/`

---

## 📁 Supabase Authentication

### supabase/auth-for-nextjs.md
**Read this for:** ANY authentication work, SSR setup, cookie handling, middleware, login/signup flows  
**Summary:** Critical Next.js SSR patterns using @supabase/ssr. MUST use getAll/setAll cookie methods only. Contains absolute requirements that will break the app if not followed.  
**Location:** `.clinefiles/supabase/auth-for-nextjs.md`

---

## 📁 Supabase Database

### database/create_migrations.md
**Read this for:** Creating database migrations, adding tables, schema changes  
**Summary:** Migration file naming conventions (YYYYMMDDHHmmss format), SQL guidelines, RLS requirements, best practices for production-ready migrations.  
**Location:** `.clinefiles/supabase/database/create_migrations.md`

### database/create_functions.md
**Read this for:** Creating PostgreSQL functions, stored procedures, triggers  
**Summary:** Patterns for creating database functions, security considerations, performance optimization.  
**Location:** `.clinefiles/supabase/database/create_functions.md`

### database/create_rls_policies.md
**Read this for:** Row Level Security policies, data access control, authorization  
**Summary:** RLS policy patterns, granular permission setup, authenticated vs anonymous access, security best practices.  
**Location:** `.clinefiles/supabase/database/create_rls_policies.md`

### database/declarative_schema.md
**Read this for:** Database schema design, table structure planning  
**Summary:** Declarative schema patterns, normalization, foreign keys, constraints, and relational design principles.  
**Location:** `.clinefiles/supabase/database/declarative_schema.md`

### database/postgres_sql_style_guide.md
**Read this for:** Writing SQL code, query optimization, code style  
**Summary:** SQL coding standards, formatting conventions, naming patterns, query best practices for PostgreSQL.  
**Location:** `.clinefiles/supabase/database/postgres_sql_style_guide.md`

### database/realtime_guide.md
**Read this for:** Comprehensive realtime setup, choosing between postgres_changes vs broadcast  
**Summary:** Complete guide to Supabase Realtime options, when to use each approach, setup patterns for real-time data sync.  
**Location:** `.clinefiles/supabase/database/realtime_guide.md`

### database/realtime-broadcast-setup.md
**Read this for:** Server-side realtime broadcast triggers, production realtime, database triggers  
**Summary:** Database-side configuration for broadcast channels, trigger functions, RLS policies for realtime.messages, topic patterns.  
**Location:** `.clinefiles/supabase/database/realtime-broadcast-setup.md`

---

## 📁 Supabase Edge Functions

### supabase/edge_functions.md
**Read this for:** Creating edge functions, serverless functions, Deno APIs  
**Summary:** Deno-based edge function patterns, deployment, environment variables, CORS handling.  
**Location:** `.clinefiles/supabase/edge_functions.md`

---

## 📁 UI & Components

### ui/ui.md
**Read this for:** General UI patterns, component structure, design principles  
**Summary:** Overall UI architecture patterns, component organization, styling approaches.  
**Location:** `.clinefiles/ui/ui.md`

### ui/shadcn-components.md
**Read this for:** Installing shadcn/ui components, component reference  
**Summary:** Complete catalog of shadcn/ui components with installation commands, links to documentation, organized by category (forms, layout, navigation, etc).  
**Location:** `.clinefiles/ui/shadcn-components.md`

### ui/shadcn-blocks.md
**Read this for:** Pre-built UI blocks, page templates, component compositions  
**Summary:** Ready-to-use shadcn blocks for common UI patterns (authentication forms, dashboards, etc).  
**Location:** `.clinefiles/ui/shadcn-blocks.md`

### ui/supabase-blocks.md
**Read this for:** Supabase-specific UI components, authentication UI, data tables  
**Summary:** Pre-built blocks specifically designed for Supabase integration.  
**Location:** `.clinefiles/ui/supabase-blocks.md`

### ui/realtime-nextjs.md
**Read this for:** Client-side realtime implementation, WebSocket setup, React hooks for realtime  
**Summary:** Client-side patterns for Supabase Realtime in Next.js. Critical JWT authentication requirements, React implementation patterns, troubleshooting WebSocket connections.  
**Location:** `.clinefiles/ui/realtime-nextjs.md`

### ui/reactflow-patterns.md
**Read this for:** Creating diagrams, node graphs, flowcharts, visual networks  
**Summary:** React Flow patterns for building interactive node-based diagrams and visualizations.  
**Location:** `.clinefiles/ui/reactflow-patterns.md`

### ui/drawer-chat-pattern.md
**Read this for:** Implementing collapsible chat drawers, chat UI components  
**Summary:** **Recommended default pattern for agent chat interfaces**. Complete guide to drawer-based chat UI using shadcn Sheet. Covers component architecture, design principles, state management, mobile responsiveness, and integration patterns. Use this for any agent chat interface unless chat is the primary/sole application interface.  
**Location:** `.clinefiles/ui/drawer-chat-pattern.md`

---



## 🎯 Common Task Scenarios

### "Create authentication for the app"
**Read these guides:**
1. `supabase/auth-for-nextjs.md` - SSR setup (CRITICAL - read first)
2. `ui/supabase-blocks.md` - Pre-built auth UI
3. `database/create_rls_policies.md` - Secure data access

### "Add a new database table"
**Read these guides:**
1. `database/create_migrations.md` - Migration creation
2. `database/declarative_schema.md` - Schema design
3. `database/create_rls_policies.md` - Security policies
4. `database/postgres_sql_style_guide.md` - SQL style

### "Implement real-time updates"
**Read these guides:**
1. `database/realtime_guide.md` - Choose approach (read first)
2. `ui/realtime-nextjs.md` - Client-side setup
3. `database/realtime-broadcast-setup.md` - If using broadcast (production)

### "Build a new UI component"
**Read these guides:**
1. `ui/shadcn-components.md` - Available components
2. `ui/shadcn-blocks.md` - Pre-built patterns
3. `ui/ui.md` - General UI patterns

### "Implement agent chat interface"
**Read these guides:**
1. `ui/drawer-chat-pattern.md` - Recommended drawer UI pattern (read first)
2. `langchain/langsmith/next-js-integration/core.md` - useStream() hook basics
3. `langchain/langsmith/next-js-integration/streaming.md` - Streaming responses
4. `langchain/langsmith/next-js-integration/threads.md` - Thread management
5. `langchain/patterns/multi-thread-actor.md` - If using multi-context actors

### "Building actor/entity-based agent system"
**Read these guides:**
1. `langchain/patterns/multi-thread-actor.md` - Multi-thread management (read first)
2. `ui/drawer-chat-pattern.md` - Drawer UI for entity selection
3. `langchain/core/short-term-memory.md` - Thread-level state
4. `langchain/core/long-term-memory.md` - Cross-thread persistent memory
5. `langchain/langsmith/local-development.md` - Testing with langgraph dev

### "Create a server function"
**Read these guides:**
1. `supabase/edge_functions.md` - Edge function patterns
2. `database/create_functions.md` - If database function needed

### "Adding a new feature to existing app"
**Read these guides:**
1. `workflows/new-feature.md` - Feature workflow overview (start here)
2. `workflows/new-feature-phases/phase-0-feature-discovery.md` - Planning and requirements gathering
3. Then follow only the relevant phase guides based on feature type
4. `workflows/new-feature-phases/phase-5-documentation-update.md` - Always required for documentation

### "Adding memory to my agent"
**Read these guides:**
1. `langchain/core/short-term-memory.md` - Thread-level conversation history
2. `langchain/core/long-term-memory.md` - Cross-thread persistent storage
3. `langchain/langsmith/local-development.md` - Setup `langgraph dev` for testing
4. `langchain/langsmith/long-term-memory.md` - Configure semantic search (if needed)

**Key principle:** LangSmith handles all checkpointers and stores automatically. You only need thread_id for persistence.

### "Building a LangChain agent"
**Read these guides:**
1. `langchain/core/agents.md` - Agent creation basics
2. `langchain/core/tools.md` - Custom tool creation
3. `langchain/core/context-engineering.md` - Optimizing agent reliability (critical)
4. `langchain/langsmith/local-development.md` - Local testing with `langgraph dev`
5. `langchain/core/middleware.md` - Advanced request/response processing (if needed)

### "Creating custom tools for agents"
**Read these guides:**
1. `langchain/core/tools.md` - Tool creation fundamentals
2. `langchain/core/runtime.md` - Accessing state/context in tools
3. `langchain/patterns/middleware-tools.md` - Production organization pattern
4. `langchain/core/short-term-memory.md` - Reading/writing agent state from tools
5. `langchain/core/long-term-memory.md` - Reading/writing persistent data from tools

### "Organizing agent code structure"
**Read these guides:**
1. `langchain/patterns/agent-folder-organization.md` - Standard folder structure (read first)
2. `langchain/patterns/middleware-centric.md` - Middleware composition patterns
3. `langchain/reference-implementations/` - Working code examples

**Key principles:** Separate core identity from tool guidance. Use {tools_list} placeholder. Follow manager vs worker patterns.

---

## ⚠️ Critical Reading Required

These guides contain **breaking patterns** that will cause failures if not followed:

1. **`supabase/auth-for-nextjs.md`** - Contains deprecated patterns that WILL BREAK auth
2. **`ui/realtime-nextjs.md`** - JWT authentication requirements that cause WebSocket failures
3. **`database/create_migrations.md`** - Naming conventions that affect migration order
4. **`langchain/core/context-engineering.md`** - Context is #1 factor in agent reliability
5. **`langchain/core/short-term-memory.md`** - LangSmith handles checkpointers - NEVER instantiate manually
6. **`langchain/core/long-term-memory.md`** - LangSmith handles stores - NEVER instantiate manually

---

## 📝 Notes for AI Assistants

- **ALWAYS read guides before implementing** - Don't rely on general knowledge
- **Guides contain project-specific patterns** - May differ from standard practices
- **Multiple guides often apply** - E.g., realtime requires both database and UI guides
- **Workflows are separate** - User manages workflow phases independently
- **When in doubt, read the guide** - Better to over-read than miss critical details
- **Use `uv add package-name`** - NOT `pip install` or `uv pip install`

---

## 🎯 Workflow Phases

### "Following the get-started workflow"
**Read these guides in sequence:**
1. `.clinefiles/workflows/get-started.md` - Master workflow anchor (start here)
2. `.clinefiles/workflows/get-started-phases/phase-0-discovery.md` - Application discovery
3. `.clinefiles/workflows/get-started-phases/phase-1-supabase-setup.md` - Database setup
4. `.clinefiles/workflows/get-started-phases/phase-2-nextjs-setup.md` - Frontend setup
5. `.clinefiles/workflows/get-started-phases/phase-3-marketing-and-ui.md` - UI foundation
6. `.clinefiles/workflows/get-started-phases/phase-4-crud-implementation.md` - CRUD operations
7. `.clinefiles/workflows/get-started-phases/phase-5-user-management.md` - User management
8. `.clinefiles/workflows/get-started-phases/phase-6-advanced-features.md` - Advanced features
9. `.clinefiles/workflows/get-started-phases/phase-7-polish-and-docs.md` - Polish & documentation
10. `.clinefiles/workflows/get-started-phases/phase-8-agentic-ai-service.md` - Agent service setup (conditional - if Phase 0 indicated agents needed)
11. `.clinefiles/workflows/get-started-phases/phase-9-system-review.md` - Final system review & integration validation


### "Following the new-feature workflow"
**Read these guides in sequence:**
1. `.clinefiles/workflows/new-feature.md` - Feature development workflow anchor (start here)
2. `.clinefiles/workflows/new-feature-phases/phase-0-feature-discovery.md` - Feature planning & requirements
3. `.clinefiles/workflows/new-feature-phases/phase-1-database-updates.md` - Database schema changes (if needed)
4. `.clinefiles/workflows/new-feature-phases/phase-2-frontend-implementation.md` - Next.js UI implementation (if needed)
5. `.clinefiles/workflows/new-feature-phases/phase-3-agent-integration.md` - AI agent capabilities (if needed)
6. `.clinefiles/workflows/new-feature-phases/phase-4-integration-testing.md` - End-to-end testing (if multiple services)
7. `.clinefiles/workflows/new-feature-phases/phase-5-documentation-update.md` - Documentation updates (always required)

**Note:** Unlike get-started, new-feature workflow is **non-linear**. Execute only phases relevant to your feature type.

### "Conducting final system review"
**Read this guide:**
- `.clinefiles/workflows/get-started-phases/phase-9-system-review.md` - Comprehensive system validation, integration point checking, documentation generation, and preparation for future development

---

## 🔄 Guide Updates

This index reflects the current state of .clinerules. If you notice a guide is missing or outdated, inform the user.

**Last Updated:** 2025-01-19  
**Recent Additions:** 
- **Multi-Thread Actor Pattern** - Complete pattern for actor/entity-based multi-context agent systems
- **Drawer Chat Pattern** - New recommended default UI pattern for agent interfaces
- **Phase 8.4 Documentation Update** - Updated to recommend drawer pattern as default
- **LangChain Documentation Section** - Complete LangChain/LangGraph guide catalog with LangSmith deployment patterns
- **LangSmith Memory Infrastructure** - Critical updates: LangSmith handles ALL checkpointers and stores automatically
- **Middleware-Centric Tools Pattern** - Production pattern for organizing custom tools in middleware
- **New-Feature Workflow** - Complete feature development workflow for adding capabilities to existing apps
- LangChain Patterns (middleware-tools, custom-subagents, multi-thread-actor)
- Phase 9: System Review & Integration Validation (complete workflow validation)
