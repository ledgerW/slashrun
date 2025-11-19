# Phase 0: Application Discovery [MANDATORY]

**Purpose:** Gather comprehensive requirements and define the application scope before any development begins.

**Prerequisites:** None - This is the first phase

**References:** None - This phase informs all subsequent phases

---

## Overview

Before writing any code, we must understand:
- What type of application is being built
- Who the users are and what they need
- What data models drive the application
- What the MVP feature set includes
- What advanced features might be needed

**This phase cannot be skipped. All subsequent phases depend on the decisions made here.**

---

## Step 1: Application Type and Purpose

### Questions to Ask the User

**1. What type of application are you building?**

Examples:
- Task/project management system
- E-commerce platform
- Social/community platform
- Analytics dashboard
- Content management system
- Workflow automation tool
- Educational platform
- Booking/scheduling system
- Inventory management
- Custom business tool

**2. What is the primary problem this application solves?**

- User pain points
- Business needs
- Workflow improvements
- Process automation

**3. Who are the target users?**

- Internal teams / External customers
- Technical / Non-technical users
- Individual users / Team collaboration
- B2B / B2C / B2B2C

---

## Step 2: Landing Page Requirements [MANDATORY]

The landing page is mandatory for every application. Gather these details:

### Design Style and Aesthetic

**Ask:** What style should the landing page have?

Options:
- **Minimalist SaaS** - Clean, simple, focused (like Linear, Vercel)
- **Bold and Colorful** - Vibrant, energetic, modern (like Stripe, Spotify)
- **Enterprise Professional** - Trustworthy, sophisticated (like Salesforce, IBM)
- **Creative/Artistic** - Unique, expressive (like portfolios, creative agencies)
- **Tech/Developer Focused** - Code-friendly, technical (like GitHub, VS Code)

### Example Sites to Emulate (Optional)

**Ask:** Are there any websites whose landing pages you admire?

Good references:
- linear.app - Minimalist SaaS
- stripe.com - Bold and colorful
- vercel.com - Modern developer-focused
- supabase.com - Developer-friendly
- notion.so - Clean and approachable
- raycast.com - Sleek and professional

### Landing Page Content Requirements

Gather information for each section:

**Hero Section:**
- Main headline (value proposition)
- Subheadline (supporting detail)
- Primary CTA text (e.g., "Get Started Free", "Start Building")
- Hero visual approach (screenshot, illustration, gradient, video)

**Features Section:**
- 3-6 key features to highlight
- Icon/visual for each feature
- Brief description for each

**Social Proof (if applicable):**
- Customer testimonials
- Company logos using the product
- Usage statistics (users, projects, etc.)

**Pricing (if applicable):**
- Pricing tiers (typically 3: Free, Pro, Enterprise)
- Key features for each tier
- Monthly/Annual pricing

**Final CTA:**
- Reinforcement message
- Strong call-to-action

---

## Step 3: Core Data Models [MANDATORY]

Identify the primary entities (database tables) for the MVP.

### Minimum Requirements

- **Minimum 3 entities** (plus users/profiles)
- Each entity should have clear purpose
- Relationships between entities should be defined

### Questions to Ask

**1. What are the main "things" your application manages?**

Examples by app type:
- Task manager: Projects, Tasks, Tags
- E-commerce: Products, Orders, Customers
- Social platform: Posts, Comments, Likes
- CMS: Articles, Categories, Authors
- Workflow tool: Workflows, Steps, Executions

**2. What properties does each entity have?**

For each entity, identify:
- Required fields (name, description, etc.)
- Optional fields
- Relationships to other entities
- Status/state fields
- Timestamps

**3. What are the relationships?**

- One-to-many (e.g., User has many Projects)
- Many-to-many (e.g., Posts have many Tags)
- One-to-one (e.g., User has one Profile)

### Data Model Documentation Template

```markdown
## Core Entities

### Entity 1: [Name]
**Purpose:** [What this entity represents]

**Fields:**
- id: bigint (primary key)
- user_id: uuid (references auth.users)
- name: text (required)
- description: text (optional)
- status: text (e.g., 'active', 'archived')
- created_at: timestamptz
- updated_at: timestamptz

**Relationships:**
- Belongs to: User
- Has many: [Related entities]

### Entity 2: [Name]
[Similar structure]

### Entity 3: [Name]
[Similar structure]
```

---

## Step 3.5: Classify Your Entities [MANDATORY]

After identifying all entities, classify each one to determine the appropriate UI implementation in Phase 4.

### Entity Categories

#### Category 1: Primary/Core Entities
These are the main business objects users directly create, view, edit, and delete.

**Characteristics:**
- Users initiate creation through forms
- Represent main domain concepts
- Need full CRUD interfaces

**Examples:**
- Projects, Tasks, Issues
- Products, Orders, Customers
- Scenarios, Actors
- Posts, Articles, Pages
- Workflows, Templates

