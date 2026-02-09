# T089 - Audit Service Main
# Phase V Todo Chatbot - Audit Log Handler
"""
Audit service that subscribes to task-events topic
and persists audit log entries.
"""

import os
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .handlers import handle_task_event

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

SERVICE_NAME = "audit"
SERVICE_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("service_starting", service=SERVICE_NAME, version=SERVICE_VERSION)
    yield
    logger.info("service_stopped", service=SERVICE_NAME)


app = FastAPI(
    title="Audit Service",
    description="Phase V Todo Chatbot - Audit log handler",
    version=SERVICE_VERSION,
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": SERVICE_NAME, "version": SERVICE_VERSION}


@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """
    Dapr subscription configuration.
    Subscribe to task-events topic for all events.
    """
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/task",
            "metadata": {
                "rawPayload": "true"
            }
        }
    ]


@app.post("/events/task")
async def receive_task_event(request: Request):
    """
    T090 - Handle task events from Kafka.
    Called by Dapr when a message arrives on task-events topic.
    Stores all events in audit log.
    """
    try:
        body = await request.json()
        logger.info("task_event_received", event_type=body.get("type"))

        # Handle the audit logging
        await handle_task_event(body)

        return {"status": "SUCCESS"}
    except Exception as e:
        logger.error("audit_processing_failed", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"status": "RETRY", "message": str(e)}
        )


@app.get("/")
async def root():
    """Service info endpoint."""
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "description": "Audit Service - persists audit log entries"
    }
