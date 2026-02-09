<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version change: 0.0.0 → 1.0.0 (MAJOR - initial ratification)
Modified principles: N/A (new document)
Added sections:
  - Core Architectural Principles (4 principles)
  - Technology Stack Constraints (Mandatory, Preferred, Forbidden)
  - Feature Implementation Standards (Advanced, Intermediate, Kafka Use Cases)
  - Deployment Standards (Minikube, Cloud, Helm Charts)
  - Code Quality Standards (Python/FastAPI, Dapr, Kubernetes)
  - Kafka Event Schemas
  - Testing & Validation Requirements
  - Security & Compliance
  - Submission Requirements
  - Performance & Scalability Targets
  - Failure Modes & Error Handling
  - Deviation Policy
  - Final Validation Checklist
  - Appendices (Quick Reference Commands, Critical Gotchas)
Removed sections: N/A
Templates requiring updates:
  - .specify/templates/plan-template.md: ⚠ pending (Constitution Check section)
  - .specify/templates/spec-template.md: ✅ compatible (no changes needed)
  - .specify/templates/tasks-template.md: ⚠ pending (add Kafka/Dapr task types)
Follow-up TODOs: None
================================================================================
-->

# Phase V Todo Chatbot Constitution

## Purpose

This constitution defines the **non-negotiable principles, architectural constraints, and quality standards** for Phase V of the Todo Chatbot Hackathon. All agents, developers, and implementation decisions MUST align with these principles.

**Project Goal**: Deploy a production-grade, event-driven Todo Chatbot with advanced features to Kubernetes (Minikube locally, then AKS/GKE/OKE in cloud) using Dapr and Kafka.

---

## Core Principles

### I. Spec-Driven Development (SDD) ONLY

All code MUST be generated via Claude Code following the SDD workflow. No manual coding or improvisation permitted.

- **Workflow**: Specify → Plan → Tasks → Implement
- Every feature MUST have a complete specification before any code is written
- All agents MUST reference Task IDs in code comments
- No "vibe coding" allowed

**Rationale**: Ensures traceability, consistency, and quality across all implementations. Enables audit of design decisions.

### II. Event-Driven Architecture

All task operations MUST publish events to Kafka. Services communicate through events, NOT direct API calls.

- **Primary Pattern**: Event sourcing via Kafka topics
- Loose coupling mandatory - services MUST be independently deployable
- **Required Topics**: `task-events`, `reminders`, `task-updates`

**Rationale**: Enables decoupled microservices, audit trails, real-time synchronization, and scalable event processing.

### III. Microservices with Dapr Abstraction

All infrastructure interactions MUST go through Dapr sidecars. NO direct Kafka/database client libraries in application code.

- Applications communicate via Dapr HTTP API (port 3500)
- Dapr components define infrastructure (YAML configuration)
- Services MUST be swappable without code changes

**Rationale**: Provides infrastructure abstraction, portability across environments, and consistent API patterns.

### IV. Cloud-Native & Kubernetes-First

All services MUST be containerized and deployed to Kubernetes with proper resource management.

- Docker containers required for all services
- Kubernetes manifests required for all deployments
- Helm charts preferred for complex deployments
- Services MUST be horizontally scalable
- Resource limits and requests MUST be defined

**Rationale**: Ensures production-ready deployments with consistent behavior across local and cloud environments.

---

## Technology Stack Constraints

### Mandatory Technologies

These CANNOT be substituted:

| Layer | Technology | Version | Justification |
|-------|-----------|---------|---------------|
| **Backend** | FastAPI | Latest | Async support, MCP integration |
| **Database** | Neon PostgreSQL | Serverless | Free tier, managed service |
| **Event Streaming** | Kafka (Redpanda/Strimzi) | Latest | Event-driven core requirement |
| **Service Mesh** | Dapr | 1.14+ | Abstraction layer mandate |
| **Orchestration** | Kubernetes | 1.28+ | Production deployment target |
| **Local K8s** | Minikube | Latest | Local development standard |
| **Cloud K8s** | AKS/GKE/OKE | Latest | Phase V deployment target |
| **Frontend** | Next.js | 14+ | Phase II integration |
| **Chat Interface** | OpenAI ChatKit | Latest | Phase III requirement |
| **MCP Protocol** | Python SDK | Latest | Tool integration standard |
| **CI/CD** | GitHub Actions | N/A | Automation requirement |

### Preferred Technologies

Recommended unless justified otherwise:

- **Container Registry**: Docker Hub or GitHub Container Registry
- **Secrets Management**: Dapr Secrets API (Kubernetes Secrets backend)
- **Monitoring**: Kubernetes native (kubectl logs, metrics-server)
- **Kafka Provider**:
  - Local: Redpanda (Docker) or Strimzi Operator
  - Cloud: Redpanda Cloud Serverless (free tier) or Strimzi self-hosted
