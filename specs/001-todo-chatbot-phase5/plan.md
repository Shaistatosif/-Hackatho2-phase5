# Implementation Plan: Phase V Todo Chatbot

**Branch**: `001-todo-chatbot-phase5` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-todo-chatbot-phase5/spec.md`

---

## Summary

Production-grade event-driven Todo Chatbot with natural language interface, recurring tasks, due date reminders, priorities, tags, search/filter/sort, deployed on Kubernetes with Dapr abstraction and Kafka event streaming. The system consists of multiple microservices communicating exclusively through Dapr APIs and Kafka events.

---

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript/Node.js 20+ (Frontend)
**Primary Dependencies**: FastAPI, Pydantic, httpx, Next.js 14+, OpenAI ChatKit, Dapr SDK
**Storage**: Neon PostgreSQL (Serverless) via Dapr State Store
**Event Streaming**: Kafka via Dapr Pub/Sub (Redpanda local, Redpanda Cloud or Strimzi for cloud)
**Testing**: pytest (backend), Jest (frontend)
**Target Platform**: Kubernetes (Minikube local, AKS/GKE/OKE cloud)
**Project Type**: Microservices (web application with multiple services)
**Performance Goals**: <200ms API p95, <50ms event publishing, 100 req/s sustained
**Constraints**: All infra via Dapr HTTP API, no direct Kafka/DB clients, resource limits enforced
**Scale/Scope**: 100 concurrent users, 10,000 tasks per user, 4 Kafka topics

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. SDD Only** | PASS | All code generated via SDD workflow, Task IDs in comments |
| **II. Event-Driven** | PASS | All CRUD publishes to Kafka, 4 topics defined |
| **III. Dapr Abstraction** | PASS | No direct Kafka/DB clients, all via Dapr HTTP API |
| **IV. Cloud-Native K8s** | PASS | Docker containers, K8s manifests, Helm charts, resource limits |
| **Mandatory Tech Stack** | PASS | FastAPI, Neon PostgreSQL, Kafka, Dapr 1.14+, K8s, Next.js 14+ |
| **Forbidden Tech** | PASS | No kafka-python, psycopg2, hardcoded secrets |
| **Kafka Use Cases** | PASS | Audit, Reminders, Recurring, Real-time Sync all implemented |

---

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-chatbot-phase5/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI specs)
│   ├── backend-api.yaml
│   └── events.yaml
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
services/
├── backend/                    # FastAPI Chat API + MCP Tools
│   ├── src/
│   │   ├── main.py            # FastAPI app entry
│   │   ├── models/            # Pydantic models
│   │   │   ├── task.py
│   │   │   ├── events.py
│   │   │   └── schemas.py
│   │   ├── services/          # Business logic
│   │   │   ├── task_service.py
│   │   │   ├── dapr_client.py
│   │   │   └── chat_handler.py
│   │   ├── api/               # FastAPI routes
│   │   │   ├── tasks.py
│   │   │   ├── chat.py
│   │   │   └── subscriptions.py
│   │   └── mcp/               # MCP tool definitions
│   │       └── tools.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # Next.js Chat Interface
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── TaskList.tsx
│   │   │   └── Notification.tsx
│   │   └── services/
│   │       ├── api.ts
│   │       └── websocket.ts
│   ├── Dockerfile
│   └── package.json
│
├── notification-service/       # Reminder Consumer
│   ├── src/
│   │   ├── main.py
│   │   └── handlers.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── recurring-task-service/     # Recurring Task Consumer
│   ├── src/
│   │   ├── main.py
│   │   └── handlers.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── audit-service/              # Audit Log Consumer
│   ├── src/
│   │   ├── main.py
│   │   └── handlers.py
│   ├── Dockerfile
│   └── requirements.txt
│
└── websocket-service/          # Real-time Sync
    ├── src/
    │   ├── main.py
    │   └── handlers.py
    ├── Dockerfile
    └── requirements.txt

dapr-components/
├── pubsub.yaml                 # Kafka Pub/Sub component
├── statestore.yaml             # PostgreSQL State Store
├── secrets.yaml                # Kubernetes Secrets
└── jobs.yaml                   # Jobs API configuration

kubernetes/
├── minikube/
│   ├── namespace.yaml
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── notification-deployment.yaml
│   ├── recurring-deployment.yaml
│   ├── audit-deployment.yaml
│   ├── websocket-deployment.yaml
│   ├── services.yaml
│   └── configmaps.yaml
└── cloud/
    └── (similar structure with LoadBalancer/Ingress)

helm-charts/
└── todo-chatbot/
    ├── Chart.yaml
    ├── values.yaml
    ├── values-minikube.yaml
    ├── values-aks.yaml
    └── templates/
        ├── deployments.yaml
        ├── services.yaml
        ├── configmaps.yaml
        ├── secrets.yaml
        └── dapr-components.yaml

.github/
└── workflows/
    ├── ci.yaml                 # Build & Test
    └── deploy.yaml             # Deploy to cloud
```

