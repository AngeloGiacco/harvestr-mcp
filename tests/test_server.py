"""Tests for the Harvestr MCP server tools."""

import json
import os
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


# Helper to get the underlying function from FunctionTool objects
def get_fn(tool):
    """Get the underlying async function from a FunctionTool."""
    return tool.fn if hasattr(tool, "fn") else tool


class TestFormatResponse:
    """Tests for the format_response helper."""

    def test_format_dict(self):
        """Test formatting a dictionary."""
        data = {"id": "123", "name": "Test"}
        result = format_response(data)
        parsed = json.loads(result)
        assert parsed == data

    def test_format_list(self):
        """Test formatting a list."""
        data = [{"id": "1"}, {"id": "2"}]
        result = format_response(data)
        parsed = json.loads(result)
        assert parsed == data

    def test_format_with_indent(self):
        """Test that output is indented."""
        data = {"key": "value"}
        result = format_response(data)
        assert "\n" in result  # Indented JSON has newlines


class TestMCPServer:
    """Tests for the MCP server configuration."""

    def test_server_exists(self):
        """Test that the MCP server is created."""
        assert mcp is not None

    def test_server_has_name(self):
        """Test that the server has a name."""
        assert mcp.name == "Harvestr MCP Server"


class TestUserTools:
    """Tests for user-related tools."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_harvestr_client):
        """Set up test environment."""
        pass

    @pytest.mark.asyncio
    async def test_list_users_success(self, sample_user_data):
        """Test listing users successfully."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = [sample_user_data]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_users)()

        parsed = json.loads(result)
        assert len(parsed) == 1
        assert parsed[0]["id"] == "user-123"
        mock_client.get.assert_called_once_with("/user")

    @pytest.mark.asyncio
    async def test_list_users_error(self):
        """Test listing users with API error."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.side_effect = HarvestrClientError("API Error", status_code=500)

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_users)()

        assert "Error:" in result
        assert "API Error" in result

    @pytest.mark.asyncio
    async def test_get_user_success(self, sample_user_data):
        """Test getting a specific user."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = sample_user_data

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_get_user)(user_id="user-123")

        parsed = json.loads(result)
        assert parsed["id"] == "user-123"
        assert parsed["email"] == "test@example.com"
        mock_client.get.assert_called_once_with("/user/user-123")

    @pytest.mark.asyncio
    async def test_list_user_attribute_values(self):
        """Test listing user attribute values."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = [{"attributeId": "attr-1", "value": "test"}]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_user_attribute_values)(user_id="user-123")

        parsed = json.loads(result)
        assert len(parsed) == 1
        mock_client.get.assert_called_once_with("/user/user-123/attribute-values")

    @pytest.mark.asyncio
    async def test_update_user_attribute_values(self):
        """Test updating user attribute values."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.patch.return_value = [{"attributeId": "attr-1", "value": "updated"}]

        attr_values = [{"attributeId": "attr-1", "value": "updated"}]
        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_update_user_attribute_values)(
                user_id="user-123",
                attribute_values=attr_values,
            )

        parsed = json.loads(result)
        assert parsed[0]["value"] == "updated"
        mock_client.patch.assert_called_once_with(
            "/user/user-123/attribute-values",
            data=attr_values,
        )


