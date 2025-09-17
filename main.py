"""Main application entry point for SlashRun Simulation API."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
from typing import Dict, Set

from backend.app.core.config import settings
from backend.app.core.database import init_db, close_db
from backend.app.api.auth import router as auth_router
from backend.app.api.users import router as users_router
from backend.app.api.simulation import router as simulation_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("Starting SlashRun Simulation API...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down SlashRun Simulation API...")
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="""
    SlashRun Simulation API - Economic scenario modeling with complete transparency
    
    ## Features
    
    * **Scenario Management**: Create, update, and manage economic simulation scenarios
    * **Time-Step Simulation**: Execute economic models with regime-aware reducers
    * **Complete Audit Trail**: Track every field change with calculation details
    * **Policy Triggers**: Implement tariffs, taxes, mobilization, and regime switches
    * **Data Integration**: Real-time data from World Bank, FRED, IMF, and other sources
    * **Template Generation**: MVS (10 countries) and FIS (30+ countries) templates
    * **Transparent Operations**: Every calculation is audited and explainable
    
    ## Authentication
    
    Most endpoints require authentication. Use `/auth/login` to obtain an access token.
    """,
    lifespan=lifespan,
    debug=settings.debug
)

# Add CORS middleware with expanded origins for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins + ["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# WebSocket connection manager for real-time simulation updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        self.active_connections[room_id].add(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast_to_room(self, room_id: str, message: dict):
        if room_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                self.active_connections[room_id].discard(connection)

manager = ConnectionManager()


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred. Please contact support if the problem persists."
        }
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.version,
        "environment": "development" if settings.debug else "production"
    }


# API Health check endpoint (for consistency with API prefix)
@app.get(f"{settings.api_prefix}/health", tags=["health"])
async def api_health_check():
    """API health check endpoint with API prefix."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.version,
        "environment": "development" if settings.debug else "production"
    }


# API version info
@app.get("/version", tags=["info"])
async def get_version():
    """Get API version information."""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "api_prefix": settings.api_prefix,
        "features": [
            "scenario_management",
            "time_step_simulation", 
            "complete_audit_trail",
            "policy_triggers",
            "data_integration",
            "template_generation",
            "transparent_operations"
        ]
    }


@app.get(f"{settings.api_prefix}", tags=["info"])
async def api_root():
    """API metadata endpoint."""
    return {
        "message": "SlashRun Simulation API",
        "description": "Economic scenario modeling with complete transparency",
        "version": settings.version,
        "docs_url": "/docs",
        "health_url": f"{settings.api_prefix}/health"
    }


# WebSocket endpoint for real-time simulation updates
@app.websocket("/ws/simulation/{scenario_id}")
async def websocket_simulation_updates(websocket: WebSocket, scenario_id: str):
    """WebSocket endpoint for real-time simulation step updates."""
    await manager.connect(websocket, f"scenario_{scenario_id}")
    try:
        while True:
            # Keep connection alive by waiting for messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, f"scenario_{scenario_id}")

# Include routers
app.include_router(auth_router, prefix=f"{settings.api_prefix}/auth", tags=["authentication"])
app.include_router(users_router, prefix=f"{settings.api_prefix}/users", tags=["users"])
app.include_router(simulation_router, prefix=settings.api_prefix, tags=["simulation"])

# Make connection manager available to simulation router
app.state.websocket_manager = manager

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )
