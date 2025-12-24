import uuid
import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def auth_header():
    email = f"test-{uuid.uuid4()}@finledger.com"
    password = "Test123!"

    db = SessionLocal()
    try:
        db.add(User(email=email, hashed_password=hash_password(password), is_active=True, is_admin=False))
        db.commit()
    finally:
        db.close()

    c = TestClient(app)
    r = c.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}