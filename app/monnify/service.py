import uuid

import httpx

from app.core.config import settings
from app.monnify.client import MonnifyClient


class MonnifyService:

    def __init__(self):
        self.client = MonnifyClient()

    def get_access_token(self) -> str:
        return self.client.authenticate()

    def create_reserved_account(
        self,
        *,
        account_name: str,
        customer_email: str,
        customer_name: str,
        bvn: str | None = None,
        nin: str | None = None,
        get_all_available_banks: bool = True,
    ) -> dict:

        if not bvn and not nin:
            raise ValueError(
                "BVN or NIN is required to create a Monnify reserved account."
            )

        account_reference = (
            f"GALAXY-{uuid.uuid4().hex[:20].upper()}"
        )

        payload = {
            "accountReference": account_reference,
            "accountName": account_name,
            "currencyCode": "NGN",
            "contractCode": settings.MONNIFY_CONTRACT_CODE,
            "customerEmail": customer_email,
            "customerName": customer_name,
            "getAllAvailableBanks": get_all_available_banks,
        }

        if bvn:
            payload["bvn"] = bvn

        if nin:
            payload["nin"] = nin

        token = self.client.authenticate()

        url = (
            f"{settings.MONNIFY_BASE_URL.rstrip('/')}"
            "/api/v2/bank-transfer/reserved-accounts"
        )

        try:
            response = httpx.post(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30.0,
            )
        except httpx.RequestError as exc:
            raise RuntimeError(
                "Unable to connect to Monnify."
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "Monnify returned an invalid response."
            ) from exc

        if response.is_error:
            message = data.get(
                "responseMessage",
                "Monnify request failed.",
            )

            raise RuntimeError(
                f"Monnify HTTP {response.status_code}: {message}"
            )

        if not data.get("requestSuccessful"):
            raise RuntimeError(
                data.get(
                    "responseMessage",
                    "Monnify reserved-account creation failed.",
                )
            )

        response_body = data.get("responseBody")

        if not response_body:
            raise RuntimeError(
                "Monnify returned an empty account response."
            )

        return response_body