- **State Management**: Dapr State Store (PostgreSQL backend)
- **Jobs Scheduling**: Dapr Jobs API (NOT cron bindings)

### Forbidden Technologies

These are explicitly prohibited:

- Direct Kafka client libraries (`kafka-python`, `aiokafka`) in app code
- Direct database clients (`psycopg2`, `asyncpg`) for state (use Dapr State API)
- Hardcoded connection strings or credentials in code
- Polling-based cron jobs (use Dapr Jobs API)
- Synchronous blocking operations in FastAPI
- Manual secret management (use Dapr Secrets or K8s Secrets)
- Stateful deployments without persistent volumes

---

## Feature Implementation Standards

### Advanced Features (MUST IMPLEMENT)

#### Recurring Tasks
- **Pattern**: Event-driven via Kafka
- When task marked complete → publish `task.completed` event
- Recurring Task Service consumes event → creates next occurrence
- MUST support: daily, weekly, monthly recurrence patterns
- MUST persist recurrence rules in database

#### Due Dates & Reminders
- **Pattern**: Dapr Jobs API (exact-time scheduling)
- When task created with due date → schedule job via Dapr Jobs API
- Job fires at `remind_at` time → publishes `reminder.due` event
- Notification Service consumes → sends notification
- NO polling - reminders fire at exact scheduled time

### Intermediate Features (MUST IMPLEMENT)

From Phase IV, must be fully functional:

- **Priorities**: High/Medium/Low with filtering
- **Tags**: Multiple tags per task, tag-based search
- **Search**: Full-text search across title and description
- **Filter**: By status, priority, tags, due date
- **Sort**: By created_at, due_date, priority

### Kafka Use Cases (ALL REQUIRED)

| Use Case | Producer | Consumer | Topic | Purpose |
|----------|----------|----------|-------|---------|
| **Audit Log** | Chat API (all CRUD) | Audit Service | `task-events` | Complete operation history |
| **Reminders** | Chat API (due date set) | Notification Service | `reminders` | Scheduled notifications |
| **Recurring Tasks** | Chat API (complete event) | Recurring Task Service | `task-events` | Auto-create next occurrence |
| **Real-time Sync** | Chat API (any change) | WebSocket Service | `task-updates` | Multi-client synchronization |

---

## Deployment Standards

### Part B: Local Deployment (Minikube)

**Acceptance Criteria**:
- [ ] Minikube cluster running with Dapr installed (`dapr init -k`)
- [ ] All services deployed as Kubernetes Deployments
- [ ] Dapr components configured: Pub/Sub (Kafka), State (PostgreSQL), Secrets, Jobs API
- [ ] Kafka running (Redpanda container or Strimzi operator)
- [ ] All 4 Kafka use cases demonstrated
- [ ] Services accessible via `kubectl port-forward`
- [ ] Complete logs showing event flow through Kafka

### Part C: Cloud Deployment (AKS/GKE/OKE)

