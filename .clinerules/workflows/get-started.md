# Get Started - New Project Setup Workflow

⚠️ **IMPORTANT: ALL PHASES ARE MANDATORY**

This comprehensive workflow guides you through building a production-ready AI-native application from scratch. Every phase, section, and feature must be fully implemented. No shortcuts, no skipping sections.

---

## 🎯 Workflow Execution Requirements

### 1. Phase Completion is Mandatory and Sequential

**All phases must be completed in order. No phase may be skipped.**

Each phase has:
- **Purpose** - What this phase accomplishes
- **Prerequisites** - What must be complete before starting
- **Key Steps** - Major tasks within the phase
- **Completion Checklist** - Verifiable items that must be checked off
- **Verification** - How to confirm phase is complete

**You CANNOT proceed to the next phase until the current phase completion checklist is 100% verified.**

### 2. Workflow Execution Pattern: Anchor → Phase → Anchor

The workflow follows this pattern for each phase:

1. **Start at Anchor (this file)** - Review phase overview and requirements
2. **Go to Phase File** - Follow detailed step-by-step instructions
3. **Complete Phase Work** - Execute all steps in the phase file
4. **Return to Anchor** - Report completion and verify checklist
5. **Proceed to Next Phase** - Only after verification is complete

**Example Flow:**
```
get-started.md (Read Phase 1 overview)
    ↓
phase-1-supabase-setup.md (Execute steps 1-8)
    ↓
get-started.md (Mark Phase 1 checklist ✓, verify)
    ↓
get-started.md (Read Phase 2 overview)
    ↓
phase-2-nextjs-setup.md (Execute steps)
    ↓
... and so on
```

### 3. Phase Completion Reporting

After completing each phase, return to this file and:

**A. Mark the phase checklist items as complete ✓**

Update the relevant section in "MANDATORY COMPLETION CHECKLIST" below.

**B. Update WORKFLOW_CHECKPOINT.md**

Document what was completed:
```markdown
# WORKFLOW_CHECKPOINT.md

## ✅ Completed Phases
- ✅ Phase 0: Application Discovery
  - Requirements documented in PROJECT_REQUIREMENTS.md
  - 5 entities identified and classified
  - 7 MVP features defined
  
- ✅ Phase 1: Supabase Setup
  - All 5 entity tables created with migrations
  - RLS policies on all tables verified
  - Per-user seed data function working
  - Database verified in Supabase Studio

## 🔄 Current Phase
- Phase 2: Next.js Setup
  - Environment variables configured
  - In progress: Fixing Supabase clients

## 📊 Overall Progress
- 2/7 phases complete (29%)
- Estimated time: 3 hours completed, 8 hours remaining

## 🔑 Key Decisions Made
- Application: Task Management Platform
- Database: 5 primary entities, 2 junction tables
- Landing style: Minimalist SaaS
- ReactFlow: Not needed for MVP

## 📁 Key Files Created
- supabase/migrations/: 7 migration files
- PROJECT_REQUIREMENTS.md: Complete spec
- DATABASE_SCHEMA.md: Schema documentation

## ⚠️ Issues Encountered & Resolved
- Variable type mismatch in seed function - fixed by using bigint
- RLS policy syntax - corrected with separate policies per operation

## ➡️ Next Steps
1. Complete Phase 2: Fix all Supabase client files
2. Verify authentication works
3. Proceed to Phase 3: Marketing & UI
```

**C. Verify Against Phase Requirements**

Before moving to the next phase, explicitly verify:
- [ ] All steps in the phase file were completed
- [ ] All phase-specific checklist items are marked ✓
- [ ] Any issues encountered were documented and resolved
- [ ] Phase verification steps passed successfully

### 4. Context Window Management

As the context window fills up (>40-50% usage):

**Condense and summarize:**
- Keep WORKFLOW_CHECKPOINT.md as the single source of truth
- Condense completed phase details into brief summaries
- Focus on key decisions, files created, and issues resolved
- Remove verbose implementation details once phase is verified

**When context exceeds 60%:**
- Create condensed summary in WORKFLOW_CHECKPOINT.md
- List only: completed phases, current phase, next steps
- Reference original workflow files for details rather than repeating them

### 5. Quality Standards (All Phases)

Maintain these standards throughout development:
- ✅ All environment variables correct and documented
- ✅ RLS policies on every database table
- ✅ Proper error handling with user feedback
- ✅ Loading states on all async operations
- ✅ Toast notifications on all user actions
- ✅ TypeScript strict mode throughout
- ✅ Consistent naming conventions
- ✅ No placeholder or TODO comments in production code

### 6. Completion Criteria Requirements

**Each phase completion checklist item must be:**
- **Specific** - Not vague or ambiguous
- **Verifiable** - Can be tested and confirmed
- **Documented** - Evidence exists (code, screenshots, tests)
- **Functional** - Actually works, not just exists

**Example of proper verification:**
- ❌ BAD: "Seed data created" (too vague)
- ✅ GOOD: "Per-user seed data function creates 3 scenarios and 5 actors for each new user, verified by signing up test user and checking dashboard displays seed data"

### 7. Critical: Reference PROJECT_REQUIREMENTS.md Throughout

Throughout all phases, continuously cross-reference PROJECT_REQUIREMENTS.md:
- **Phase 0:** Create it with complete entity classification
- **Phase 1:** Use it to create all database tables
- **Phase 4:** Verify CRUD exists for appropriate entity types
- **Phase 7:** Confirm all documented features are implemented

**Before marking workflow complete:**
- [ ] Count entities in PROJECT_REQUIREMENTS.md
- [ ] Verify implementation matches requirements exactly
- [ ] Confirm all entity classifications have appropriate UI
- [ ] Validate all documented features are functional

---

## 📚 Tech Stack

- **Supabase** - Database, authentication, storage
- **Next.js 16** - React framework with TypeScript and Tailwind CSS v3.4.18
- **LangChain/LangSmith** - Agentic AI services and deployment platform
- **UI Libraries** - shadcn/ui blocks and components
- **React Flow** - Node-based visualizations (when applicable)
- **Local Development** - Supabase CLI, Docker Compose, LangGraph dev server

---

## 📋 Workflow Phases

### Phase 0: Application Discovery [MANDATORY]
**📄 [Full Guide: phase-0-discovery.md](.clinefiles/workflows/get-started-phases/phase-0-discovery.md)**

**Purpose:** Gather requirements and define the application scope for an agentic-first application

**Key Steps:**
- Determine application type and purpose
- Define landing page style and content
- Identify core data models (minimum 3 entities)
- Classify all entities by category (Primary, Junction, System-Generated, Configuration)
- List primary MVP features (minimum 5)
- **MANDATORY: Comprehensive agentic AI assessment** (architecture, middleware, tools, memory, streaming, RAG)
- Assess ReactFlow/advanced feature needs

**Critical Decisions Made in Phase 0:**

All applications are agentic-first. Phase 0 defines the intelligence layer:

- **Agent architecture** (Supervisor/Simple/Hybrid) - drives Phase 8 implementation
- **Middleware stack** - what capabilities agents will have (tools, prompts, state)
- **Tool design** - what domain-specific actions agents can perform
- **Memory strategy** - short-term (threads) and long-term (store) requirements
- **Streaming approach** - real-time vs batch processing
- **LangSmith features** - HITL, background runs, cron jobs, RAG, multiple assistants

**Cannot proceed without completing discovery. Phase 0 decisions directly drive Phase 8 implementation.**

---

### Phase 1: Supabase Local Setup [MANDATORY]
**📄 [Full Guide: phase-1-supabase-setup.md](.clinefiles/workflows/get-started-phases/phase-1-supabase-setup.md)**

**References:** 
- `.clinefiles/supabase/database/create_migrations.md`
- `.clinefiles/supabase/database/create_rls_policies.md`
- `.clinefiles/supabase/database/postgres_sql_style_guide.md`

**Purpose:** Complete database setup with all entities, security, and seed data

**Key Steps:**
- Initialize and start Supabase
- Create migrations for ALL entities
- Add RLS policies to ALL tables
- Create seed data for ALL entities
- Verify in Supabase Studio

**Cannot proceed without complete, working database.**

---

### Phase 2: Next.js Application Setup [MANDATORY]
**📄 [Full Guide: phase-2-nextjs-setup.md](.clinefiles/workflows/get-started-phases/phase-2-nextjs-setup.md)**

