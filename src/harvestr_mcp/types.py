"""Pydantic models for Harvestr API entities."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Segment(BaseModel):
    """A company segment."""

    id: str
    client_id: str = Field(alias="clientId")
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class Company(BaseModel):
    """A Harvestr company."""

    id: str
    client_id: str = Field(alias="clientId")
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    import_id: str | None = Field(default=None, alias="importId")
    external_uid: str | None = Field(default=None, alias="externalUid")
    segments: list[Segment] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class CompanyCreate(BaseModel):
    """Payload for creating a company."""

    name: str
    external_uid: str | None = Field(default=None, alias="externalUid")
    segment_ids: list[str] | None = Field(default=None, alias="segmentIds")

    model_config = {"populate_by_name": True}


class CompanyUpdate(BaseModel):
    """Payload for updating a company."""

    name: str | None = None
    external_uid: str | None = Field(default=None, alias="externalUid")
    segment_ids: list[str] | None = Field(default=None, alias="segmentIds")

    model_config = {"populate_by_name": True}


class Component(BaseModel):
    """A Harvestr component."""

    id: str
    client_id: str = Field(alias="clientId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    title: str
    description: str | None = None
    parent_id: str | None = Field(default=None, alias="parentId")

    model_config = {"populate_by_name": True}


class DiscoveryField(BaseModel):
    """A discovery field definition."""

    id: str
    client_id: str = Field(alias="clientId")
    name: str

    model_config = {"populate_by_name": True}


class DiscoveryFieldValue(BaseModel):
    """A discovery field value."""

    field: DiscoveryField
    value: str


class Discovery(BaseModel):
    """A Harvestr discovery."""

    id: str
    client_id: str = Field(alias="clientId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    title: str
    description: str | None = None
    discovery_state_id: str = Field(alias="discoveryStateId")
    parent_id: str = Field(alias="parentId")
    parent_type: Literal["COMPONENT", "DISCOVERY", "NONE"] = Field(alias="parentType")
    assignee_id: str | None = Field(default=None, alias="assigneeId")
    tags: list[str] = Field(default_factory=list)
    last_discoverystate_updated_at: datetime = Field(alias="lastDiscoverystateUpdatedAt")
    last_feedback: str = Field(alias="lastFeedback")
    fields_values: list[DiscoveryFieldValue] | None = Field(default=None, alias="fieldsValues")

    model_config = {"populate_by_name": True}


class DiscoveryState(BaseModel):
    """A discovery state."""

    id: str
    client_id: str = Field(alias="clientId")
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class Selection(BaseModel):
    """A feedback selection."""

    id: str
    client_id: str = Field(alias="clientId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    content: str
    full_selection: bool = Field(alias="fullSelection")

    model_config = {"populate_by_name": True}


class Feedback(BaseModel):
    """A Harvestr feedback item."""

    id: str
    client_id: str = Field(alias="clientId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    starred: bool = False
    score: int = 0
    message_id: str = Field(alias="messageId")
    discovery_id: str = Field(alias="discoveryId")
    selections: list[Selection] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class Message(BaseModel):
    """A Harvestr message."""

    id: str
    client_id: str = Field(alias="clientId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    content: str | None = None
    author_id: str | None = Field(default=None, alias="authorId")

    model_config = {"populate_by_name": True}


class User(BaseModel):
    """A Harvestr user."""

    id: str
    client_id: str = Field(alias="clientId")
    email: str | None = None
    name: str | None = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class Attribute(BaseModel):
    """An attribute definition."""

    id: str
    client_id: str = Field(alias="clientId")
    name: str
    type: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class AttributeValue(BaseModel):
    """An attribute value."""

    attribute_id: str = Field(alias="attributeId")
    value: str

    model_config = {"populate_by_name": True}
