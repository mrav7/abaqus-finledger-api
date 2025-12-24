# app/api/routes/transactions.py
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Transaction
from app.schemas.transaction import TransactionCreate, TransactionList, TransactionOut
from app.services.transaction import (
    AccountInactiveError,
    AccountNotFoundError,
    TxValidationError,
    create_transaction,
)

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "",
    response_model=TransactionOut,
    status_code=status.HTTP_201_CREATED,
)
def post_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
) -> Transaction:
    try:
        tx = create_transaction(
            db=db,
            account_id=payload.account_id,
            tx_type=payload.type,
            amount=payload.amount,
            description=payload.description,
        )
        db.commit()
        db.refresh(tx)
        return tx
    except TxValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except AccountInactiveError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.get("", response_model=TransactionList)
def list_transactions(
    account_id: uuid.UUID = Query(...),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> TransactionList:
    base = select(Transaction).where(Transaction.account_id == account_id)

    items = (
        db.execute(
            base.order_by(Transaction.created_at.desc(), Transaction.id.desc())
            .limit(limit)
            .offset(offset)
        )
        .scalars()
        .all()
    )

    total = db.execute(
        select(func.count()).select_from(Transaction).where(Transaction.account_id == account_id)
    ).scalar_one()

    return TransactionList(items=items, total=total)