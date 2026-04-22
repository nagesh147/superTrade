# Test and verification rules

## Scope
Applies to test code, smoke validation, and completion claims across the repo.

## Rules
1. Do not claim a fix without at least one relevant verification command.
2. Prefer behavior-level tests over trivial implementation-coupled assertions.
3. Cover negative paths when changing API, risk, order, or WebSocket behavior.
4. When frontend test infrastructure is absent, use type-check + build + targeted manual smoke steps instead of pretending automated coverage exists.
5. When backend tests are absent or thin, add the narrowest useful test near the changed behavior.
6. Do not weaken assertions just to make tests pass.
7. Record exact commands run and whether they passed, failed, or were not possible.

## Typical verification matrix
### Frontend
- `cd frontend && npm run type-check`
- `cd frontend && npm run build`
- `cd frontend && npm run lint`

### Backend
- `cd backend && source .venv/bin/activate && python -m compileall app`
- `cd backend && source .venv/bin/activate && python -c "from app.main import app; print(app.title)"`
- `cd backend && source .venv/bin/activate && pytest`

### Integration
- `bash infra/scripts/start.sh`
- open `http://localhost:5173`
- open `http://localhost:8000/api/docs`
- verify WS feed reaches the dashboard