**References:** 
- `.clinefiles/ui/ui.md`
- `.clinefiles/langchain/langsmith/next-js-integration/` (awareness only, implemented in Phase 8)

**Purpose:** Set up Next.js application with all critical fixes and prepare for agentic AI integration

**Key Steps:**
- Create app with Supabase template
- Fix environment variables (ANON_KEY)
- Fix all Supabase client files
- Fix routing and navigation
- Verify authentication works
- **Add placeholder for agent API URL** (`NEXT_PUBLIC_AGENT_API_URL` in `.env.local`)

**Agent Integration Awareness:**

All apps are agentic-first. While the agent service is built in Phase 8, prepare the Next.js architecture now:

**Built-in Next.js 16 Support:**
- Native Server-Sent Events (SSE) for streaming
- Async React Server Components
- Streaming responses out-of-the-box
- No additional configuration needed

**LangSmith Integration Features (Implemented in Phase 8):**

Review `.clinefiles/langchain/langsmith/next-js-integration/` to understand what's coming:
- **Streaming** - `useStream()` hook for token-by-token responses
- **Threads** - URL-based thread persistence for conversation history  
- **Human-in-the-Loop** - Approval workflows with interrupt/resume patterns
- **Background Runs** - Long-running agent tasks
- **Cron Jobs** - Scheduled agent executions
- **Assistants** - Multiple agent types per application

**Environment Variable Setup:**

Add to `.env.local` (placeholder for now, configured in Phase 8):
```bash
# Agent Service (to be configured in Phase 8)
NEXT_PUBLIC_AGENT_API_URL=http://localhost:2024
```

This prepares the app architecture for seamless Phase 8 integration.

**Cannot proceed without verified working application.**

---

### Phase 3: Marketing & UI Foundation [MANDATORY]
**📄 [Full Guide: phase-3-marketing-and-ui.md](.clinefiles/workflows/get-started-phases/phase-3-marketing-and-ui.md)**

**References:** 
- `.clinefiles/ui/ui.md`
- `.clinefiles/ui/shadcn-blocks.md`
- `.clinefiles/ui/shadcn-components.md`

**Purpose:** Build complete UI foundation including landing page and dashboard

**Sub-Phases:**
- **3.0: Marketing/Landing Page [MANDATORY]** - Hero, features, pricing, CTAs
- **3.1: Dashboard Installation [MANDATORY]** - Sidebar navigation layout
- **3.2: Core UI Components [MANDATORY]** - Forms, cards, dialogs, etc.
- **3.3: Navigation Complete [MANDATORY]** - All menu items have working pages

**Agent UI Considerations (If Phase 0 Identified Agents):**
- If Phase 0 included agentic capabilities, consider agent interaction patterns:
  - Chat interface components (message bubbles, input areas)
  - Streaming text display components (for real-time responses)
  - Loading/thinking indicators for agent processing
  - Components will be implemented in Phase 8, but UI foundation prepared here

**Cannot proceed until ALL UI is in place and ALL menu items work.**

---

### Phase 4: CRUD Implementation [MANDATORY]
**📄 [Full Guide: phase-4-crud-implementation.md](.clinefiles/workflows/get-started-phases/phase-4-crud-implementation.md)**

**References:** 
- `.clinefiles/ui/shadcn-blocks.md`
- `.clinefiles/supabase/database/create_rls_policies.md`

**Purpose:** Implement complete CRUD operations for ALL entities with seed data display

**Key Areas:**
- **Display Seed Data [MANDATORY]** - Show existing data in tables/cards
- **Create Operations [MANDATORY]** - Working forms for all entities
- **Read Operations [MANDATORY]** - Detail pages for all entities
- **Update Operations [MANDATORY]** - Edit forms for all entities
- **Delete Operations [MANDATORY]** - Safe deletion with confirmations

**Cannot proceed until full CRUD works for ALL entities and seed data is visible.**

---

### Phase 5: User Management [MANDATORY]
**📄 [Full Guide: phase-5-user-management.md](.clinefiles/workflows/get-started-phases/phase-5-user-management.md)**

**References:** 
- `.clinefiles/ui/supabase-blocks.md`
- `.clinefiles/supabase/auth-for-nextjs.md`

**Purpose:** Implement complete user management functionality

