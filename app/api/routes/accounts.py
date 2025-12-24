import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.account import Account
from app.models.customer import Customer
from app.models.user import User
from app.schemas.account import AccountCreate, AccountOut

router = APIRouter(tags=["accounts"])


@router.post("/accounts", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
def create_account(
    payload: AccountCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    customer = db.scalar(select(Customer).where(Customer.id == payload.customer_id))
    if not customer or not customer.is_active:
        raise HTTPException(status_code=404, detail="Customer not found")

    acc = Account(customer_id=payload.customer_id, currency=payload.currency.upper())
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return acc


@router.get("/accounts/{account_id}", response_model=AccountOut)
def get_account(
    account_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    acc = db.scalar(select(Account).where(Account.id == account_id))
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return acc


@router.get("/customers/{customer_id}/accounts", response_model=list[AccountOut])
def list_accounts_by_customer(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    customer = db.scalar(select(Customer).where(Customer.id == customer_id))
    if not customer or not customer.is_active:
        raise HTTPException(status_code=404, detail="Customer not found")

    rows = db.execute(
        select(Account)
        .where(Account.customer_id == customer_id)
        .where(Account.is_active.is_(True))
        .order_by(Account.created_at.desc())
    ).scalars().all()

    return list(rows)