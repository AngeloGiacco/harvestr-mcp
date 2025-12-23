"""Type definitions for Harvestr API entities."""

from typing import Literal, TypedDict


class Segment(TypedDict):
    """A company segment."""

    id: str
    clientId: str
    name: str
    createdAt: str
    updatedAt: str


class Company(TypedDict, total=False):
    """A Harvestr company."""

    id: str
    clientId: str
    name: str
    createdAt: str
    updatedAt: str
    importId: str  # Only if created from XLSX import
    externalUid: str  # Only if external UID configured
    segments: list[Segment]


class CompanyCreate(TypedDict, total=False):
    """Payload for creating a company."""

    name: str
    externalUid: str
    segmentIds: list[str]


class CompanyUpdate(TypedDict, total=False):
    """Payload for updating a company."""

    name: str
    externalUid: str
    segmentIds: list[str]


class Component(TypedDict, total=False):
    """A Harvestr component."""

    id: str
    clientId: str
    createdAt: str
    updatedAt: str
    title: str
    description: str
    parentId: str


class DiscoveryField(TypedDict):
    """A discovery field definition."""

    id: str
    clientId: str
    name: str


class DiscoveryFieldValue(TypedDict):
    """A discovery field value."""

    field: DiscoveryField
    value: str


class Discovery(TypedDict, total=False):
    """A Harvestr discovery."""

    id: str
    clientId: str
    createdAt: str
    updatedAt: str
    title: str
    description: str
    discoveryStateId: str
    parentId: str
    parentType: Literal["COMPONENT", "DISCOVERY", "NONE"]
    assigneeId: str
    tags: list[str]
    lastDiscoverystateUpdatedAt: str
    lastFeedback: str
    fieldsValues: list[DiscoveryFieldValue]


class DiscoveryState(TypedDict):
    """A discovery state."""

    id: str
    clientId: str
    name: str
    createdAt: str
    updatedAt: str


class Selection(TypedDict):
    """A feedback selection."""

    id: str
    clientId: str
    createdAt: str
    updatedAt: str
    content: str
    fullSelection: bool


class Feedback(TypedDict, total=False):
    """A Harvestr feedback item."""

    id: str
    clientId: str
    createdAt: str
    updatedAt: str
    starred: bool
    score: int
    messageId: str
    discoveryId: str
    selections: list[Selection]


class Message(TypedDict, total=False):
    """A Harvestr message."""

    id: str
    clientId: str
    createdAt: str
    updatedAt: str
    content: str
    authorId: str


class User(TypedDict, total=False):
    """A Harvestr user."""

    id: str
    clientId: str
    email: str
    name: str
    createdAt: str
    updatedAt: str


class Attribute(TypedDict):
    """An attribute definition."""

    id: str
    clientId: str
    name: str
    type: str
    createdAt: str
    updatedAt: str


class AttributeValue(TypedDict):
    """An attribute value."""

    attributeId: str
    value: str
