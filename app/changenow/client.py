import httpx

from app.core.config import settings


class ChangeNOWClient:
    def __init__(self):
        self.base_url = settings.CHANGENOW_BASE_URL.rstrip("/")
        self.api_key = settings.CHANGENOW_API_KEY

    def _headers(self) -> dict[str, str]:
        return {
            "x-changenow-api-key": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def get_available_currencies(self) -> list:
        response = httpx.get(
            self._url("/v2/exchange/currencies"),
            headers=self._headers(),
            params={
                "active": "",
                "flow": "standard",
                "buy": "",
                "sell": "",
            },
            timeout=30.0,
        )

        if response.is_error:
            raise RuntimeError(
                f"ChangeNOW HTTP {response.status_code}: {response.text}"
            )

        return response.json()

    def create_exchange(
        self,
        *,
        from_currency: str,
        to_currency: str,
        from_amount: str,
        address: str,
        from_network: str | None = None,
        to_network: str | None = None,
        extra_id: str | None = None,
        refund_address: str | None = None,
        refund_extra_id: str | None = None,
        user_id: str | None = None,
        contact_email: str | None = None,
        source: str | None = None,
        flow: str = "standard",
        exchange_type: str = "direct",
        rate_id: str | None = None,
    ) -> dict:
        payload = {
            "fromCurrency": from_currency,
            "toCurrency": to_currency,
            "fromAmount": from_amount,
            "toAmount": "",
            "address": address,
            "extraId": extra_id or "",
            "refundAddress": refund_address or "",
            "refundExtraId": refund_extra_id or "",
            "userId": user_id or "",
            "contactEmail": contact_email or "",
            "source": source or "",
            "flow": flow,
            "type": exchange_type,
            "rateId": rate_id or "",
        }

        if from_network:
            payload["fromNetwork"] = from_network

        if to_network:
            payload["toNetwork"] = to_network

        response = httpx.post(
            self._url("/v2/exchange"),
            headers=self._headers(),
            json=payload,
            timeout=30.0,
        )

        if response.is_error:
            raise RuntimeError(
                f"ChangeNOW HTTP {response.status_code}: {response.text}"
            )

        return response.json()

    def get_exchange_status(self, transaction_id: str) -> dict:
        response = httpx.get(
            self._url(f"/v2/exchange/by-id/{transaction_id}"),
            headers=self._headers(),
            timeout=30.0,
        )

        if response.is_error:
            raise RuntimeError(
                f"ChangeNOW HTTP {response.status_code}: {response.text}"
            )

        return response.json()