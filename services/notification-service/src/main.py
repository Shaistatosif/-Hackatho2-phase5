# T056 - Notification Service Main
# Phase V Todo Chatbot - Reminder Notification Handler
"""
Notification service that subscribes to reminders topic
and sends notifications when tasks are due.
"""

import os
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .handlers import handle_reminder_event

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

SERVICE_NAME = "notification"
SERVICE_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("service_starting", service=SERVICE_NAME, version=SERVICE_VERSION)
    yield
    logger.info("service_stopped", service=SERVICE_NAME)


app = FastAPI(
    title="Notification Service",
    description="Phase V Todo Chatbot - Reminder notification handler",
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
    Subscribe to reminders topic.
    """
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/events/reminder",
            "metadata": {
                "rawPayload": "true"
            }
        }
    ]


@app.post("/events/reminder")
async def receive_reminder(request: Request):
    """
    T057 - Handle reminder events from Kafka.
    Called by Dapr when a message arrives on reminders topic.
    """
    try:
        body = await request.json()
        logger.info("reminder_received", event=body)

        # Handle the reminder
        await handle_reminder_event(body)

        return {"status": "SUCCESS"}
    except Exception as e:
        logger.error("reminder_processing_failed", error=str(e))
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
        "description": "Notification Service - handles reminder notifications"
    }
