---
id: 001
title: Phase V Constitution Creation
stage: constitution
date: 2026-02-09
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: unknown
command: /sp.constitution
labels: ["constitution", "phase-v", "hackathon", "dapr", "kafka", "kubernetes"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A
---

## Prompt

# SP.CONSTITUTION
**Phase V: Advanced Cloud Deployment - Todo Chatbot**

The user provided a comprehensive constitution document defining non-negotiable principles, architectural constraints, and quality standards for Phase V of the Todo Chatbot Hackathon. The constitution includes:

1. **Core Architectural Principles** (4 principles):
   - Spec-Driven Development (SDD) ONLY
   - Event-Driven Architecture (Kafka)
   - Microservices with Dapr Abstraction
   - Cloud-Native & Kubernetes-First

2. **Technology Stack Constraints**:
   - Mandatory: FastAPI, Neon PostgreSQL, Kafka, Dapr 1.14+, Kubernetes 1.28+, Minikube, AKS/GKE/OKE, Next.js 14+, OpenAI ChatKit, MCP Python SDK, GitHub Actions
   - Preferred: Docker Hub/GHCR, Dapr Secrets API, Redpanda/Strimzi
   - Forbidden: Direct Kafka/DB clients, hardcoded credentials, polling cron jobs, synchronous blocking

3. **Feature Requirements**:
   - Advanced: Recurring tasks (event-driven), Due dates & reminders (Dapr Jobs API)
   - Intermediate: Priorities, Tags, Search, Filter, Sort
   - Kafka Use Cases: Audit Log, Reminders, Recurring Tasks, Real-time Sync

4. **Deployment Standards**: Minikube local, AKS/GKE/OKE cloud, Helm charts required

5. **Code Quality**: Python/FastAPI standards, Dapr integration patterns, K8s manifest standards

6. **Additional sections**: Kafka schemas, testing requirements, security compliance, submission requirements, performance targets, failure handling, deviation policy, validation checklists

## Response snapshot

Created constitution v1.0.0 at `.specify/memory/constitution.md` with:
- 4 core architectural principles with rationale
- Complete technology stack (mandatory, preferred, forbidden)
- Feature implementation standards (advanced + intermediate)
- 4 required Kafka use cases
- Deployment standards for Minikube and cloud (AKS/GKE/OKE)
- Code quality standards with examples
- Kafka event schemas (TaskEvent, ReminderEvent)
- Testing & validation checklists
- Security & compliance requirements
- Submission requirements (repo structure, README, demo video)
- Performance targets (response times, throughput, resource limits)
- Failure mode handling (Kafka, Dapr, database)
- Deviation policy with hierarchy of truth
- Final validation checklist
- Appendices with quick commands and gotchas
- Governance section with amendment process

Sync Impact Report included as HTML comment at top of file.

## Outcome

- Impact: Created foundational governance document for Phase V hackathon
- Tests: N/A (documentation artifact)
- Files: 1 file created (.specify/memory/constitution.md)
- Next prompts: /sp.specify to create feature specifications, /sp.plan for implementation planning
- Reflection: Comprehensive constitution captures all hackathon requirements; templates flagged for consistency updates

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate template consistency propagation in subsequent /sp.plan execution