**Structure Decision**: Microservices architecture with 6 services (backend, frontend, notification, recurring-task, audit, websocket) deployed to Kubernetes via Helm charts. Each service is independently deployable with Dapr sidecar.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              KUBERNETES CLUSTER                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────────────┐ │
│  │  Frontend   │    │   Backend   │    │          Dapr Sidecar           │ │
│  │  (Next.js)  │───▶│  (FastAPI)  │◀──▶│  (Pub/Sub, State, Jobs, Secrets)│ │
│  └─────────────┘    └──────┬──────┘    └─────────────────────────────────┘ │
│                            │                                                │
│                            ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         KAFKA (via Dapr Pub/Sub)                        ││
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       ││
│  │  │ task-events │ │  reminders  │ │task-updates │ │   (DLQ)     │       ││
│  │  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └─────────────┘       ││
│  └─────────┼───────────────┼───────────────┼────────────────────────────────┘│
│            │               │               │                                │
│            ▼               ▼               ▼                                │
│  ┌─────────────┐  ┌─────────────────┐  ┌─────────────┐                     │
│  │   Audit     │  │  Notification   │  │  WebSocket  │                     │
│  │  Service    │  │    Service      │  │   Service   │                     │
│  └─────────────┘  └─────────────────┘  └─────────────┘                     │
│            │               │                                                │
│            │               │                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │              Recurring Task Service (consumes task-events)              ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │           Neon PostgreSQL (via Dapr State Store)                        ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Service Responsibilities

| Service | Port | Dapr App ID | Responsibility |
|---------|------|-------------|----------------|
| **Backend** | 8000 | `backend` | Chat API, Task CRUD, MCP Tools, Event Publishing |
| **Frontend** | 3000 | `frontend` | Chat UI, Task Display, WebSocket Client |
| **Notification** | 8001 | `notification` | Consume `reminders`, Send Notifications |
| **Recurring Task** | 8002 | `recurring` | Consume `task-events`, Create Next Occurrence |
| **Audit** | 8003 | `audit` | Consume `task-events`, Persist Audit Log |
| **WebSocket** | 8004 | `websocket` | Consume `task-updates`, Push to Clients |

---

## Kafka Topics

| Topic | Producer | Consumer(s) | Event Types |
|-------|----------|-------------|-------------|
| `task-events` | Backend | Audit, Recurring | created, updated, completed, deleted |
| `reminders` | Backend (via Dapr Jobs) | Notification | reminder.due |
| `task-updates` | Backend | WebSocket | task.changed (for real-time sync) |

---

## Dapr Components

### 1. Pub/Sub (Kafka)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka:9092"  # Redpanda/Strimzi endpoint
    - name: consumerGroup
      value: "todo-chatbot"
    - name: authRequired
      value: "false"
```

### 2. State Store (PostgreSQL)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: neon-secret
        key: connection-string
```

### 3. Jobs API (Reminders)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: jobs
spec:
  type: jobs
  version: v1alpha1
```

---

## API Endpoints (Backend)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Process natural language command |
| GET | `/api/tasks` | List tasks (with filter/sort) |
| POST | `/api/tasks` | Create task |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |
| POST | `/api/tasks/{id}/complete` | Mark complete |
| GET | `/api/audit` | Get audit log |
| POST | `/dapr/subscribe` | Dapr subscription endpoint |

---

## Event Flow Examples

### 1. Create Task with Reminder
```
User: "Add task: Buy groceries tomorrow at 5pm, remind me 1 hour before"
    │
    ▼
Backend (Chat API)
    │
    ├──▶ Parse NL command (MCP/LLM)
    ├──▶ POST Dapr State Store (save task)
    ├──▶ POST Dapr Jobs API (schedule reminder)
    └──▶ POST Dapr Pub/Sub → task-events (created)
                │
                ├──▶ Audit Service → Log event
                └──▶ WebSocket Service → Push to clients
```

### 2. Complete Recurring Task
```
User: "Mark Take vitamins complete"
    │
    ▼
Backend
    │
    ├──▶ Update task status (Dapr State)
    ├──▶ Cancel reminder job (Dapr Jobs)
    └──▶ Publish → task-events (completed)
                │
                └──▶ Recurring Task Service
                        │
                        ├──▶ Detect recurrence_pattern
                        ├──▶ Calculate next due date
                        └──▶ Create new task (via Backend API)
```

### 3. Reminder Fires
```
Dapr Jobs API (at remind_at time)
    │
    ▼
Backend callback endpoint
    │
    └──▶ Publish → reminders topic
                │
                └──▶ Notification Service
                        │
                        └──▶ Push notification to user
```

---

## Complexity Tracking

> No violations - design follows all Constitution principles

| Aspect | Justification |
|--------|---------------|
| 6 Microservices | Required for loose coupling, independent scaling, Kafka consumers |
| Dapr abstraction | Constitution mandate - no direct Kafka/DB clients |
| Helm charts | Constitution mandate - required for cloud deployment |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Dapr Jobs API alpha | Use stable workaround patterns, test thoroughly |
| Kafka unavailable | Exponential backoff, local queue fallback |
| Neon cold start | Connection pooling with warm connections |
| MCP/LLM latency | Cache common command patterns, async processing |

---

## Next Steps

1. **Phase 0**: Generate `research.md` (Dapr patterns, Kafka best practices)
2. **Phase 1**: Generate `data-model.md`, `contracts/`, `quickstart.md`
3. **Phase 2**: Run `/sp.tasks` to generate task breakdown
4. **Phase 3**: Run `/sp.implement` to generate code

---

## References

- [Dapr Documentation](https://docs.dapr.io/)
- [Dapr Jobs API](https://docs.dapr.io/reference/api/jobs_api/)
- [Strimzi Kafka Operator](https://strimzi.io/)
- [Neon PostgreSQL](https://neon.tech/docs)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/docs)
