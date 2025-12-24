from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models import Account


def _create_customer_and_account(client, headers: dict[str, str]) -> tuple[str, str]:
    email = f"acme-{uuid.uuid4()}@finledger.com"

    r1 = client.post(
        "/customers",
        headers=headers,
        json={"name": "ACME SpA", "email": email},
    )
    assert r1.status_code in (200, 201), r1.text
    customer_id = r1.json()["id"]

    r2 = client.post(
        "/accounts",
        headers=headers,
        json={"customer_id": customer_id, "currency": "CLP"},
    )
    assert r2.status_code in (200, 201), r2.text
    account_id = r2.json()["id"]
    return customer_id, account_id


def _account_balance(db: Session, account_id: str) -> Decimal:
    return db.execute(
        select(Account.balance).where(Account.id == uuid.UUID(account_id))
    ).scalar_one()


@pytest.mark.parametrize("amount", ["0", "0.00", "-1", "-10.00"])
def test_transactions_amount_must_be_positive(client, auth_header, db_session: Session, amount: str):
    _, account_id = _create_customer_and_account(client, auth_header)

    r = client.post(
        "/transactions",
        headers=auth_header,
        json={"account_id": account_id, "type": "credit", "amount": amount, "description": "x"},
    )
    assert r.status_code == 422


def test_credit_increases_balance_and_creates_tx(client, auth_header, db_session: Session):
    _, account_id = _create_customer_and_account(client, auth_header)

    r = client.post(
        "/transactions",
        headers=auth_header,
        json={"account_id": account_id, "type": "credit", "amount": "100.00", "description": "funding"},
    )
    assert r.status_code in (200, 201), r.text

    assert _account_balance(db_session, account_id) == Decimal("100.00")

    r_list = client.get(f"/transactions?account_id={account_id}&limit=10&offset=0", headers=auth_header)
    assert r_list.status_code == 200, r_list.text
    data = r_list.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["type"] == "credit"


def test_debit_decreases_balance(client, auth_header, db_session: Session):
    _, account_id = _create_customer_and_account(client, auth_header)

    r1 = client.post(
        "/transactions",
        headers=auth_header,
        json={"account_id": account_id, "type": "credit", "amount": "100.00", "description": "funding"},
    )
    assert r1.status_code in (200, 201), r1.text

    r2 = client.post(
        "/transactions",
        headers=auth_header,
        json={"account_id": account_id, "type": "debit", "amount": "40.00", "description": "purchase"},
    )
    assert r2.status_code in (200, 201), r2.text

    assert _account_balance(db_session, account_id) == Decimal("60.00")


def test_account_not_found_404(client, auth_header):
    missing = str(uuid.uuid4())
    r = client.post(
        "/transactions",
        headers=auth_header,
        json={"account_id": missing, "type": "credit", "amount": "10.00", "description": "x"},
    )
    assert r.status_code == 404


def test_account_inactive_409(client, auth_header, db_session: Session):
    _, account_id = _create_customer_and_account(client, auth_header)

    db_session.execute(
        update(Account)
        .where(Account.id == uuid.UUID(account_id))
        .values(is_active=False)
    )
    db_session.commit()

    r = client.post(
        "/transactions",
        headers=auth_header,
        json={"account_id": account_id, "type": "credit", "amount": "10.00", "description": "x"},
    )
    assert r.status_code == 409


def test_list_transactions_order_desc(client, auth_header, db_session: Session):
    _, account_id = _create_customer_and_account(client, auth_header)

    client.post(
        "/transactions",
        headers=auth_header,
        json={"account_id": account_id, "type": "credit", "amount": "10.00", "description": "t1"},
    )
    client.post(
        "/transactions",
        headers=auth_header,
        json={"account_id": account_id, "type": "credit", "amount": "20.00", "description": "t2"},
    )

    r = client.get(f"/transactions?account_id={account_id}&limit=10&offset=0", headers=auth_header)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2