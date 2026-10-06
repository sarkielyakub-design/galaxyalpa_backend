import httpx

from app.core.config import settings


class MonnifyClient:
    def __init__(self):
        self.base_url = settings.MONNIFY_BASE_URL.rstrip("/")
        self.api_key = settings.MONNIFY_API_KEY
        self.secret_key = settings.MONNIFY_SECRET_KEY

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def authenticate(self) -> str:
        try:
            with httpx.Client(
                http2=False,
                follow_redirects=True,
                timeout=30.0,
            ) as client:
                response = client.post(
                    self._url("/api/v1/auth/login"),
                    auth=(
                        self.api_key,
                        self.secret_key,
                    ),
                    headers={
                        "Accept": "application/json",
                    },
                )
        except httpx.RequestError as exc:
            raise RuntimeError(
                f"Unable to connect to Monnify authentication service: {exc}"
            ) from exc

        try:
            response_data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                f"Monnify returned an invalid authentication response. "
                f"HTTP {response.status_code}"
            ) from exc

        if response.is_error:
            message = response_data.get(
                "responseMessage",
                "Monnify authentication failed.",
            )

            raise RuntimeError(
                f"Monnify HTTP {response.status_code}: {message}"
            )

        if not response_data.get("requestSuccessful"):
            raise RuntimeError(
                response_data.get(
                    "responseMessage",
                    "Monnify authentication failed.",
                )
            )

        response_body = response_data.get("responseBody") or {}

        access_token = response_body.get("accessToken")

        if not access_token:
            raise RuntimeError(
                "Monnify authentication response did not contain "
                "an access token."
            )

        return access_token

    # ============================================================
    # AUTHENTICATED GET
    # ============================================================

    def get(
        self,
        path: str,
        params: dict | None = None,
    ):
        access_token = self.authenticate()

        try:
            with httpx.Client(
                http2=False,
                follow_redirects=True,
                timeout=30.0,
            ) as client:
                response = client.get(
                    self._url(path),
                    params=params,
                    headers={
                        "Accept": "application/json",
                        "Authorization": f"Bearer {access_token}",
                    },
                )
        except httpx.RequestError as exc:
            raise RuntimeError(
                f"Unable to connect to Monnify service: {exc}"
            ) from exc

        try:
            response_data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                f"Monnify returned an invalid response. "
                f"HTTP {response.status_code}"
            ) from exc

        if response.is_error:
            message = response_data.get(
                "responseMessage",
                response_data.get(
                    "message",
                    "Monnify request failed.",
                ),
            )

            raise RuntimeError(
                f"Monnify HTTP {response.status_code}: {message}"
            )

        return response_data

    # ============================================================
    # AUTHENTICATED POST
    # ============================================================

    def post(
        self,
        path: str,
        data: dict | None = None,
    ):
        access_token = self.authenticate()

        try:
            with httpx.Client(
                http2=False,
                follow_redirects=True,
                timeout=30.0,
            ) as client:
                response = client.post(
                    self._url(path),
                    json=data or {},
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {access_token}",
                    },
                )
        except httpx.RequestError as exc:
            raise RuntimeError(
                f"Unable to connect to Monnify service: {exc}"
            ) from exc

        try:
            response_data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                f"Monnify returned an invalid response. "
                f"HTTP {response.status_code}"
            ) from exc

        if response.is_error:
            message = response_data.get(
                "responseMessage",
                response_data.get(
                    "message",
                    "Monnify request failed.",
                ),
            )

            raise RuntimeError(
                f"Monnify HTTP {response.status_code}: {message}"
            )

        return response_data