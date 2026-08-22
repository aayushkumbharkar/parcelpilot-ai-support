# ParcelPilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable local ParcelPilot AI support assessment app.

**Architecture:** FastAPI backend with scoped data stores, retrieval authority layer, deterministic tool-using agent, and React/Vite frontend. Seeded data replaces missing PDFs/Excel while preserving interfaces.

**Tech Stack:** Python, FastAPI, pandas, pytest, React, Vite, Tailwind.

**Spec:** `docs/superpowers/specs/2026-08-22-parcelpilot-design.md`

## Global Constraints

- Enforce account access in data/retrieval functions, not prompt text.
- All state-changing tools must stage drafts before execution.
- Mock external services with `MOCK_MODE=true`.
- Keep dependencies minimal and standard for the stack.

---

### Task 1: Backend Core

**Files:** `backend/config.py`, `backend/auth/*`, `backend/data/*`

- [x] Create settings and mock auth tokens.
- [x] Seed accounts, orders, tickets, and document chunks.
- [x] Implement account and ticket stores with role checks.
- [x] Add tests for cross-account denial and internal access.

### Task 2: Retrieval And Authority

**Files:** `backend/retrieval/*`, `tests/test_authority_resolution.py`

- [x] Encode authority ranks and metadata.
- [x] Filter chunks by customer scope and deprecated visibility.
- [x] Label deprecated and historical context.
- [x] Detect authority conflicts.

### Task 3: Tools And Agent

**Files:** `backend/agent/*`, `tests/test_tools.py`, `tests/test_multistep.py`, `tests/test_confirmation.py`

- [x] Implement six distinct tools.
- [x] Add deterministic calculations for cancellation and credits.
- [x] Stage confirmation-only actions.
- [x] Implement required multi-step flows.

### Task 4: Frontend

**Files:** `frontend/src/*`

- [x] Add auth switcher, chat, tool trace, source badge, confirmation modal, and issue radar.
- [x] Connect frontend to backend API.

### Task 5: Ship Docs And Verification

**Files:** `README.md`, `docker-compose.yml`, Dockerfiles.

- [x] Add local setup docs and deployment notes.
- [x] Run backend tests.
- [x] Run frontend build.