**Key Features:**
- **User Profile [MANDATORY]** - View and edit profile pages
- **Account Settings [MANDATORY]** - Email, password, preferences
- **Logout Functionality [MANDATORY]** - Working logout with session cleanup
- **User Preferences [MANDATORY]** - Settings persistence

**Cannot proceed without complete user management.**

---

### Phase 6: Advanced Features [MANDATORY]
**📄 [Full Guide: phase-6-advanced-features.md](.clinefiles/workflows/get-started-phases/phase-6-advanced-features.md)**

**References:** 
- `.clinefiles/ui/reactflow-patterns.md`
- `.clinefiles/supabase/database/realtime_guide.md`
- `.clinefiles/ui/realtime-nextjs.md` (Client-side implementation patterns, critical JWT auth)
- `.clinefiles/supabase/database/realtime-broadcast-setup.md` (Server-side triggers and RLS)
- `.clinefiles/stripe/stripe-integration.md` (Complete Stripe billing integration)

**Purpose:** Implement advanced features based on application needs

**Key Features:**
- **ReactFlow Integration [IF APPLICABLE - MANDATORY]** - Node-based visualizations
- **Real-time Features [IF APPLICABLE]** - Live updates and collaboration
- **File Uploads [IF APPLICABLE]** - Document/image handling
- **Analytics [IF APPLICABLE]** - Charts and dashboards
- **Stripe Billing [IF APPLICABLE]** - Subscription payments and feature gating

**All applicable features must be fully implemented.**

---

### Phase 7: Polish & Documentation [MANDATORY]
**📄 [Full Guide: phase-7-polish-and-docs.md](.clinefiles/workflows/get-started-phases/phase-7-polish-and-docs.md)**

**References:** 
- `.clinefiles/ui/shadcn-components.md`

**Purpose:** Polish the application and create comprehensive documentation

**Key Areas:**
- **Polish [MANDATORY]** - Loading states, empty states, error handling
- **Theme [MANDATORY]** - Customization and branding
- **Documentation [MANDATORY]** - Comprehensive README.md

**Cannot mark workflow complete without comprehensive documentation.**

---

### Phase 8: Agentic AI Service [MANDATORY]
**📄 [Full Guide: phase-8-agentic-ai-service.md](.clinefiles/workflows/get-started-phases/phase-8-agentic-ai-service.md)**

**Purpose:** Set up LangChain/LangGraph agent service with production patterns using LangGraph dev server

**Time Estimate:** 2-3 hours (split across 5 sub-phases)

**Philosophy:** All applications built with this workflow are **agentic-first** and **generative-first**. The agent service is not an add-on feature—it's a core architectural component that defines how users interact with your application's intelligence layer.

**Sub-Phases:**
- **[8.1: Agent Setup](.clinefiles/workflows/get-started-phases/phase-8-1-agent-setup.md)** - Directory structure with middleware/, models/, tools/, prompts/ (15-20 min)
- **[8.2: Agent Implementation](.clinefiles/workflows/get-started-phases/phase-8-2-agent-implementation.md)** - Middleware-first architecture, tools with prompt additions (30-40 min)
- **[8.3: LangSmith Features](.clinefiles/workflows/get-started-phases/phase-8-3-langsmith-features.md)** - Memory, threads, HITL, background runs (20-30 min)
- **[8.4: Next.js Integration](.clinefiles/workflows/get-started-phases/phase-8-4-nextjs-integration.md)** - Client SDK, streaming, agent hooks (25-35 min)
- **[8.5: Testing & Documentation](.clinefiles/workflows/get-started-phases/phase-8-5-testing-docs.md)** - Testing, troubleshooting, docs (20-25 min)

**Key References:**
- `.clinefiles/langchain/core/` - All core concepts (agents, tools, middleware, memory, streaming)
- `.clinefiles/langchain/patterns/` - Production patterns (middleware-centric, custom subagents)
- `.clinefiles/langchain/langsmith/` - Deployment and local development with langgraph dev
- `.clinefiles/langchain/langsmith/next-js-integration/` - Complete Next.js integration patterns

