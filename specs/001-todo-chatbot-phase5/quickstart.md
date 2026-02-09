# Quickstart: Phase V Todo Chatbot

**Branch**: `001-todo-chatbot-phase5`
**Date**: 2026-02-09

---

## Prerequisites

- Docker Desktop (with Kubernetes enabled) OR Minikube
- kubectl CLI
- Dapr CLI (`dapr`)
- Node.js 20+ (for frontend)
- Python 3.11+ (for backend services)
- Helm 3.x

---

## Quick Setup (Local - Minikube)

### 1. Start Minikube

```bash
minikube start --memory=8192 --cpus=4
minikube addons enable ingress
```

### 2. Install Dapr

```bash
# Install Dapr CLI (if not installed)
# Windows: winget install Dapr.CLI
# Mac: brew install dapr/tap/dapr-cli
# Linux: wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr on Kubernetes
dapr init -k
dapr status -k  # Verify all components are running
```

### 3. Deploy Kafka (Redpanda)

```bash
# Option A: Redpanda (simpler)
kubectl create namespace kafka
helm repo add redpanda https://charts.redpanda.com
helm install redpanda redpanda/redpanda -n kafka \
  --set statefulset.replicas=1 \
  --set resources.cpu.cores=1 \
  --set resources.memory.container.max=2Gi

# Wait for Redpanda to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redpanda -n kafka --timeout=300s
```

### 4. Configure Dapr Components

```bash
kubectl apply -f dapr-components/
```

### 5. Set Secrets

```bash
# Create Neon PostgreSQL connection secret
kubectl create secret generic neon-secret \
  --from-literal=connection-string="postgresql://user:pass@host.neon.tech/dbname?sslmode=require&pooling=true"

# Create API key secret (for development)
kubectl create secret generic api-secrets \
  --from-literal=openai-api-key="sk-..."
```

### 6. Deploy Services

```bash
# Deploy all services
kubectl apply -f kubernetes/minikube/

# OR use Helm
helm install todo-chatbot helm-charts/todo-chatbot -f helm-charts/todo-chatbot/values-minikube.yaml
```

### 7. Wait for Pods

```bash
kubectl get pods -w
# Wait until all pods show 2/2 READY (app + Dapr sidecar)
```

### 8. Access Services

```bash
# Port forward backend
kubectl port-forward svc/backend 8000:8000 &

# Port forward frontend
kubectl port-forward svc/frontend 3000:3000 &

# Open in browser
open http://localhost:3000
```

---

## Verify Installation

### Check Dapr Sidecars

```bash
dapr list -k
# Should show: backend, frontend, notification, recurring, audit, websocket
```

### Check Kafka Topics

```bash
kubectl exec -it redpanda-0 -n kafka -- rpk topic list
# Should show: task-events, reminders, task-updates
```

### Test Chat API

```bash
# Create a task
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{"message": "Add task: Test todo chatbot with high priority"}'

# List tasks
curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer test-token"
```

### Test Event Flow

```bash
# Watch Kafka events
kubectl exec -it redpanda-0 -n kafka -- rpk topic consume task-events --offset start

# In another terminal, create a task and watch events flow
```

---

## Development Mode (Without Kubernetes)

For faster development iteration:

### 1. Run Dapr Locally

```bash
dapr init
```

### 2. Run Redis (for local state/pubsub)

```bash
docker run -d --name redis -p 6379:6379 redis:alpine
```

### 3. Run Backend

```bash
cd services/backend
pip install -r requirements.txt
dapr run --app-id backend --app-port 8000 -- uvicorn src.main:app --reload
```

### 4. Run Frontend

```bash
cd services/frontend
npm install
npm run dev
```

---

## Common Commands

```bash
# View logs
kubectl logs -f deployment/backend -c backend
kubectl logs -f deployment/backend -c daprd  # Dapr sidecar logs

# Restart a service
kubectl rollout restart deployment/backend

# Scale up
kubectl scale deployment/backend --replicas=3

# Check Dapr components
kubectl get components.dapr.io

# Delete everything
helm uninstall todo-chatbot
kubectl delete namespace kafka
```

---

## Troubleshooting

### Dapr Sidecar Not Starting

```bash
# Check Dapr status
dapr status -k

# Reinstall Dapr
dapr uninstall -k
dapr init -k
```

### Kafka Connection Failed

```bash
# Check Redpanda logs
kubectl logs -n kafka redpanda-0

# Verify broker endpoint
kubectl exec -it redpanda-0 -n kafka -- rpk cluster info
```

### Pod CrashLoopBackOff

```bash
# Check events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name> --previous
```

---

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Run `/sp.implement` to generate code
3. Follow task list for implementation order
4. Deploy to cloud with `/sp.git.commit_pr`
