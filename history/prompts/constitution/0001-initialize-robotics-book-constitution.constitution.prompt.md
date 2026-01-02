---
id: 0001
title: Initialize Robotics Book Constitution
stage: constitution
date: 2026-01-02
surface: agent
model: claude-sonnet-4.5
feature: none
branch: main
user: maaz
command: /sp.constitution
labels: [constitution, SDD, robotics]
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

# Physical and Humanoid Robotics Book Constitution

  Establish core principles for an AI-native textbook project using the Spec-Driven Development (SDD) flow.

  ## 1. Branch-Locked Execution Flow
  - Development must be section-aware. Follow a strict branch naming convention: `section-N-feature-name`.
  - Agents must only perform work relevant to the current branch section.
  - Progression: Section 1 (Foundation) -> Section 2 (Intelligence/RAG) -> Section 3 (User/Auth) -> Section 4 (AI
  Features).

  ## 2. Technical Invariants & Safety
  - Environment: Use `uv` for all Python backend management.
  - Frontend: Docusaurus using JavaScript for simplicity and modularity.
  - Backend: FastAPI with Neon (Postgres) and Qdrant (Vector DB).
  - Verification: NEVER guess documentation. Use `context7` MCP or WebSearch before implementing any third-party tool
  or formula.
  - Physics: All robotics content must use SI units and a Z-up coordinate system.

  ## 3. Intelligence & Bonus Optimization
  - Modular IQ: Architect complex features (RAG, Translation, Personalization) as reusable Claude Code Subagents and
  Agent Skills to maximize score.
  - SDD Rigor: Every code change requires a Spec -> Plan -> Task -> Implement cycle. No "quick fixes" or code drift
  allowed.
  - PHR Mandate: A Prompt History Record must be created for every single user interaction.

  ## 4. Feature Requirements
  - RAG: Chatbot must support general content Q&A and user-selected text context.
  - Auth: Better-Auth integration for user profiling (Software/Hardware background).
  - AI Buttons: Implement server-side "Personalize" and "Urdu Translate" logic based on user session data.

  ## 5. Directory Structure
  - /server: FastAPI Backend
  - /content: Docusaurus Frontend
  - /specs: SDD Artifacts
  - /history: PHRs and ADRs

## Response snapshot

The project constitution has been successfully initialized (v1.0.0). It establishes the core SDD workflow, technical stack (FastAPI, Docusaurus, uv), and the branch-locked execution strategy to ensure high-quality, professional development of the Physical and Humanoid Robotics Book with a focus on maximizing bonus points via modular AI skills.

## Outcome

- ✅ Impact: High - Established project governance and technical guardrails.
- 🧪 Tests: N/A (Methodology setup)
- 📁 Files: Updated .specify/memory/constitution.md
- 🔁 Next prompts: Use /sp.specify to define the book structure in Section 1.
- 🧠 Reflection: The constitution now explicitly supports the branch-locked workflow and bonus point optimization through subagents.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Start Section 1 specification.
