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
        response = httpx.post(
            self._url("/api/v1/auth/login"),
            auth=(
                self.api_key,
                self.secret_key,
            ),
            timeout=30.0,
        )

        response.raise_for_status()

        data = response.json()

        return data["responseBody"]["accessToken"]