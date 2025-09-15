# LangGraph FastAPI Integration

## Critical Rule: Async Streaming in APIs
**ALWAYS use async streaming and proper context handling in FastAPI endpoints**

```python
# ✅ CORRECT - Async streaming with context
from fastapi import FastAPI
from sqlmodel import SQLModel
from typing import Optional

@app.post("/chat", response_model=Response)
async def chat(req: Request):
    ctx = MyContext(user_name=req.user_name, db_uri=DB_URI)
    async for update in agent.astream(
        {"messages": [{"role": "user", "content": req.question}]},
        context=ctx.__dict__,
        stream_mode="messages",
    ):
        answer = update["messages"][-1].content
    return Response(answer=answer)

# ❌ WRONG - Sync blocking calls
def chat_sync(req: Request):
    result = agent.invoke(...)  # Blocking
```

## Essential Patterns

### 1. Request/Response Models
**Define clear Pydantic models for API contracts**
```python
from sqlmodel import SQLModel, Field
from typing import Optional

class ChatRequest(SQLModel):
    user_name: str
    question: str
    session_id: Optional[str] = None

class ChatResponse(SQLModel):
    answer: str
    session_id: str
    metadata: Optional[dict] = None
```

### 2. Context Creation from Request
**Build runtime context from request data**
```python
from dataclasses import dataclass
from langgraph.context import ContextSchema

@dataclass
class MyContext(ContextSchema):
    user_name: str
    db_uri: str
    session_id: str

@app.post("/chat")
async def chat(req: ChatRequest):
    # Build context from request
    ctx = MyContext(
        user_name=req.user_name,
        db_uri=DB_URI,
        session_id=req.session_id or f"user_{req.user_name}"
    )
    
        # Use context in agent streaming
        async for update in agent.astream(
            {"messages": [{"role": "user", "content": req.question}]},
            context=ctx.__dict__,
            stream_mode="messages",
        ):
            final_message = update["messages"][-1].content
    
    return ChatResponse(answer=final_message, session_id=ctx.session_id)
```

### 3. Streaming Endpoints
**Implement proper streaming responses for real-time updates**
```python
from fastapi.responses import StreamingResponse
import json

@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    ctx = MyContext(user_name=req.user_name, db_uri=DB_URI)
    
    async def generate_stream():
        async for update in agent.astream(
            {"messages": [{"role": "user", "content": req.question}]},
            context=ctx.__dict__,
            stream_mode="updates",
        ):
            # Yield each update as server-sent events
            yield f"data: {json.dumps(update)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache"}
    )
```

### 4. Error Handling and Validation
**Robust error handling for agent failures**
```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        ctx = MyContext(user_name=req.user_name, db_uri=DB_URI)
        
        # Validate context
        if not ctx.user_name:
            raise HTTPException(status_code=400, detail="user_name is required")
        
        async for update in agent.astream(
            {"messages": [{"role": "user", "content": req.question}]},
            context=ctx.__dict__,
            stream_mode="messages",
        ):
            answer = update["messages"][-1].content
            
        return ChatResponse(answer=answer, session_id=ctx.session_id)
        
    except Exception as e:
        logger.error(f"Chat error for user {req.user_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 5. Agent Lifecycle Management
**Proper agent initialization and reuse**
```python
from contextlib import asynccontextmanager

# Global agent instance
agent = None
store = None
checkpointer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent, store, checkpointer
    
    # Startup: Initialize agent
    store = AsyncPostgresStore.from_conn_string(DB_URI)
    await store.setup()
    
    checkpointer = AsyncPostgresSaver.from_conn_string(DB_URI)
    await checkpointer.setup()
    
    agent = create_react_agent(
        model="anthropic:claude-3-5-sonnet-latest",
        tools=[get_user_email],
        context_schema=MyContext,
        checkpointer=checkpointer,
        store=store,
    )
    
    yield
    
    # Shutdown: Clean up resources
    # Add cleanup logic if needed

app = FastAPI(lifespan=lifespan)
```

## Common Pitfalls

### 1. Blocking Calls in Async Endpoints
```python
# ❌ WRONG - Blocking invoke() call
@app.post("/chat")
async def chat(req: ChatRequest):
    result = agent.invoke({"messages": [...]})  # Blocks async event loop

# ✅ CORRECT - Async streaming
@app.post("/chat")
async def chat(req: ChatRequest):
    async for update in agent.astream({"messages": [...]}):
        result = update
```

### 2. Missing Context in API Calls
```python
# ❌ WRONG - No context passed
async for update in agent.astream({"messages": [...]}):
    pass

# ✅ CORRECT - Context included
async for update in agent.astream(
    {"messages": [...]},
    context=ctx.__dict__,
):
    pass
```

### 3. Poor Error Handling
```python
# ❌ WRONG - Unhandled exceptions
@app.post("/chat")
async def chat(req: ChatRequest):
    # No try/catch - errors crash the endpoint
    async for update in agent.astream(...):
        pass

# ✅ CORRECT - Proper error handling
@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        async for update in agent.astream(...):
            pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 4. Agent Recreation on Every Request
```python
# ❌ WRONG - Recreate agent per request (expensive)
@app.post("/chat")
async def chat(req: ChatRequest):
    agent = create_react_agent(...)  # Recreated every time
    
# ✅ CORRECT - Reuse global agent instance
agent = create_react_agent(...)  # Created once at startup

@app.post("/chat")
async def chat(req: ChatRequest):
    # Reuse existing agent
    async for update in agent.astream(...):
        pass
```

## Complete FastAPI Integration Example

```python
from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel
from dataclasses import dataclass
from langgraph.context import ContextSchema
from langgraph.storage import AsyncPostgresStore
from langgraph.checkpoint.postgres import AsyncPostgresSaver
from langgraph.prebuilt import create_react_agent
from contextlib import asynccontextmanager
import os

# Models
class ChatRequest(SQLModel):
    user_name: str
    question: str
    session_id: str = None

class ChatResponse(SQLModel):
    answer: str
    session_id: str

# Context
@dataclass
class MyContext(ContextSchema):
    user_name: str
    db_uri: str
    session_id: str

# Global agent
agent = None
DB_URI = os.getenv("DATABASE_URL")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    
    # Initialize storage
    store = AsyncPostgresStore.from_conn_string(DB_URI)
    await store.setup()
    
    checkpointer = AsyncPostgresSaver.from_conn_string(DB_URI)
    await checkpointer.setup()
    
    # Create agent
    agent = create_react_agent(
        model="anthropic:claude-3-5-sonnet-latest",
        tools=[get_user_email],
        context_schema=MyContext,
        checkpointer=checkpointer,
        store=store,
    )
    
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        # Build context
        session_id = req.session_id or f"user_{req.user_name}"
        ctx = MyContext(
            user_name=req.user_name,
            db_uri=DB_URI,
            session_id=session_id
        )
        
        # Stream agent response
        async for update in agent.astream(
            {"messages": [{"role": "user", "content": req.question}]},
            context=ctx.__dict__,
            stream_mode="messages",
        ):
            answer = update["messages"][-1].content
            
        return ChatResponse(answer=answer, session_id=session_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
```

## Quick Reference

- **Async Only**: Always use `async def` and `agent.astream()`
- **Context Required**: Pass context dict to all agent calls
- **Error Handling**: Wrap agent calls in try/except blocks
- **Agent Reuse**: Initialize agent once at startup, reuse per request
- **Thread Management**: Use consistent thread IDs in context for conversation persistence
- **Stream Modes**: Use `"messages"` for final responses, `"updates"` for progress

**Memory Aid**: "Async streaming, context passing, proper error handling, agent reuse."
