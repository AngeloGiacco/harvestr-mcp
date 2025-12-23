"""Tests for the Harvestr Pydantic models."""

from datetime import datetime, timezone

import pytest

from harvestr_mcp.types import (
    Attribute,
    AttributeValue,
    Company,
    CompanyCreate,
    CompanyUpdate,
    Component,
    Discovery,
    DiscoveryField,
    DiscoveryFieldValue,
    DiscoveryState,
    Feedback,
    Message,
    Segment,
    Selection,
    User,
)


class TestSegment:
    """Tests for Segment model."""

    def test_create_from_camel_case(self, sample_company_data):
        """Test creating Segment from camelCase API response."""
        segment_data = sample_company_data["segments"][0]
        segment = Segment(**segment_data)

        assert segment.id == "segment-1"
        assert segment.client_id == "client-456"
        assert segment.name == "Enterprise"
        assert isinstance(segment.created_at, datetime)
        assert isinstance(segment.updated_at, datetime)

    def test_create_from_snake_case(self):
        """Test creating Segment using snake_case names."""
        segment = Segment(
            id="seg-1",
            client_id="client-1",
            name="Test Segment",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        assert segment.id == "seg-1"
        assert segment.client_id == "client-1"


class TestCompany:
    """Tests for Company model."""

    def test_create_from_api_response(self, sample_company_data):
        """Test creating Company from API response."""
        company = Company(**sample_company_data)

        assert company.id == "company-123"
        assert company.client_id == "client-456"
        assert company.name == "Test Company"
        assert company.external_uid == "ext-uid-789"
        assert len(company.segments) == 1
        assert company.segments[0].name == "Enterprise"
        assert company.import_id is None

    def test_optional_fields_default_values(self):
        """Test that optional fields have correct defaults."""
        company = Company(
            id="c-1",
            clientId="client-1",
            name="Simple Company",
            createdAt="2024-01-01T00:00:00Z",
            updatedAt="2024-01-01T00:00:00Z",
        )
        assert company.import_id is None
        assert company.external_uid is None
        assert company.segments == []


class TestCompanyCreate:
    """Tests for CompanyCreate model."""

    def test_create_minimal(self):
        """Test creating with only required fields."""
        payload = CompanyCreate(name="New Company")
        assert payload.name == "New Company"
        assert payload.external_uid is None
        assert payload.segment_ids is None

    def test_create_full(self):
        """Test creating with all fields."""
        payload = CompanyCreate(
            name="Full Company",
            external_uid="ext-123",
            segment_ids=["seg-1", "seg-2"],
        )
        assert payload.name == "Full Company"
        assert payload.external_uid == "ext-123"
        assert payload.segment_ids == ["seg-1", "seg-2"]


class TestCompanyUpdate:
    """Tests for CompanyUpdate model."""

    def test_update_single_field(self):
        """Test updating a single field."""
        payload = CompanyUpdate(name="Updated Name")
        assert payload.name == "Updated Name"
        assert payload.external_uid is None

    def test_update_multiple_fields(self):
        """Test updating multiple fields."""
        payload = CompanyUpdate(
            name="New Name",
            external_uid="new-uid",
            segment_ids=["seg-new"],
        )
        assert payload.name == "New Name"
        assert payload.external_uid == "new-uid"
        assert payload.segment_ids == ["seg-new"]


class TestComponent:
    """Tests for Component model."""

    def test_create_from_api_response(self, sample_component_data):
        """Test creating Component from API response."""
        component = Component(**sample_component_data)

        assert component.id == "component-123"
        assert component.client_id == "client-456"
        assert component.title == "Test Component"
        assert component.description == "A test component for testing"
        assert component.parent_id is None

    def test_component_with_parent(self):
        """Test component with parent ID."""
        component = Component(
            id="comp-child",
            clientId="client-1",
            title="Child Component",
            parentId="comp-parent",
            createdAt="2024-01-01T00:00:00Z",
            updatedAt="2024-01-01T00:00:00Z",
        )
        assert component.parent_id == "comp-parent"


class TestDiscovery:
    """Tests for Discovery model."""

    def test_create_from_api_response(self, sample_discovery_data):
        """Test creating Discovery from API response."""
        discovery = Discovery(**sample_discovery_data)

        assert discovery.id == "discovery-123"
        assert discovery.title == "Feature Request"
        assert discovery.description == "A new feature request"
        assert discovery.discovery_state_id == "state-789"
        assert discovery.parent_id == "component-123"
        assert discovery.parent_type == "COMPONENT"
        assert discovery.assignee_id == "user-123"
        assert discovery.tags == ["feature", "priority-high"]

    def test_discovery_with_fields_values(self):
        """Test discovery with field values."""
        data = {
            "id": "disc-1",
            "clientId": "client-1",
            "title": "Test Discovery",
            "discoveryStateId": "state-1",
            "parentId": "comp-1",
            "parentType": "COMPONENT",
            "tags": [],
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z",
            "lastDiscoverystateUpdatedAt": "2024-01-01T00:00:00Z",
            "lastFeedback": "",
            "fieldsValues": [
                {
                    "field": {
                        "id": "field-1",
                        "clientId": "client-1",
                        "name": "Priority",
                    },
                    "value": "High",
                }
            ],
        }
        discovery = Discovery(**data)
        assert discovery.fields_values is not None
        assert len(discovery.fields_values) == 1
        assert discovery.fields_values[0].field.name == "Priority"
        assert discovery.fields_values[0].value == "High"

    def test_discovery_parent_types(self):
        """Test all valid parent types."""
        for parent_type in ["COMPONENT", "DISCOVERY", "NONE"]:
            discovery = Discovery(
                id="disc-1",
                clientId="client-1",
                title="Test",
                discoveryStateId="state-1",
                parentId="parent-1",
                parentType=parent_type,
                tags=[],
                createdAt="2024-01-01T00:00:00Z",
                updatedAt="2024-01-01T00:00:00Z",
                lastDiscoverystateUpdatedAt="2024-01-01T00:00:00Z",
                lastFeedback="",
            )
            assert discovery.parent_type == parent_type


class TestDiscoveryState:
    """Tests for DiscoveryState model."""

    def test_create_from_api_response(self, sample_discovery_state_data):
        """Test creating DiscoveryState from API response."""
        state = DiscoveryState(**sample_discovery_state_data)

        assert state.id == "state-789"
        assert state.client_id == "client-456"
        assert state.name == "In Progress"


class TestDiscoveryField:
    """Tests for DiscoveryField model."""

    def test_create_field(self):
        """Test creating a discovery field."""
        field = DiscoveryField(
            id="field-1",
            clientId="client-1",
            name="Custom Field",
        )
        assert field.id == "field-1"
        assert field.name == "Custom Field"


class TestDiscoveryFieldValue:
    """Tests for DiscoveryFieldValue model."""

    def test_create_field_value(self):
        """Test creating a field value."""
        field = DiscoveryField(
            id="field-1",
            clientId="client-1",
            name="Priority",
        )
        field_value = DiscoveryFieldValue(field=field, value="High")
        assert field_value.field.name == "Priority"
        assert field_value.value == "High"


class TestMessage:
    """Tests for Message model."""

    def test_create_from_api_response(self, sample_message_data):
        """Test creating Message from API response."""
        message = Message(**sample_message_data)

        assert message.id == "message-123"
        assert message.client_id == "client-456"
        assert message.content == "This is a test message with feedback"
        assert message.author_id == "user-123"

    def test_message_optional_fields(self):
        """Test message with optional fields as None."""
        message = Message(
            id="msg-1",
            clientId="client-1",
            createdAt="2024-01-01T00:00:00Z",
            updatedAt="2024-01-01T00:00:00Z",
        )
        assert message.content is None
        assert message.author_id is None


class TestSelection:
    """Tests for Selection model."""

    def test_create_selection(self):
        """Test creating a selection."""
        selection = Selection(
            id="sel-1",
            clientId="client-1",
            content="Important text",
            fullSelection=False,
            createdAt="2024-01-01T00:00:00Z",
            updatedAt="2024-01-01T00:00:00Z",
        )
        assert selection.id == "sel-1"
        assert selection.content == "Important text"
        assert selection.full_selection is False


class TestFeedback:
    """Tests for Feedback model."""

    def test_create_from_api_response(self, sample_feedback_data):
        """Test creating Feedback from API response."""
        feedback = Feedback(**sample_feedback_data)

        assert feedback.id == "feedback-123"
        assert feedback.starred is True
        assert feedback.score == 5
        assert feedback.message_id == "message-123"
        assert feedback.discovery_id == "discovery-123"
        assert len(feedback.selections) == 1
        assert feedback.selections[0].content == "This is important"

    def test_feedback_default_values(self):
        """Test feedback with default values."""
        feedback = Feedback(
            id="fb-1",
            clientId="client-1",
            messageId="msg-1",
            discoveryId="disc-1",
            createdAt="2024-01-01T00:00:00Z",
            updatedAt="2024-01-01T00:00:00Z",
        )
        assert feedback.starred is False
        assert feedback.score == 0
        assert feedback.selections == []


class TestUser:
    """Tests for User model."""

    def test_create_from_api_response(self, sample_user_data):
        """Test creating User from API response."""
        user = User(**sample_user_data)

        assert user.id == "user-123"
        assert user.client_id == "client-456"
        assert user.email == "test@example.com"
        assert user.name == "Test User"

    def test_user_optional_fields(self):
        """Test user with optional fields as None."""
        user = User(
            id="user-1",
            clientId="client-1",
            createdAt="2024-01-01T00:00:00Z",
            updatedAt="2024-01-01T00:00:00Z",
        )
        assert user.email is None
        assert user.name is None


class TestAttribute:
    """Tests for Attribute model."""

    def test_create_from_api_response(self, sample_attribute_data):
        """Test creating Attribute from API response."""
        attribute = Attribute(**sample_attribute_data)

        assert attribute.id == "attr-123"
        assert attribute.client_id == "client-456"
        assert attribute.name == "Industry"
        assert attribute.type == "string"


class TestAttributeValue:
    """Tests for AttributeValue model."""

    def test_create_attribute_value(self):
        """Test creating an attribute value."""
        attr_value = AttributeValue(
            attributeId="attr-1",
            value="Technology",
        )
        assert attr_value.attribute_id == "attr-1"
        assert attr_value.value == "Technology"

    def test_create_with_snake_case(self):
        """Test creating with snake_case."""
        attr_value = AttributeValue(
            attribute_id="attr-1",
            value="Finance",
        )
        assert attr_value.attribute_id == "attr-1"
        assert attr_value.value == "Finance"
