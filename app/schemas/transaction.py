# app/schemas/transaction.py
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Literal


TransactionType = Literal["credit", "debit"]


class TransactionCreate(BaseModel):
    """
    Payload para crear una transacción.
    - type: "credit" | "debit"
    - amount: Decimal positivo (se rechaza <= 0)
    """
    model_config = ConfigDict(extra="forbid")

    account_id: uuid.UUID
    type: TransactionType
    amount: Decimal = Field(..., description="Monto positivo. Se almacena como Numeric(18,2).")
    description: str | None = Field(default=None, max_length=500)

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v is None:
            raise ValueError("amount es requerido")
        # Evita floats: debe venir como string/number parseable a Decimal
        if v <= Decimal("0"):
            raise ValueError("amount debe ser > 0")
        return v


class TransactionOut(BaseModel):
    """Respuesta de una transacción."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: uuid.UUID
    type: TransactionType
    amount: Decimal
    description: str | None
    created_at: datetime


class TransactionList(BaseModel):
    """Lista paginada simple para MVP."""
    items: list[TransactionOut]
    total: int
