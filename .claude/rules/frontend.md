---
paths:
  - "frontend/**/*.{ts,tsx,js,jsx,css,scss,html}"
  - "frontend/package.json"
  - "frontend/vite.config.ts"
  - "frontend/tsconfig*.json"
  - "frontend/tailwind.config.js"
  - "frontend/postcss.config.js"
  - "frontend/Dockerfile"
---

# Frontend rules

## Scope
Applies to React, TypeScript, Vite, Tailwind, Zustand, and query-layer work in `frontend/`.

## Stack facts
- React 18 + TypeScript + Vite
- State store: Zustand in `frontend/src/store/index.ts`
- Server state: `@tanstack/react-query`
- HTTP client: Axios in `frontend/src/utils/api.ts`
- Realtime: native WebSocket in `frontend/src/hooks/useWebSocket.ts`
- App shell currently uses a tab-driven page switch in `frontend/src/App.tsx`
- Path alias: `@/`

## Rules
1. Use `@tanstack/react-query` only. Do not introduce new usage of legacy `react-query` v3 APIs.
2. Do not invent API fields that the backend does not return.
3. Prefer extending `frontend/src/types/index.ts` over scattered inline types.
4. Keep transport details centralized in `frontend/src/utils/api.ts`.
5. Keep WebSocket parsing defensive. Ignore malformed messages rather than crashing the UI.
6. Keep global trading state in Zustand only when multiple screens need it. Keep page-local UI state local.
7. Preserve the existing tab-driven app shell unless the task explicitly introduces router-based navigation.
8. When backend responses are placeholder or random, label UI semantics carefully. Do not imply institutional-grade truth if the source is simulated.
9. Prefer composition and reusable components over page-local duplication.
10. Maintain dark-theme compatibility and current visual language unless the task explicitly changes design.

## Verification
- `cd frontend && npm run type-check`
- `cd frontend && npm run build`
- `cd frontend && npm run lint`

## Review checklist
- Are all new API fields backed by the backend?
- Are query keys stable and specific?
- Is polling frequency justified?
- Is WebSocket cleanup correct on unmount?
- Did any change duplicate types or transport logic?
