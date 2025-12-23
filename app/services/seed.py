from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User


def seed_admin(db: Session) -> None:
    email = "admin@finledger.com"
    password = "Admin123!"  # solo para dev; cambia después

    exists = db.scalar(select(User).where(User.email == email))
    if exists:
        return

    user = User(
        email=email,
        hashed_password=hash_password(password),
        is_active=True,
        is_admin=True,
    )
    db.add(user)
    db.commit()