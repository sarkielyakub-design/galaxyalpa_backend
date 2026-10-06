from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.bigisub.service import BigisubService


router = APIRouter(
    prefix="/bigisub",
    tags=["Bigisub"],
)


def get_bigisub_service() -> BigisubService:
    return BigisubService()


# ============================================================
# REQUEST MODELS
# ============================================================

class BigisubLoginRequest(BaseModel):
    email_or_username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class AirtimePurchaseRequest(BaseModel):
    network: int
    phone_number: str = Field(..., min_length=5)
    amount: str
    airtime_type: str = "vtu"
    pin: str = Field(..., min_length=4, max_length=4)


class ElectricityPurchaseRequest(BaseModel):
    disco: str = Field(..., min_length=2, max_length=50)
    meter_number: str = Field(..., min_length=5, max_length=50)
    meter_type: str = Field(
        ...,
        pattern="^(prepaid|postpaid)$",
    )
    amount: str = Field(..., min_length=1)


# ============================================================
# BIGISUB LOGIN
# ============================================================

@router.post("/login")
def bigisub_login(
    payload: BigisubLoginRequest,
    service: BigisubService = Depends(get_bigisub_service),
):
    try:
        return service.login(
            email_or_username=payload.email_or_username,
            password=payload.password,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


# ============================================================
# BIGISUB WALLET BALANCE
# ============================================================

@router.get("/wallet/balance")
def get_wallet_balance(
    current_user=Depends(get_current_user),
    service: BigisubService = Depends(get_bigisub_service),
):
    try:
        return service.get_wallet_balance()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


# ============================================================
# AIRTIME
# ============================================================

@router.post("/airtime/purchase")
def purchase_airtime(
    payload: AirtimePurchaseRequest,
    current_user=Depends(get_current_user),
    service: BigisubService = Depends(get_bigisub_service),
):
    try:
        return service.purchase_airtime(
            network=payload.network,
            phone_number=payload.phone_number,
            amount=payload.amount,
            airtime_type=payload.airtime_type,
            pin=payload.pin,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


# ============================================================
# DATA
# ============================================================

@router.get("/data/plans")
def get_data_plans(
    current_user=Depends(get_current_user),
    service: BigisubService = Depends(get_bigisub_service),
):
    try:
        return service.get_data_plans()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


# ============================================================
# CABLE TV
# ============================================================

@router.get("/cable/plans")
def get_cable_plans(
    current_user=Depends(get_current_user),
    service: BigisubService = Depends(get_bigisub_service),
):
    try:
        return service.get_cable_plans()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


# ============================================================
# RECHARGE PIN
# ============================================================

@router.get("/recharge-pin/plans")
def get_recharge_pin_plans(
    current_user=Depends(get_current_user),
    service: BigisubService = Depends(get_bigisub_service),
):
    try:
        return service.get_recharge_pin_plans()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


# ============================================================
# RESULT CHECKER
# ============================================================

@router.get("/result-checker/prices")
def get_result_checker_prices(
    current_user=Depends(get_current_user),
    service: BigisubService = Depends(get_bigisub_service),
):
    try:
        return service.get_result_checker_prices()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


# ============================================================
# INTERNET / SMILE
# ============================================================

@router.get("/smile/plans")
def get_smile_plans(
    current_user=Depends(get_current_user),
    service: BigisubService = Depends(get_bigisub_service),
):
    try:
        return service.get_smile_plans()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


# ============================================================
# BETTING
# ============================================================

@router.get("/betting/billers")
def get_betting_billers(
    current_user=Depends(get_current_user),
    service: BigisubService = Depends(get_bigisub_service),
):
    try:
        return service.get_betting_billers()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


# ============================================================
# ELECTRICITY
# ============================================================

@router.post("/electricity/purchase")
def purchase_electricity(
    payload: ElectricityPurchaseRequest,
    current_user=Depends(get_current_user),
    service: BigisubService = Depends(get_bigisub_service),
):
    try:
        return service.purchase_electricity(
            disco=payload.disco,
            meter_number=payload.meter_number,
            meter_type=payload.meter_type,
            amount=payload.amount,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc