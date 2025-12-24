from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.core.config import settings
from app.db.session import SessionLocal
from app.services.seed import seed_admin

from app.api.routes.customers import router as customers_router
from app.api.routes.accounts import router as accounts_router

app = FastAPI(title="FinLedger API", version="0.1.0")
app.include_router(auth_router)
app.include_router(customers_router)
app.include_router(accounts_router)

@app.on_event("startup")
def on_startup():
    if settings.app_env == "dev":
        db = SessionLocal()
        try:
            seed_admin(db)
        finally:
            db.close()


@app.get("/health")
def health():
    return {"status": "ok"}