**Phase 4 Implementation:** Full CRUD with list, create, view, edit, delete pages

#### Category 2: Junction/Association Tables
These connect other entities in many-to-many relationships.

**Characteristics:**
- Link two entities together
- Usually just foreign key pairs
- No meaningful data besides the relationship
- Managed through parent entity UIs

**Examples:**
- scenario_actors (scenarios ↔ actors)
- project_members (projects ↔ users)
- post_tags (posts ↔ tags)
- order_products (orders ↔ products)

**Phase 4 Implementation:** Managed in parent forms (multi-select, add/remove buttons)

#### Category 3: System-Generated Data
These records are created automatically by the application, not through user forms.

**Characteristics:**
- Created during app processes (simulations, workflows, etc.)
- Users can view and possibly delete
- Should not have create/edit forms
- Often timestamped event logs

**Examples:**
- actor_messages (created during simulation)
- audit_logs (created on entity changes)
- notifications (created by system events)
- workflow_executions (created when workflows run)
- activity_feed (created from user actions)

**Phase 4 Implementation:** Read-only displays with optional delete/clear functionality

#### Category 4: Configuration/Reference Data
Lookup tables, settings, or metadata that rarely changes.

**Characteristics:**
- Limited set of options
- Admin-managed or seed data
- Used as dropdowns/selectors in other forms
- Infrequent updates

**Examples:**
- actor_types (nation, organization, individual)
- project_statuses (active, archived, completed)
- priority_levels (low, medium, high, critical)
- categories, tags, labels

**Phase 4 Implementation:** Simple admin interface or managed through seed data

### Entity Classification Template

Document your classification in PROJECT_REQUIREMENTS.md:

```markdown
## Entity Classification

### Primary/Core Entities (Full CRUD Required)
These need complete list, create, view, edit, delete pages:

1. **[Entity Name]**
   - Purpose: [Description]
   - Key fields: [List main fields]
   - Relationships: [List related entities]

2. **[Entity Name]**
   - Purpose: [Description]
   - Key fields: [List main fields]
   - Relationships: [List related entities]

[Continue for all primary entities]

### Junction/Association Tables (Managed in Parent Forms)
These are managed through parent entity interfaces:

1. **[Table Name]** - Links [Entity A] to [Entity B]
   - Managed in: [Which entity's form/detail page]
   - UI approach: [Multi-select / Add-remove list / etc.]

2. **[Table Name]** - Links [Entity A] to [Entity B]
   - Managed in: [Which entity's form/detail page]
   - UI approach: [Multi-select / Add-remove list / etc.]

[Continue for all junction tables]

### System-Generated Data (Read-Only + Optional Delete)
These are created by the application automatically:

1. **[Entity Name]** - Created by: [Process/trigger]
   - Display in: [Where users see this data]
   - User actions: View, Filter, Delete
   - Purpose: [Why this data exists]

2. **[Entity Name]** - Created by: [Process/trigger]
   - Display in: [Where users see this data]
   - User actions: View, Filter, Delete
   - Purpose: [Why this data exists]

[Continue for all system-generated entities]

### Configuration/Reference Data (Minimal CRUD)
Lookup tables or settings:

1. **[Entity Name]**
   - Management: [Admin only / Seed data / Rare edits]
   - Used in: [Which forms reference this]

2. **[Entity Name]**
   - Management: [Admin only / Seed data / Rare edits]
   - Used in: [Which forms reference this]

[Continue for all configuration entities]
```

### Decision Criteria

**Use this flowchart to classify entities:**

1. **Does the user directly create this through a form?**
   - Yes, and it's a main domain object → **Primary Entity**
   - Yes, but it's just linking two entities → **Junction Table**
   - No, the app creates it automatically → **System-Generated Data**
   - Rarely, mostly predefined → **Configuration/Reference**

2. **For uncertain cases, ask:**
   - Would a typical user create this? → **Primary**
   - Is this just connecting two things? → **Junction**
   - Does this happen during a process? → **System-Generated**
   - Is this more like settings/metadata? → **Configuration**

### Common Patterns by Application Type

**Task/Project Management:**
- Primary: Projects, Tasks, Milestones
- Junction: project_members, task_assignees
- System-Generated: activity_logs, time_tracking_entries
- Configuration: task_statuses, priority_levels

**E-commerce:**
- Primary: Products, Orders, Customers
- Junction: order_products, product_categories
- System-Generated: payment_transactions, inventory_adjustments
- Configuration: shipping_methods, payment_types

**Social/Community:**
- Primary: Posts, Comments, Groups
- Junction: group_members, post_tags
- System-Generated: notifications, activity_feed
- Configuration: post_types, group_categories

