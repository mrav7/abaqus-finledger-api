import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    customer_id: uuid.UUID
    currency: str = Field(min_length=3, max_length=3)


class AccountUpdate(BaseModel):
    is_active: Optional[bool] = None


class AccountOut(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    currency: str
    balance: Decimal
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}