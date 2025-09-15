# LangGraph Storage & Checkpointing

## Critical Rule: Always Use Async PostgreSQL
**ALWAYS use `AsyncPostgresStore` and `AsyncPostgresSaver` with proper context managers**

```python
# ✅ CORRECT - Async PostgreSQL with context manager
from langgraph.storage import AsyncPostgresStore
from langgraph.checkpoint.postgres import AsyncPostgresSaver

async def main(runtime_context: MyContext):
    # Async store and saver with proper setup
    store = AsyncPostgresStore.from_conn_string(runtime_context.db_uri)
    await store.setup()
    
    checkpointer = AsyncPostgresSaver.from_conn_string(runtime_context.db_uri)
    await checkpointer.setup()
    
    # Use in agent creation...

# ❌ WRONG - Sync versions
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string(DB_URI)  # No async
```

## Essential Patterns

### 1. Async Setup Pattern
**Always setup storage components before use**
```python
from langgraph.storage import AsyncPostgresStore
from langgraph.checkpoint.postgres import AsyncPostgresSaver

async def setup_agent_storage(db_uri: str):
    # Create store and checkpointer
    store = AsyncPostgresStore.from_conn_string(db_uri)
    await store.setup()  # Required for first-time table creation
    
    checkpointer = AsyncPostgresSaver.from_conn_string(db_uri)
    await checkpointer.setup()  # Required for first-time table creation
    
    return store, checkpointer
```

### 3. Agent Integration with Storage
**Integrate storage components with prebuilt agents**
```python
async def create_agent_with_storage(runtime_context: MyContext):
    # Setup storage
    store = AsyncPostgresStore.from_conn_string(runtime_context.db_uri)
    await store.setup()
    
    checkpointer = AsyncPostgresSaver.from_conn_string(runtime_context.db_uri)
    await checkpointer.setup()
    
    # Create agent with storage
    agent = create_react_agent(
        model=llm,
        tools=[get_weather, get_user_email],
        prompt=prompt,
        context_schema=MyContext,
        state_schema=MyState,
        checkpointer=checkpointer,  # Async checkpointer
        store=store,               # Async store
    )
    
    return agent
```

### 4. Thread Management
**Use context for conversation persistence with thread IDs**
```python
# Runtime context with thread ID for persistence
runtime_context = MyContext(
    user_name="Alice", 
    db_uri="postgresql://...", 
    thread_id="user_123_session_1"
)

# Stream with thread context
async for update in agent.astream(
    {"messages": [{"role": "user", "content": "Hello"}]},
    context=runtime_context.__dict__,
    stream_mode="updates",
):
    print(update)

# Continue conversation in same thread context
async for update in agent.astream(
    {"messages": [{"role": "user", "content": "What did I just say?"}]},
    context=runtime_context.__dict__,  # Same thread_id in context
    stream_mode="updates",
):
    print(update)
```

### 5. State Inspection and Management
**Access conversation history and snapshots**
```python
# Context with thread ID for state operations
context_dict = {"user_name": "Alice", "thread_id": "user_123_session_1"}

# Get current state snapshot
snapshot = graph.get_state(context_dict)

# Get conversation history
history = list(graph.get_state_history(context_dict))

# Clean up thread when done
checkpointer.delete_thread("user_123_session_1")
```

## Common Pitfalls

### 1. Using Sync Instead of Async
```python
# ❌ WRONG - Sync components
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string(DB_URI)

# ✅ CORRECT - Async components
from langgraph.checkpoint.postgres import AsyncPostgresSaver
checkpointer = AsyncPostgresSaver.from_conn_string(db_uri)
await checkpointer.setup()
```

### 2. Missing Setup Calls
```python
# ❌ WRONG - No setup() call
store = AsyncPostgresStore.from_conn_string(db_uri)
# Missing: await store.setup()

# ✅ CORRECT - Always call setup()
store = AsyncPostgresStore.from_conn_string(db_uri)
await store.setup()  # Required!
```

### 3. Forgetting Thread Configuration
```python
# ❌ WRONG - No thread ID in context
async for update in agent.astream(
    {"messages": [{"role": "user", "content": "Hello"}]},
    context={"user_name": "Alice"}  # Missing thread_id for persistence
):
    pass

# ✅ CORRECT - Include thread_id in context
context_dict = {"user_name": "Alice", "thread_id": "session_1"}
async for update in agent.astream(
    {"messages": [{"role": "user", "content": "Hello"}]},
    context=context_dict,  # Required for persistence
):
    pass
```

### 4. Hardcoded Connection Strings
```python
# ❌ WRONG - Hardcoded connection
DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres"

# ✅ CORRECT - From environment or context
db_uri = runtime_context.db_uri  # From context
# or
db_uri = os.getenv("DATABASE_URL")  # From environment
```

## Complete Storage Setup Example

```python
import asyncio
from dataclasses import dataclass
from langgraph.context import ContextSchema
from langgraph.storage import AsyncPostgresStore
from langgraph.checkpoint.postgres import AsyncPostgresSaver
from langgraph.prebuilt import create_react_agent

@dataclass
class MyContext(ContextSchema):
    user_name: str
    db_uri: str
    thread_id: str = None

async def main():
    runtime_context = MyContext(
        user_name="Alice",
        db_uri="postgresql://user:pass@localhost:5432/langgraph"
    )
    
    # Setup storage components
    store = AsyncPostgresStore.from_conn_string(runtime_context.db_uri)
    await store.setup()
    
    checkpointer = AsyncPostgresSaver.from_conn_string(runtime_context.db_uri)
    await checkpointer.setup()
    
    # Create agent with storage
    agent = create_react_agent(
        model=llm,
        tools=[get_user_email],
        context_schema=MyContext,
        checkpointer=checkpointer,
        store=store,
    )
    
    # Use agent with thread persistence via context
    runtime_context.thread_id = f"user_{runtime_context.user_name}"
    
    async for update in agent.astream(
        {"messages": [{"role": "user", "content": "Hello!"}]},
        context=runtime_context.__dict__,
        stream_mode="updates",
    ):
        print(update)

if __name__ == "__main__":
    asyncio.run(main())
```

## Environment Configuration

```python
# Database connection from environment
import os

DB_URI = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/langgraph?sslmode=disable"
)

# Or use with context
@dataclass
class MyContext(ContextSchema):
    user_name: str
    db_uri: str = os.getenv("DATABASE_URL", "postgresql://...")
```

## Quick Reference

- **Storage**: `AsyncPostgresStore.from_conn_string()`
- **Checkpointer**: `AsyncPostgresSaver.from_conn_string()`
- **Setup**: Always call `await store.setup()` and `await checkpointer.setup()`
- **Thread ID**: Include `thread_id` in context dict for persistence
- **Context Manager**: Use `with` for sync PostgresSaver only (fallback)

**Memory Aid**: "Always Async, always setup(), always configure threads for persistence."
