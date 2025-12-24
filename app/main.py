from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.accounts import router as accounts_router
from app.api.routes.auth import router as auth_router
from app.api.routes.customers import router as customers_router
from app.api.routes.transactions import router as transactions_router
from app.core.config import settings
from app.db.session import SessionLocal
from app.services.seed import seed_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.app_env == "dev":
        db = SessionLocal()
        try:
            seed_admin(db)
        finally:
            db.close()
    yield


app = FastAPI(title="FinLedger API", version="0.1.0", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(customers_router)
app.include_router(accounts_router)
app.include_router(transactions_router)


@app.get("/health")
def health():
    return {"status": "ok"}