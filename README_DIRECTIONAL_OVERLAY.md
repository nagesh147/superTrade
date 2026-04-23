# superTrade directional options overlay

This bundle adds a production-oriented directional-options subsystem beside the existing payoff-template strategy engine.

## What is included
- 4H macro regime engine
- 1H HA + triple SuperTrend signal engine
- setup activation engine
- 15m pullback/continuation execution engine
- option translation engine
- contract health engine
- structure selector
- sizing engine
- monitor engine
- orchestrator
- pytest suite

## Intended integration
Copy these files into your repo root so `backend/app/...` merges into the existing backend package. Wire the new routers in `backend/app/api/v1/router.py`, and attach a `DirectionalOrchestrator` singleton in `main.py` alongside the existing engines.

## Run tests
From repo root:

```bash
cd backend
pytest -q ../tests/directional
```