**Simulation/Workflow:**
- Primary: Scenarios, Actors, Workflows
- Junction: scenario_actors, workflow_steps
- System-Generated: execution_logs, actor_messages, timesteps
- Configuration: actor_types, workflow_types

---

## Step 4: MVP Feature Set [MANDATORY]

Define the minimum viable product features.

### Minimum Requirements

- **Minimum 5 primary features**
- Each feature should deliver clear user value
- Features should cover the core user journey

### Questions to Ask

**1. What are the essential actions users need to perform?**

Examples:
- Create and manage [entities]
- Search and filter [entities]
- Collaborate with team members
- Export/import data
- View analytics/reports

**2. What would make this MVP useful on day one?**

Focus on:
- Core functionality that solves the main problem
- Basic CRUD operations for core entities
- Essential workflows
- Critical user interactions

**3. What features can wait for v2?**

Separate:
- Nice-to-have features
- Advanced functionality
- Integrations
- Complex workflows

### MVP Feature Documentation Template

```markdown
## MVP Features

### 1. [Feature Name]
**Description:** [What this feature does]
**User Value:** [Why users need this]
**Entities Involved:** [Which data models]

### 2. [Feature Name]
[Similar structure]

### 3. [Feature Name]
[Similar structure]

[Continue for all features]
```

---

## Step 5: Agentic AI Capabilities Assessment [MANDATORY]

Determine if the application needs AI agent capabilities and which LangChain features are required.

**Reference Guides:**
- `.clinefiles/langchain/patterns/custom-subagents.md` - Production-ready subagent delegation pattern with supervisor patterns
- `.clinefiles/langchain/patterns/middleware-centric.md` - Middleware-centric architecture and composition
- `.clinefiles/langchain/reference-implementations/filesystem-prompt-example.py` - Custom filesystem prompt guidance for file operations

### Agent Architecture Decision

**When to Use Agents:**

✅ **Use Supervisor Pattern** if:
- Complex, multi-step tasks requiring planning
- Need to delegate to specialized capabilities
- Research tasks benefiting from file persistence
- Long-running conversations with context management
- Tasks where planning/organization adds value

✅ **Use Simple Agent Pattern** if:
- Single-step tasks with direct tool calling
- No delegation needed
- Short, stateless operations
- Straightforward Q&A without planning

❌ **Skip Agents** if:
- Pure CRUD operations suffice
- No AI capabilities needed
- Static content only

**Important:** Applications can have BOTH supervisor AND simple agents for different use cases. They are NOT mutually exclusive.

**Document Decision:**
```markdown
## Agent Architecture Decision
**Patterns Needed:** [Supervisor / Simple / Both / Not Needed]
**Rationale:** [Why these patterns fit your use cases]
**Use Cases:**
- Supervisor: [If applicable, what tasks]
- Simple: [If applicable, what tasks]
```

### Middleware Assessment (CRITICAL)

Middleware is the **PRIMARY approach** for adding capabilities to agents. For each middleware, assess if it's needed:

#### Standard Supervisor Middleware Stack (7 Middlewares)

**This is the recommended baseline for supervisor agents capable of deep/shallow research:**

| Middleware | Purpose | Needed When | Package | Always Include? |
|------------|---------|-------------|---------|-----------------|
| **TodoListMiddleware** | Planning & task breakdown | Multi-step tasks, research projects | langchain | If supervisor |
| **FilesystemMiddleware** | File operations (read/write/edit) | Persistent work, reports, research | deepagents | If file persistence needed |
| **CustomSubagentMiddleware** | Subagent delegation | Specialized capabilities needed | Custom (see pattern guide) | If delegation needed |
| **SummarizationMiddleware** | Context management | Long conversations (>170K tokens) | langchain | If long conversations |
| **AnthropicPromptCachingMiddleware** | Cost optimization | Using Anthropic models | langchain-anthropic | If Anthropic models |
| **PatchToolCallsMiddleware** | Error handling | Production systems | deepagents | Recommended for production |
| **Custom Logging/Rate Limiting** | Observability/Control | All production systems | Custom | As needed |

**Note:** The `deepagents` package is a utility library that provides FilesystemMiddleware and PatchToolCallsMiddleware. Install via `uv add deepagents`.

#### Assessment Questions

**1. TodoListMiddleware (Planning)**
- Will users give complex, multi-step requests?
- Would task breakdown help organize work?
- Are research/analysis tasks expected?

**Decision:** [ ] YES - Include TodoListMiddleware / [ ] NO - Skip

**2. FilesystemMiddleware (File Operations)**
- Will agents create reports or documentation?
- Need to persist findings across sessions?
- Conducting deep research requiring file storage?

**Decision:** [ ] YES - Include FilesystemMiddleware / [ ] NO - Skip

**3. CustomSubagentMiddleware (Delegation)**
- Need specialized capabilities (research, data, etc.)?
- Tasks benefit from expert delegation?
- Want to avoid context bloat in main agent?

