# superTrade / APEX — Claude project memory

## Session defaults
These rules apply on every task unless the user explicitly overrides them.
The user should not need to restate them in chat.

1. Read the exact owner files before editing.
2. Trust implemented code over README claims.
3. Preserve existing API contracts unless the task explicitly requests a contract change.
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

## Task-mode defaults
### If the prompt starts with `Implement`
- inspect current ownership first
- propose the smallest safe plan
- code
- verify
- report changed files, commands, results, and risks

### If the prompt starts with `Fix` or `Debug`
- reproduce or trace first
- find the first proven divergence
- patch only after the root cause is identified
- verify the fix directly

### If the prompt starts with `Audit`, `Map`, or `Review`
- do not code unless explicitly asked
- inspect current implementation only
- separate facts, gaps, assumptions, and risks

### If the prompt says `No behavior change`
- keep external contracts and runtime behavior stable
- treat this as refactor-only work

## Project map
- Backend: `backend/app`
- Frontend: `frontend/src`
- Infrastructure: `infra/`, `docker-compose.yml`, Dockerfiles, nginx
- Docs: `README.md`, `docs/`
- Skills: `.claude/skills/`
- Path-scoped rules: `.claude/rules/`

## Current repo realities
- The README describes a broader target architecture than the current implementation. Validate on disk before relying on claims.
- Some backend endpoints and market values are placeholder or random. Treat them as simulated until replaced.
- The frontend dependency list includes both `react-query` and `@tanstack/react-query`, but the code imports `@tanstack/react-query`. Do not deepen that inconsistency.
- `backend/tests/` exists but is thin. Stronger verification may require adding narrow tests plus smoke checks.
- The pinned scientific Python stack in `backend/requirements.txt` is compatible with Python 3.12, not Python 3.14. Prefer a backend venv on Python 3.12 until dependencies are upgraded.

## Core commands
### Local dev
- backend install: `cd backend && python3.12 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- backend run: `cd backend && source .venv/bin/activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- frontend install: `cd frontend && npm install`
- frontend dev: `cd frontend && npm run dev`
- one-command start: `bash infra/scripts/start.sh`

### Verification
- backend smoke import: `cd backend && source .venv/bin/activate && python -c "from app.main import app; print(app.title)"`
- backend compile: `cd backend && source .venv/bin/activate && python -m compileall app`
- frontend type-check: `cd frontend && npm run type-check`
- frontend build: `cd frontend && npm run build`
- frontend lint: `cd frontend && npm run lint`
- docker stack: `docker-compose config && docker-compose up --build`

## Output format
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
- `backend/requirements.txt`
- `frontend/package.json`
- `frontend/src/App.tsx`
- `frontend/src/utils/api.ts`
- `frontend/src/store/index.ts`
