# T083, T084 - WebSocket Service Main
# Phase V Todo Chatbot - Real-time Sync Handler
"""
WebSocket service that subscribes to task-updates topic
and broadcasts changes to connected clients.
"""

import os
from contextlib import asynccontextmanager
from typing import Set

import structlog
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from .handlers import ConnectionManager, handle_task_update

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

SERVICE_NAME = "websocket"
SERVICE_VERSION = "1.0.0"

# Global connection manager
manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("service_starting", service=SERVICE_NAME, version=SERVICE_VERSION)
    yield
    # Disconnect all clients on shutdown
    await manager.disconnect_all()
    logger.info("service_stopped", service=SERVICE_NAME)


app = FastAPI(
    title="WebSocket Service",
    description="Phase V Todo Chatbot - Real-time sync handler",
    version=SERVICE_VERSION,
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "connected_clients": manager.get_connection_count()
    }


@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """
    T084 - Dapr subscription configuration.
    Subscribe to task-updates topic for real-time sync.
    """
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-updates",
            "route": "/events/task-update",
            "metadata": {
                "rawPayload": "true"
            }
        }
    ]


@app.post("/events/task-update")
async def receive_task_update(request: Request):
    """
    Handle task update events from Kafka.
    Called by Dapr when a message arrives on task-updates topic.
    Broadcasts to all connected WebSocket clients.
    """
    try:
        body = await request.json()
        logger.info("task_update_received", event_type=body.get("type"))

        # T085 - Broadcast to connected clients
        await handle_task_update(manager, body)

        return {"status": "SUCCESS"}
    except Exception as e:
        logger.error("task_update_processing_failed", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"status": "RETRY", "message": str(e)}
        )


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time task updates.
    Clients connect with their user_id to receive their task updates.
    """
    await manager.connect(websocket, user_id)
    logger.info("websocket_connected", user_id=user_id)

    try:
        while True:
            # Keep connection alive, receive any client messages
            data = await websocket.receive_text()
            logger.debug("websocket_message", user_id=user_id, data=data)

            # Echo back acknowledgment
            await websocket.send_json({"type": "ack", "message": "received"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info("websocket_disconnected", user_id=user_id)


@app.get("/")
async def root():
    """Service info endpoint."""
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "description": "WebSocket Service - real-time task sync",
        "websocket_url": "/ws/{user_id}",
        "connected_clients": manager.get_connection_count()
    }
