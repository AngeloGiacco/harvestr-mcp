"""Tests for the Harvestr MCP server tools."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from harvestr_mcp.client import HarvestrClient, HarvestrClientError
import harvestr_mcp.server as server_module
from harvestr_mcp.server import (
    format_response,
    harvestr_create_company,
    harvestr_get_company,
    harvestr_get_component,
    harvestr_get_discovery,
    harvestr_get_discovery_state,
    harvestr_get_discovery_state_by_id,
    harvestr_get_feedback,
    harvestr_get_message,
    harvestr_get_user,
    harvestr_list_companies,
    harvestr_list_company_attribute_values,
    harvestr_list_company_attributes,
    harvestr_list_components,
    harvestr_list_discoveries,
    harvestr_list_discovery_feedback,
    harvestr_list_discovery_states,
    harvestr_list_feedback,
    harvestr_list_message_feedback,
    harvestr_list_messages,
    harvestr_list_user_attribute_values,
    harvestr_list_user_attributes,
    harvestr_list_users,
    harvestr_update_company,
    harvestr_update_company_attribute_values,
    harvestr_update_user_attribute_values,
    mcp,
)


def get_fn(tool):
    """Get the underlying async function from a FunctionTool."""
    return tool.fn if hasattr(tool, "fn") else tool


# --- Fixtures ---


@pytest.fixture
def mock_client():
    return AsyncMock(spec=HarvestrClient)


@pytest.fixture
def sample_user():
    return {"id": "user-123", "clientId": "c-1", "email": "test@example.com", "name": "Test User"}


@pytest.fixture
def sample_company():
    return {"id": "company-123", "clientId": "c-1", "name": "Test Company", "segments": []}


@pytest.fixture
def sample_component():
    return {"id": "component-123", "clientId": "c-1", "title": "Test Component"}


@pytest.fixture
def sample_discovery():
    return {"id": "discovery-123", "clientId": "c-1", "title": "Feature Request"}


@pytest.fixture
def sample_discovery_state():
    return {"id": "state-789", "clientId": "c-1", "name": "In Progress"}


@pytest.fixture
def sample_message():
    return {"id": "message-123", "clientId": "c-1", "content": "Test message"}


@pytest.fixture
def sample_feedback():
    return {"id": "feedback-123", "clientId": "c-1", "starred": True, "score": 5}


@pytest.fixture
def sample_attribute():
    return {"id": "attr-123", "clientId": "c-1", "name": "Industry", "type": "string"}


# --- format_response tests ---


def test_format_response_dict():
    result = format_response({"id": "123"})
    assert json.loads(result) == {"id": "123"}


def test_format_response_list():
    result = format_response([{"id": "1"}, {"id": "2"}])
    assert json.loads(result) == [{"id": "1"}, {"id": "2"}]


def test_format_response_indented():
    result = format_response({"key": "value"})
    assert "\n" in result


# --- MCP server tests ---


def test_server_exists():
    assert mcp is not None


def test_server_has_name():
    assert mcp.name == "Harvestr MCP Server"


# --- List endpoint tests (parametrized) ---


@pytest.mark.asyncio
@pytest.mark.parametrize("tool,endpoint,fixture_name", [
    (harvestr_list_users, "/user", "sample_user"),
    (harvestr_list_companies, "/company", "sample_company"),
    (harvestr_list_components, "/component", "sample_component"),
    (harvestr_list_discoveries, "/discovery", "sample_discovery"),
    (harvestr_list_discovery_states, "/discovery-state", "sample_discovery_state"),
    (harvestr_list_messages, "/message", "sample_message"),
    (harvestr_list_feedback, "/feedback", "sample_feedback"),
])
async def test_list_endpoints(tool, endpoint, fixture_name, mock_client, request):
    sample_data = request.getfixturevalue(fixture_name)
    mock_client.get.return_value = [sample_data]

    with patch.object(server_module, "get_client", return_value=mock_client):
        result = await get_fn(tool)()

    parsed = json.loads(result)
    assert len(parsed) == 1
    # Check that endpoint was called (with or without params)
    assert mock_client.get.called
    call_args = mock_client.get.call_args
    assert endpoint in call_args[0][0]


# --- Get by ID endpoint tests (parametrized) ---


@pytest.mark.asyncio
@pytest.mark.parametrize("tool,endpoint_template,id_param,fixture_name", [
    (harvestr_get_user, "/user/{}", "user_id", "sample_user"),
    (harvestr_get_company, "/company/{}", "company_id", "sample_company"),
    (harvestr_get_component, "/component/{}", "component_id", "sample_component"),
    (harvestr_get_discovery, "/discovery/{}", "discovery_id", "sample_discovery"),
    (harvestr_get_discovery_state_by_id, "/discovery-state/{}", "state_id", "sample_discovery_state"),
    (harvestr_get_message, "/message/{}", "message_id", "sample_message"),
    (harvestr_get_feedback, "/feedback/{}", "feedback_id", "sample_feedback"),
])
async def test_get_by_id_endpoints(tool, endpoint_template, id_param, fixture_name, mock_client, request):
    sample_data = request.getfixturevalue(fixture_name)
    mock_client.get.return_value = sample_data
    test_id = "test-123"

    with patch.object(server_module, "get_client", return_value=mock_client):
        result = await get_fn(tool)(**{id_param: test_id})

    parsed = json.loads(result)
    assert parsed["id"] == sample_data["id"]
    mock_client.get.assert_called()


# --- Attribute endpoints tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize("tool,endpoint", [
    (harvestr_list_user_attributes, "/attribute/user"),
    (harvestr_list_company_attributes, "/attribute/company"),
])
async def test_list_attribute_endpoints(tool, endpoint, mock_client, sample_attribute):
    mock_client.get.return_value = [sample_attribute]

    with patch.object(server_module, "get_client", return_value=mock_client):
        result = await get_fn(tool)()

    parsed = json.loads(result)
    assert len(parsed) == 1
    assert parsed[0]["name"] == "Industry"
    mock_client.get.assert_called_once_with(endpoint)


# --- User tools specific tests ---


@pytest.mark.asyncio
async def test_list_user_attribute_values(mock_client):
    mock_client.get.return_value = [{"attributeId": "attr-1", "value": "test"}]

    with patch.object(server_module, "get_client", return_value=mock_client):
        result = await get_fn(harvestr_list_user_attribute_values)(user_id="user-123")

    assert json.loads(result)[0]["value"] == "test"
    mock_client.get.assert_called_once_with("/user/user-123/attribute-values")


@pytest.mark.asyncio
async def test_update_user_attribute_values(mock_client):
    attr_values = [{"attributeId": "attr-1", "value": "updated"}]
    mock_client.patch.return_value = attr_values

    with patch.object(server_module, "get_client", return_value=mock_client):
        result = await get_fn(harvestr_update_user_attribute_values)(
            user_id="user-123", attribute_values=attr_values
        )

    assert json.loads(result)[0]["value"] == "updated"
    mock_client.patch.assert_called_once_with("/user/user-123/attribute-values", data=attr_values)


# --- Company tools specific tests ---


@pytest.mark.asyncio
async def test_list_companies_with_external_uid(mock_client, sample_company):
    mock_client.get.return_value = [sample_company]

    with patch.object(server_module, "get_client", return_value=mock_client):
        await get_fn(harvestr_list_companies)(external_uid="ext-123")

    mock_client.get.assert_called_once_with("/company", params={"externalUid": "ext-123"})


@pytest.mark.asyncio
async def test_create_company(mock_client):
    mock_client.post.return_value = {"id": "new-company", "name": "New Company"}

    with patch.object(server_module, "get_client", return_value=mock_client):
        result = await get_fn(harvestr_create_company)(name="New Company")

    assert json.loads(result)["id"] == "new-company"
    mock_client.post.assert_called_once_with("/company", data={"name": "New Company"})


@pytest.mark.asyncio
async def test_create_company_with_all_options(mock_client):
    mock_client.post.return_value = {"id": "new", "name": "Full", "externalUid": "ext"}

    with patch.object(server_module, "get_client", return_value=mock_client):
        await get_fn(harvestr_create_company)(
            name="Full", external_uid="ext", segment_ids=["seg-1"]
        )

    mock_client.post.assert_called_once_with(
        "/company",
        data={"name": "Full", "externalUid": "ext", "segmentIds": ["seg-1"]},
    )


@pytest.mark.asyncio
async def test_update_company(mock_client):
    mock_client.patch.return_value = {"id": "c-123", "name": "Updated"}

    with patch.object(server_module, "get_client", return_value=mock_client):
        result = await get_fn(harvestr_update_company)(company_id="c-123", name="Updated")

    assert json.loads(result)["name"] == "Updated"
    mock_client.patch.assert_called_once_with("/company/c-123", data={"name": "Updated"})


@pytest.mark.asyncio
async def test_list_company_attribute_values(mock_client):
    mock_client.get.return_value = [{"attributeId": "a-1", "value": "test"}]

    with patch.object(server_module, "get_client", return_value=mock_client):
        await get_fn(harvestr_list_company_attribute_values)(company_id="c-123")

    mock_client.get.assert_called_once_with("/company/c-123/attribute-values")


@pytest.mark.asyncio
async def test_update_company_attribute_values(mock_client):
    attr_values = [{"attributeId": "a-1", "value": "new"}]
    mock_client.patch.return_value = attr_values

    with patch.object(server_module, "get_client", return_value=mock_client):
        await get_fn(harvestr_update_company_attribute_values)(
            company_id="c-123", attribute_values=attr_values
        )

    mock_client.patch.assert_called_once()


# --- Component tools specific tests ---


@pytest.mark.asyncio
async def test_list_components_with_parent_filter(mock_client, sample_component):
    mock_client.get.return_value = [sample_component]

    with patch.object(server_module, "get_client", return_value=mock_client):
        await get_fn(harvestr_list_components)(parent_id="parent-comp")

    mock_client.get.assert_called_once_with("/component", params={"parentId": "parent-comp"})


# --- Discovery tools specific tests ---


@pytest.mark.asyncio
async def test_list_discoveries_with_fields(mock_client, sample_discovery):
    mock_client.get.return_value = [sample_discovery]

    with patch.object(server_module, "get_client", return_value=mock_client):
        await get_fn(harvestr_list_discoveries)(include_fields=True)

    mock_client.get.assert_called_once_with("/discovery", params={"select": "discoveryfields"})


@pytest.mark.asyncio
async def test_get_discovery_state(mock_client, sample_discovery_state):
    mock_client.get.return_value = sample_discovery_state

    with patch.object(server_module, "get_client", return_value=mock_client):
        result = await get_fn(harvestr_get_discovery_state)(discovery_id="d-123")

    assert json.loads(result)["name"] == "In Progress"
    mock_client.get.assert_called_once_with("/discovery/d-123/discovery-state")


@pytest.mark.asyncio
async def test_list_discovery_feedback(mock_client, sample_feedback):
    mock_client.get.return_value = [sample_feedback]

    with patch.object(server_module, "get_client", return_value=mock_client):
        await get_fn(harvestr_list_discovery_feedback)(discovery_id="d-123")

    mock_client.get.assert_called_once_with("/discovery/d-123/feedback")


# --- Message/Feedback tools specific tests ---


@pytest.mark.asyncio
async def test_list_message_feedback(mock_client, sample_feedback):
    mock_client.get.return_value = [sample_feedback]

    with patch.object(server_module, "get_client", return_value=mock_client):
        await get_fn(harvestr_list_message_feedback)(message_id="m-123")

    mock_client.get.assert_called_once_with("/message/m-123/feedback")


@pytest.mark.asyncio
@pytest.mark.parametrize("filter_param,filter_key", [
    ({"message_id": "m-123"}, {"messageId": "m-123"}),
    ({"discovery_id": "d-123"}, {"discoveryId": "d-123"}),
])
async def test_list_feedback_with_filters(filter_param, filter_key, mock_client, sample_feedback):
    mock_client.get.return_value = [sample_feedback]

    with patch.object(server_module, "get_client", return_value=mock_client):
        await get_fn(harvestr_list_feedback)(**filter_param)

    mock_client.get.assert_called_once_with("/feedback", params=filter_key)


# --- Error handling tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize("tool,kwargs", [
    (harvestr_get_user, {"user_id": "x"}),
    (harvestr_list_companies, {}),
])
async def test_error_handling(tool, kwargs, mock_client):
    mock_client.get.side_effect = HarvestrClientError("API Error", status_code=500)

    with patch.object(server_module, "get_client", return_value=mock_client):
        result = await get_fn(tool)(**kwargs)

    assert "Error:" in result
    assert "API Error" in result
