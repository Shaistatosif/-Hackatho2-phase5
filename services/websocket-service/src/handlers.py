# T085 - WebSocket Event Handlers
# Phase V Todo Chatbot - WebSocket Broadcasting
"""
Handlers for managing WebSocket connections and broadcasting task updates.
"""

import json
from typing import Dict, Set

import structlog
from fastapi import WebSocket

logger = structlog.get_logger()


class ConnectionManager:
    """
    Manages WebSocket connections grouped by user_id.
    Enables targeted broadcasting of task updates to specific users.
    """

    def __init__(self):
        # Map user_id to set of active WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """
        Accept a new WebSocket connection.
        """
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)
        logger.info(
            "client_connected",
            user_id=user_id,
            total_connections=self.get_connection_count()
        )

    def disconnect(self, websocket: WebSocket, user_id: str):
        """
        Remove a WebSocket connection.
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        logger.info(
            "client_disconnected",
            user_id=user_id,
            total_connections=self.get_connection_count()
        )

    async def disconnect_all(self):
        """
        Disconnect all clients (for shutdown).
        """
        for user_id, connections in list(self.active_connections.items()):
            for websocket in list(connections):
                try:
                    await websocket.close()
                except Exception:
                    pass
        self.active_connections.clear()

    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        return sum(len(conns) for conns in self.active_connections.values())

    def get_user_connections(self, user_id: str) -> Set[WebSocket]:
        """Get all connections for a specific user."""
        return self.active_connections.get(user_id, set())

    async def send_to_user(self, user_id: str, message: dict):
        """
        Send a message to all connections for a specific user.
        """
        connections = self.get_user_connections(user_id)

        if not connections:
            logger.debug("no_connections_for_user", user_id=user_id)
            return

        disconnected = set()

        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(
                    "send_failed",
                    user_id=user_id,
                    error=str(e)
                )
                disconnected.add(websocket)

        # Clean up disconnected sockets
        for ws in disconnected:
            self.disconnect(ws, user_id)

        if connections - disconnected:
            logger.info(
                "message_sent",
                user_id=user_id,
                recipients=len(connections - disconnected)
            )

    async def broadcast(self, message: dict):
        """
        Broadcast a message to all connected clients.
        """
        for user_id in list(self.active_connections.keys()):
            await self.send_to_user(user_id, message)


async def handle_task_update(manager: ConnectionManager, event: dict) -> None:
    """
    T085 - Process a task update event and broadcast to relevant clients.

    Args:
        manager: WebSocket connection manager
        event: Task update event from Kafka
    """
    data = event.get("data", event)
    user_id = data.get("user_id")

    if not user_id:
        logger.warning("no_user_id_in_event")
        return

    # Build WebSocket message
    message = {
        "type": "task_update",
        "action": data.get("action", event.get("type", "").split(".")[-1]),
        "task_id": str(data.get("task_id", "")),
        "task": data.get("task_data"),
        "timestamp": event.get("time", data.get("timestamp"))
    }

    # Send to user's connections
    await manager.send_to_user(user_id, message)

    logger.info(
        "task_update_broadcast",
        user_id=user_id,
        action=message["action"],
        task_id=message["task_id"]
    )
