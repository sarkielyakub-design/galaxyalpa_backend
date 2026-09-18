import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.services.email_service import send_password_reset_email
from app.auth.dependencies import get_current_user
from app.auth.password_reset import (
    create_password_reset_token,
    reset_password,
)
from app.auth.security import hash_password
from app.database.database import get_db
from app.models.monnify_account import MonnifyAccount
from app.models.user import User
from app.models.wallet import Wallet
from app.monnify.service import MonnifyService
from app.schemas.auth import RegisterRequest, RegisterResponse
from app.schemas.password_reset import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    # -------------------------------
    # KYC validation
    # -------------------------------

    if not payload.bvn and not payload.nin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="BVN or NIN is required.",
        )

    # -------------------------------
    # Check email
    # -------------------------------

    existing_user = db.scalar(
        select(User).where(User.email == payload.email)
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # -------------------------------
    # Check phone
    # -------------------------------

    if payload.phone:
        existing_phone = db.scalar(
            select(User).where(User.phone == payload.phone)
        )

        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this phone number already exists.",
            )

    # -------------------------------
    # Create user
    # -------------------------------

    user = User(
        id=uuid.uuid4(),
        email=payload.email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
    )

    db.add(user)
    db.flush()

    # -------------------------------
    # Create internal wallet
    # -------------------------------

    wallet = Wallet(
        id=uuid.uuid4(),
        user_id=user.id,
        currency="NGN",
        balance=0,
        status="active",
    )

    db.add(wallet)
    db.flush()

    # -------------------------------
    # Customer name
    # -------------------------------

    customer_name = " ".join(
        part
        for part in (
            payload.first_name,
            payload.last_name,
        )
        if part
    ).strip()

    if not customer_name:
        customer_name = str(payload.email)

    # -------------------------------
    # Create Monnify reserved account
    # -------------------------------

    monnify = MonnifyService()

    try:
        response = monnify.create_reserved_account(
            account_name=customer_name,
            customer_email=str(payload.email),
            customer_name=customer_name,
            bvn=payload.bvn,
            nin=payload.nin,
        )

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to create Monnify virtual account.",
        ) from exc

    # -------------------------------
    # Validate Monnify response
    # -------------------------------

    accounts = response.get("accounts") or []

    if not accounts:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Monnify returned no virtual account.",
        )

    primary_account = accounts[0]

    account_reference = response.get("accountReference")
    reservation_reference = response.get(
        "reservationReference"
    )

    if not account_reference or not reservation_reference:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Monnify returned incomplete account information.",
        )

    account_number = primary_account.get("accountNumber")
    bank_name = primary_account.get("bankName")
    bank_code = primary_account.get("bankCode")

    if not account_number:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Monnify returned no account number.",
        )

    # -------------------------------
    # Save Monnify account
    # -------------------------------

    monnify_account = MonnifyAccount(
        id=uuid.uuid4(),
        user_id=user.id,
        wallet_id=wallet.id,
        account_reference=account_reference,
        reservation_reference=reservation_reference,
        account_name=primary_account.get(
            "accountName",
            customer_name,
        ),
        account_number=account_number,
        bank_name=bank_name,
        bank_code=bank_code,
        currency=response.get(
            "currencyCode",
            "NGN",
        ),
        status=response.get(
            "status",
            "ACTIVE",
        ),
        provider="monnify",
    )

    db.add(monnify_account)

    # -------------------------------
    # Commit transaction
    # -------------------------------

    db.commit()

    return RegisterResponse(
        id=str(user.id),
        email=user.email,
        wallet_currency=wallet.currency,
        account_number=monnify_account.account_number,
        bank_name=monnify_account.bank_name,
        bank_code=monnify_account.bank_code,
        message=(
            "Account and Monnify virtual account "
            "created successfully."
        ),
    )


# ============================================================
# GET CURRENT USER
# ============================================================

@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "phone": current_user.phone,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "is_verified": current_user.is_verified,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
    }


# ============================================================
# FORGOT PASSWORD
# ============================================================

@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
)
def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(User.email == payload.email)
    )

    # Do not reveal whether the email exists.
    if not user or not user.is_active:
        return ForgotPasswordResponse(
            message=(
                "If an account exists with this email, "
                "a password reset link has been sent."
            )
        )

    reset_token, token = create_password_reset_token(
        db=db,
        user=user,
    )

    try:
        send_password_reset_email(
            recipient_email=str(user.email),
            reset_token=token,
        )

        db.commit()

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to send password reset email.",
        ) from exc

    return ForgotPasswordResponse(
        message=(
            "If an account exists with this email, "
            "a password reset link has been sent."
        )
    )
# ============================================================
# RESET PASSWORD
# ============================================================

@router.post(
    "/reset-password",
    response_model=ResetPasswordResponse,
)
def reset_user_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    try:
        reset_password(
            db=db,
            token=payload.token,
            new_password=payload.new_password,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ResetPasswordResponse(
        message="Password has been reset successfully."
    )