**Decision:** [ ] YES - Include CustomSubagentMiddleware / [ ] NO - Skip

**If YES, identify subagents:**
- Research Subagent: Web search, analysis
- Data Subagent: Database queries, processing
- [Custom]: [Specific domain expertise]

**4. SummarizationMiddleware (Context Management)**
- Expect conversations >50 messages?
- Long-running analysis tasks?
- Need automatic context management?

**Decision:** [ ] YES - Include SummarizationMiddleware / [ ] NO - Skip

**5. Error Handling & Optimization**
- Production system requiring robustness? → PatchToolCallsMiddleware
- Using Anthropic models? → AnthropicPromptCachingMiddleware
- Need observability? → Custom logging middleware

### Memory Requirements (AUTOMATIC via LangSmith)

**CRITICAL:** Memory infrastructure is AUTOMATICALLY provided by LangSmith. You NEVER manually configure PostgresSaver or PostgresStore.

#### 1. Short-Term Memory [ALWAYS REQUIRED]

**Purpose:** Conversation persistence within threads

**How it works:**
- LangSmith automatically provides checkpointer when you use `thread_id`
- Conversation state persisted in LangSmith's managed PostgreSQL
- Zero configuration needed - just pass `thread_id` parameter
- Memory survives server restarts (in production, not `langgraph dev`)

**Assessment Questions:**
- How should threads be organized? (per user session, per project, per task)
- How long to retain thread data? (7 days, 30 days, indefinitely)

**Decision:** Always YES

**Document:**
```markdown
#### Short-Term Memory (Automatic via LangSmith)
**Thread Management:**
- Thread per: [conversation / user session / project]
- Retention: [Duration before cleanup]
**Implementation:** Automatic via thread_id parameter - no manual setup
```

#### 2. Long-Term Memory [ASSESS PER APP]

**Purpose:** Data persistence across threads

**How it works:**
- LangSmith automatically provides `runtime.store` when you access it
- Cross-conversation persistence handled automatically
- Access via `runtime.store` in tools/middleware
- Zero configuration needed - LangSmith handles infrastructure

**Needed When:**
- User preferences persist across sessions
- Knowledge bases accumulate over time
- Project state spans multiple conversations
- Agent learns from historical feedback

**Assessment Questions:**
- What data needs to persist beyond single conversations?
- Do users customize agent behavior over time?
- Is there a knowledge base that grows?

**Decision:** [ ] YES - Use runtime.store / [ ] NO - Skip

**If YES, document:**
```markdown
#### Long-Term Memory (Automatic via LangSmith)
**Use Cases:**
- [User preferences: theme, language, defaults]
- [Knowledge base: accumulated facts, context]
- [Project state: ongoing work, decisions made]
**Data Types:** [Specific data to persist]
**Implementation:** Automatic via runtime.store - no manual setup
```

**Reference:** `.clinefiles/langchain/core/short-term-memory.md` and `.clinefiles/langchain/core/long-term-memory.md`

### Additional Capabilities

#### 1. Structured Output

**Purpose:** Enforce specific response formats with schemas

**Needed When:**
- Extracting structured data from text (entities, classifications)
- Form filling from natural language input
- Database inserts requiring specific schemas
- API responses with defined structure

**Strategies:**
- ToolStrategy (universal, works with any model)
- ProviderStrategy (native, more reliable with supported models)

**Assessment Questions:**
- Do responses need consistent schema?
- Parsing agent output into database records?
- Classification or extraction tasks?

**Decision:** [ ] YES - Include structured output / [ ] NO - Skip

**If YES, document:**
```markdown
#### Structured Output
**Use Cases:**
- [Extract: entities, dates, classifications from text]
- [Database: insert records from natural language]
- [Forms: auto-fill from descriptions]
**Schemas:** [List required output schemas]
```

#### 2. Streaming [RECOMMENDED FOR ALL]

**Purpose:** Real-time response updates via SSE or WebSocket

**Benefits:**
- Better UX during long operations
- Token-by-token display
- Progress indicators
- User feedback during processing

**Assessment:** Recommended for all agent interfaces

**Decision:** [ ] YES - Include streaming (recommended) / [ ] NO - Skip

**Document:**
```markdown
#### Streaming
**Implementation:** [SSE / WebSocket]
**Use Cases:**
- [Real-time token display]
- [Progress updates during research]
- [Long-running operations feedback]
```

#### 3. Retrieval (RAG)

**Purpose:** Query external knowledge bases and documents

**Needed When:**
- Document search and Q&A systems
- Knowledge base over organizational data
- Context-aware responses from documents
- Semantic search capabilities
- FAQ/help systems

**RAG Approaches:**
- **2-Step RAG**: Predictable retrieval → LLM
- **Agentic RAG**: Agent decides when to retrieve
- **Hybrid RAG**: Validation after retrieval

