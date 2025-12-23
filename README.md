# FinLedger API (Abaqus Demo)

Demo backend tipo fintech: **FastAPI + PostgreSQL + SQLAlchemy/Alembic + JWT Auth + Docker**.  
Pensado para ser “AWS‑friendly” (RDS/S3/ECS) vía diseño desacoplado (adapters).

> Estado actual: baseline funcional con **/health + auth JWT + migraciones Alembic + Docker (dev/prod) + tests smoke + ruff**.  
> Roadmap: Customers/Accounts/Transactions/Reports.

---

## Stack
- **API:** FastAPI + Uvicorn
- **DB:** PostgreSQL + SQLAlchemy + Alembic (migraciones)
- **Auth:** JWT (login + endpoints protegidos)
- **Infra:** Docker Compose + Dockerfile multi-stage (dev/prod)
- **Quality:** Ruff + Pytest
- **CI (opcional):** GitHub Actions (lint + tests + migraciones)

---

## Requisitos
- Docker Desktop

---

## Quickstart (Docker)
```bash
cp .env.example .env
docker compose up --build
```

Luego:
- Swagger UI: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

---

## Configuración (.env)
Variables típicas:

- `DATABASE_URL=postgresql+psycopg://finledger:finledger@db:5432/finledger`
- `JWT_SECRET=change-me`
- `APP_ENV=dev`
- `RUN_MIGRATIONS=1`
- `PORT=8000`

> `.env` está en `.gitignore` y no se sube al repo. Usa `.env.example` como plantilla.

---

## Migraciones (Alembic)
Si `RUN_MIGRATIONS=1`, el contenedor aplica `alembic upgrade head` al arrancar (con retry).

Generar migración:
```bash
docker compose exec api alembic revision --autogenerate -m "message"
```

Aplicar migraciones manualmente:
```bash
docker compose exec api alembic upgrade head
```

---

## Auth (JWT)

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@finledger.com&password=Admin123!"
```

### Usuario actual
```bash
curl "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer <TOKEN>"
```

> Nota: en modo `APP_ENV=dev` se crea un usuario admin de ejemplo en el startup (seed).

---

## Tests y lint (dentro de Docker)
Este repo usa Dockerfile multi-stage. En `docker-compose.yml` se construye el target **dev** (incluye `pytest` y `ruff`).

```bash
docker compose exec api python -m pytest -q
docker compose exec api ruff check .
```

---

## Dev vs Prod

### Levantar dev (por defecto con compose)
`docker compose` usa `target: dev`.

### Build de imagen prod (sin herramientas de dev)
```bash
docker build -f docker/Dockerfile --target prod -t finledger-api:prod .
docker run --rm -p 8000:8000 --env-file ./.env finledger-api:prod
```

---

## Endpoints actuales
- `GET /health`
- `POST /auth/login`
- `GET /auth/me`

---

## Roadmap (próximo)
- Customers + Accounts CRUD
- Transferencias atómicas (DB transactions)
- Reports + export (CSV/S3)
- Hardening básico + observabilidad