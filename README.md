# Phase V Todo Chatbot

**Event-driven task management with natural language interface**

[![CI](https://github.com/phase-v/todo-chatbot/actions/workflows/ci.yaml/badge.svg)](https://github.com/phase-v/todo-chatbot/actions/workflows/ci.yaml)

## Overview

A production-grade Todo Chatbot built with microservices architecture, featuring:

- **Natural Language Interface** - Create and manage tasks via chat
- **Recurring Tasks** - Daily, weekly, monthly patterns with auto-regeneration
- **Due Dates & Reminders** - Scheduled notifications via Dapr Jobs API
- **Real-time Sync** - WebSocket-based multi-client synchronization
- **Event Streaming** - Kafka-based audit log and event processing
- **Kubernetes Native** - Helm charts for local and cloud deployment

## Architecture

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
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                       ││
│  │  │ task-events │ │  reminders  │ │task-updates │                       ││
│  │  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘                       ││
│  └─────────┼───────────────┼───────────────┼────────────────────────────────┘│
│            │               │               │                                │
│            ▼               ▼               ▼                                │
│  ┌─────────────┐  ┌─────────────────┐  ┌─────────────┐                     │
│  │   Audit     │  │  Notification   │  │  WebSocket  │                     │
│  │  Service    │  │    Service      │  │   Service   │                     │
│  └─────────────┘  └─────────────────┘  └─────────────┘                     │
│                                                                             │
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

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend API | FastAPI (Python 3.11+) |
| Frontend | Next.js 14+ (TypeScript) |
| Database | Neon PostgreSQL (Serverless) |
| Event Streaming | Kafka via Redpanda |
| Orchestration | Kubernetes + Dapr |
| Package Manager | Helm 3.x |
| CI/CD | GitHub Actions |

## Services

| Service | Port | Description |
|---------|------|-------------|
| Backend | 8000 | Chat API, Task CRUD, MCP Tools |
| Frontend | 3000 | Chat UI, Task Display |
| Notification | 8001 | Reminder notifications |
| Recurring | 8002 | Auto-regenerate completed tasks |
| Audit | 8003 | Event log persistence |
| WebSocket | 8004 | Real-time client sync |

## Kafka Topics

| Topic | Producer | Consumer(s) |
|-------|----------|-------------|
| `task-events` | Backend | Audit, Recurring |
| `reminders` | Backend (Jobs) | Notification |
| `task-updates` | Backend | WebSocket |

## Quick Start (Minikube)

### Prerequisites

- Docker Desktop or Minikube
- kubectl CLI
- Dapr CLI
- Helm 3.x
- Node.js 20+
- Python 3.11+

### 1. Start Minikube

```bash
minikube start --memory=8192 --cpus=4
minikube addons enable ingress
```

### 2. Install Dapr

```bash
dapr init -k
dapr status -k
```

### 3. Deploy Kafka (Redpanda)

```bash
kubectl create namespace kafka
helm repo add redpanda https://charts.redpanda.com
helm install redpanda redpanda/redpanda -n kafka \
  --set statefulset.replicas=1 \
  --set resources.cpu.cores=1 \
  --set resources.memory.container.max=2Gi

# Wait for ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redpanda -n kafka --timeout=300s
```

### 4. Set Secrets

```bash
# Create secrets
kubectl create secret generic neon-secret \
  --from-literal=connection-string="postgresql://user:pass@host.neon.tech/db?sslmode=require"

kubectl create secret generic api-secrets \
  --from-literal=openai-api-key="sk-..."
```

### 5. Deploy with Helm

```bash
helm install todo-chatbot helm-charts/todo-chatbot \
  -f helm-charts/todo-chatbot/values-minikube.yaml
```

### 6. Access Services

```bash
# Port forward
kubectl port-forward svc/backend 8000:8000 &
kubectl port-forward svc/frontend 3000:3000 &

# Open browser
open http://localhost:3000
```

## Development Mode (Without Kubernetes)

### Backend

```bash
cd services/backend
pip install -r requirements.txt
dapr run --app-id backend --app-port 8000 -- uvicorn src.main:app --reload
```

### Frontend

```bash
cd services/frontend
npm install
npm run dev
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Example Chat Commands

```
"Add task: Buy groceries with high priority"
"Show my tasks"
"Mark Buy groceries as complete"
"Add task: Take vitamins every day" (recurring)
"Find tasks about shopping"
"Delete the groceries task"
```

## Project Structure

```
├── services/
│   ├── backend/              # FastAPI Chat API
│   ├── frontend/             # Next.js Chat UI
│   ├── notification-service/ # Reminder consumer
│   ├── recurring-task-service/ # Recurring logic
│   ├── audit-service/        # Event logging
│   └── websocket-service/    # Real-time sync
├── dapr-components/          # Dapr component configs
├── kubernetes/minikube/      # K8s manifests
├── helm-charts/todo-chatbot/ # Helm charts
├── .github/workflows/        # CI/CD
└── specs/                    # SDD artifacts
```

## Constitution Compliance

This project follows the Phase V Hackathon Constitution:

- **SDD Only**: All code generated via Spec-Driven Development
- **Event-Driven**: All CRUD operations publish to Kafka
- **Dapr Abstraction**: No direct Kafka/DB clients
- **Cloud-Native K8s**: Docker, K8s manifests, Helm charts, resource limits

## License

MIT
