---
name: implement-feature
description: Safely implement a feature in the superTrade codebase with minimal drift.
---

When asked to implement a feature in this repository:

1. Read `CLAUDE.md` first.
2. Read the exact owner files for the behavior.
3. Distinguish current implemented behavior from README-level aspirations.
4. Summarize:
   - current state
   - affected files
   - contract impact
   - verification plan
5. Prefer the smallest safe diff.
6. If the task touches API data:
   - update backend producer
   - update frontend consumer
   - update types
7. If the task touches realtime behavior:
   - inspect `frontend/src/hooks/useWebSocket.ts`
   - inspect `frontend/src/utils/api.ts`
   - inspect relevant backend WS endpoint
8. If the task touches execution or risk:
   - preserve paper mode defaults
   - do not overclaim live readiness
9. Run the narrowest relevant verification.
10. Report:
   - files changed
   - commands run
   - results
   - remaining risks or assumptions
