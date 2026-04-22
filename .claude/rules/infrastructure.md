---
paths:
  - "docker-compose.yml"
  - "infra/**/*"
  - "backend/Dockerfile"
  - "frontend/Dockerfile"
  - "backend/.env.example"
  - "frontend/.env.example"
---

# Infrastructure rules

## Scope
Applies to compose, Docker, nginx, environment examples, and local bootstrap scripts.

## Rules
1. Keep local paper-mode startup simple. Do not make Postgres or Redis mandatory for basic UI/backend bring-up unless the task explicitly requires it.
2. Preserve the current port expectations unless the task explicitly changes them:
   - backend local: 8000
   - frontend dev: 5173
   - frontend container: 3000
   - nginx: 80/443
3. If changing environment variables, update `.env.example`, compose wiring, and any code that reads them.
4. If changing reverse-proxy behavior, verify both API and frontend asset routing.
5. Keep Docker changes minimal and reproducible.
6. Prefer backend execution from `backend/.venv`; do not rely on system-wide `pip install`.
7. If startup depends on a Python version, fail clearly and document it. Current backend dependency pins are safest on Python 3.12.
8. Do not assume production-grade secrets management exists unless you implement it.

## Verification
- `docker-compose config`
- `docker-compose up --build`
- verify `/health`
- verify `/api/docs`
- verify frontend loads through nginx if relevant
