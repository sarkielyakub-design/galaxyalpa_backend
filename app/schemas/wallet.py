from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class WalletResponse(BaseModel):
    id: UUID
    currency: str
    balance: Decimal
    status: str


class TransactionResponse(BaseModel):
    id: UUID
    reference: str
    transaction_type: str
    direction: str
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    currency: str
    status: str
    provider: str | None = None
    provider_reference: str | None = None
    description: str | None = None
    created_at: datetime