class TestCompanyTools:
    """Tests for company-related tools."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_harvestr_client):
        """Set up test environment."""
        pass

    @pytest.mark.asyncio
    async def test_list_companies_success(self, sample_company_data):
        """Test listing companies successfully."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = [sample_company_data]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_companies)()

        parsed = json.loads(result)
        assert len(parsed) == 1
        assert parsed[0]["name"] == "Test Company"
        mock_client.get.assert_called_once_with("/company", params=None)

    @pytest.mark.asyncio
    async def test_list_companies_with_external_uid(self, sample_company_data):
        """Test listing companies with external UID filter."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = [sample_company_data]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_companies)(external_uid="ext-123")

        mock_client.get.assert_called_once_with(
            "/company",
            params={"externalUid": "ext-123"},
        )

    @pytest.mark.asyncio
    async def test_create_company(self):
        """Test creating a company."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.post.return_value = {"id": "new-company", "name": "New Company"}

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_create_company)(name="New Company")

        parsed = json.loads(result)
        assert parsed["id"] == "new-company"
        mock_client.post.assert_called_once_with("/company", data={"name": "New Company"})

    @pytest.mark.asyncio
    async def test_create_company_with_all_options(self):
        """Test creating a company with all options."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.post.return_value = {
            "id": "new-company",
            "name": "Full Company",
            "externalUid": "ext-uid",
        }

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_create_company)(
                name="Full Company",
                external_uid="ext-uid",
                segment_ids=["seg-1", "seg-2"],
            )

        mock_client.post.assert_called_once_with(
            "/company",
            data={
                "name": "Full Company",
                "externalUid": "ext-uid",
                "segmentIds": ["seg-1", "seg-2"],
            },
        )

    @pytest.mark.asyncio
    async def test_get_company(self, sample_company_data):
        """Test getting a specific company."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = sample_company_data

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_get_company)(company_id="company-123")

        parsed = json.loads(result)
        assert parsed["id"] == "company-123"
        mock_client.get.assert_called_once_with("/company/company-123")

    @pytest.mark.asyncio
    async def test_update_company(self):
        """Test updating a company."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.patch.return_value = {"id": "company-123", "name": "Updated Name"}

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_update_company)(
                company_id="company-123",
                name="Updated Name",
            )

        parsed = json.loads(result)
        assert parsed["name"] == "Updated Name"
        mock_client.patch.assert_called_once_with(
            "/company/company-123",
            data={"name": "Updated Name"},
        )

    @pytest.mark.asyncio
    async def test_list_company_attribute_values(self):
        """Test listing company attribute values."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = [{"attributeId": "attr-1", "value": "test"}]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_company_attribute_values)(company_id="company-123")

        mock_client.get.assert_called_once_with("/company/company-123/attribute-values")

    @pytest.mark.asyncio
    async def test_update_company_attribute_values(self):
        """Test updating company attribute values."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.patch.return_value = [{"attributeId": "attr-1", "value": "new"}]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_update_company_attribute_values)(
                company_id="company-123",
                attribute_values=[{"attributeId": "attr-1", "value": "new"}],
            )

        mock_client.patch.assert_called_once()


class TestComponentTools:
    """Tests for component-related tools."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_harvestr_client):
        """Set up test environment."""
        pass

    @pytest.mark.asyncio
    async def test_list_components(self, sample_component_data):
        """Test listing components."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = [sample_component_data]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_components)()

        parsed = json.loads(result)
        assert len(parsed) == 1
        mock_client.get.assert_called_once_with("/component", params=None)

    @pytest.mark.asyncio
    async def test_list_components_with_parent_filter(self, sample_component_data):
        """Test listing components with parent filter."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = [sample_component_data]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_components)(parent_id="parent-comp")

        mock_client.get.assert_called_once_with(
            "/component",
            params={"parentId": "parent-comp"},
        )

    @pytest.mark.asyncio
    async def test_get_component(self, sample_component_data):
        """Test getting a specific component."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = sample_component_data

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_get_component)(component_id="component-123")

        parsed = json.loads(result)
        assert parsed["title"] == "Test Component"
        mock_client.get.assert_called_once_with("/component/component-123")


class TestDiscoveryTools:
    """Tests for discovery-related tools."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_harvestr_client):
        """Set up test environment."""
        pass

    @pytest.mark.asyncio
    async def test_list_discoveries(self, sample_discovery_data):
        """Test listing discoveries."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = [sample_discovery_data]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_discoveries)()

        parsed = json.loads(result)
        assert len(parsed) == 1
        mock_client.get.assert_called_once_with("/discovery", params=None)

    @pytest.mark.asyncio
    async def test_list_discoveries_with_fields(self, sample_discovery_data):
        """Test listing discoveries with fields included."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = [sample_discovery_data]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_discoveries)(include_fields=True)

        mock_client.get.assert_called_once_with(
            "/discovery",
            params={"select": "discoveryfields"},
        )

    @pytest.mark.asyncio
    async def test_get_discovery(self, sample_discovery_data):
        """Test getting a specific discovery."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = sample_discovery_data

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_get_discovery)(discovery_id="discovery-123")

        parsed = json.loads(result)
        assert parsed["title"] == "Feature Request"
        mock_client.get.assert_called_once_with("/discovery/discovery-123", params=None)

    @pytest.mark.asyncio
    async def test_get_discovery_state(self, sample_discovery_state_data):
        """Test getting a discovery's state."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = sample_discovery_state_data

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_get_discovery_state)(discovery_id="discovery-123")

        parsed = json.loads(result)
        assert parsed["name"] == "In Progress"
        mock_client.get.assert_called_once_with("/discovery/discovery-123/discovery-state")

    @pytest.mark.asyncio
    async def test_list_discovery_feedback(self, sample_feedback_data):
        """Test listing feedback for a discovery."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = [sample_feedback_data]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_discovery_feedback)(discovery_id="discovery-123")

        mock_client.get.assert_called_once_with("/discovery/discovery-123/feedback")


class TestDiscoveryStateTools:
    """Tests for discovery state tools."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_harvestr_client):
        """Set up test environment."""
        pass

    @pytest.mark.asyncio
    async def test_list_discovery_states(self, sample_discovery_state_data):
        """Test listing discovery states."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = [sample_discovery_state_data]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_discovery_states)()

        parsed = json.loads(result)
        assert len(parsed) == 1
        mock_client.get.assert_called_once_with("/discovery-state")

    @pytest.mark.asyncio
    async def test_get_discovery_state_by_id(self, sample_discovery_state_data):
        """Test getting a specific discovery state."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = sample_discovery_state_data

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_get_discovery_state_by_id)(state_id="state-789")

        parsed = json.loads(result)
        assert parsed["id"] == "state-789"
        mock_client.get.assert_called_once_with("/discovery-state/state-789")


