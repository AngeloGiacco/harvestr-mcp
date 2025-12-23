"""Harvestr API client."""

import os
from typing import Any

import httpx

API_BASE_URL = "https://rest.harvestr.io/v1"


class HarvestrClientError(Exception):
    """Exception raised for Harvestr API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class HarvestrClient:
    """Client for interacting with the Harvestr API."""

    def __init__(self, token: str | None = None):
        """Initialize the Harvestr client.

        Args:
            token: Harvestr API token. If not provided, reads from HARVESTR_API_TOKEN env var.
        """
        self.token = token or os.environ.get("HARVESTR_API_TOKEN")
        if not self.token:
            raise HarvestrClientError(
                "HARVESTR_API_TOKEN environment variable is required. "
                "Create a token in Harvestr Settings > Integrations > API Access Token"
            )
        self.base_url = API_BASE_URL
        self._client: httpx.AsyncClient | None = None

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Harvestr-Private-App-Token": self.token,
        }

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create an async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self._get_headers(),
                timeout=30.0,
            )
        return self._client

    async def _handle_response(self, response: httpx.Response) -> Any:
        """Handle API response and raise errors if needed."""
        if response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("message", response.text)
            except Exception:
                message = response.text
            raise HarvestrClientError(
                f"API error ({response.status_code}): {message}",
                status_code=response.status_code,
            )
        if response.status_code == 204:
            return None
        return response.json()

    async def get(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        """Make a GET request to the Harvestr API."""
        client = await self._get_client()
        # Filter out None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}
        response = await client.get(endpoint, params=params)
        return await self._handle_response(response)

    async def post(self, endpoint: str, data: dict[str, Any] | None = None) -> Any:
        """Make a POST request to the Harvestr API."""
        client = await self._get_client()
        response = await client.post(endpoint, json=data)
        return await self._handle_response(response)

    async def patch(self, endpoint: str, data: dict[str, Any] | None = None) -> Any:
        """Make a PATCH request to the Harvestr API."""
        client = await self._get_client()
        response = await client.patch(endpoint, json=data)
        return await self._handle_response(response)

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# Global client instance
_client: HarvestrClient | None = None


def get_client() -> HarvestrClient:
    """Get or create the global Harvestr client."""
    global _client
    if _client is None:
        _client = HarvestrClient()
    return _client
