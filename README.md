# To-Do API + Celery + ML (Production-like Skeleton)

## Overview
Production-oriented skeleton for test task:
- FastAPI (CRUD to-do, in-memory)
- Celery + Redis (external API integration + CSV)
- Simple ML `/predict` (TF-IDF + linear classifier)

## Goals
- Show best practices: layered architecture, ENV config, logging, tests, Docker, healthchecks, documentation.

## Roadmap (Commits)
1. Initialize repo
2. Tooling: pyproject, pre-commit, CI
3. ENV & settings skeleton
4. Production-like layout
5. Health & readiness
6. Tasks CRUD contracts
7. Dockerfiles & Compose
8. Celery worker + fetch-users
9. ML training plan + /predict
10. README finalization + ADR summaries

## Tech Stack
- Python 3.11+, FastAPI, Pydantic
- Celery, Redis
- Docker, docker compose
- Pytest, ruff/black/isort/mypy
- scikit-learn, pandas

## Quality Bar
- Single main branch with CI gates (lint/type/tests)
- Test coverage ≥60% (target 80%+)
- Conventional Commits
- Structured logging (JSON in prod), request_id correlation, error context
- Documentation: README + ADR for key decisions

## Error Handling & Logging (Policy)
- All errors → consistent JSON responses (422/404/5xx).
- Logs: `ts, level, logger, msg, request_id, method, path, status, latency_ms, error.type, error.message`.
- For integrations: retries with backoff, timeouts, payload limits.
- No PII/secrets in logs.

## Directory Layout (Planned)

## Tooling

Install and enable pre-commit locally:
```bash
python -m pip install --upgrade pip
pip install pre-commit ruff black isort mypy pytest pytest-cov
pre-commit install