**Critical Requirements:**
- Memory infrastructure is AUTOMATIC via LangSmith (never manually configure PostgresSaver/PostgresStore)
- Use `uv add` for all Python dependencies (NOT pip or uv pip install)
- Reference ONLY patterns from `.clinefiles/langchain/` docs
- Streaming and async are defaults, not opt-in features
- **Middleware-first architecture:** Every tool comes with prompt additions and optional state modifications

**Cannot mark workflow complete without agentic AI service integration.**

---

### Phase 9: System Review & Integration Validation [MANDATORY]
**📄 [Full Guide: phase-9-system-review.md](.clinefiles/workflows/get-started-phases/phase-9-system-review.md)**

**Purpose:** Comprehensive review of all work, validation of integration points, and creation of developer reference documentation

**Key Steps:**
- Validate all integration points (Next.js ↔ Supabase ↔ Agent Service)
- Verify feature completeness against PROJECT_REQUIREMENTS.md
- Generate comprehensive SYSTEM_REFERENCE.md documentation
- Create INTEGRATION_CHECKLIST.md with validation results
- Test end-to-end user workflows
- Document common development patterns
- Identify and fix any gaps or issues

**This is the FINAL validation checkpoint before declaring workflow complete.**

---

## ✅ MANDATORY COMPLETION CHECKLIST

**Instructions:** After completing each phase, return to this file and mark items ✓. Each item must be specifically verified before proceeding.

### Phase 0: Discovery ✓
- [ ] PROJECT_REQUIREMENTS.md created with all sections complete
- [ ] Minimum 3 core entities identified and classified by category
- [ ] Each entity has fields, relationships, and category documented
- [ ] Minimum 5 MVP features defined with user value statements
- [ ] Landing page style chosen with specific reference examples
- [ ] ReactFlow need determined (YES/NO) with clear rationale

**Verification:** PROJECT_REQUIREMENTS.md exists and contains complete entity classification and feature definitions.

---

### Phase 1: Supabase ✓
- [ ] `supabase start` runs successfully, API URL and anon key saved
- [ ] Migration file exists for profiles table with RLS and trigger
- [ ] Migration file exists for each entity (count matches Phase 0)
- [ ] Each entity table has RLS enabled with all 4 policies (select, insert, update, delete)
- [ ] Per-user seed data function created and tested with new user signup
- [ ] New test user signup creates seed data visible in dashboard
- [ ] Supabase Studio shows all tables with correct schemas
- [ ] User isolation verified (2 test users can't see each other's data)

**Verification:** Run `supabase db reset` without errors, sign up new user, see seed data in UI immediately.

---

### Phase 2: Next.js ✓
- [ ] Next.js app created using Supabase template command
- [ ] `.env.local` has NEXT_PUBLIC_SUPABASE_ANON_KEY (not PUBLISHABLE_KEY)
- [ ] `.env.local` has NEXT_PUBLIC_AGENT_API_URL=http://localhost:2024 (placeholder for Phase 8)
- [ ] All three Supabase client files (client.ts, server.ts, middleware.ts) use correct env vars
- [ ] Test user can sign up successfully without database errors
- [ ] After signup, user is redirected to dashboard (not error page)
- [ ] Dashboard route (/dashboard) loads without 404 error
- [ ] All navigation links in sidebar are functional (no console errors)

**Verification:** Sign up new user, confirm redirect to dashboard, click all sidebar links to verify they work.

---

### Phase 3: Marketing & UI ✓
- [ ] Landing page (/) has hero section with headline, subheadline, and CTA
- [ ] Landing page has features section with at least 3 feature cards
- [ ] Landing page has pricing section (if applicable) or additional CTA
- [ ] Landing page has final CTA section
- [ ] Dashboard layout uses shadcn sidebar block with `collapsible="icon"`
- [ ] Sidebar shows all planned menu items from Phase 0 requirements
- [ ] Each menu item in sidebar links to a working page (no 404s)
- [ ] All core UI components needed for forms installed (Button, Input, Form, Textarea, etc.)

**Verification:** Visit landing page and verify all sections present. Click every sidebar menu item to confirm no 404 errors.

---

### Phase 4: CRUD ✓

**For Primary Entities (Full CRUD):**
- [ ] List page for each primary entity shows seed data in table/cards (not empty state)
- [ ] Create page for each primary entity has working form with validation
- [ ] Detail page for each primary entity displays all fields
- [ ] Edit page for each primary entity pre-populates form and saves changes
- [ ] Delete button on each detail page shows confirmation dialog and deletes record
- [ ] All relationship data displayed (no raw IDs, related entity names shown)
- [ ] Related entities are clickable links that navigate to those entities