**Vector Store:** PostgreSQL with pgvector extension

**Assessment Questions:**
- Need to search documents or knowledge bases?
- Users ask questions about stored content?
- Context requires external information?

**Decision:** [ ] YES - Include RAG / [ ] NO - Skip

**If YES, document:**
```markdown
#### Retrieval (RAG)
**RAG Approach:** [2-Step / Agentic / Hybrid]
**Use Cases:**
- [Document Q&A: search internal docs]
- [Knowledge base: semantic search]
- [Context: pull relevant information]
**Document Sources:** [PDFs, markdown, databases, APIs]
**Vector Store:** PostgreSQL with pgvector
```

### Custom Tools Assessment

**What domain-specific tools does the agent need?**

Examples by domain:
- **Database**: Query tables, insert records, analytics
- **External APIs**: Weather, news, stock data, social media
- **Business Logic**: Calculate pricing, validate rules, generate reports
- **File Operations**: Read/write/edit files (via FilesystemMiddleware)
- **Communication**: Send emails, Slack messages, notifications

**Document:**
```markdown
#### Custom Tools Required

1. **[Tool Name]**: [Purpose]
   - Implementation: [Database query / API call / Custom logic]
   - Inputs: [What parameters needed]
   - Outputs: [What it returns]

2. **[Tool Name]**: [Purpose]
   - Implementation: [Details]
   - Inputs: [Parameters]
   - Outputs: [Returns]

[Continue for all custom tools]
```

### User Interaction Patterns

**How will users interact with the agent?**

- [ ] **Chat Interface**: Conversational back-and-forth (most common)
- [ ] **Form-Based**: Fill forms, agent assists with suggestions
- [ ] **Background Processing**: Agent runs autonomously, reports results
- [ ] **Scheduled Tasks**: Periodic execution (daily reports, monitoring)
- [ ] **Real-Time Collaboration**: Multiple users, live updates

**Document:**
```markdown
#### User Interaction Patterns
**Primary Interface:** [Chat / Forms / Background / Scheduled / Real-time]
**User Flow:**
1. User: [Initial action]
2. Agent: [Response pattern]
3. User: [Follow-up]
4. Agent: [Completion]

**Integration Points:**
- [Where in app agent is accessed]
- [How results are presented]
- [Error handling approach]
```

### Complete Agent Capabilities Template

```markdown
## Agent Capabilities Assessment

### Architecture Decision
**Pattern:** [Supervisor / Simple / Not Needed]
**Rationale:** [Why this pattern fits the use case]

### Middleware Stack (If Supervisor Pattern)

**Include in Stack:**
- [ ] TodoListMiddleware - Planning and task breakdown
- [ ] FilesystemMiddleware - File operations for persistence
- [ ] CustomSubagentMiddleware - Delegation to specialists
  - Subagents needed: [Research, Data, Other]
- [ ] SummarizationMiddleware - Context management (>170K tokens)
- [ ] AnthropicPromptCachingMiddleware - Cost optimization (Anthropic only)
- [ ] PatchToolCallsMiddleware - Production error handling
- [ ] Custom Middleware: [Logging, Rate Limiting, Other]

**Rationale:** [Why these specific middlewares are needed]

### Memory Configuration

#### Short-Term Memory
**Always Required:** YES
**Thread Management:**
- Thread per: [conversation / session / project]
- Retention: [7 days / 30 days / indefinite]

#### Long-Term Memory
**Needed:** [YES / NO]
**Use Cases (if YES):**
- [User preferences persistence]
- [Knowledge base accumulation]
- [Project state across sessions]

### Additional Capabilities

#### Structured Output
**Needed:** [YES / NO]
**Use Cases (if YES):**
- [Extract entities from text]
- [Database inserts with schemas]
- [Classification tasks]

#### Streaming
**Needed:** [YES / NO (recommended YES)]
**Implementation:** [SSE / WebSocket]

#### Retrieval (RAG)
**Needed:** [YES / NO]
**Approach (if YES):** [2-Step / Agentic / Hybrid]
**Document Sources:** [PDFs, docs, databases]

### Custom Tools

1. **[Tool Name]**: [Purpose and implementation]
2. **[Tool Name]**: [Purpose and implementation]
[Continue for all tools]

### User Interaction

**Primary Pattern:** [Chat / Forms / Background / Other]
**Integration Points:** [Where in app]
**User Flow:** [Describe typical interaction]
```

### LangSmith Features Assessment

**Reference:** `.clinefiles/langchain/langsmith/next-js-integration/` folder for implementation details

Beyond basic agent capabilities, LangSmith provides additional features for advanced applications:

