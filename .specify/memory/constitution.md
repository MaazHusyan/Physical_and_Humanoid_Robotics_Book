<!--
Sync Impact Report:
- Version change: none → 1.0.0
- List of modified principles:
  - [I. Branch-Locked Execution]
  - [II. Technical Invariants & Safety]
  - [III. Intelligence & Bonus Optimization]
  - [IV. Feature Requirements]
  - [V. Directory Structure]
- Added sections: Core Principles, Governance
- Removed sections: N/A
- Templates requiring updates:
  - ✅ updated: .specify/templates/plan-template.md
  - ✅ updated: .specify/templates/spec-template.md
  - ✅ updated: .specify/templates/tasks-template.md
- Follow-up TODOs: none
-->

# Physical and Humanoid Robotics Book Constitution

Establish core principles for an AI-native textbook project using the Spec-Driven Development (SDD) flow.

## Core Principles

### I. Branch-Locked Execution Flow
Development must be section-aware. Follow a strict branch naming convention: `section-N-feature-name`. Agents must only perform work relevant to the current branch section. Progression: Section 1 (Foundation) -> Section 2 (Intelligence/RAG) -> Section 3 (User/Auth) -> Section 4 (AI Features).

### II. Technical Invariants & Safety
- Environment: Use `uv` for all Python backend management.
- Frontend: Docusaurus using JavaScript for simplicity and modularity.
- Backend: FastAPI with Neon (Postgres) and Qdrant (Vector DB).
- Verification: NEVER guess documentation. Use `context7` MCP or WebSearch before implementing any third-party tool or formula.
- Physics: All robotics content must use SI units and a Z-up coordinate system.

### III. Intelligence & Bonus Optimization
- Modular IQ: Architect complex features (RAG, Translation, Personalization) as reusable Claude Code Subagents and Agent Skills to maximize score.
- SDD Rigor: Every code change requires a Spec -> Plan -> Task -> Implement cycle. No "quick fixes" or code drift allowed.
- PHR Mandate: A Prompt History Record must be created for every single user interaction.

### IV. Feature Requirements
- RAG: Chatbot must support general content Q&A and user-selected text context.
- Auth: Better-Auth integration for user profiling (Software/Hardware background).
- AI Buttons: Implement server-side "Personalize" and "Urdu Translate" logic based on user session data.

### V. Directory Structure
Ensure clean separation of concerns.
- `/server`: FastAPI Backend
- `/content`: Docusaurus Frontend
- `/specs`: SDD Artifacts
- `/history`: PHRs and ADRs

## Governance
This constitution is the authoritative guide for all project development.

### Amendment Procedure
1. Propose change via conversation.
2. Draft amendment and update version.
3. Run `/sp.analyze` to ensure across-artifact consistency.

### Versioning Policy
- Semantic versioning (MAJOR.MINOR.PATCH) is strictly followed.
- Version increments are decided by the impact on existing principles.

### Compliance
All automated agents and human developers must adhere to these principles. Deviations are considered critical failures and must be corrected immediately.

**Version**: 1.0.0 | **Ratified**: 2026-01-02 | **Last Amended**: 2026-01-02
