---
name: architecture-review
description: Map the actual implemented architecture of superTrade before proposing large changes.
---

When asked to review architecture or plan a large change:

1. Read `CLAUDE.md` first.
2. Read these files before making claims:
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
3. Produce four sections:
   - implemented current state
   - gaps vs stated architecture
   - target design
   - smallest migration sequence
4. Explicitly separate:
   - FACT
   - INFERENCE
   - ASSUMPTION
   - UNKNOWN
5. Call out contract boundaries, runtime boundaries, and state ownership.
6. Flag places where the README overstates the current implementation.
7. Do not recommend a rewrite if an incremental path exists.