- [ ] **Threads** - Thread management (ALWAYS required for agents)
- [ ] **Streaming** - Real-time responses (DEFAULT enabled)
- [ ] **Assistants** - Multiple agent configurations  
- [ ] **Human-in-the-loop** - Approval workflows
- [ ] **Background runs** - Async processing
- [ ] **Cron jobs** - Scheduled tasks
- [ ] **Generative UI** - Dynamic UI from agent responses
- [ ] **Multiple agents same thread** - Multi-agent conversations
- [ ] **Time travel** - Conversation branching/replay

**Document decisions:**
```markdown
## LangSmith Features
**Features Needed:**
- Threads: YES (always required)
- Streaming: YES (default)
- Human-in-the-loop: [YES/NO - when needed]
- Background runs: [YES/NO - use cases]
- Cron jobs: [YES/NO - schedule]
- Other: [List any additional features]
```

### Critical Questions to Ask User

Before completing Phase 0, explicitly ask:

1. **What complex tasks will the agent handle?**
   - Simple Q&A or multi-step research?
   - Need planning and delegation?

2. **What tools must the agent access?**
   - Database queries?
   - External APIs?
   - File operations?

3. **How will users interact with the agent?**
   - Chat interface?
   - Background automation?
   - Form assistance?

4. **What data persists?**
   - Just conversation history?
   - User preferences?
   - Accumulated knowledge?

5. **Are there documents to search?**
   - Need document Q&A?
   - Semantic search required?

6. **What LangSmith features are needed?**
   - Approval workflows?
   - Background/scheduled tasks?
   - Multiple agent types?

---

## Step 6: LLM Model Provider Selection [MANDATORY FOR AGENTS]

If your application includes AI agents (determined in Step 5), you must choose an LLM provider and model.

**Reference:** `.clinefiles/langchain/MODEL_UPDATE_2025.md` - Complete guide to current model options and pricing

### Provider Options

**OpenAI (Recommended for most applications)**
- **Latest Models (2025):**
  - `gpt-5.1` - Latest reasoning model with advanced capabilities
    - ⚠️ **Does NOT support `temperature`** - Use `reasoning_effort` and `verbosity` instead
  - `gpt-5` - Latest standard generation
    - ⚠️ **Does NOT support `temperature`** - Use `verbosity` instead
  - `gpt-5-mini` - Fast and cost-effective
    - ⚠️ **Does NOT support `temperature`** - Use `verbosity` instead
  - `gpt-4.1` - Previous generation, still excellent
    - ✅ Still supports `temperature` parameter
- **Strengths:** Reliable, fast, great documentation, reasoning capabilities, broad capability
- **Pricing:** Moderate to high
- **Best for:** Production applications, complex reasoning, general purpose

**Anthropic Claude (Recommended for research/analysis)**
- **Latest Models (2025):**
  - `claude-sonnet-4-5-20250929` - Best balance (recommended default)
  - `claude-haiku-4-5-20251001` - Fast and cheap
  - `claude-opus-4-1-20250805` - Premium, complex reasoning
- **Strengths:** Excellent at analysis, great with long context, strong reasoning
- **Pricing:** Competitive, especially Haiku for high-volume
- **Best for:** Research tasks, document analysis, detailed reasoning

**Other Providers:**
- **Google Gemini:** Multimodal capabilities, competitive pricing
- **AWS Bedrock:** Enterprise deployment, compliance needs
- **Azure OpenAI:** Enterprise Microsoft integration
- **Local (Ollama):** Privacy-first, no API costs, lower capability

### Selection Questions

**1. What is your budget for LLM API calls?**
- High volume, need cost control → Claude Haiku or GPT-5-mini
- Quality over cost → Claude Opus or GPT-5
- Balanced → Claude Sonnet 4.5 (recommended)

**2. What tasks will the LLM perform?**
- Research and analysis → Claude Sonnet/Opus
- General purpose agents → GPT-5 or Claude Sonnet
- Simple Q&A → GPT-5-mini or Claude Haiku
- Multimodal (images/audio) → GPT-5 or Gemini

**3. Do you have compliance/privacy requirements?**
- Enterprise compliance → AWS Bedrock or Azure
- Data privacy critical → Ollama (local)
- Standard → OpenAI or Anthropic

**4. Do you need specific features?**
- Extended thinking → Claude models (all support)
- Prompt caching → Claude (explicit) or OpenAI (implicit)
- Long context (>100K tokens) → Claude Sonnet 4.5 (200K)

### Model Selection Template