class TestMessageTools:
    """Tests for message-related tools."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_harvestr_client):
        """Set up test environment."""
        pass

    @pytest.mark.asyncio
    async def test_list_messages(self, sample_message_data):
        """Test listing messages."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = [sample_message_data]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_messages)()

        parsed = json.loads(result)
        assert len(parsed) == 1
        mock_client.get.assert_called_once_with("/message")

    @pytest.mark.asyncio
    async def test_get_message(self, sample_message_data):
        """Test getting a specific message."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = sample_message_data

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_get_message)(message_id="message-123")

        parsed = json.loads(result)
        assert parsed["content"] == "This is a test message with feedback"
        mock_client.get.assert_called_once_with("/message/message-123")

    @pytest.mark.asyncio
    async def test_list_message_feedback(self, sample_feedback_data):
        """Test listing feedback for a message."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = [sample_feedback_data]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_message_feedback)(message_id="message-123")

        mock_client.get.assert_called_once_with("/message/message-123/feedback")


class TestFeedbackTools:
    """Tests for feedback-related tools."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_harvestr_client):
        """Set up test environment."""
        pass

    @pytest.mark.asyncio
    async def test_list_feedback(self, sample_feedback_data):
        """Test listing feedback."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = [sample_feedback_data]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_feedback)()

        parsed = json.loads(result)
        assert len(parsed) == 1
        mock_client.get.assert_called_once_with("/feedback", params=None)

    @pytest.mark.asyncio
    async def test_list_feedback_with_message_filter(self, sample_feedback_data):
        """Test listing feedback filtered by message."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = [sample_feedback_data]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_feedback)(message_id="msg-123")

        mock_client.get.assert_called_once_with(
            "/feedback",
            params={"messageId": "msg-123"},
        )

    @pytest.mark.asyncio
    async def test_list_feedback_with_discovery_filter(self, sample_feedback_data):
        """Test listing feedback filtered by discovery."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = [sample_feedback_data]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_feedback)(discovery_id="disc-123")

        mock_client.get.assert_called_once_with(
            "/feedback",
            params={"discoveryId": "disc-123"},
        )

    @pytest.mark.asyncio
    async def test_get_feedback(self, sample_feedback_data):
        """Test getting specific feedback."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = sample_feedback_data

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_get_feedback)(feedback_id="feedback-123")

        parsed = json.loads(result)
        assert parsed["starred"] is True
        mock_client.get.assert_called_once_with("/feedback/feedback-123")


class TestAttributeTools:
    """Tests for attribute-related tools."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_harvestr_client):
        """Set up test environment."""
        pass

    @pytest.mark.asyncio
    async def test_list_user_attributes(self, sample_attribute_data):
        """Test listing user attributes."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = [sample_attribute_data]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_user_attributes)()

        parsed = json.loads(result)
        assert len(parsed) == 1
        assert parsed[0]["name"] == "Industry"
        mock_client.get.assert_called_once_with("/attribute/user")

    @pytest.mark.asyncio
    async def test_list_company_attributes(self, sample_attribute_data):
        """Test listing company attributes."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.return_value = [sample_attribute_data]

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_company_attributes)()

        parsed = json.loads(result)
        assert len(parsed) == 1
        mock_client.get.assert_called_once_with("/attribute/company")


class TestErrorHandling:
    """Tests for error handling across tools."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_harvestr_client):
        """Set up test environment."""
        pass

    @pytest.mark.asyncio
    async def test_error_returns_message(self):
        """Test that errors return a formatted message."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.side_effect = HarvestrClientError("Not found", status_code=404)

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_get_user)(user_id="nonexistent")

        assert "Error:" in result
        assert "Not found" in result

    @pytest.mark.asyncio
    async def test_server_error_handling(self):
        """Test handling of server errors."""
        mock_client = AsyncMock(spec=HarvestrClient)
        mock_client.get.side_effect = HarvestrClientError(
            "Internal server error",
            status_code=500,
        )

        with patch.object(server_module, "get_client", return_value=mock_client):
            result = await get_fn(harvestr_list_companies)()

        assert "Error:" in result
        assert "Internal server error" in result
