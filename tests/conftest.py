import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def db_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def auth_header(client: TestClient, db_session: Session) -> dict[str, str]:
    email = f"test-{uuid.uuid4()}@finledger.com"
    password = "Test123!"

    db_session.add(
        User(
            email=email,
            hashed_password=hash_password(password),
            is_active=True,
            is_admin=False,
        )
    )
    db_session.commit()

    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
