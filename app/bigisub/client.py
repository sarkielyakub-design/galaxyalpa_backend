import httpx

from app.core.config import settings


class BigisubClient:
    def __init__(self):
        self.base_url = settings.BIGISUB_BASE_URL.rstrip("/")
        self.api_key = settings.BIGISUB_API_KEY

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Token {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _handle_response(self, response: httpx.Response) -> dict:
        if response.is_error:
            raise RuntimeError(
                f"Bigisub HTTP {response.status_code}: {response.text}"
            )

        return response.json()

    def login(
        self,
        email_or_username: str,
        password: str,
    ) -> dict:
        payload = {
            "email_or_username": email_or_username,
            "password": password,
        }

        with httpx.Client(
            http2=False,
            follow_redirects=True,
            timeout=30.0,
        ) as client:
            response = client.post(
                self._url("/api/v2/auth/login/"),
                headers=self._headers(),
                json=payload,
            )

        return self._handle_response(response)

    def get_wallet_balance(self) -> dict:
        with httpx.Client(
            http2=False,
            follow_redirects=True,
            timeout=30.0,
        ) as client:
            response = client.get(
                self._url("/api/v2/financial/wallet/balance/"),
                headers=self._headers(),
            )

        return self._handle_response(response)

    def purchase_airtime(
        self,
        network: int,
        phone_number: str,
        amount: str,
        airtime_type: str,
        pin: str,
    ) -> dict:
        payload = {
            "network": network,
            "phone_number": phone_number,
            "amount": amount,
            "airtime_type": airtime_type,
            "pin": pin,
        }

        with httpx.Client(
            http2=False,
            follow_redirects=True,
            timeout=60.0,
        ) as client:
            response = client.post(
                self._url("/api/v2/vtu/airtime/purchase/"),
                headers=self._headers(),
                json=payload,
            )

        return self._handle_response(response)

    def get_data_plans(self) -> dict:
        with httpx.Client(
            http2=False,
            follow_redirects=True,
            timeout=30.0,
        ) as client:
            response = client.get(
                self._url("/api/v2/vtu/data/plans/"),
                headers=self._headers(),
            )

        return self._handle_response(response)

    def get_cable_plans(self) -> dict:
        with httpx.Client(
            http2=False,
            follow_redirects=True,
            timeout=30.0,
        ) as client:
            response = client.get(
                self._url("/api/v2/vtu/cable/plans/"),
                headers=self._headers(),
            )

        return self._handle_response(response)

    def get_recharge_pin_plans(self) -> dict:
        with httpx.Client(
            http2=False,
            follow_redirects=True,
            timeout=30.0,
        ) as client:
            response = client.get(
                self._url("/api/v2/vtu/recharge-pin/plans/"),
                headers=self._headers(),
            )

        return self._handle_response(response)

    def get_result_checker_prices(self) -> dict:
        with httpx.Client(
            http2=False,
            follow_redirects=True,
            timeout=30.0,
        ) as client:
            response = client.get(
                self._url("/api/v2/bills/result-checker/prices/"),
                headers=self._headers(),
            )

        return self._handle_response(response)

    def get_smile_plans(self) -> dict:
        with httpx.Client(
            http2=False,
            follow_redirects=True,
            timeout=30.0,
        ) as client:
            response = client.get(
                self._url("/api/v2/isp/smile/plans/"),
                headers=self._headers(),
            )

        return self._handle_response(response)

    def get_betting_billers(self) -> dict:
        with httpx.Client(
            http2=False,
            follow_redirects=True,
            timeout=30.0,
        ) as client:
            response = client.get(
                self._url("/api/v2/betting/billers/"),
                headers=self._headers(),
            )

        return self._handle_response(response)