**For Junction Tables (Association Management):**
- [ ] Junction tables managed in parent entity forms (multi-select or add/remove UI)
- [ ] Both sides of many-to-many relationships display associated entities
- [ ] Can add and remove associations through parent entity UI

**For System-Generated Data:**
- [ ] System-generated tables have read-only displays where appropriate
- [ ] Optional clear/delete functionality implemented where needed
- [ ] No create or edit forms for system-generated tables

**Cross-Reference:**
- [ ] Counted all entities in PROJECT_REQUIREMENTS.md
- [ ] Verified appropriate UI exists for each entity category
- [ ] All relationship data displays correctly (one-to-many and many-to-many)

**Verification:** Test full CRUD cycle for each primary entity. Verify all relationship data displays entity names, not IDs.

---

### Phase 5: User Management ✓
- [ ] Profile page (/dashboard/profile) displays current user information
- [ ] Profile page has edit form that updates user profile successfully
- [ ] Settings page (/dashboard/settings) exists with configuration options
- [ ] Password change functionality works (test with password update)
- [ ] Logout button in sidebar/nav menu logs user out completely
- [ ] After logout, user redirected to home page (not dashboard)
- [ ] User preferences saved to database and persist across sessions
- [ ] Avatar upload works (if applicable to your app)

**Verification:** Edit profile, change password, logout, login, verify changes persisted.

---

### Phase 6: Advanced Features ✓

**For Apps Requiring ReactFlow:**
- [ ] ReactFlow component created and displays nodes correctly
- [ ] User can interact with nodes (drag, connect, select)
- [ ] Visual state saves to database
- [ ] Node-based UI serves its intended purpose from requirements

**For Apps with Real-time Features:**
- [ ] Supabase Realtime configured and subscriptions working
- [ ] Live updates appear without page refresh
- [ ] Multiple users can collaborate in real-time

**For Apps with File Uploads:**
- [ ] Supabase Storage bucket created with RLS policies
- [ ] File upload UI implemented and functional
- [ ] Uploaded files display in UI correctly

**For Apps with Analytics:**
- [ ] Analytics dashboard displays relevant metrics
- [ ] Charts and visualizations render correctly
- [ ] Data filtering and date range selection works

**For Apps with Stripe Billing:**
- [ ] Stripe account created and test keys obtained
- [ ] Products and prices created in Stripe Dashboard
- [ ] Environment variables configured (test mode)
- [ ] Database migration added stripe columns to profiles
- [ ] Stripe SDK installed (stripe, @stripe/stripe-js)
- [ ] Checkout Session API route created and working
- [ ] Webhook handler created and signature verification working
- [ ] Webhook endpoint configured in Stripe Dashboard
- [ ] Customer Portal API route created
- [ ] Billing page created with plan display and upgrade buttons
- [ ] Subscribe buttons redirect to Stripe Checkout successfully
- [ ] Manage Billing button opens Customer Portal
- [ ] Feature gating implemented (requirePlan function)
- [ ] Test payment flow completed with test card successfully
- [ ] Webhook updates user plan in database after payment
- [ ] Plan display updates in UI after subscription change

**Verification:** Test each applicable advanced feature according to Phase 0 requirements.

---

### Phase 7: Polish & Docs ✓
- [ ] Loading states visible on all async operations (forms, page loads, data fetching)
- [ ] Empty states show helpful messages on all list views when no data exists
- [ ] Error handling displays user-friendly messages (not raw errors)
- [ ] Toast notifications configured globally and appear on all CRUD operations
- [ ] Theme switcher works (if implemented) and persists user preference
- [ ] README.md documents: setup, features, tech stack, and how to run locally
- [ ] README.md includes: database schema overview and seed data information

**Verification:** Review every page for loading states, test error scenarios, confirm README is comprehensive.

---

### Phase 8: Agentic AI Service ✓

