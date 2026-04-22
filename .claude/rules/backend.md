---
paths:
  - "backend/**/*.py"
  - "backend/requirements.txt"
  - "backend/.env.example"
  - "backend/Dockerfile"
---

# Backend rules

## Scope
Applies to FastAPI app wiring, engines, endpoints, config, and backend services.

## Stack facts
- FastAPI app entry: `backend/app/main.py`
- App settings: `backend/app/core/config.py`
- Router root: `backend/app/api/v1/router.py`
- Engine modules in `backend/app/engines/`
- App state singletons created in FastAPI lifespan
- Preferred backend runtime: Python 3.12 venv in `backend/.venv`

## Rules
1. Preserve FastAPI lifespan startup/shutdown behavior unless the task explicitly changes it.
2. Keep app-state dependencies explicit: endpoints should use `request.app.state.*` instead of hidden globals where possible.
3. Preserve the health endpoint and API docs unless the task explicitly changes public API shape.
4. Fail safely on missing or invalid market data. Do not silently fabricate live-trading truth.
5. Keep paper-trading behavior the default execution mode.
6. If an endpoint contract changes, update schemas, route handlers, frontend consumers, and README/API references as needed.
7. Prefer explicit Pydantic request/response models for non-trivial payloads.
8. Keep placeholder or random data clearly separated from production-like logic.
9. Do not suggest installing backend dependencies into the system interpreter. Use `backend/.venv`.
10. Add or update tests whenever changing business logic, endpoint behavior, or risk/execution semantics.

## Verification
- `cd backend && source .venv/bin/activate && python -c "from app.main import app; print(app.title)"`
- `cd backend && source .venv/bin/activate && python -m compileall app`
- If tests exist or are added: `cd backend && source .venv/bin/activate && pytest`

## Review checklist
- Does the endpoint use the correct engine from app state?
- Are config defaults still safe for local paper mode?
- Does the change distinguish simulated values from exchange values?
- Are async boundaries handled correctly?
- Did startup/shutdown behavior remain valid?
