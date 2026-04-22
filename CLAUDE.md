# superTrade / APEX — Claude project memory

## Default operating mode

These rules apply on every task unless the user explicitly overrides them.
The user should not need to restate them in chat.

1. Read the exact owner files before editing.
2. Trust implemented code over README claims.
3. Preserve current API contracts unless the task explicitly requests a contract change.
4. If a contract changes, update backend producer, frontend consumer, and shared types together.
5. Keep paper trading as the default execution mode unless the task explicitly changes it.
6. Prefer the smallest safe diff over broad rewrites.
7. Do not invent missing modules, endpoints, files, or exchange integrations.
8. Do not present simulated or random data as live exchange truth.
9. Do not mark work complete without reporting exact verification commands and outcomes.
10. Keep responses concise. Do not repeat repo context or these rules back to the user unless necessary.

## Prompt minimization rule

Treat each user message as task delta only.
Short prompts such as these are sufficient:

- `Implement <feature>.`
- `Fix <bug>.`
- `Refactor <area>. No behavior change.`
- `Audit <module>. No code yet.`
- `Add <feature> end-to-end.`
- `Change API contract for <x> and update all consumers.`

Do not require the user to prepend instructions like:

- read CLAUDE.md
- inspect code first
- preserve contracts
- keep paper mode default
- use minimal diff
- report verification

Those are already mandatory here.

## Task mode defaults

### If the prompt starts with `Implement`

- inspect current ownership first
- propose smallest safe plan
- code
- verify
- report changed files, commands, results, and risks

### If the prompt starts with `Fix` or `Debug`

- reproduce or trace first
- find first divergent layer
- patch only after root cause is identified
- verify the fix directly

### If the prompt starts with `Audit`, `Map`, or `Review`

- do not code unless explicitly asked
- inspect current implementation only
- separate facts, gaps, assumptions, and risks

### If the prompt says `No behavior change`

- keep external contracts and runtime behavior stable
- treat this as refactor-only work

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
- backend compile: `cd backend && python -m compileall app`
- frontend type-check: `cd frontend && npm run type-check`
- frontend build: `cd frontend && npm run build`
- frontend lint: `cd frontend && npm run lint`
- docker stack: `docker-compose up --build`

## Known repo realities

- The frontend dependency list includes both `react-query` and `@tanstack/react-query`, but the code imports `@tanstack/react-query`. Do not deepen that inconsistency.
- Some backend endpoints use generated or random values. Treat them as placeholders until replaced.
- The README mentions directories and capabilities that may not yet exist. Validate on disk before relying on them.
- `backend/tests/` exists but is minimal. Stronger verification may require adding tests plus smoke checks.

## Preferred answer format

Keep answers compact.
Default output should usually be:

1. current finding or plan
2. files changed or files inspected
3. verification commands and outcomes
4. remaining risks or assumptions

Do not add long preambles.
Do not restate obvious repo context.
Do not produce marketing language.

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
