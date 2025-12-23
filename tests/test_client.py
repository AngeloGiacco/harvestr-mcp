"""Tests for the Harvestr API client module."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from harvestr_mcp.client import (
    API_BASE_URL,
    HarvestrClient,
    HarvestrClientError,
    get_client,
)
import harvestr_mcp.client as client_module


class TestHarvestrClientError:
    """Tests for HarvestrClientError exception."""

    def test_error_with_message_only(self):
        """Test creating an error with just a message."""
        error = HarvestrClientError("Something went wrong")
        assert error.message == "Something went wrong"
        assert error.status_code is None
        assert str(error) == "Something went wrong"

    def test_error_with_message_and_status_code(self):
        """Test creating an error with message and status code."""
        error = HarvestrClientError("Not found", status_code=404)
        assert error.message == "Not found"
        assert error.status_code == 404


class TestHarvestrClientInit:
    """Tests for HarvestrClient initialization."""

    def test_init_with_token_parameter(self):
        """Test initializing client with explicit token parameter."""
        client = HarvestrClient(token="my-api-token")
        assert client.token == "my-api-token"
        assert client.base_url == API_BASE_URL

    def test_init_with_env_var(self):
        """Test initializing client with environment variable."""
        with patch.dict(os.environ, {"HARVESTR_API_TOKEN": "env-token"}):
            client = HarvestrClient()
            assert client.token == "env-token"

    def test_init_prefers_explicit_token(self):
        """Test that explicit token parameter takes precedence over env var."""
        with patch.dict(os.environ, {"HARVESTR_API_TOKEN": "env-token"}):
            client = HarvestrClient(token="explicit-token")
            assert client.token == "explicit-token"

    def test_init_without_token_raises_error(self):
        """Test that missing token raises HarvestrClientError."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove HARVESTR_API_TOKEN if it exists
            os.environ.pop("HARVESTR_API_TOKEN", None)
            with pytest.raises(HarvestrClientError) as exc_info:
                HarvestrClient()
            assert "HARVESTR_API_TOKEN" in exc_info.value.message

    def test_client_starts_without_http_client(self):
        """Test that HTTP client is not created on init."""
        client = HarvestrClient(token="test-token")
        assert client._client is None


class TestHarvestrClientHeaders:
    """Tests for client headers."""

    def test_get_headers_contains_auth_token(self):
        """Test that headers include the authentication token."""
        client = HarvestrClient(token="test-token")
        headers = client._get_headers()
        assert headers["X-Harvestr-Private-App-Token"] == "test-token"

    def test_get_headers_contains_content_type(self):
        """Test that headers include proper content type."""
        client = HarvestrClient(token="test-token")
        headers = client._get_headers()
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"


class TestHarvestrClientHttpMethods:
    """Tests for HTTP methods."""

    @pytest.fixture
    def client(self):
        """Create a client for testing."""
        return HarvestrClient(token="test-token")

    @pytest.mark.asyncio
    async def test_get_request(self, client, mock_httpx_response):
        """Test GET request."""
        expected_data = {"id": "123", "name": "Test"}
        mock_response = mock_httpx_response(expected_data)

        mock_http_client = AsyncMock()
        mock_http_client.get.return_value = mock_response
        mock_http_client.is_closed = False

        with patch.object(client, "_get_client", return_value=mock_http_client):
            result = await client.get("/test-endpoint")

        assert result == expected_data
        mock_http_client.get.assert_called_once_with("/test-endpoint", params=None)

    @pytest.mark.asyncio
    async def test_get_request_with_params(self, client, mock_httpx_response):
        """Test GET request with query parameters."""
        expected_data = [{"id": "1"}, {"id": "2"}]
        mock_response = mock_httpx_response(expected_data)

        mock_http_client = AsyncMock()
        mock_http_client.get.return_value = mock_response
        mock_http_client.is_closed = False

        with patch.object(client, "_get_client", return_value=mock_http_client):
            result = await client.get("/test", params={"filter": "active"})

        assert result == expected_data
        mock_http_client.get.assert_called_once_with("/test", params={"filter": "active"})

    @pytest.mark.asyncio
    async def test_get_filters_none_params(self, client, mock_httpx_response):
        """Test that None values are filtered from params."""
        mock_response = mock_httpx_response([])
        mock_http_client = AsyncMock()
        mock_http_client.get.return_value = mock_response
        mock_http_client.is_closed = False

        with patch.object(client, "_get_client", return_value=mock_http_client):
            await client.get("/test", params={"filter": "active", "empty": None})

        mock_http_client.get.assert_called_once_with("/test", params={"filter": "active"})

    @pytest.mark.asyncio
    async def test_post_request(self, client, mock_httpx_response):
        """Test POST request."""
        request_data = {"name": "New Item"}
        response_data = {"id": "new-123", "name": "New Item"}
        mock_response = mock_httpx_response(response_data)

        mock_http_client = AsyncMock()
        mock_http_client.post.return_value = mock_response
        mock_http_client.is_closed = False

        with patch.object(client, "_get_client", return_value=mock_http_client):
            result = await client.post("/items", data=request_data)

        assert result == response_data
        mock_http_client.post.assert_called_once_with("/items", json=request_data)

    @pytest.mark.asyncio
    async def test_patch_request(self, client, mock_httpx_response):
        """Test PATCH request."""
        request_data = {"name": "Updated Name"}
        response_data = {"id": "123", "name": "Updated Name"}
        mock_response = mock_httpx_response(response_data)

        mock_http_client = AsyncMock()
        mock_http_client.patch.return_value = mock_response
        mock_http_client.is_closed = False

        with patch.object(client, "_get_client", return_value=mock_http_client):
            result = await client.patch("/items/123", data=request_data)

        assert result == response_data
        mock_http_client.patch.assert_called_once_with("/items/123", json=request_data)


