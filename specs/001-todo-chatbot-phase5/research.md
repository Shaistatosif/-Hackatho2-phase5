# Research: Phase V Todo Chatbot

**Date**: 2026-02-09
**Branch**: `001-todo-chatbot-phase5`

---

## 1. Dapr Integration Patterns

### Decision: Use Dapr HTTP API for all infrastructure

**Rationale**: Constitution mandates no direct Kafka/DB clients. Dapr provides consistent abstraction.

**Alternatives Considered**:
- Direct Kafka clients (kafka-python) - REJECTED: Constitution forbidden
- Direct PostgreSQL (asyncpg) - REJECTED: Constitution forbidden
- Dapr SDK - Acceptable but HTTP API more portable

### Key Patterns

#### Pub/Sub via Dapr
```python
# Publishing events
async def publish_event(topic: str, data: dict):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"http://localhost:3500/v1.0/publish/kafka-pubsub/{topic}",
            json=data
        )

# Subscribing (FastAPI endpoint)
@app.post("/dapr/subscribe")
async def subscribe():
    return [
        {"pubsubname": "kafka-pubsub", "topic": "task-events", "route": "/events/task"},
        {"pubsubname": "kafka-pubsub", "topic": "reminders", "route": "/events/reminder"}
    ]
```

#### State Store via Dapr
```python
# Save state
async def save_task(task_id: str, task: dict):
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:3500/v1.0/state/statestore",
            json=[{"key": f"task-{task_id}", "value": task}]
        )

# Get state
async def get_task(task_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"http://localhost:3500/v1.0/state/statestore/task-{task_id}"
        )
        return resp.json()

# Query state (for search/filter)
async def query_tasks(filter: dict) -> list:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://localhost:3500/v1.0-alpha1/state/statestore/query",
            json={"filter": filter}
        )
        return resp.json()["results"]
```

#### Jobs API via Dapr (Alpha)
```python
# Schedule job
async def schedule_reminder(task_id: int, remind_at: datetime):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"http://localhost:3500/v1.0-alpha1/jobs/reminder-{task_id}",
            json={
                "dueTime": remind_at.isoformat() + "Z",
                "data": {"task_id": task_id, "action": "remind"}
            }
        )

# Delete job (cancel reminder)
async def cancel_reminder(task_id: int):
    async with httpx.AsyncClient() as client:
        await client.delete(
            f"http://localhost:3500/v1.0-alpha1/jobs/reminder-{task_id}"
        )
```

---

## 2. Kafka Best Practices

### Decision: Use Redpanda for local, Strimzi/Redpanda Cloud for production

**Rationale**: Redpanda is Kafka-compatible, simpler to run locally. Strimzi for K8s-native deployment.

**Topic Design**:

| Topic | Partitions | Retention | Purpose |
|-------|------------|-----------|---------|
| `task-events` | 3 | 7 days | Audit, recurring task processing |
| `reminders` | 1 | 1 day | Reminder notifications |
| `task-updates` | 3 | 1 hour | Real-time sync (ephemeral) |

**Event Schema Standards**:
- Use CloudEvents format for interoperability
- Include `specversion`, `type`, `source`, `id`, `time`, `data`
- All timestamps in ISO 8601 UTC

---

## 3. Kubernetes Deployment Patterns

### Decision: Helm charts with environment-specific values

**Rationale**: Constitution requires Helm for cloud deployment.

**Deployment Strategy**:
```yaml
# values-minikube.yaml
replicaCount: 1
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"

# values-aks.yaml
replicaCount: 2
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

**Dapr Annotations**:
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "backend"
  dapr.io/app-port: "8000"
  dapr.io/enable-api-logging: "true"
```

---

## 4. Natural Language Processing

### Decision: Use OpenAI API with MCP tools

**Rationale**: Constitution specifies OpenAI ChatKit for chat interface.

**Pattern**: Define MCP tools for task operations

```python
TOOLS = [
    {
        "name": "create_task",
        "description": "Create a new task",
        "parameters": {
            "title": {"type": "string", "required": True},
            "priority": {"type": "string", "enum": ["High", "Medium", "Low"]},
            "due_at": {"type": "string", "format": "datetime"},
            "tags": {"type": "array", "items": {"type": "string"}}
        }
    },
    {
        "name": "complete_task",
        "description": "Mark a task as complete",
        "parameters": {
            "task_identifier": {"type": "string", "required": True}
        }
    },
    # ... more tools
]
```

---

## 5. Recurring Task Logic

### Decision: Calculate next occurrence on completion event

**Rationale**: Event-driven pattern per Constitution.

**Calculation Logic**:
```python
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def calculate_next_due(current_due: datetime, pattern: str) -> datetime:
    if pattern == "daily":
        return current_due + timedelta(days=1)
    elif pattern == "weekly":
        return current_due + timedelta(weeks=1)
    elif pattern == "monthly":
        return current_due + relativedelta(months=1)
    else:
        raise ValueError(f"Invalid pattern: {pattern}")
```

---

## 6. Real-time Sync via WebSocket

### Decision: WebSocket service subscribes to Kafka, pushes to clients

**Rationale**: Decoupled architecture per Constitution.

**Pattern**:
```
Backend → Kafka (task-updates) → WebSocket Service → Browser clients
```

**Implementation**:
- WebSocket service uses FastAPI WebSocket endpoints
- Clients connect with user_id for filtering
- Server-sent events (SSE) as fallback

---

## 7. Error Handling & Resilience

### Decision: Exponential backoff with circuit breaker

**Rationale**: Constitution requires graceful degradation.

**Retry Pattern**:
```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=60)
)
async def publish_with_retry(topic: str, data: dict):
    await publish_event(topic, data)
```

**Dead Letter Queue**:
- Failed events after max retries → DLQ topic
- Monitor DLQ for operational alerts

---

## Summary

All technical decisions align with Constitution requirements:
- Dapr HTTP API for all infrastructure
- Kafka via Dapr Pub/Sub
- PostgreSQL via Dapr State Store
- Kubernetes with Helm charts
- No direct clients for forbidden technologies
