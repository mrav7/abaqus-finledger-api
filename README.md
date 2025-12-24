# FinLedger API (Abaqus Demo)

API backend tipo fintech enfocada en un **ledger** simple: **Customers → Accounts → Transactions**.  

> **Estado:** MVP funcional con auth JWT, migraciones Alembic, endpoints protegidos, tests (pytest) y lint (ruff), y soporte para dev/prod con Dockerfile multi-stage.

---

## Stack
- **API:** FastAPI + Uvicorn
- **DB:** PostgreSQL + SQLAlchemy 2.0 + Alembic (migraciones)
- **Auth:** JWT (OAuth2 password flow)
- **Infra:** Docker Compose + Dockerfile multi-stage (dev/prod)
- **Quality:** Ruff + Pytest


## Estructura del repositorio

```text
.
├─ app/
│  ├─ main.py
│  ├─ api/
│  │  ├─ deps.py
│  │  └─ routes/
│  │     ├─ auth.py
│  │     ├─ customers.py
│  │     ├─ accounts.py
│  │     ├─ transactions.py
│  ├─ core/
│  ├─ db/
│  │  ├─ base.py
│  │  ├─ session.py
│  │  └─ migrations/
│  │     └─ versions/
│  │        ├─ 32c33471743c_create_users_table.py
│  │        ├─ 330a511dcdc8_create_customers.py
│  │        ├─ e55738caa7e5_create_accounts.py
│  │        └─ 9e201cc7d1b7_create_transactions.py
│  ├─ models/
│  │  ├─ user.py
│  │  ├─ customer.py
│  │  ├─ account.py
│  │  ├─ transaction.py
│  ├─ schemas/
│  │  ├─ user.py
│  │  ├─ customer.py
│  │  ├─ account.py
│  │  └─ transaction.py
│  └─ services/
│     ├─ seed.py
│     ├─ transaction.py
├─ tests/
│  ├─ conftest.py
│  ├─ test_health.py
│  ├─ test_auth.py
│  ├─ test_accounts.py
│  ├─ test_accounts_get_by_id.py
│  ├─ test_transactions.py
│  ├─ test_smoke_e2e.py
├─ docker/
│  └─ Dockerfile
├─ .github/
│  └─ workflows/
│     └─ ci.yml
├─ docker-compose.yml
├─ docker-compose.override.yml
├─ alembic.ini
└─ pyproject.toml
```

> Nota: `reports.py` / `transfers.py` aparecen como placeholders en esta versión.

---

## Requisitos
- Docker Desktop (Windows/macOS/Linux)

---

## Quickstart (Docker)

```bash
cp .env.example .env
docker compose up -d --build
```

Luego:
- Swagger UI: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

> Recomendación: expón la API solo en localhost (ej. `127.0.0.1:8000:8000`) para evitar acceso desde la red local.

---

## Configuración (.env)

Ejemplo típico:

- `DATABASE_URL=postgresql+psycopg://finledger:finledger@db:5432/finledger`
- `JWT_SECRET=change-me`
- `APP_ENV=dev`
- `RUN_MIGRATIONS=1`
- `PORT=8000`

> `.env` está en `.gitignore` y no se sube al repo. Usa `.env.example` como plantilla.

---

## Migraciones (Alembic)

Aplicar migraciones:

```bash
docker compose exec api alembic upgrade head
docker compose exec api alembic current
docker compose exec api alembic heads
```

Generar migración:

```bash
docker compose exec api alembic revision --autogenerate -m "mensaje"
```

---

## Auth (JWT)

### Login (obtener token)

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

> En modo `APP_ENV=dev`, el sistema puede crear un usuario admin de ejemplo (seed) en startup según configuración del proyecto.

---

## Uso de la API desde PowerShell (Windows)

### 1) Login y headers

```powershell
$token = (curl.exe -s -X POST "http://localhost:8000/auth/login" `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=admin@finledger.com&password=Admin123!" | ConvertFrom-Json).access_token

$auth = "Authorization: Bearer $token"
```

### 2) Crear Customer

```powershell
$customer = curl.exe -s -X POST "http://localhost:8000/customers" `
  -H $auth -H "Content-Type: application/json" `
  -d "{ `"name`": `"ACME SpA`", `"email`": `"acme-$([guid]::NewGuid())@finledger.com`" }" | ConvertFrom-Json

$customer.id
```

### 3) Crear Account

```powershell
$account = curl.exe -s -X POST "http://localhost:8000/accounts" `
  -H $auth -H "Content-Type: application/json" `
  -d "{ `"customer_id`": `"$($customer.id)`", `"currency`": `"CLP`" }" | ConvertFrom-Json

$account.id
```

### 4) Ver Account (incluye balance)

```powershell
curl.exe -s "http://localhost:8000/accounts/$($account.id)" -H $auth
```

### 5) Crear Transactions (credit/debit)

```powershell
$tx1 = curl.exe -s -X POST "http://localhost:8000/transactions" `
  -H $auth -H "Content-Type: application/json" `
  -d "{ `"account_id`": `"$($account.id)`", `"type`": `"credit`", `"amount`": `"100.00`", `"description`": `"topup`" }" | ConvertFrom-Json

$tx2 = curl.exe -s -X POST "http://localhost:8000/transactions" `
  -H $auth -H "Content-Type: application/json" `
  -d "{ `"account_id`": `"$($account.id)`", `"type`": `"debit`", `"amount`": `"35.50`", `"description`": `"buy`" }" | ConvertFrom-Json
```

### 6) Listar transactions de una cuenta

```powershell
curl.exe -s "http://localhost:8000/transactions?account_id=$($account.id)&limit=50&offset=0" -H $auth
```

---

## Reglas de negocio (Transactions)

- `type` ∈ `credit` | `debit`
- `amount` siempre positivo (se valida, se normaliza a 2 decimales)
- Balance persistido en `accounts.balance` (`Decimal` en Python / `Numeric(18,2)` en DB)
- Concurrencia: lock de cuenta con `SELECT ... FOR UPDATE` para evitar race conditions
- Rechaza transacciones si la cuenta está inactiva

---

## Tests y lint (dentro de Docker)

```bash
docker compose exec api ruff check .
docker compose exec api python -m pytest -q
```

---

## Dev vs Prod

### Dev (por defecto con compose)
`docker compose` usa `target: dev` (incluye herramientas de dev).

### Imagen prod (sin herramientas de dev)
```bash
docker build -f docker/Dockerfile --target prod -t finledger-api:prod .
docker run --rm -p 8000:8000 --env-file ./.env finledger-api:prod
```

---

## Endpoints principales

### Health
- `GET /health`

### Auth
- `POST /auth/login`
- `GET /auth/me`

### Customers
- `POST /customers`
- `GET /customers`

### Accounts
- `POST /accounts`
- `GET /accounts/{account_id}`
- `GET /customers/{customer_id}/accounts`

### Transactions
- `POST /transactions`
- `GET /transactions?account_id=<uuid>&limit=<n>&offset=<n>`