# superTrade / APEX — Claude project memory

## Project identity
superTrade is a full-stack crypto options trading platform with:
- FastAPI backend in `backend/app`
- React + TypeScript + Vite frontend in `frontend/src`
- Docker Compose stack in `docker-compose.yml`
- Nginx reverse proxy in `infra/nginx/nginx.conf`
- Paper trading enabled by default

## Source-of-truth rule
Trust the implemented code more than the README.
The README describes a broader target architecture. Some current endpoints and feeds are simulated or random. Do not overclaim production readiness unless the code proves it.

## Current implemented architecture
### Backend
- Entry point: `backend/app/main.py`
- API router: `backend/app/api/v1/router.py`
- REST + WS endpoints under `backend/app/api/v1/endpoints/`
- Core engines under `backend/app/engines/`
- App state singletons attached during FastAPI lifespan:
  - `app.state.market`
  - `app.state.risk`
  - `app.state.oms`
  - `app.state.strategy`
- Health endpoint: `GET /health`
- API docs: `/api/docs`
- WebSocket feed: `/api/v1/ws/feed`

### Frontend
- Entry: `frontend/src/main.tsx`
- App shell: `frontend/src/App.tsx`
- Global state: `frontend/src/store/index.ts`
- HTTP client: `frontend/src/utils/api.ts`
- WebSocket hook: `frontend/src/hooks/useWebSocket.ts`
- Data hooks: `frontend/src/hooks/useMarketData.ts`
- Pages:
  - `Dashboard.tsx`
  - `ChainPage.tsx`
  - `StrategyPage.tsx`
  - `BacktestPage.tsx`
  - `OrdersPage.tsx`
  - `RiskPage.tsx`
- Uses path alias `@/`
- Uses Zustand and `@tanstack/react-query`

### Infrastructure
- Local bootstrap: `infra/scripts/start.sh`
- Compose services: postgres, redis, backend, frontend, nginx
- Backend local default port: `8000`
- Frontend local default port: `5173`
- Docker frontend port mapping: `3000`

## Commands
### Local dev
- backend install: `cd backend && pip install -r requirements.txt`
- backend run: `cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- frontend install: `cd frontend && npm install`
- frontend dev: `cd frontend && npm run dev`
- one-command start: `bash infra/scripts/start.sh`

### Verification
- backend smoke import: `cd backend && python -c "from app.main import app; print(app.title)"`
- frontend type-check: `cd frontend && npm run type-check`
- frontend build: `cd frontend && npm run build`
- frontend lint: `cd frontend && npm run lint`
- docker stack: `docker-compose up --build`

## Hard rules
1. Read the relevant existing files before editing.
2. Preserve the current API contract unless the task explicitly includes a contract change.
3. If a contract changes, update backend producer, frontend consumer, and related types together.
4. Keep paper trading as the default unless the task explicitly changes execution mode.
5. Do not represent simulated/random data paths as live exchange truth.
6. Do not invent missing components or directories and then act as if they already exist.
7. Prefer small diffs over broad rewrites.
8. Do not mark work complete without reporting exact verification commands and outcomes.
9. Keep WebSocket and REST URL construction aligned with `frontend/src/utils/api.ts`.
10. Preserve `/health`, `/api/docs`, and the FastAPI lifespan engine wiring unless the task explicitly changes startup architecture.

## Known repo realities
- The frontend dependency list includes both `react-query` and `@tanstack/react-query`, but the code imports `@tanstack/react-query`. Do not deepen that inconsistency.
- Some backend endpoints use generated or random values. Treat them as placeholders until replaced.
- The README mentions directories and capabilities that may not yet exist. Validate on disk before relying on them.
- `backend/tests/` exists but is minimal. Stronger verification may require adding tests plus smoke checks.

## Preferred workflow
For implementation tasks:
1. Read `CLAUDE.md` and relevant scoped rules.
2. Read the exact files that own the behavior.
3. Summarize current state and smallest safe plan.
4. Implement with minimal surface area.
5. Run the narrowest useful verification.
6. Report changed files, verification results, and remaining risks.

## Files that usually matter first
- `README.md`
- `docker-compose.yml`
- `infra/scripts/start.sh`
- `backend/app/main.py`
- `backend/app/core/config.py`
- `backend/app/api/v1/router.py`
- `frontend/package.json`
- `frontend/src/App.tsx`
- `frontend/src/utils/api.ts`
- `frontend/src/store/index.ts`
