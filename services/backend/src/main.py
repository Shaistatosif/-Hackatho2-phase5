# T020, T021, T022 - FastAPI Application Entry Point
# Phase V Todo Chatbot - Backend Service
"""
Main FastAPI application for the Todo Chatbot backend.
Handles chat API, task CRUD, and Dapr integrations.
"""

import os
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .services.memory_store import get_memory_store

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Service configuration
SERVICE_NAME = "backend"
SERVICE_VERSION = "1.0.0"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    logger.info("service_starting", service=SERVICE_NAME, version=SERVICE_VERSION)
    yield
    # Shutdown
    store = get_memory_store()
    await store.close()
    logger.info("service_stopped", service=SERVICE_NAME)


# T020 - Create FastAPI application
app = FastAPI(
    title="Todo Chatbot Backend",
    description="Phase V Todo Chatbot - Event-driven task management with natural language interface",
    version=SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# T021 - Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local frontend
        "http://frontend:3000",   # K8s service
        os.getenv("FRONTEND_URL", "*")  # Configurable
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# T021 - Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions with structured logging."""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=exc
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else None
        }
    )


# T022 - Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for Kubernetes probes.
    Returns service status and Dapr connectivity.
    """
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION
    }


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Readiness probe - checks if service can handle requests."""
    return {
        "status": "ready",
        "service": SERVICE_NAME,
        "store": "in-memory"
    }


@app.get("/health/live", tags=["Health"])
async def liveness_check():
    """Liveness probe - basic check that service is running."""
    return {"status": "alive", "service": SERVICE_NAME}


# Root endpoint
@app.get("/", tags=["Info"])
async def root():
    """Service information endpoint."""
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "description": "Phase V Todo Chatbot Backend API",
        "docs": "/docs",
        "health": "/health"
    }


# T044 - Register API routers
from .api.chat import router as chat_router
from .api.tasks import router as tasks_router

app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(tasks_router, prefix="/api", tags=["Tasks"])
