# Backend rules for `backend/**`

## Scope
Applies to FastAPI app wiring, engines, endpoints, config, and backend services.

## Stack facts
- FastAPI app entry: `backend/app/main.py`
- App settings: `backend/app/core/config.py`
- Router root: `backend/app/api/v1/router.py`
- Engine modules in `backend/app/engines/`
- App state singletons created in FastAPI lifespan

## Rules
1. Preserve FastAPI lifespan startup/shutdown behavior unless the task explicitly changes it.
2. Keep app-state dependencies explicit: endpoints should use `request.app.state.*` instead of hidden globals where possible.
3. Preserve current docs endpoints and health endpoint unless the task explicitly changes public API shape.
4. Fail safely on missing or invalid market data. Do not silently fabricate live-trading truth.
5. Keep paper-trading behavior the default execution mode.
6. If an endpoint contract changes, update schemas, route handlers, frontend consumers, and README/API references as needed.
7. Prefer explicit Pydantic request/response models for non-trivial payloads.
8. Keep placeholder or random data clearly separated from production-like logic.
9. Avoid adding heavy infra dependencies unless the task requires them and wiring is complete.
10. Add or update tests whenever changing business logic, endpoint behavior, or risk/execution semantics.

## Verification
- `cd backend && python -c "from app.main import app; print(app.title)"`
- `cd backend && python -m compileall app`
- If tests exist or are added: `cd backend && pytest`

## Review checklist
- Does the endpoint use the correct engine from app state?
- Are config defaults still safe for local paper mode?
- Does the change distinguish simulated values from exchange values?
- Are async boundaries handled correctly?
- Did startup/shutdown behavior remain valid?
