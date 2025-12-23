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


# --- Sample data fixtures ---


@pytest.fixture
def segment_data():
    return {
        "id": "segment-1",
        "clientId": "client-456",
        "name": "Enterprise",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z",
    }


@pytest.fixture
def company_data(segment_data):
    return {
        "id": "company-123",
        "clientId": "client-456",
        "name": "Test Company",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z",
        "importId": None,
        "externalUid": "ext-uid-789",
        "segments": [segment_data],
    }


@pytest.fixture
def component_data():
    return {
        "id": "component-123",
        "clientId": "client-456",
        "title": "Test Component",
        "description": "A test component",
        "parentId": None,
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z",
    }


@pytest.fixture
def discovery_data():
    return {
        "id": "discovery-123",
        "clientId": "client-456",
        "title": "Feature Request",
        "description": "A new feature",
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
def discovery_state_data():
    return {
        "id": "state-789",
        "clientId": "client-456",
        "name": "In Progress",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z",
    }


@pytest.fixture
def message_data():
    return {
        "id": "message-123",
        "clientId": "client-456",
        "content": "Test message content",
        "authorId": "user-123",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z",
    }


@pytest.fixture
def feedback_data():
    return {
        "id": "feedback-123",
        "clientId": "client-456",
        "starred": True,
        "score": 5,
        "messageId": "message-123",
        "discoveryId": "discovery-123",
        "selections": [{
            "id": "selection-1",
            "clientId": "client-456",
            "content": "Important text",
            "fullSelection": False,
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-02T00:00:00Z",
        }],
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z",
    }


@pytest.fixture
def user_data():
    return {
        "id": "user-123",
        "clientId": "client-456",
        "email": "test@example.com",
        "name": "Test User",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z",
    }


@pytest.fixture
def attribute_data():
    return {
        "id": "attr-123",
        "clientId": "client-456",
        "name": "Industry",
        "type": "string",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z",
    }


# --- Segment tests ---


def test_segment_from_camel_case(segment_data):
    segment = Segment(**segment_data)
    assert segment.id == "segment-1"
    assert segment.client_id == "client-456"
    assert segment.name == "Enterprise"
    assert isinstance(segment.created_at, datetime)


def test_segment_from_snake_case():
    segment = Segment(
        id="seg-1",
        client_id="client-1",
        name="Test",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    assert segment.id == "seg-1"


# --- Company tests ---


def test_company_from_api_response(company_data):
    company = Company(**company_data)
    assert company.id == "company-123"
    assert company.client_id == "client-456"
    assert company.name == "Test Company"
    assert company.external_uid == "ext-uid-789"
    assert len(company.segments) == 1
    assert company.segments[0].name == "Enterprise"


def test_company_optional_fields_defaults():
    company = Company(
        id="c-1",
        clientId="client-1",
        name="Simple",
        createdAt="2024-01-01T00:00:00Z",
        updatedAt="2024-01-01T00:00:00Z",
    )
    assert company.import_id is None
    assert company.external_uid is None
    assert company.segments == []


# --- CompanyCreate/Update tests ---


def test_company_create_minimal():
    payload = CompanyCreate(name="New Company")
    assert payload.name == "New Company"
    assert payload.external_uid is None
    assert payload.segment_ids is None


def test_company_create_full():
    payload = CompanyCreate(
        name="Full Company",
        external_uid="ext-123",
        segment_ids=["seg-1", "seg-2"],
    )
    assert payload.external_uid == "ext-123"
    assert payload.segment_ids == ["seg-1", "seg-2"]


def test_company_update_partial():
    payload = CompanyUpdate(name="Updated")
    assert payload.name == "Updated"
    assert payload.external_uid is None


# --- Component tests ---


def test_component_from_api_response(component_data):
    component = Component(**component_data)
    assert component.id == "component-123"
    assert component.title == "Test Component"
    assert component.description == "A test component"
    assert component.parent_id is None


def test_component_with_parent():
    component = Component(
        id="child",
        clientId="c-1",
        title="Child",
        parentId="parent",
        createdAt="2024-01-01T00:00:00Z",
        updatedAt="2024-01-01T00:00:00Z",
    )
    assert component.parent_id == "parent"


# --- Discovery tests ---


def test_discovery_from_api_response(discovery_data):
    discovery = Discovery(**discovery_data)
    assert discovery.id == "discovery-123"
    assert discovery.title == "Feature Request"
    assert discovery.discovery_state_id == "state-789"
    assert discovery.parent_type == "COMPONENT"
    assert discovery.tags == ["feature", "priority-high"]


def test_discovery_with_fields_values():
    data = {
        "id": "disc-1",
        "clientId": "c-1",
        "title": "Test",
        "discoveryStateId": "s-1",
        "parentId": "p-1",
        "parentType": "COMPONENT",
        "tags": [],
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
        "lastDiscoverystateUpdatedAt": "2024-01-01T00:00:00Z",
        "lastFeedback": "",
        "fieldsValues": [{"field": {"id": "f-1", "clientId": "c-1", "name": "Priority"}, "value": "High"}],
    }
    discovery = Discovery(**data)
    assert discovery.fields_values[0].field.name == "Priority"
    assert discovery.fields_values[0].value == "High"


@pytest.mark.parametrize("parent_type", ["COMPONENT", "DISCOVERY", "NONE"])
def test_discovery_parent_types(parent_type):
    discovery = Discovery(
        id="d-1",
        clientId="c-1",
        title="Test",
        discoveryStateId="s-1",
        parentId="p-1",
        parentType=parent_type,
        tags=[],
        createdAt="2024-01-01T00:00:00Z",
        updatedAt="2024-01-01T00:00:00Z",
        lastDiscoverystateUpdatedAt="2024-01-01T00:00:00Z",
        lastFeedback="",
    )
    assert discovery.parent_type == parent_type


# --- DiscoveryState tests ---


def test_discovery_state_from_api_response(discovery_state_data):
    state = DiscoveryState(**discovery_state_data)
    assert state.id == "state-789"
    assert state.name == "In Progress"


# --- DiscoveryField tests ---


def test_discovery_field_creation():
    field = DiscoveryField(id="f-1", clientId="c-1", name="Custom Field")
    assert field.name == "Custom Field"


def test_discovery_field_value_creation():
    field = DiscoveryField(id="f-1", clientId="c-1", name="Priority")
    field_value = DiscoveryFieldValue(field=field, value="High")
    assert field_value.field.name == "Priority"
    assert field_value.value == "High"


# --- Message tests ---


def test_message_from_api_response(message_data):
    message = Message(**message_data)
    assert message.id == "message-123"
    assert message.content == "Test message content"
    assert message.author_id == "user-123"


def test_message_optional_fields():
    message = Message(
        id="m-1",
        clientId="c-1",
        createdAt="2024-01-01T00:00:00Z",
        updatedAt="2024-01-01T00:00:00Z",
    )
    assert message.content is None
    assert message.author_id is None


# --- Selection tests ---


def test_selection_creation():
    selection = Selection(
        id="s-1",
        clientId="c-1",
        content="Important",
        fullSelection=False,
        createdAt="2024-01-01T00:00:00Z",
        updatedAt="2024-01-01T00:00:00Z",
    )
    assert selection.content == "Important"
    assert selection.full_selection is False


# --- Feedback tests ---


def test_feedback_from_api_response(feedback_data):
    feedback = Feedback(**feedback_data)
    assert feedback.id == "feedback-123"
    assert feedback.starred is True
    assert feedback.score == 5
    assert len(feedback.selections) == 1


def test_feedback_default_values():
    feedback = Feedback(
        id="fb-1",
        clientId="c-1",
        messageId="m-1",
        discoveryId="d-1",
        createdAt="2024-01-01T00:00:00Z",
        updatedAt="2024-01-01T00:00:00Z",
    )
    assert feedback.starred is False
    assert feedback.score == 0
    assert feedback.selections == []


# --- User tests ---


def test_user_from_api_response(user_data):
    user = User(**user_data)
    assert user.id == "user-123"
    assert user.email == "test@example.com"
    assert user.name == "Test User"


def test_user_optional_fields():
    user = User(
        id="u-1",
        clientId="c-1",
        createdAt="2024-01-01T00:00:00Z",
        updatedAt="2024-01-01T00:00:00Z",
    )
    assert user.email is None
    assert user.name is None


# --- Attribute tests ---


def test_attribute_from_api_response(attribute_data):
    attribute = Attribute(**attribute_data)
    assert attribute.id == "attr-123"
    assert attribute.name == "Industry"
    assert attribute.type == "string"


@pytest.mark.parametrize("alias,snake", [
    ("attributeId", "attribute_id"),
])
def test_attribute_value_creation(alias, snake):
    attr_value = AttributeValue(attributeId="attr-1", value="Tech")
    assert attr_value.attribute_id == "attr-1"
    assert attr_value.value == "Tech"


def test_attribute_value_snake_case():
    attr_value = AttributeValue(attribute_id="attr-1", value="Finance")
    assert attr_value.attribute_id == "attr-1"
