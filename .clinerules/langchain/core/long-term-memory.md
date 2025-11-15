# Long-term memory

## Overview

LangChain agents use [LangGraph persistence](/oss/python/langgraph/persistence#memory-store) to enable long-term memory. This is a more advanced topic and requires knowledge of LangGraph to use.

## LangSmith handles store infrastructure

<Warning>
  **Important:** When using LangSmith (both deployment and `langgraph dev`), stores are **automatically configured and managed**. You do NOT need to instantiate or configure stores yourself.
  
  - ✅ Access stores via `runtime.store` in tools
  - ✅ LangSmith handles all store infrastructure automatically
  - ❌ Do NOT create `InMemoryStore()` or pass `store=` parameters to `create_agent`
  
  For local development setup, see [Local Development](/langsmith/local-development).
  For semantic search configuration, see [LangSmith Long-term Memory](/langsmith/long-term-memory).
</Warning>

## Memory storage

LangGraph stores long-term memories as JSON documents in a [store](/oss/python/langgraph/persistence#memory-store).

Each memory is organized under a custom `namespace` (similar to a folder) and a distinct `key` (like a file name). Namespaces often include user or org IDs or other labels that makes it easier to organize information.

This structure enables hierarchical organization of memories. Cross-namespace searching is then supported through content filters.

```python  theme={null}
# Example of how stores work conceptually
# (In practice, access via runtime.store - see examples below)

user_id = "my-user"
application_context = "chitchat"
namespace = (user_id, application_context) # [!code highlight]

# Store operations (accessed via runtime.store in actual code)
# store.put(namespace, "a-memory", {...})  # Save data
# item = store.get(namespace, "a-memory")  # Retrieve by key
# items = store.search(namespace, query="...")  # Semantic search
```

For more information about the memory store, see the [Persistence](/oss/python/langgraph/persistence#memory-store) guide.

For semantic search configuration in LangSmith deployment, see [LangSmith Long-term Memory](/langsmith/long-term-memory).

## Read long-term memory in tools

```python A tool the agent can use to look up user information theme={null}
from dataclasses import dataclass

from langchain_core.runnables import RunnableConfig
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime


@dataclass
class Context:
    user_id: str

@tool
def get_user_info(runtime: ToolRuntime[Context]) -> str:
    """Look up user info."""
    # Access the store - automatically provided by LangSmith
    store = runtime.store # [!code highlight]
    user_id = runtime.context.user_id
    # Retrieve data from store - returns StoreValue object with value and metadata
    user_info = store.get(("users",), user_id) # [!code highlight]
    return str(user_info.value) if user_info else "Unknown user"

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    tools=[get_user_info],
    context_schema=Context
)

# Run the agent
agent.invoke(
    {"messages": [{"role": "user", "content": "look up user information"}]},
    context=Context(user_id="user_123") # [!code highlight]
)
```

<Note>
  The store is automatically available via `runtime.store` when using LangSmith. You do not need to instantiate or pass a store to `create_agent`.
</Note>

<a id="write-long-term" />

## Write long-term memory from tools

```python Example of a tool that updates user information theme={null}
from dataclasses import dataclass
from typing_extensions import TypedDict

from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime


@dataclass
class Context:
    user_id: str

# TypedDict defines the structure of user information for the LLM
class UserInfo(TypedDict):
    name: str

# Tool that allows agent to update user information (useful for chat applications)
@tool
def save_user_info(user_info: UserInfo, runtime: ToolRuntime[Context]) -> str:
    """Save user info."""
    # Access the store - automatically provided by LangSmith
    store = runtime.store # [!code highlight]
    user_id = runtime.context.user_id # [!code highlight]
    # Store data in the store (namespace, key, data)
    store.put(("users",), user_id, user_info) # [!code highlight]
    return "Successfully saved user info."

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    tools=[save_user_info],
    context_schema=Context
)

# Run the agent
agent.invoke(
    {"messages": [{"role": "user", "content": "My name is John Smith"}]},
    # user_id passed in context to identify whose information is being updated
    context=Context(user_id="user_123") # [!code highlight]
)
```

<Note>
  The store is automatically available via `runtime.store` when using LangSmith. You do not need to instantiate or pass a store to `create_agent`.
</Note>
