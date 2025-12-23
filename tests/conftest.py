"""Shared pytest fixtures for Harvestr MCP tests."""

import os
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import harvestr_mcp.client as client_module


@pytest.fixture
def mock_api_token():
    """Provide a mock API token for testing."""
    return "test-api-token-12345"


@pytest.fixture
def sample_user_data():
    """Sample user data matching the Harvestr API response format."""
    return {
        "id": "user-123",
        "clientId": "client-456",
        "email": "test@example.com",
        "name": "Test User",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z",
    }


@pytest.fixture
def sample_company_data():
    """Sample company data matching the Harvestr API response format."""
    return {
        "id": "company-123",
        "clientId": "client-456",
        "name": "Test Company",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z",
        "importId": None,
        "externalUid": "ext-uid-789",
        "segments": [
            {
                "id": "segment-1",
                "clientId": "client-456",
                "name": "Enterprise",
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-02T00:00:00Z",
            }
        ],
    }


@pytest.fixture
def sample_component_data():
    """Sample component data matching the Harvestr API response format."""
    return {
        "id": "component-123",
        "clientId": "client-456",
        "title": "Test Component",
        "description": "A test component for testing",
        "parentId": None,
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z",
    }


@pytest.fixture
def sample_discovery_data():
    """Sample discovery data matching the Harvestr API response format."""
    return {
        "id": "discovery-123",
        "clientId": "client-456",
        "title": "Feature Request",
        "description": "A new feature request",
        "discoveryStateId": "state-789",
        "parentId": "component-123",
        "parentType": "COMPONENT",
        "assigneeId": "user-123",
        "tags": ["feature", "priority-high"],
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z",
        "lastDiscoverystateUpdatedAt": "2024-01-02T00:00:00Z",
        "lastFeedback": "Some feedback",
        "fieldsValues": None,
    }


@pytest.fixture
def sample_discovery_state_data():
    """Sample discovery state data matching the Harvestr API response format."""
    return {
        "id": "state-789",
        "clientId": "client-456",
        "name": "In Progress",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z",
    }


@pytest.fixture
def sample_message_data():
    """Sample message data matching the Harvestr API response format."""
    return {
        "id": "message-123",
        "clientId": "client-456",
        "content": "This is a test message with feedback",
        "authorId": "user-123",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z",
    }


@pytest.fixture
def sample_feedback_data():
    """Sample feedback data matching the Harvestr API response format."""
    return {
        "id": "feedback-123",
        "clientId": "client-456",
        "starred": True,
        "score": 5,
        "messageId": "message-123",
        "discoveryId": "discovery-123",
        "selections": [
            {
                "id": "selection-1",
                "clientId": "client-456",
                "content": "This is important",
                "fullSelection": False,
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-02T00:00:00Z",
            }
        ],
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z",
    }


@pytest.fixture
def sample_attribute_data():
    """Sample attribute data matching the Harvestr API response format."""
    return {
        "id": "attr-123",
        "clientId": "client-456",
        "name": "Industry",
        "type": "string",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z",
    }


@pytest.fixture
def mock_httpx_response():
    """Create a mock httpx response factory."""

    def _create_response(json_data, status_code=200):
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = json_data
        response.text = str(json_data)
        return response

    return _create_response


@pytest.fixture
def mock_harvestr_client(mock_api_token):
    """Create a mocked HarvestrClient for testing."""
    with patch.dict(os.environ, {"HARVESTR_API_TOKEN": mock_api_token}):
        # Reset global client before each test
        client_module._client = None
        yield
        # Cleanup after test
        client_module._client = None


@pytest.fixture
def mock_async_client(mock_httpx_response):
    """Create a mock async client for HTTP requests."""
    mock_client = AsyncMock()
    mock_client.is_closed = False
    return mock_client
