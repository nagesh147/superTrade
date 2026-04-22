---
name: investigate-bug
description: Investigate a bug in superTrade without jumping to an unverified fix.
---

When asked to debug or investigate a failure:

1. Read `CLAUDE.md` and the relevant scoped rules.
2. Identify the failing surface:
   - backend endpoint
   - engine logic
   - WebSocket feed
   - frontend page
   - compose/nginx/bootstrap
3. Reproduce with the smallest possible command or path.
4. Trace the ownership chain from entry point to data source.
5. Separate:
   - observed behavior
   - expected behavior
   - first proven divergence
6. Do not patch until the first proven divergence is identified.
7. Prefer narrow instrumentation and smoke checks over speculative rewrites.
8. After fixing, run the smallest verification that proves the regression is closed.
