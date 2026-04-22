# Infrastructure rules for compose, Docker, nginx, and scripts

## Scope
Applies to `docker-compose.yml`, `infra/**`, Dockerfiles, and local bootstrapping.

## Rules
1. Keep local paper-mode startup simple. Do not make DB or Redis mandatory for basic UI/backend bring-up unless the task explicitly requires it.
2. Preserve the current port expectations unless the task explicitly changes them:
   - backend local: 8000
   - frontend dev: 5173
   - frontend container: 3000
   - nginx: 80/443
3. If changing environment variables, update `.env.example`, compose wiring, and any code that reads them.
4. If changing reverse-proxy behavior, verify both API and frontend asset routing.
5. Keep Docker changes minimal and reproducible.
6. Do not assume production-grade secrets management exists unless you implement it.

## Verification
- `docker-compose config`
- `docker-compose up --build`
- verify `/health`
- verify `/api/docs`
- verify frontend loads through nginx if relevant
