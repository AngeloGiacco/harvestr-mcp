"""Tests for the Harvestr API client module."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from harvestr_mcp.client import (
    API_BASE_URL,
    HarvestrClient,
    HarvestrClientError,
    get_client,
)
import harvestr_mcp.client as client_module


# --- HarvestrClientError tests ---


def test_error_with_message_only():
    error = HarvestrClientError("Something went wrong")
    assert error.message == "Something went wrong"
    assert error.status_code is None
    assert str(error) == "Something went wrong"


def test_error_with_message_and_status_code():
    error = HarvestrClientError("Not found", status_code=404)
    assert error.message == "Not found"
    assert error.status_code == 404


# --- HarvestrClient initialization tests ---


def test_client_init_with_token_parameter():
    client = HarvestrClient(token="my-api-token")
    assert client.token == "my-api-token"
    assert client.base_url == API_BASE_URL


def test_client_init_with_env_var():
    with patch.dict(os.environ, {"HARVESTR_API_TOKEN": "env-token"}):
        client = HarvestrClient()
        assert client.token == "env-token"


def test_client_init_prefers_explicit_token():
    with patch.dict(os.environ, {"HARVESTR_API_TOKEN": "env-token"}):
        client = HarvestrClient(token="explicit-token")
        assert client.token == "explicit-token"


def test_client_init_without_token_raises_error():
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("HARVESTR_API_TOKEN", None)
        with pytest.raises(HarvestrClientError) as exc_info:
            HarvestrClient()
        assert "HARVESTR_API_TOKEN" in exc_info.value.message


def test_client_starts_without_http_client():
    client = HarvestrClient(token="test-token")
    assert client._client is None


# --- Headers tests ---


def test_headers_contain_auth_token():
    client = HarvestrClient(token="test-token")
    headers = client._get_headers()
    assert headers["X-Harvestr-Private-App-Token"] == "test-token"


def test_headers_contain_content_type():
    client = HarvestrClient(token="test-token")
    headers = client._get_headers()
    assert headers["Content-Type"] == "application/json"
    assert headers["Accept"] == "application/json"


# --- HTTP methods tests ---


@pytest.fixture
def client():
    return HarvestrClient(token="test-token")


@pytest.fixture
def mock_httpx_response():
    def _create_response(json_data, status_code=200):
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = json_data
        response.text = str(json_data)
        return response
    return _create_response


@pytest.mark.asyncio
async def test_get_request(client, mock_httpx_response):
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
async def test_get_request_with_params(client, mock_httpx_response):
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
async def test_get_filters_none_params(client, mock_httpx_response):
    mock_response = mock_httpx_response([])
    mock_http_client = AsyncMock()
    mock_http_client.get.return_value = mock_response
    mock_http_client.is_closed = False

    with patch.object(client, "_get_client", return_value=mock_http_client):
        await client.get("/test", params={"filter": "active", "empty": None})

    mock_http_client.get.assert_called_once_with("/test", params={"filter": "active"})


@pytest.mark.asyncio
async def test_post_request(client, mock_httpx_response):
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
async def test_patch_request(client, mock_httpx_response):
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


# --- Response handling tests ---


@pytest.mark.asyncio
async def test_handle_successful_response(client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}

    result = await client._handle_response(mock_response)
    assert result == {"success": True}


@pytest.mark.asyncio
async def test_handle_204_no_content(client):
    mock_response = MagicMock()
    mock_response.status_code = 204

    result = await client._handle_response(mock_response)
    assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code,error_message", [
    (400, "Bad request data"),
    (404, "Resource not found"),
    (500, "Internal Server Error"),
])
async def test_handle_error_responses(client, status_code, error_message):
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = {"message": error_message}
    mock_response.text = error_message

    with pytest.raises(HarvestrClientError) as exc_info:
        await client._handle_response(mock_response)

    assert exc_info.value.status_code == status_code
    assert error_message in exc_info.value.message


@pytest.mark.asyncio
async def test_handle_error_response_without_json(client):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.side_effect = Exception("Not JSON")
    mock_response.text = "Internal Server Error"

    with pytest.raises(HarvestrClientError) as exc_info:
        await client._handle_response(mock_response)

    assert exc_info.value.status_code == 500
    assert "Internal Server Error" in exc_info.value.message


# --- Client close tests ---


@pytest.mark.asyncio
async def test_close_with_active_client():
    client = HarvestrClient(token="test-token")
    mock_http_client = AsyncMock()
    mock_http_client.is_closed = False
    client._client = mock_http_client

    await client.close()
    mock_http_client.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_close_without_client():
    client = HarvestrClient(token="test-token")
    await client.close()  # Should not raise


@pytest.mark.asyncio
async def test_close_already_closed_client():
    client = HarvestrClient(token="test-token")
    mock_http_client = AsyncMock()
    mock_http_client.is_closed = True
    client._client = mock_http_client

    await client.close()
    mock_http_client.aclose.assert_not_called()


# --- Global client getter tests ---


@pytest.fixture
def reset_global_client():
    client_module._client = None
    yield
    client_module._client = None


def test_get_client_creates_new_instance(reset_global_client):
    with patch.dict(os.environ, {"HARVESTR_API_TOKEN": "test-token"}):
        result = get_client()
        assert result is not None
        assert isinstance(result, HarvestrClient)


def test_get_client_returns_same_instance(reset_global_client):
    with patch.dict(os.environ, {"HARVESTR_API_TOKEN": "test-token"}):
        client1 = get_client()
        client2 = get_client()
        assert client1 is client2


def test_get_client_raises_without_token(reset_global_client):
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("HARVESTR_API_TOKEN", None)
        with pytest.raises(HarvestrClientError):
            get_client()
