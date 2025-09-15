"""Main application entry point for SlashRun Simulation API."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .core.config import settings
from .core.database import init_db, close_db
from .api.auth import router as auth_router
from .api.simulation import router as simulation_router

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


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


# Root endpoint
@app.get("/", tags=["info"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to SlashRun Simulation API",
        "description": "Economic scenario modeling with complete transparency",
        "version": settings.version,
        "docs_url": "/docs",
        "health_url": "/health"
    }


# Include routers
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(simulation_router, prefix=settings.api_prefix)


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )
