# Phase 8.1: Agent Service Setup

**Time Estimate:** 15-20 minutes

**Purpose:** Create agent service directory structure and initialize LangGraph development environment

**Prerequisites:**
- Phase 0 completed with Agent Capabilities Assessment documented in PROJECT_REQUIREMENTS.md
- Python 3.11+ installed
- `uv` package manager available (from general.md rules)

---

## Step 1: Create Agent Service Directory

Create `agent-service/` as a peer directory to your Next.js app and Supabase:

```bash
# From project root
mkdir agent-service
cd agent-service
```

Your directory structure should now be:

```
your-app/
├── your-nextjs-app/     # Next.js frontend
├── supabase/            # Database
├── agent-service/       # NEW - LangChain agents (this phase)
└── .clinerules/         # Documentation
```

---

## Step 2: Initialize Python Project with uv

**Per `.clinerules/general.md` rules, use `uv` for Python dependency management:**

```bash
# Initialize Python project
uv init

# This creates:
# - pyproject.toml
# - .python-version
```

---

## Step 3: Install Core Dependencies

**Install LangChain ecosystem packages using `uv add` (NOT pip):**

```bash
# Core LangChain packages
uv add langchain
uv add langchain-core
uv add langchain-openai
uv add langchain-anthropic

# LangGraph for agent orchestration
uv add langgraph
uv add "langgraph-cli[inmem]"

# Deep agents utilities (FilesystemMiddleware, PatchToolCallsMiddleware)
uv add deepagents

# Additional utilities
uv add python-dotenv
```

**Why these packages?**
- `langchain` - Core framework
- `langchain-openai` / `langchain-anthropic` - Model providers
- `deepagents` - Production middleware utilities
- `langgraph` - Agent orchestration and memory
- `langgraph-cli[inmem]` - Local development server

---

## Step 4: Create Agent Directory Structure

**Important:** Agents should be organized with clear folder structure for maintainability.

Create the following structure:

```bash
mkdir -p src/agent/middleware
mkdir -p src/agent/models
mkdir -p src/agent/tools
mkdir -p src/agent/prompts
touch src/agent/__init__.py
touch src/agent/graph.py
touch src/agent/middleware/__init__.py
touch src/agent/models/__init__.py
touch src/agent/tools/__init__.py
touch src/agent/prompts/__init__.py
```

**Recommended structure** (following middleware-centric pattern):

```
agent-service/
├── pyproject.toml
├── .python-version
├── .env                 # Create in next step
├── langgraph.json       # Create in next step
└── src/
    └── agent/
        ├── __init__.py
        ├── graph.py         # Main agent entry point
        ├── middleware/      # Custom middleware (tools, guardrails, etc.)
        │   └── __init__.py
        ├── models/          # Structured output schemas
        │   └── __init__.py
        ├── tools/           # Tool definitions (if not in middleware)
        │   └── __init__.py
        └── prompts/         # System prompts and prompt templates
            └── __init__.py
```

**Why this structure?**
- **middleware/** - Generalizable middleware with init parameters for tools, prompts, rules
- **models/** - Pydantic models for structured outputs
- **tools/** - Tool definitions (though middleware-centric pattern preferred)
- **prompts/** - System prompts paired with tools/middleware

**Reference:** `.clinerules/langchain/patterns/middleware-centric.md` for organization patterns

---

## Step 5: Create LangGraph Configuration

Create `langgraph.json` in `agent-service/` root:

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/agent/graph.py:graph"
  },
  "env": ".env"
}
```

**Configuration breakdown:**
- `dependencies: ["."]` - Install local package in editable mode
- `graphs.agent` - Exposes agent at `/agent` endpoint, references `graph` variable in `graph.py`
- `env: ".env"` - Load environment variables from .env file

**Reference:** `.clinerules/langchain/langsmith/local-development.md` for configuration details

---

## Step 6: Create Environment File

Create `.env` file in `agent-service/`:

```bash
# LangSmith API Key (required for langgraph dev)
# Get free key at: https://smith.langchain.com/settings
LANGSMITH_API_KEY=lsv2_pt_...

# Model API Keys (add based on Phase 0 model choice)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Tavily for web search tools
TAVILY_API_KEY=tvly-...
```

**Get LangSmith API Key:**
1. Visit https://smith.langchain.com/settings
2. Create account (free tier available)
3. Generate API key
4. Copy to `.env` file

**Important:** Add `.env` to `.gitignore` to avoid committing secrets

---

## Step 7: Create Minimal Agent (Test Setup)

Create a minimal agent in `src/agent/graph.py` to verify setup:

```python
"""
Minimal agent for testing LangGraph dev setup.
Replace with actual implementation in Phase 8.2.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    """Agent state - will be expanded in Phase 8.2"""
    messages: list[dict]


def agent_node(state: State):
    """Simple echo node - replace in Phase 8.2"""
    return {
        "messages": state["messages"] + [
            {"role": "assistant", "content": "Agent service is running!"}
        ]
    }


# Build minimal graph
builder = StateGraph(State)
builder.add_node("agent", agent_node)
builder.add_edge(START, "agent")
builder.add_edge("agent", END)

# Export graph (langgraph.json references this)
graph = builder.compile()
```

---

## Step 8: Start LangGraph Dev Server

**From `agent-service/` directory, start the dev server:**

```bash
langgraph dev
```

**Expected output:**

```
>    Ready!
>
>    - API: http://localhost:2024
>    - Docs: http://localhost:2024/docs
>    - Studio Web UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

**What `langgraph dev` provides:**
- ✅ **Local API server** on port 2024
- ✅ **Automatic memory infrastructure** (checkpointer + store) - no manual setup needed
- ✅ **Hot reload** - code changes auto-reload
- ✅ **Studio UI** - visual debugging interface
- ✅ **API docs** - interactive OpenAPI documentation

**Critical:** This simulates the LangSmith cloud platform locally. Memory (checkpointer, store) is automatically available - you never configure it manually.

---

## Step 9: Verify Setup

### Test 1: API Accessibility

Visit http://localhost:2024/docs - should see OpenAPI documentation

### Test 2: Studio UI

Open Studio UI link from terminal output - should see agent visualization

### Test 3: Test Run via curl

```bash
curl -X POST http://localhost:2024/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "agent",
    "input": {
      "messages": [{"role": "user", "content": "test"}]
    },
    "stream_mode": "values"
  }'
```

Should return streaming response with "Agent service is running!"

---

## Phase 8.1 Completion Checklist

Before proceeding to Phase 8.2, verify:

- [ ] `agent-service/` directory created as peer to Next.js app
- [ ] Python 3.11+ confirmed: `python --version`
- [ ] Project initialized with `uv init`
- [ ] All dependencies installed via `uv add` (NOT pip)
- [ ] Directory structure matches specification
- [ ] `langgraph.json` configuration created
- [ ] `.env` file created with `LANGSMITH_API_KEY`
- [ ] `.env` added to `.gitignore`
- [ ] Minimal agent in `src/agent/graph.py`
- [ ] `langgraph dev` runs without errors
- [ ] API accessible at http://localhost:2024
- [ ] API docs viewable at http://localhost:2024/docs
- [ ] Studio UI accessible via provided link
- [ ] Test curl command returns successful response

---

## Troubleshooting

### Issue: `uv: command not found`

Install uv following project requirements. If using brew:
```bash
brew install uv
```

### Issue: `langgraph: command not found`

Ensure CLI installed correctly:
```bash
uv add "langgraph-cli[inmem]"
```

Then use via uv:
```bash
uv run langgraph dev
```

### Issue: Port 2024 already in use

Kill existing process or specify different port:
```bash
langgraph dev --port 2025
```

Update `NEXT_PUBLIC_AGENT_API_URL` in Phase 8.4 accordingly.

### Issue: LangSmith API key invalid

- Verify key starts with `lsv2_pt_`
- Check for typos in `.env`
- Generate new key at https://smith.langchain.com/settings

### Issue: Import errors when starting server

Ensure installed in editable mode:
```bash
uv pip install -e .
```

---

## Important Notes

### Memory Infrastructure (CRITICAL)

**DO NOT manually configure memory/checkpointer/store.**

When you run `langgraph dev`, LangSmith automatically provides:
- ✅ PostgreSQL-backed checkpointer (short-term memory)
- ✅ Store for cross-thread data (long-term memory)
- ✅ Thread management infrastructure

You simply USE these via:
- `thread_id` parameter for conversation persistence
- `runtime.store` in tools/middleware for long-term data

**Reference:** `.clinerules/langchain/core/short-term-memory.md` and `.clinerules/langchain/core/long-term-memory.md`

### Using uv for Python

Per `.clinerules/general.md`:
- ✅ Use `uv add package-name` to install packages
- ✅ Use `uv run` to run commands
- ❌ Do NOT use `pip install`
- ❌ Do NOT use `uv pip install`

---

## Next Steps

**Proceed to:** [Phase 8.2: Agent Implementation](./phase-8-2-agent-implementation.md)

**With:** Working LangGraph dev server running on port 2024 with memory infrastructure automatically available.