**Phase 8.1: Agent Setup**
- [ ] Agent service directory created with proper folder structure: `middleware/`, `models/`, `tools/`, `prompts/`
- [ ] Python 3.11+ verified with `python --version`
- [ ] Project initialized with `uv init` in agent directory
- [ ] Dependencies installed via `uv add` (langchain-core, langchain, langgraph, langchain-openai, langchain-anthropic, deepagents, langgraph-cli[inmem])
- [ ] `langgraph.json` created with correct configuration
- [ ] `langgraph dev` starts successfully and shows "Ready!" on port 2024
- [ ] LangGraph Studio accessible at http://localhost:2024

**Phase 8.2: Agent Implementation**
- [ ] Agent pattern selected (simple vs supervisor) based on Phase 0 decisions
- [ ] Core agent file created with proper imports from `.clinefiles/langchain/` patterns
- [ ] Middleware functions organized in `middleware/` folder
- [ ] Each middleware function adds tools with accompanying prompt additions
- [ ] Agent state models defined in `models/` folder (agent state, context, structured output schemas)
- [ ] Custom tools organized in `tools/` folder with InjectedState for runtime access
- [ ] Each tool includes system prompt addition explaining tool purpose and usage
- [ ] Base system prompt in `prompts/` folder
- [ ] Streaming configured (model initialization with streaming=True by default)
- [ ] Agent tested in LangGraph Studio with sample inputs

**Tavily Integration (If Phase 0 Identified Need):**
- [ ] `langchain-tavily` package installed via `uv add` (NOT langchain_community)
- [ ] Tavily tools configured per Phase 0 specifications (search, extract)
- [ ] Web search prompts created explaining when/how to use Tavily
- [ ] Tavily tools tested with web search queries
- [ ] Content extraction tested with URL processing
- [ ] Configuration matches Phase 0 use cases (news monitoring, research, etc.)
- [ ] Credit usage optimized (basic vs advanced depth based on Phase 0)

**Phase 8.3: LangSmith Features**
- [ ] Thread management works (thread_id persistence verified)
- [ ] Memory automatic (confirmed NO manual PostgresSaver/PostgresStore configuration)
- [ ] Human-in-the-loop implemented with interrupt() if needed
- [ ] Background runs configured in langgraph.json if needed
- [ ] Cron jobs configured in langgraph.json if needed
- [ ] RAG with SupabaseVectorStore implemented if Phase 0 indicated need
- [ ] Multiple assistants configured if Phase 0 indicated multiple agent types

**Phase 8.4: Next.js Integration**
- [ ] @langchain/langgraph-sdk installed in Next.js app
- [ ] NEXT_PUBLIC_AGENT_API_URL environment variable configured
- [ ] useAgent custom hook created with useStream()
- [ ] Agent client component created with streaming UI
- [ ] Thread persistence implemented (URL-based recommended)
- [ ] Human-in-the-loop UI components implemented if needed
- [ ] End-to-end test: Next.js component → Agent → Response stream

**Phase 8.5: Testing & Documentation**
- [ ] Agent responds to simple queries via LangGraph Studio
- [ ] Streaming works (tokens appear progressively, not all at once)
- [ ] Memory persists across thread interactions
- [ ] Tools execute successfully and return expected results
- [ ] Next.js integration streams responses correctly
- [ ] README.md in agent directory documents setup and architecture
- [ ] AGENT_TROUBLESHOOTING.md created with common issues
- [ ] Deployment checklist verified (LangSmith platform preparation)

**Critical Verification:**
- [ ] Confirmed NO manual PostgresSaver or PostgresStore configuration anywhere
- [ ] All Python packages installed via `uv add` (NOT pip)
- [ ] All patterns reference ONLY `.clinefiles/langchain/` docs
- [ ] Streaming enabled by default (no opt-in required)

**Verification:** Test complete agent workflow: Next.js UI → send message → agent processes with streaming → response appears token-by-token → memory persists → tools execute correctly.

---

### Phase 9: System Review ✓
- [ ] Integration points validated (Next.js ↔ Supabase ↔ Agent Service if applicable)
- [ ] SYSTEM_REFERENCE.md generated with complete system documentation
- [ ] INTEGRATION_CHECKLIST.md created with all validation results
- [ ] End-to-end user workflows tested successfully
- [ ] All features from PROJECT_REQUIREMENTS.md implemented
- [ ] Common development patterns documented
- [ ] All gaps and issues identified and resolved

