# T063 - Recurring Task Service Main
# Phase V Todo Chatbot - Recurring Task Handler
"""
Recurring task service that subscribes to task-events topic
and creates new task occurrences when recurring tasks are completed.
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

SERVICE_NAME = "recurring"
SERVICE_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("service_starting", service=SERVICE_NAME, version=SERVICE_VERSION)
    yield
    logger.info("service_stopped", service=SERVICE_NAME)


app = FastAPI(
    title="Recurring Task Service",
    description="Phase V Todo Chatbot - Recurring task handler",
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
    Subscribe to task-events topic for completed events.
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
    T064 - Handle task events from Kafka.
    Called by Dapr when a message arrives on task-events topic.
    Only processes task.completed events for recurring tasks.
    """
    try:
        body = await request.json()
        event_type = body.get("type", "")

        # Only process completed events
        if event_type != "task.completed":
            logger.debug("ignoring_event", event_type=event_type)
            return {"status": "SUCCESS"}

        logger.info("task_completed_received", event=body)

        # Handle the recurring task logic
        await handle_task_event(body)

        return {"status": "SUCCESS"}
    except Exception as e:
        logger.error("task_event_processing_failed", error=str(e))
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
        "description": "Recurring Task Service - auto-creates next occurrence"
    }