```markdown
## LLM Model Selection

### Primary Provider: [OpenAI / Anthropic / Other]
**Rationale:** [Why this provider fits your needs]

### Primary Model: [Specific model name]
**Use Cases:** [What this model will handle]
**Rationale:** [Why this specific model]

### Secondary Model (Optional): [Model name]
**Use Cases:** [When to use this instead]
**Rationale:** [Cost optimization, specific capabilities, etc.]

### Configuration:
**⚠️ CRITICAL:** GPT-5 family models (`gpt-5`, `gpt-5.1`, `gpt-5-mini`, `gpt-5-nano`, `gpt-5-chat`) do NOT support `temperature`.
- For GPT-5.1: Use `reasoning_effort` (low/medium/high) and `verbosity` (low/medium/high)
- For other GPT-5 models: Use `verbosity` (low/medium/high) instead of temperature
- GPT-4.x and Claude models still support `temperature` normally

**Model Parameters:**
- **Temperature** (GPT-4.x, Claude only): [0.0-1.0, typically 0.7 for creative, 0.0 for deterministic]
- **Verbosity** (GPT-5 family only): [low/medium/high - controls response detail level]
- **Reasoning Effort** (GPT-5.1 only): [low/medium/high - controls reasoning depth]
- **Max Tokens:** [Response length limit]
- **Timeout:** [Request timeout in seconds]

### Cost Estimates:
**Expected Monthly Volume:** [Estimated tokens per month]
**Estimated Cost:** [Based on provider pricing]
**Budget Considerations:** [Any cost constraints]
```

### Recommended Defaults by Use Case

**Supervisor Agents (Research/Analysis):**
```python
# Recommended: Claude Sonnet 4.5 - Best balance for research
model = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    temperature=0.7,
    max_tokens=4096
)

# Alternative: GPT-5.1 with reasoning (NO temperature - GPT-5 family doesn't support it)
model = ChatOpenAI(
    model="gpt-5.1",
    reasoning_effort="medium",  # low/medium/high - controls reasoning depth
    verbosity="medium",         # low/medium/high - controls response detail
    max_tokens=4096
)

# Alternative: GPT-5 for general purpose (NO temperature - GPT-5 family doesn't support it)
model = ChatOpenAI(
    model="gpt-5",
    verbosity="medium",  # low/medium/high - use this instead of temperature
    max_tokens=4096
)

# GPT-4.1 still supports temperature if you need it
model = ChatOpenAI(
    model="gpt-4.1",
    temperature=0.7,
    max_tokens=4096
)
```

**Simple Agents (Q&A, Simple Tasks):**
```python
# Recommended: Claude Haiku - Fast and cheap
model = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    temperature=0.5,
    max_tokens=2048
)

# Alternative: GPT-5-mini for OpenAI users (NO temperature - GPT-5 family doesn't support it)
model = ChatOpenAI(
    model="gpt-5-mini",
    verbosity="low",  # low/medium/high - use this instead of temperature
    max_tokens=2048
)

# GPT-4.1-mini still supports temperature if you need it
model = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.5,
    max_tokens=2048
)
```

**High-Volume Applications:**
```python
# Use mini/haiku models for cost control
# Upgrade to full models only when needed
```

### Multi-Model Strategy (Advanced)

For production applications, consider using different models for different tasks:

```markdown
### Multi-Model Strategy

**Supervisor Agent (Planning):** [claude-sonnet-4-5-20250929]
- Rationale: Complex reasoning needed for planning

**Research Subagent:** [claude-sonnet-4-5-20250929]
- Rationale: Analysis and synthesis tasks

**Simple Subagents:** [claude-haiku-4-5-20251001]
- Rationale: Fast, cheap for simple operations

**Fallback Model:** [gpt-5-mini]
- Rationale: Backup if primary provider has issues
```

### API Key Setup

Document required API keys:

```markdown
### Required API Keys

**Provider:** [OpenAI / Anthropic / Both]

**Environment Variables:**
```bash
# For OpenAI
OPENAI_API_KEY=sk-...

# For Anthropic  
ANTHROPIC_API_KEY=sk-ant-...

# For both (if using multi-model)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

**Where to get keys:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys
```

---

## Step 7: ReactFlow and Advanced Features Assessment

Determine if the application needs node-based visualizations or other advanced features.

### ReactFlow Decision Criteria

**ReactFlow is MANDATORY if the application includes ANY of:**

✅ **Workflow Designers**
- Building automation workflows
- Creating multi-step processes
- Designing approval chains

✅ **Mind Maps / Concept Mapping**
- Visual brainstorming tools
- Knowledge organization
- Idea clustering

✅ **System Architecture Diagrams**
- Infrastructure visualization
- Service dependency maps
- Network topology

✅ **Data Flow Visualizations**
- ETL pipeline designers
- Data transformation workflows
- Process flow diagrams

✅ **Decision Trees**
- Rule-based logic builders
- Conditional path visualization
- Scenario planning

✅ **Node-Based Editors**
- Visual programming interfaces
- Graph-based data structures
- Any draggable/connectable UI

❌ **ReactFlow NOT needed for:**
- Simple CRUD applications
- List/table-based interfaces
- Form-based data entry
- Standard dashboards

### Other Advanced Features

Assess need for:

**Real-time Features:**
- Live collaboration
- Real-time notifications
- Presence indicators
- Live cursors

**File Upload:**
- Document management
- Image uploads
- File attachments
- Media galleries

**Analytics/Charts:**
- Data visualization
- Reporting dashboards
- Metrics tracking
- Trend analysis

### Advanced Features Documentation Template

```markdown
## Advanced Features Assessment