**Verification:** Complete system validation checklist in INTEGRATION_CHECKLIST.md shows 100% pass rate.

---

### Final Verification ✓

**Before declaring workflow complete, verify:**

- [ ] App runs locally with `npm run dev` without errors
- [ ] All routes in sidebar navigate successfully
- [ ] Full CRUD tested for every primary entity (create → read → update → delete)
- [ ] New user signup creates seed data automatically
- [ ] Seed data visible immediately in dashboard after signup
- [ ] User profile and settings work correctly
- [ ] Logout works and properly clears session
- [ ] Landing page loads without errors
- [ ] All forms validate and show appropriate error messages
- [ ] All relationships display entity names, not IDs
- [ ] PROJECT_REQUIREMENTS.md cross-referenced - all features implemented

**Documentation Complete:**
- [ ] README.md has: installation steps, feature list, tech stack, local dev instructions
- [ ] DATABASE_SCHEMA.md documents all tables with relationships
- [ ] WORKFLOW_CHECKPOINT.md shows completed phases with summaries



**The workflow is NOT complete until ALL items above are verified ✓**

**When 100% complete, update WORKFLOW_CHECKPOINT.md with "✅ WORKFLOW COMPLETE" status.**

---

## 🔧 Common Issues - Quick Reference

When encountering issues during development, first check the relevant phase file for detailed troubleshooting:

### Phase-Specific Issue Guides

- **Database Issues** → [Phase 1: Supabase Setup](.clinefiles/workflows/get-started-phases/phase-1-supabase-setup.md)
  - Seed data implementation
  - Variable type mismatches
  - Schema qualification errors
  - RLS permission problems
  
- **Next.js Setup Issues** → [Phase 2: Next.js Setup](.clinefiles/workflows/get-started-phases/phase-2-nextjs-setup.md)
  - Environment variable problems
  - Supabase client configuration
  - Authentication setup
  
- **UI Component Issues** → [Phase 3: Marketing & UI](.clinefiles/workflows/get-started-phases/phase-3-marketing-and-ui.md)
  - Sidebar configuration
  - Navigation link problems
  - Component installation
  - Tailwind v3 vs v4 syntax
  
- **CRUD & Form Issues** → [Phase 4: CRUD Implementation](.clinefiles/workflows/get-started-phases/phase-4-crud-implementation.md)
  - Form validation
  - Redirect path problems
  - Data fetching errors
  - Relationship display
  
- **User Management Issues** → [Phase 5: User Management](.clinefiles/workflows/get-started-phases/phase-5-user-management.md)
  - Profile management
  - Logout functionality
  - Settings persistence

### Quick Fixes (Common Across Phases)

#### Next.js 16 Dynamic Routes
All dynamic route pages must unwrap params as a Promise:
```typescript
// ✅ CORRECT for Next.js 16+
export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;  // Must unwrap Promise
  // ...
}
```

#### Environment Variables
Always use the correct variable names:
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` (not PUBLISHABLE_KEY)

#### Form Schema Alignment
Always match form fields to actual database column names:
```typescript
// Check your table schema first, then match exactly
const formSchema = z.object({
  type: z.enum(['nation', 'organization']),  // If column is 'type'
  // NOT: actor_type, entityType, etc.
});
```

**For detailed troubleshooting, always refer to the specific phase file where the issue occurs.**

---

## 🎯 Final Verification

Before using `attempt_completion`:

1. ✅ Run through entire completion checklist
2. ✅ Verify ALL features work
3. ✅ Confirm README is comprehensive
4. ✅ Test the complete user journey
5. ✅ Verify seed data is visible
6. ✅ Confirm all navigation works
7. ✅ Test all CRUD operations
8. ✅ Verify user management works
9. ✅ Confirm logout works properly
10. ✅ Test landing page loads correctly

**Only use attempt_completion when 100% complete.**

---

## 📖 Next Steps After Completion

Once the workflow is complete and verified:

1. Deploy to production:
   - Frontend: Vercel
   - Database: Supabase Cloud
   - Agent Service (if applicable): LangSmith platform
2. Set up CI/CD pipelines
3. Add monitoring and analytics
4. Implement additional features
5. Scale based on user feedback

**The foundation is solid - now build upon it!** 🚀
