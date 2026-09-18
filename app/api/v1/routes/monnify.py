import hashlib
import hmac
import json
from decimal import Decimal

from fastapi import APIRouter, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.database import SessionLocal
from app.models.monnify_account import MonnifyAccount
from app.models.transaction import Transaction
from app.wallet.service import WalletService

router = APIRouter(
    prefix="/monnify",
    tags=["Monnify"],
)


def verify_signature(
    raw_body: bytes,
    signature: str | None,
) -> bool:
    """
    Verify Monnify webhook signature.

    Sandbox webhook requests may not contain the signature header,
    so sandbox requests are allowed without one.
    """

    if not signature:
        if "sandbox" in settings.MONNIFY_BASE_URL.lower():
            return True

        return False

    expected_signature = hmac.new(
        settings.MONNIFY_SECRET_KEY.encode("utf-8"),
        raw_body,
        hashlib.sha512,
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        signature,
    )


@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
)
async def monnify_webhook(
    request: Request,
    monnify_signature: str | None = Header(
        default=None,
        alias="monnify-signature",
    ),
):
    raw_body = await request.body()

    if not verify_signature(
        raw_body,
        monnify_signature,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Monnify webhook signature.",
        )

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload.",
        )

    event_type = payload.get("eventType")

    if event_type != "SUCCESSFUL_TRANSACTION":
        return {
            "status": "ignored",
            "message": "Event type not handled.",
        }

    event_data = payload.get("eventData") or {}

    product = event_data.get("product") or {}

    if product.get("type") != "RESERVED_ACCOUNT":
        return {
            "status": "ignored",
            "message": "Transaction is not for a reserved account.",
        }

    if event_data.get("paymentStatus") != "PAID":
        return {
            "status": "ignored",
            "message": "Payment is not completed.",
        }

    account_reference = product.get("reference")
    transaction_reference = event_data.get(
        "transactionReference"
    )
    amount_paid = event_data.get("amountPaid")
    currency = event_data.get(
        "currency",
        "NGN",
    )

    if not account_reference:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing reserved account reference.",
        )

    if not transaction_reference:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing transaction reference.",
        )

    if amount_paid is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing payment amount.",
        )

    amount = Decimal(str(amount_paid))

    if amount <= Decimal("0.00"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment amount.",
        )

    db: Session = SessionLocal()

    try:
        # Idempotency protection.
        existing_transaction = db.scalar(
            select(Transaction).where(
                Transaction.reference
                == transaction_reference
            )
        )

        if existing_transaction:
            return {
                "status": "already_processed",
                "transaction_id": str(
                    existing_transaction.id
                ),
            }

        account = db.scalar(
            select(MonnifyAccount).where(
                MonnifyAccount.account_reference
                == account_reference
            )
        )

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Monnify reserved account not found.",
            )

        if account.status.upper() != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Monnify account is not active.",
            )

        if account.currency != currency:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Currency mismatch.",
            )

        transaction = WalletService.credit(
            db,
            wallet_id=account.wallet_id,
            amount=amount,
            reference=transaction_reference,
            transaction_type="deposit",
            provider="monnify",
            provider_reference=event_data.get(
                "paymentReference"
            ),
            description=(
                event_data.get("paymentDescription")
                or "Monnify bank transfer deposit"
            ),
        )

        db.commit()
        db.refresh(transaction)

        return {
            "status": "processed",
            "transaction_id": str(transaction.id),
            "wallet_id": str(account.wallet_id),
            "amount": str(amount),
            "currency": currency,
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process Monnify webhook.",
        )

    finally:
        db.close()