### ReactFlow Needed: [YES/NO]
**Reason:** [Why or why not]
**Use Cases:** [If yes, list specific use cases]

### Real-time Features Needed: [YES/NO]
**Use Cases:** [If yes, list specific use cases]

### File Upload Needed: [YES/NO]
**Use Cases:** [If yes, list specific use cases]

### Analytics Needed: [YES/NO]
**Metrics:** [If yes, list what metrics to track]
```

---

## Step 7: Document Everything

Create a comprehensive requirements document that will guide all subsequent phases.

### Requirements Document Template

```markdown
# [Application Name] - Requirements Document

## Application Overview

**Type:** [Application type]
**Purpose:** [Primary problem solved]
**Target Users:** [User description]

## Landing Page

**Style:** [Design aesthetic]
**Reference Sites:** [List any example sites]

**Hero Section:**
- Headline: [Main headline]
- Subheadline: [Supporting text]
- CTA: [Call-to-action text]
- Visual: [Approach to hero visual]

**Features Section:**
1. [Feature 1: Title and description]
2. [Feature 2: Title and description]
3. [Feature 3: Title and description]

**Pricing:**
- Free Tier: [Features]
- Pro Tier: [Features and price]
- Enterprise: [Features and pricing approach]

## Data Models

### [Entity 1 Name]
[Full entity definition]

### [Entity 2 Name]
[Full entity definition]

### [Entity 3 Name]
[Full entity definition]

[Additional entities]

## MVP Features

1. [Feature 1: Full description]
2. [Feature 2: Full description]
3. [Feature 3: Full description]
4. [Feature 4: Full description]
5. [Feature 5: Full description]

[Additional features]

## Advanced Features

**ReactFlow:** [YES/NO and use cases]
**Real-time:** [YES/NO and use cases]
**File Upload:** [YES/NO and use cases]
**Analytics:** [YES/NO and metrics]

## User Flows

### Primary User Flow
1. [Step 1]
2. [Step 2]
3. [Step 3]

[Additional important flows]

## Technical Decisions

**Authentication:** Email/password, social auth, magic links
**Data Access:** Public, private, role-based
**File Storage:** Needed/not needed
**External APIs:** [List any needed integrations]

---

## Next Steps

With requirements documented, proceed to:
- **Phase 1:** Supabase Setup (database migrations for all entities)
- **Phase 2:** Next.js Setup (application foundation)
- **Phase 3:** Marketing & UI (landing page and dashboard)
```

---

## Verification Checklist

Before proceeding to Phase 1, verify:

- [ ] Application type and purpose clearly defined
- [ ] Landing page style and content requirements gathered
- [ ] Minimum 3 core entities identified with fields and relationships
- [ ] Minimum 5 MVP features defined
- [ ] ReactFlow need determined (YES/NO with rationale)
- [ ] Advanced features assessed
- [ ] Complete requirements document created
- [ ] User has reviewed and approved requirements

**Cannot proceed to Phase 1 without completing all discovery items.**

---

## Common Discovery Questions

### For Task/Project Management Apps

- Do you need time tracking?
- Are tasks assigned to specific users?
- Do you need recurring tasks?
- Should tasks have subtasks/dependencies?
- Do you need kanban boards or just lists?

### For E-commerce Apps

- Physical products, digital products, or services?
- Do you need inventory tracking?
- Multiple payment methods?
- Shipping calculations needed?
- Product variants (sizes, colors, etc.)?

### For Social/Community Apps

- Public posts or private groups?
- Real-time chat needed?
- Content moderation tools?
- User profiles with followers?
- Content types (text, images, video)?

### For Analytics/Dashboard Apps

- What metrics need to be tracked?
- Real-time or batch updated data?
- Who defines the visualizations?
- Export capabilities needed?
- Custom date range filtering?

---

## Tips for Effective Discovery

1. **Ask open-ended questions** - Let the user describe their vision
2. **Identify the core problem** - What pain point are we solving?
3. **Start simple** - MVP should be minimal but useful
4. **Think in user stories** - "As a [user], I want to [action] so that [benefit]"
5. **Document assumptions** - Make implicit requirements explicit
6. **Get examples** - "Show me how you do this today"
7. **Define success** - What does a successful MVP look like?

---

## Next Phase

**Proceed to:** [Phase 1: Supabase Local Setup](./phase-1-supabase-setup.md)

**With:** Complete requirements document including all data models, features, and advanced feature decisions.