**Acceptance Criteria**:
- [ ] Kubernetes cluster provisioned (AKS/GKE/OKE)
- [ ] Dapr installed on cloud cluster
- [ ] Kafka on Redpanda Cloud Serverless OR Strimzi self-hosted
- [ ] CI/CD pipeline via GitHub Actions (build → push → deploy)
- [ ] Monitoring configured (kubectl top, logs aggregation)
- [ ] Public URLs accessible for frontend and backend
- [ ] SSL/TLS configured (Let's Encrypt or cloud provider)
- [ ] Resource limits enforced (CPU/Memory)

### Helm Charts (REQUIRED for Cloud)

Phase IV Helm charts MUST be used. Charts MUST include:
- Deployments for all services
- Services (ClusterIP/LoadBalancer)
- ConfigMaps for non-sensitive config
- Secrets for credentials
- Dapr Component definitions
- Ingress rules (if applicable)

---

## Code Quality Standards

### Python/FastAPI Standards

```python
# MANDATORY: Every file must have this header
"""
Task: [TASK_ID from speckit.tasks]
Spec: [Section reference from speckit.specify]
Plan: [Component reference from speckit.plan]
"""
```

**Required Patterns**:
- Async/await for all I/O operations
- Type hints on all function signatures
- Pydantic models for request/response validation
- FastAPI dependency injection for services
- HTTPException with proper status codes
- Structured logging (not print statements)

### Dapr Integration Patterns

```python
# CORRECT: Publish via Dapr (NO direct Kafka client)
import httpx

async def publish_event(topic: str, event: dict):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"http://localhost:3500/v1.0/publish/kafka-pubsub/{topic}",
            json=event
        )

# CORRECT: Save state via Dapr (NO direct DB client)
async def save_state(key: str, value: dict):
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:3500/v1.0/state/statestore",
            json=[{"key": key, "value": value}]
        )

# CORRECT: Schedule job via Dapr Jobs API
async def schedule_reminder(task_id: int, remind_at: datetime):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"http://localhost:3500/v1.0-alpha1/jobs/reminder-{task_id}",
            json={
                "dueTime": remind_at.isoformat(),
                "data": {"task_id": task_id}
            }
        )
```

### Kubernetes Manifest Standards

```yaml
# MANDATORY: All Deployments must have:
apiVersion: apps/v1
kind: Deployment
metadata:
  name: service-name
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "service-name"
    dapr.io/app-port: "8000"
spec:
  replicas: 2  # Minimum 2 for production
  template:
    spec:
      containers:
      - name: app
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

---

## Kafka Event Schemas

### Task Event Schema

```python
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"
    DELETED = "deleted"

class TaskEvent(BaseModel):
    event_type: EventType
    task_id: int
    task_data: dict  # Full task object
    user_id: str
    timestamp: datetime
    metadata: dict | None = None
```

### Reminder Event Schema

```python
class ReminderEvent(BaseModel):
    task_id: int
    title: str
    due_at: datetime
    remind_at: datetime
    user_id: str
    notification_channels: list[str] = ["email"]  # Future: push, sms
```

---

## Testing & Validation Requirements

### Pre-Deployment Checklist

**Local (Minikube)**:
- [ ] All services start without errors
- [ ] Dapr sidecars inject successfully
- [ ] Kafka topics auto-created
- [ ] Events flow through Kafka (verify with `kubectl logs`)
- [ ] Reminders fire at scheduled times
- [ ] Recurring tasks auto-create next occurrence
- [ ] Search/filter/sort work correctly

**Cloud**:
- [ ] CI/CD pipeline executes successfully
- [ ] Services accessible via public URLs
- [ ] SSL certificates valid
- [ ] Monitoring shows metrics
- [ ] Load testing passes (100 concurrent users minimum)

### Event Flow Validation

For EVERY Kafka use case, logs MUST show:
```
[Producer] Published event to {topic}: {event_id}
[Kafka] Event {event_id} committed to partition {N}
[Consumer] Received event from {topic}: {event_id}
[Consumer] Processed event successfully
```

---

## Security & Compliance

### Secrets Management

- **NO secrets in code or Git** - automatic failure
- Use Dapr Secrets API or Kubernetes Secrets
- Secrets injected as environment variables
- Rotate secrets regularly (manual for hackathon)

### Network Security

- Dapr mTLS enabled for inter-service communication
- Kubernetes Network Policies (optional for hackathon)
- API authentication required (JWT or API keys)
- HTTPS only for production endpoints

### Database Security

- Connection pooling mandatory (SQLModel/SQLAlchemy)
- Prepared statements to prevent SQL injection
- No raw SQL queries without validation

---

## Submission Requirements

### GitHub Repository Structure

```
/
├── specs/
│   ├── sp.constitution (this file)
│   ├── sp.specify
│   ├── sp.plan
│   └── sp.tasks
├── AGENTS.md (agent instructions)
├── CLAUDE.md (Claude Code shim: @AGENTS.md)
├── README.md (setup instructions)
├── .github/workflows/ (CI/CD pipelines)
├── services/
│   ├── backend/
│   ├── frontend/
│   ├── notification-service/
│   └── recurring-task-service/
├── kubernetes/
│   ├── minikube/
│   └── cloud/
├── helm-charts/
└── dapr-components/
```

### README.md Requirements

MUST include:
1. Architecture diagram (showing Kafka + Dapr + services)
2. Local setup instructions (Minikube + Dapr)
3. Cloud deployment guide (AKS/GKE/OKE)
4. Kafka topic descriptions
5. Dapr component explanations
6. Testing instructions
7. Deployed URLs (frontend, backend, chatbot)

### Demo Video (90 seconds MAX)

MUST demonstrate:
- [ ] Spec-driven workflow (show speckit files)
- [ ] Creating recurring task → auto-creates next occurrence
- [ ] Setting due date → reminder fires
- [ ] Search/filter/sort functionality
- [ ] Kafka event flow (show logs)
- [ ] Cloud deployment (show live URLs)

**Judges stop watching after 90 seconds - front-load the best content!**

---

## Performance & Scalability Targets

### Response Time Requirements

- API endpoints: < 200ms (p95)
- Event publishing: < 50ms
- Reminder scheduling: < 100ms
- Search queries: < 500ms

### Throughput Requirements

- Minimum 100 requests/second sustained
- Kafka topics handle 1000 events/second
- Horizontal scaling demonstrated (2+ replicas)

### Resource Limits

**Per Service**:
- Memory: 256Mi limit, 128Mi request
- CPU: 200m limit, 100m request
- Startup time: < 30 seconds

---

## Failure Modes & Error Handling

### Kafka Connection Failures

- Services MUST retry with exponential backoff
- Dead letter queue for failed events
- Graceful degradation (e.g., in-memory queue)

### Dapr Sidecar Failures

- Applications detect sidecar unavailability
- Return HTTP 503 Service Unavailable
- Log errors clearly for debugging

### Database Failures

- Connection pool exhaustion handled
- Retry logic with circuit breaker pattern
- Read replicas for failover (optional)

---

## Deviation Policy

### How to Request Changes

If any principle conflicts with implementation reality:

1. **Stop implementation immediately**
2. Create a deviation request in `sp.specify`:
```markdown
## DEVIATION REQUEST
**From**: Constitution §X.Y
**Reason**: [Detailed justification]
**Proposed Alternative**: [Specific solution]
**Impact Assessment**: [What breaks/changes]
```
3. Update `sp.plan` to reflect proposed change
4. Get explicit approval before proceeding
5. Update Constitution if approved

### Hierarchy of Truth

When conflicts arise:
1. **Constitution** (this file) - principles & constraints
2. **Specify** - requirements & acceptance criteria
3. **Plan** - architecture & design decisions
4. **Tasks** - implementation breakdown

Lower levels CANNOT override higher levels without explicit deviation approval.

---

## Final Validation Checklist

Before submission, run this checklist:

**Spec Compliance**:
- [ ] All code references Task IDs in comments
- [ ] No code exists without corresponding task
- [ ] All features in `sp.specify` are implemented
- [ ] All components in `sp.plan` are deployed

**Technology Compliance**:
- [ ] NO direct Kafka/DB clients in app code
- [ ] All infrastructure via Dapr HTTP API
- [ ] All services have Dapr sidecars
- [ ] Kubernetes manifests have resource limits

**Deployment Compliance**:
- [ ] Minikube deployment works locally
- [ ] Cloud deployment accessible via URLs
- [ ] CI/CD pipeline executes without errors
- [ ] All 4 Kafka use cases demonstrated

**Submission Compliance**:
- [ ] Public GitHub repository with all code
- [ ] `/specs` folder with all spec files
- [ ] CLAUDE.md and AGENTS.md present
- [ ] README.md complete with diagrams
- [ ] 90-second demo video uploaded
- [ ] WhatsApp number provided

---

## Appendix A: Quick Reference Commands

### Minikube Setup

```bash
# Start Minikube
minikube start --memory=8192 --cpus=4

# Install Dapr
dapr init -k

# Deploy Kafka (Strimzi)
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka
kubectl apply -f kafka-cluster.yaml

# Deploy services
kubectl apply -f kubernetes/minikube/

# Port forward
kubectl port-forward svc/frontend 3000:3000
kubectl port-forward svc/backend 8000:8000
```

### Cloud Deployment (GitHub Actions)

```yaml
# .github/workflows/deploy.yml triggers on push to main
# Automatically builds, pushes, and deploys to AKS/GKE/OKE
```

---

## Appendix B: Critical Gotchas

1. **Dapr Jobs API is alpha** - use `v1.0-alpha1` in endpoint path
2. **Kafka topic auto-creation** - ensure `auto.create.topics.enable=true`
3. **Neon DB connection pooling** - use `?pooling=true` in connection string
4. **Minikube ingress** - run `minikube addons enable ingress` first
5. **Dapr sidecar readiness** - wait for sidecar before app starts (use init containers or health checks)
6. **Kubernetes resource limits** - without them, pods can be evicted unpredictably
7. **GitHub Actions secrets** - add KUBECONFIG and registry credentials to repo secrets

---

## Governance

This constitution is the authoritative source for all Phase V development decisions. It supersedes all other practices and documentation when conflicts arise.

**Amendment Process**:
1. Create deviation request per §12.1
2. Get stakeholder approval
3. Update constitution with version bump
4. Update dependent artifacts per Sync Impact Report

**Compliance Review**:
- All PRs MUST verify compliance with this constitution
- Code reviews MUST check for forbidden technologies
- Deployment pipelines MUST validate resource limits

**Version**: 1.0.0 | **Ratified**: 2026-02-09 | **Last Amended**: 2026-02-09
