import uuid
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.core.security import hash_password
from app.models.user import User

def test_login_and_me():
    email = f"test-{uuid.uuid4()}@finledger.com"
    password = "Test123!"
    db = SessionLocal()
    try:
        db.add(User(email=email, hashed_password=hash_password(password), is_active=True, is_admin=False))
        db.commit()
    finally:
        db.close()

    client = TestClient(app)
    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200
    token = r.json()["access_token"]

    r2 = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert r2.json()["email"] == email