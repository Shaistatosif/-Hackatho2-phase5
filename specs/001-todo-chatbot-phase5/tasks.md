# Tasks: Phase V Todo Chatbot

**Input**: Design documents from `/specs/001-todo-chatbot-phase5/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/, research.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create project structure, initialize all services with dependencies

- [x] T001 Create monorepo directory structure per plan.md in repository root
- [x] T002 [P] Initialize backend Python project in services/backend/ with requirements.txt (FastAPI, Pydantic, httpx, uvicorn)
- [x] T003 [P] Initialize frontend Next.js project in services/frontend/ with package.json
- [x] T004 [P] Initialize notification-service Python project in services/notification-service/
- [x] T005 [P] Initialize recurring-task-service Python project in services/recurring-task-service/
- [x] T006 [P] Initialize audit-service Python project in services/audit-service/
- [x] T007 [P] Initialize websocket-service Python project in services/websocket-service/
- [x] T008 [P] Create Dapr components directory with pubsub.yaml in dapr-components/pubsub.yaml
- [x] T009 [P] Create Dapr statestore component in dapr-components/statestore.yaml
- [x] T010 [P] Create Dapr secrets component in dapr-components/secrets.yaml
- [x] T011 [P] Create Dapr jobs component in dapr-components/jobs.yaml
- [x] T012 Create .env.example with required environment variables at repository root

**Checkpoint**: Project structure ready, all service directories initialized

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T013 Create Task Pydantic model in services/backend/src/models/task.py
- [x] T014 Create TaskEvent Pydantic model in services/backend/src/models/events.py
- [x] T015 Create ReminderEvent Pydantic model in services/backend/src/models/events.py
- [x] T016 Create request/response schemas in services/backend/src/models/schemas.py
- [x] T017 Implement DaprClient service for state operations in services/backend/src/services/dapr_client.py
- [x] T018 Implement DaprClient publish_event method for Kafka in services/backend/src/services/dapr_client.py
- [x] T019 Implement DaprClient schedule_job method for reminders in services/backend/src/services/dapr_client.py
- [x] T020 Create FastAPI app entry point in services/backend/src/main.py
- [x] T021 Configure CORS, logging, and error handlers in services/backend/src/main.py
- [x] T022 Create health check endpoint in services/backend/src/main.py
- [x] T023 [P] Create Dockerfile for backend in services/backend/Dockerfile
- [x] T024 [P] Create Dockerfile for frontend in services/frontend/Dockerfile
- [x] T025 [P] Create Dockerfile for notification-service in services/notification-service/Dockerfile
- [x] T026 [P] Create Dockerfile for recurring-task-service in services/recurring-task-service/Dockerfile
- [x] T027 [P] Create Dockerfile for audit-service in services/audit-service/Dockerfile
- [x] T028 [P] Create Dockerfile for websocket-service in services/websocket-service/Dockerfile

**Checkpoint**: Foundation ready - models, Dapr client, and Dockerfiles complete

---

## Phase 3: User Story 1 - Create and Manage Tasks via Chat (Priority: P1) MVP

**Goal**: Users can create, update, complete, and delete tasks via natural language chat

**Independent Test**: Send "Add task: Buy groceries" and verify task created

### Implementation for User Story 1

- [x] T029 [US1] Implement TaskService.create_task() in services/backend/src/services/task_service.py
- [x] T030 [US1] Implement TaskService.get_task() in services/backend/src/services/task_service.py
- [x] T031 [US1] Implement TaskService.update_task() in services/backend/src/services/task_service.py
- [x] T032 [US1] Implement TaskService.delete_task() in services/backend/src/services/task_service.py
- [x] T033 [US1] Implement TaskService.complete_task() in services/backend/src/services/task_service.py
- [x] T034 [US1] Implement TaskService.list_tasks() in services/backend/src/services/task_service.py
- [x] T035 [US1] Add event publishing to all CRUD operations in services/backend/src/services/task_service.py
- [x] T036 [US1] Create MCP tool definitions for task operations in services/backend/src/mcp/tools.py
- [x] T037 [US1] Implement ChatHandler for NL command parsing in services/backend/src/services/chat_handler.py
- [x] T038 [US1] Create POST /api/chat endpoint in services/backend/src/api/chat.py
- [x] T039 [US1] Create GET /api/tasks endpoint in services/backend/src/api/tasks.py
- [x] T040 [US1] Create POST /api/tasks endpoint in services/backend/src/api/tasks.py
- [x] T041 [US1] Create PUT /api/tasks/{id} endpoint in services/backend/src/api/tasks.py
- [x] T042 [US1] Create DELETE /api/tasks/{id} endpoint in services/backend/src/api/tasks.py
- [x] T043 [US1] Create POST /api/tasks/{id}/complete endpoint in services/backend/src/api/tasks.py
- [x] T044 [US1] Register API routers in main.py in services/backend/src/main.py
- [x] T045 [US1] Create ChatInterface component in services/frontend/src/components/ChatInterface.tsx
- [x] T046 [US1] Create TaskList component in services/frontend/src/components/TaskList.tsx
- [x] T047 [US1] Create API service for backend calls in services/frontend/src/services/api.ts
- [x] T048 [US1] Create main page with chat UI in services/frontend/src/app/page.tsx
- [x] T049 [US1] Create app layout in services/frontend/src/app/layout.tsx

**Checkpoint**: User Story 1 complete - basic task CRUD via chat working

---

## Phase 4: User Story 2 - Due Dates and Reminders (Priority: P2)

**Goal**: Users can set due dates and receive reminders at scheduled times

**Independent Test**: Create task with due date 5 min ahead, verify reminder fires

### Implementation for User Story 2

- [x] T050 [US2] Extend TaskService to handle due_at and remind_at in services/backend/src/services/task_service.py
- [x] T051 [US2] Implement reminder scheduling via Dapr Jobs API in services/backend/src/services/task_service.py
- [x] T052 [US2] Implement reminder cancellation on task complete/delete in services/backend/src/services/task_service.py
- [x] T053 [US2] Create job callback endpoint /api/jobs/reminder in services/backend/src/api/tasks.py
- [x] T054 [US2] Update ChatHandler to parse due dates from NL in services/backend/src/services/chat_handler.py
- [x] T055 [US2] Update MCP tools with due_at and remind_at params in services/backend/src/mcp/tools.py
- [x] T056 [US2] Create notification-service main.py with Dapr subscription in services/notification-service/src/main.py
- [x] T057 [US2] Implement reminder event handler in services/notification-service/src/handlers.py
- [x] T058 [US2] Create Notification component in services/frontend/src/components/Notification.tsx
- [x] T059 [US2] Integrate notification display in frontend in services/frontend/src/app/page.tsx

**Checkpoint**: User Story 2 complete - reminders fire at scheduled times

---

## Phase 5: User Story 3 - Recurring Tasks (Priority: P3)

**Goal**: Recurring tasks auto-regenerate on completion

**Independent Test**: Create daily recurring task, complete it, verify next occurrence created

### Implementation for User Story 3

- [x] T060 [US3] Add recurrence_pattern field handling in TaskService in services/backend/src/services/task_service.py
- [x] T061 [US3] Update MCP tools with recurrence pattern parsing in services/backend/src/mcp/tools.py
- [x] T062 [US3] Update ChatHandler for recurring task commands in services/backend/src/services/chat_handler.py
- [x] T063 [US3] Create recurring-task-service main.py with Dapr subscription in services/recurring-task-service/src/main.py
- [x] T064 [US3] Implement completed event handler with recurrence logic in services/recurring-task-service/src/handlers.py
- [x] T065 [US3] Implement calculate_next_due() function in services/recurring-task-service/src/handlers.py
- [x] T066 [US3] Call backend API to create next task occurrence in services/recurring-task-service/src/handlers.py

**Checkpoint**: User Story 3 complete - recurring tasks auto-regenerate

---

## Phase 6: User Story 4 - Search, Filter, Sort (Priority: P4)

**Goal**: Users can search/filter/sort their task list

**Independent Test**: Create multiple tasks, verify search returns correct results

### Implementation for User Story 4

- [x] T067 [US4] Implement search_tasks() with full-text search in services/backend/src/services/task_service.py
- [x] T068 [US4] Implement filter_tasks() with status/priority/due date filters in services/backend/src/services/task_service.py
- [x] T069 [US4] Implement sort_tasks() with multiple sort options in services/backend/src/services/task_service.py
- [x] T070 [US4] Add query parameters to GET /api/tasks endpoint in services/backend/src/api/tasks.py
- [x] T071 [US4] Update ChatHandler for search/filter NL commands in services/backend/src/services/chat_handler.py
- [x] T072 [US4] Update MCP tools with search/filter definitions in services/backend/src/mcp/tools.py
- [x] T073 [US4] Add filter/sort controls to TaskList component in services/frontend/src/components/TaskList.tsx

**Checkpoint**: User Story 4 complete - search/filter/sort working

---

## Phase 7: User Story 5 - Tags (Priority: P5)

**Goal**: Users can add/remove tags and filter by tags

**Independent Test**: Add tags to task, filter by tag, verify results

### Implementation for User Story 5

- [x] T074 [US5] Implement add_tags() method in TaskService in services/backend/src/services/task_service.py
- [x] T075 [US5] Implement remove_tags() method in TaskService in services/backend/src/services/task_service.py
- [x] T076 [US5] Add tag filtering to filter_tasks() in services/backend/src/services/task_service.py
- [x] T077 [US5] Create POST /api/tasks/{id}/tags endpoint in services/backend/src/api/tasks.py
- [x] T078 [US5] Create DELETE /api/tasks/{id}/tags endpoint in services/backend/src/api/tasks.py
- [x] T079 [US5] Update ChatHandler for tag commands in services/backend/src/services/chat_handler.py
- [x] T080 [US5] Update MCP tools with tag operations in services/backend/src/mcp/tools.py
- [x] T081 [US5] Add tag display and filter to TaskList in services/frontend/src/components/TaskList.tsx

**Checkpoint**: User Story 5 complete - tags working

---

## Phase 8: User Story 6 - Real-time Sync (Priority: P6)

**Goal**: Changes sync across multiple clients in real-time

**Independent Test**: Open two browsers, make change in one, see update in other

### Implementation for User Story 6

- [x] T082 [US6] Add task-updates topic publishing to TaskService in services/backend/src/services/task_service.py
- [x] T083 [US6] Create websocket-service main.py with FastAPI WebSocket in services/websocket-service/src/main.py
- [x] T084 [US6] Implement Dapr subscription for task-updates in services/websocket-service/src/main.py
- [x] T085 [US6] Implement WebSocket broadcast to connected clients in services/websocket-service/src/handlers.py
- [x] T086 [US6] Create WebSocket client service in frontend in services/frontend/src/services/websocket.ts
- [x] T087 [US6] Integrate WebSocket updates in TaskList in services/frontend/src/components/TaskList.tsx

**Checkpoint**: User Story 6 complete - real-time sync working

---

## Phase 9: User Story 7 - Audit History (Priority: P7)

**Goal**: View complete history of all task operations

**Independent Test**: Perform CRUD operations, view audit log with all events

### Implementation for User Story 7

- [x] T088 [US7] Create AuditEntry model in services/backend/src/models/events.py
- [x] T089 [US7] Create audit-service main.py with Dapr subscription in services/audit-service/src/main.py
- [x] T090 [US7] Implement task event handler to store audit entries in services/audit-service/src/handlers.py
- [x] T091 [US7] Implement get_audit_log() in audit-service in services/audit-service/src/handlers.py
- [x] T092 [US7] Create GET /api/audit endpoint in backend in services/backend/src/api/tasks.py
- [x] T093 [US7] Update ChatHandler for audit log commands in services/backend/src/services/chat_handler.py

**Checkpoint**: User Story 7 complete - audit history accessible

---

## Phase 10: Kubernetes Deployment (Minikube)

**Purpose**: Deploy all services to local Minikube cluster

- [x] T094 Create namespace.yaml in kubernetes/minikube/namespace.yaml
- [x] T095 [P] Create backend-deployment.yaml with Dapr annotations in kubernetes/minikube/backend-deployment.yaml
- [x] T096 [P] Create frontend-deployment.yaml in kubernetes/minikube/frontend-deployment.yaml
- [x] T097 [P] Create notification-deployment.yaml in kubernetes/minikube/notification-deployment.yaml
- [x] T098 [P] Create recurring-deployment.yaml in kubernetes/minikube/recurring-deployment.yaml
- [x] T099 [P] Create audit-deployment.yaml in kubernetes/minikube/audit-deployment.yaml
- [x] T100 [P] Create websocket-deployment.yaml in kubernetes/minikube/websocket-deployment.yaml
- [x] T101 Create services.yaml with ClusterIP services in kubernetes/minikube/services.yaml
- [x] T102 Create configmaps.yaml in kubernetes/minikube/configmaps.yaml
- [x] T103 Create secrets.yaml template in kubernetes/minikube/secrets.yaml

**Checkpoint**: All K8s manifests ready for Minikube

---

## Phase 11: Helm Charts

**Purpose**: Create Helm charts for production deployment

- [x] T104 Create Chart.yaml in helm-charts/todo-chatbot/Chart.yaml
- [x] T105 Create values.yaml with defaults in helm-charts/todo-chatbot/values.yaml
- [x] T106 Create values-minikube.yaml in helm-charts/todo-chatbot/values-minikube.yaml
- [x] T107 Create values-aks.yaml for Azure in helm-charts/todo-chatbot/values-aks.yaml
- [x] T108 Create deployments.yaml template in helm-charts/todo-chatbot/templates/deployments.yaml
- [x] T109 Create services.yaml template in helm-charts/todo-chatbot/templates/services.yaml
- [x] T110 Create configmaps.yaml template in helm-charts/todo-chatbot/templates/configmaps.yaml
- [x] T111 Create secrets.yaml template in helm-charts/todo-chatbot/templates/secrets.yaml
- [x] T112 Create dapr-components.yaml template in helm-charts/todo-chatbot/templates/dapr-components.yaml

**Checkpoint**: Helm charts ready for cloud deployment

---

## Phase 12: CI/CD Pipeline

**Purpose**: Automated build and deployment via GitHub Actions

- [x] T113 Create CI workflow for build and test in .github/workflows/ci.yaml
- [x] T114 Create deploy workflow for cloud deployment in .github/workflows/deploy.yaml
- [x] T115 Add Docker build steps for all services in .github/workflows/ci.yaml
- [x] T116 Add Helm deploy steps in .github/workflows/deploy.yaml

**Checkpoint**: CI/CD pipeline ready

---

## Phase 13: Polish & Documentation

**Purpose**: Final polish, documentation, and validation

- [x] T117 [P] Create README.md with architecture diagram at repository root
- [x] T118 [P] Add local setup instructions to README.md
- [x] T119 [P] Add cloud deployment guide to README.md
- [x] T120 [P] Document Kafka topics and Dapr components in README.md
- [ ] T121 Validate all Kafka use cases work (audit, reminders, recurring, sync)
- [ ] T122 Run quickstart.md validation
- [ ] T123 Create AGENTS.md with agent instructions

**Checkpoint**: Documentation complete, all features validated

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    │
    ▼
Phase 2 (Foundational) ─────────────────────────┐
    │                                           │
    ▼                                           ▼
Phase 3 (US1: Task CRUD) ──► Phase 10 (K8s) ──► Phase 11 (Helm)
    │                                           │
    ▼                                           ▼
Phase 4 (US2: Reminders)                   Phase 12 (CI/CD)
    │                                           │
    ▼                                           ▼
Phase 5 (US3: Recurring)                   Phase 13 (Docs)
    │
    ▼
Phase 6 (US4: Search)
    │
    ▼
Phase 7 (US5: Tags)
    │
    ▼
Phase 8 (US6: Real-time)
    │
    ▼
Phase 9 (US7: Audit)
```

### User Story Independence

- **US1**: No dependencies on other stories - can be deployed as MVP
- **US2**: Depends on US1 (needs tasks to set reminders on)
- **US3**: Depends on US1 (needs tasks to recur)
- **US4**: Depends on US1 (needs tasks to search)
- **US5**: Depends on US1 (needs tasks to tag)
- **US6**: Depends on US1 (needs task changes to sync)
- **US7**: Depends on US1 (needs task events to audit)

### Parallel Opportunities

**Phase 1 - All setup tasks (T002-T012) can run in parallel**
```bash
# Launch in parallel:
T002, T003, T004, T005, T006, T007, T008, T009, T010, T011
```

**Phase 2 - Dockerfiles (T023-T028) can run in parallel**
```bash
# Launch in parallel:
T023, T024, T025, T026, T027, T028
```

**Phase 10 - All deployment YAMLs (T095-T100) can run in parallel**
```bash
# Launch in parallel:
T095, T096, T097, T098, T099, T100
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test task CRUD via chat
5. Deploy to Minikube (Phase 10)
6. Demo MVP

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Task CRUD) → Deploy/Demo (MVP!)
3. Add US2 (Reminders) → Deploy/Demo
4. Add US3 (Recurring) → Deploy/Demo
5. Add US4 (Search/Filter) → Deploy/Demo
6. Add US5 (Tags) → Deploy/Demo
7. Add US6 (Real-time) → Deploy/Demo
8. Add US7 (Audit) → Deploy/Demo
9. Complete Helm + CI/CD → Cloud Deploy

---

## Task Summary

| Phase | Story | Task Count |
|-------|-------|------------|
| Phase 1: Setup | - | 12 |
| Phase 2: Foundational | - | 16 |
| Phase 3: US1 Task CRUD | P1 | 21 |
| Phase 4: US2 Reminders | P2 | 10 |
| Phase 5: US3 Recurring | P3 | 7 |
| Phase 6: US4 Search | P4 | 7 |
| Phase 7: US5 Tags | P5 | 8 |
| Phase 8: US6 Real-time | P6 | 6 |
| Phase 9: US7 Audit | P7 | 6 |
| Phase 10: K8s | - | 10 |
| Phase 11: Helm | - | 9 |
| Phase 12: CI/CD | - | 4 |
| Phase 13: Docs | - | 7 |
| **Total** | | **123** |

---

## Notes

- All code MUST include Task ID in file header per Constitution
- All Dapr calls via HTTP API (no direct Kafka/DB clients)
- All K8s deployments MUST have resource limits
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