class TestHarvestrClientResponseHandling:
    """Tests for response handling."""

    @pytest.fixture
    def client(self):
        """Create a client for testing."""
        return HarvestrClient(token="test-token")

    @pytest.mark.asyncio
    async def test_handle_successful_response(self, client):
        """Test handling a successful response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        result = await client._handle_response(mock_response)
        assert result == {"success": True}

    @pytest.mark.asyncio
    async def test_handle_204_no_content(self, client):
        """Test handling 204 No Content response."""
        mock_response = MagicMock()
        mock_response.status_code = 204

        result = await client._handle_response(mock_response)
        assert result is None

    @pytest.mark.asyncio
    async def test_handle_error_response_with_json(self, client):
        """Test handling error response with JSON body."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Bad request data"}
        mock_response.text = "Bad request data"

        with pytest.raises(HarvestrClientError) as exc_info:
            await client._handle_response(mock_response)

        assert exc_info.value.status_code == 400
        assert "Bad request data" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_handle_error_response_without_json(self, client):
        """Test handling error response without JSON body."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.side_effect = Exception("Not JSON")
        mock_response.text = "Internal Server Error"

        with pytest.raises(HarvestrClientError) as exc_info:
            await client._handle_response(mock_response)

        assert exc_info.value.status_code == 500
        assert "Internal Server Error" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_handle_404_response(self, client):
        """Test handling 404 Not Found response."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Resource not found"}
        mock_response.text = "Not found"

        with pytest.raises(HarvestrClientError) as exc_info:
            await client._handle_response(mock_response)

        assert exc_info.value.status_code == 404


class TestHarvestrClientClose:
    """Tests for client cleanup."""

    @pytest.mark.asyncio
    async def test_close_with_active_client(self):
        """Test closing an active HTTP client."""
        client = HarvestrClient(token="test-token")
        mock_http_client = AsyncMock()
        mock_http_client.is_closed = False
        client._client = mock_http_client

        await client.close()
        mock_http_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_without_client(self):
        """Test closing when no HTTP client exists."""
        client = HarvestrClient(token="test-token")
        # Should not raise an error
        await client.close()

    @pytest.mark.asyncio
    async def test_close_already_closed_client(self):
        """Test closing an already closed HTTP client."""
        client = HarvestrClient(token="test-token")
        mock_http_client = AsyncMock()
        mock_http_client.is_closed = True
        client._client = mock_http_client

        await client.close()
        mock_http_client.aclose.assert_not_called()


class TestGetClient:
    """Tests for the global client getter."""

    def test_get_client_creates_new_instance(self, mock_harvestr_client):
        """Test that get_client creates a new instance when none exists."""
        client = get_client()
        assert client is not None
        assert isinstance(client, HarvestrClient)

    def test_get_client_returns_same_instance(self, mock_harvestr_client):
        """Test that get_client returns the same instance on subsequent calls."""
        client1 = get_client()
        client2 = get_client()
        assert client1 is client2

    def test_get_client_raises_without_token(self):
        """Test that get_client raises error when token is not configured."""
        # Reset global client
        client_module._client = None
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("HARVESTR_API_TOKEN", None)
            with pytest.raises(HarvestrClientError):
                get_client()
