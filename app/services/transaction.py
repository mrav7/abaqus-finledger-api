from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.transaction import Transaction

ALLOWED_TX_TYPES = {"credit", "debit"}
TWOPLACES = Decimal("0.01")


# ---- Errores tipados para mapear a HTTP en routes ----
@dataclass
class TxError(Exception):
    message: str


class TxValidationError(TxError):
    """422"""


class AccountNotFoundError(TxError):
    """404"""


class AccountInactiveError(TxError):
    """409"""


def _to_money_2dp(value: Decimal | str | int | float) -> Decimal:
    """
    Convierte a Decimal estricto y fuerza 2 decimales.
    Rechaza NaN/Infinity y valores no positivos.
    """
    try:
        d = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise TxValidationError("amount inválido")

    if not d.is_finite():
        raise TxValidationError("amount inválido")

    d = d.quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    if d <= Decimal("0.00"):
        raise TxValidationError("amount debe ser > 0")

    return d


def _q2(value: Decimal) -> Decimal:
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def create_transaction(
    db: Session,
    *,
    account_id: uuid.UUID,
    tx_type: str,
    amount: Decimal | str | int | float,
    description: str | None = None,
) -> Transaction:
    if tx_type not in ALLOWED_TX_TYPES:
        raise TxValidationError("type debe ser 'credit' o 'debit'")

    amt = _to_money_2dp(amount)

    # Lock FOR UPDATE para evitar carreras
    account = db.scalar(
        select(Account).where(Account.id == account_id).with_for_update()
    )
    if not account:
        raise AccountNotFoundError("account no existe")

    if not account.is_active:
        raise AccountInactiveError("account inactiva")

    # Balance siempre Decimal cuantizado
    current_balance = account.balance or Decimal("0.00")
    current_balance = _q2(Decimal(current_balance))

    delta = amt if tx_type == "credit" else -amt
    new_balance = _q2(current_balance + delta)

    tx = Transaction(
        account_id=account.id,
        type=tx_type,
        amount=amt,
        description=description,
    )

    db.add(tx)
    account.balance = new_balance

    db.flush()

    return tx
