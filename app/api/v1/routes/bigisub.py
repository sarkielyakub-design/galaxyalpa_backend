from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.bigisub.service import BigisubService
from app.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/bigisub",
    tags=["Bigisub"],
)


def get_bigisub_service() -> BigisubService:
    return BigisubService()


class BigisubLoginRequest(BaseModel):
    email_or_username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class AirtimePurchaseRequest(BaseModel):
    network: int
    phone_number: str = Field(..., min_length=5)
    amount: str
    airtime_type: str = "vtu"
    pin: str = Field(..., min_length=4, max_length=4)


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