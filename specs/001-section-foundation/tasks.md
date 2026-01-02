# Tasks: Physical and Humanoid Robotics Book Foundation

**Input**: Design documents from `/specs/001-section-foundation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)

## Path Conventions

- **Frontend**: `content/`
- **Backend**: `server/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan (server/ and content/ directories)
- [x] T002 [P] Initialize Docusaurus project in content/ using JavaScript
- [x] T003 Initialize FastAPI project in server/ using uv (uv init)
- [x] T004 [P] Configure .gitignore to exclude build artifacts and .env files

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 [P] Install core backend dependencies in server/ (fastapi, uvicorn, pydantic, python-dotenv)
- [x] T006 Create main.py entry point in server/ with basic health check router
- [x] T007 [P] Create placeholder core and services modules in server/ (core/, services/vector_db.py, services/storage.py)
- [x] T008 [P] Configure basic Docusaurus navbar and footer in content/docusaurus.config.js
- [x] T009 Create sidebars.js template in content/ for auto-generated documentation hierarchy

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Global Navigation & Layout (Priority: P1) 🎯 MVP

**Goal**: Establish the book's visual structure and navigation hierarchy

**Independent Test**: Verify that the Docusaurus site loads with the correct "Physical and Humanoid Robotics Book" title and sidebar.

### Implementation for User Story 1

- [x] T010 [P] [US1] Update Docusaurus title and navbar links in content/docusaurus.config.js
- [x] T011 [US1] Configure sidebar to auto-generate from content/docs directory in content/sidebars.js
- [x] T012 [P] [US1] Add a link to the GitHub repository in the navbar

**Checkpoint**: User Story 1 functional and testable independently

---

## Phase 4: User Story 2 - RAG Backend Foundation (Priority: P1)

**Goal**: Prepare the FastAPI backend for RAG logic and database connections

**Independent Test**: Verify that the FastAPI server starts and has defined router placeholders.

### Implementation for User Story 2

- [x] T013 [P] [US2] Create APIRouter for chat/RAG in server/routes/chat.py
- [x] T014 [P] [US2] Create APIRouter for personalizing content in server/routes/personalize.py
- [x] T015 [US2] Include routers in the main FastAPI app in server/main.py
- [x] T016 [P] [US2] Define pydantic models for chat requests and responses (referencing api-v1.md)

**Checkpoint**: User Story 2 functional and testable independently

---

## Phase 5: User Story 3 - Initial Chapter Content (Priority: P2)

**Goal**: Initialize the first three chapters as placeholders

**Independent Test**: Verify that all 3 chapters render in the Docusaurus UI.

### Implementation for User Story 3

- [x] T017 [P] [US3] Create Chapter 1: Introduction to Physical Robotics in content/docs/intro.md
- [x] T018 [P] [US3] Create Chapter 2: Humanoid Kinematics in content/docs/kinematics.md
- [x] T019 [P] [US3] Create Chapter 3: Dynamics and Control in content/docs/dynamics.md

**Checkpoint**: All user stories functional and testable independently

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T020 [P] Finalize quickstart.md with local development instructions
- [x] T021 Run final consistency check across /server and /content
- [x] T022 [P] Verify all robotics content uses SI units

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Phase 1
- **User Stories (Phase 3-5)**: All depend on Phase 2 completion
- **Polish (Phase 6)**: Depends on all user stories being complete

### Parallel Opportunities

- T002 and T003 (Frontend/Backend init) can run in parallel
- T010 and T012 (Docusaurus config) can run in parallel
- T013 and T014 (Backend routers) can run in parallel
- T017, T018, T019 (Content creation) can run in parallel
