from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.wallet import WalletResponse, TransactionResponse
from app.wallet.service import WalletService


router = APIRouter(
    prefix="/wallet",
    tags=["Wallet"],
)


class WalletTransactionRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    reference: str = Field(min_length=3, max_length=100)
    description: str | None = None


@router.get(
    "",
    response_model=WalletResponse,
)
def get_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = db.scalar(
        select(Wallet).where(Wallet.user_id == current_user.id)
    )

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found.",
        )

    return wallet


@router.get(
    "/transactions",
    response_model=list[TransactionResponse],
)
def get_wallet_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = db.scalar(
        select(Wallet).where(Wallet.user_id == current_user.id)
    )

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found.",
        )

    return WalletService.get_transactions(
        db,
        wallet_id=wallet.id,
    )


@router.post(
    "/credit",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def credit_wallet(
    payload: WalletTransactionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = db.scalar(
        select(Wallet).where(Wallet.user_id == current_user.id)
    )

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found.",
        )

    try:
        transaction = WalletService.credit(
            db,
            wallet_id=wallet.id,
            amount=payload.amount,
            reference=payload.reference,
            description=payload.description,
        )

        db.commit()
        db.refresh(transaction)

        return transaction

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to credit wallet.",
        )


@router.post(
    "/debit",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def debit_wallet(
    payload: WalletTransactionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = db.scalar(
        select(Wallet).where(Wallet.user_id == current_user.id)
    )

    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found.",
        )

    try:
        transaction = WalletService.debit(
            db,
            wallet_id=wallet.id,
            amount=payload.amount,
            reference=payload.reference,
            description=payload.description,
        )

        db.commit()
        db.refresh(transaction)

        return transaction

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to debit wallet.",
        )