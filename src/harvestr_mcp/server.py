"""Harvestr.io MCP Server - FastMCP implementation."""

import json
from typing import Annotated

from fastmcp import FastMCP

from harvestr_mcp.client import HarvestrClientError, get_client

# Create the FastMCP server
mcp = FastMCP(
    "Harvestr MCP Server",
    instructions="""
    This MCP server provides access to the Harvestr.io API - a product management platform
    for managing customer feedback, discoveries, and components.

    Available capabilities:
    - List and manage companies
    - Browse components and discoveries
    - Access feedback and messages
    - Manage users and attributes

    All tools require a valid HARVESTR_API_TOKEN environment variable.
    """,
)


def format_response(data: any) -> str:
    """Format API response data as JSON string."""
    return json.dumps(data, indent=2, default=str)


# =============================================================================
# User Tools
# =============================================================================


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_list_users() -> str:
    """List all users in Harvestr.

    Returns a list of user objects with their details including id, email, name,
    and timestamps.
    """
    try:
        client = get_client()
        result = await client.get("/user")
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_get_user(
    user_id: Annotated[str, "The unique identifier of the user to retrieve"],
) -> str:
    """Retrieve a specific user by ID.

    Returns the user object with details including id, email, name, and timestamps.
    """
    try:
        client = get_client()
        result = await client.get(f"/user/{user_id}")
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_list_user_attribute_values(
    user_id: Annotated[str, "The unique identifier of the user"],
) -> str:
    """List attribute values for a specific user.

    Returns a list of attribute values associated with the user.
    """
    try:
        client = get_client()
        result = await client.get(f"/user/{user_id}/attribute-values")
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_update_user_attribute_values(
    user_id: Annotated[str, "The unique identifier of the user"],
    attribute_values: Annotated[
        list[dict],
        "List of attribute value objects with 'attributeId' and 'value' keys",
    ],
) -> str:
    """Update attribute values for a specific user.

    Args:
        user_id: The unique identifier of the user
        attribute_values: List of objects like [{"attributeId": "...", "value": "..."}]

    Returns the updated attribute values.
    """
    try:
        client = get_client()
        result = await client.patch(
            f"/user/{user_id}/attribute-values",
            data=attribute_values,
        )
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


# =============================================================================
# Company Tools
# =============================================================================


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_list_companies(
    external_uid: Annotated[
        str | None,
        "Optional filter by external unique identifier",
    ] = None,
) -> str:
    """List all companies in Harvestr with optional filtering.

    Returns a list of company objects with id, name, segments, and timestamps.
    """
    try:
        client = get_client()
        params = {}
        if external_uid:
            params["externalUid"] = external_uid
        result = await client.get("/company", params=params if params else None)
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    }
)
async def harvestr_create_company(
    name: Annotated[str, "The name of the company"],
    external_uid: Annotated[
        str | None,
        "Optional external unique identifier for the company",
    ] = None,
    segment_ids: Annotated[
        list[str] | None,
        "Optional list of segment IDs to associate with the company",
    ] = None,
) -> str:
    """Create a new company in Harvestr.

    Returns the created company object with id, name, segments, and timestamps.
    """
    try:
        client = get_client()
        data = {"name": name}
        if external_uid:
            data["externalUid"] = external_uid
        if segment_ids:
            data["segmentIds"] = segment_ids
        result = await client.post("/company", data=data)
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_get_company(
    company_id: Annotated[str, "The unique identifier of the company to retrieve"],
) -> str:
    """Retrieve a specific company by ID.

    Returns the company object with details including id, name, segments, and timestamps.
    """
    try:
        client = get_client()
        result = await client.get(f"/company/{company_id}")
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_update_company(
    company_id: Annotated[str, "The unique identifier of the company to update"],
    name: Annotated[str | None, "New name for the company"] = None,
    external_uid: Annotated[
        str | None,
        "New external unique identifier for the company",
    ] = None,
    segment_ids: Annotated[
        list[str] | None,
        "New list of segment IDs to associate with the company",
    ] = None,
) -> str:
    """Update an existing company in Harvestr.

    Returns the updated company object.
    """
    try:
        client = get_client()
        data = {}
        if name is not None:
            data["name"] = name
        if external_uid is not None:
            data["externalUid"] = external_uid
        if segment_ids is not None:
            data["segmentIds"] = segment_ids
        result = await client.patch(f"/company/{company_id}", data=data)
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_list_company_attribute_values(
    company_id: Annotated[str, "The unique identifier of the company"],
) -> str:
    """List attribute values for a specific company.

    Returns a list of attribute values associated with the company.
    """
    try:
        client = get_client()
        result = await client.get(f"/company/{company_id}/attribute-values")
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_update_company_attribute_values(
    company_id: Annotated[str, "The unique identifier of the company"],
    attribute_values: Annotated[
        list[dict],
        "List of attribute value objects with 'attributeId' and 'value' keys",
    ],
) -> str:
    """Update attribute values for a specific company.

    Args:
        company_id: The unique identifier of the company
        attribute_values: List of objects like [{"attributeId": "...", "value": "..."}]

    Returns the updated attribute values.
    """
    try:
        client = get_client()
        result = await client.patch(
            f"/company/{company_id}/attribute-values",
            data=attribute_values,
        )
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


# =============================================================================
# Component Tools
# =============================================================================


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_list_components(
    parent_id: Annotated[
        str | None,
        "Optional filter by parent component ID for hierarchy navigation",
    ] = None,
) -> str:
    """List all components in Harvestr with optional parent filtering.

    Components represent product areas or features in Harvestr.
    Returns a list of component objects with id, title, description, and timestamps.
    """
    try:
        client = get_client()
        params = {}
        if parent_id:
            params["parentId"] = parent_id
        result = await client.get("/component", params=params if params else None)
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_get_component(
    component_id: Annotated[str, "The unique identifier of the component to retrieve"],
) -> str:
    """Retrieve a specific component by ID.

    Returns the component object with details including id, title, description,
    parentId, and timestamps.
    """
    try:
        client = get_client()
        result = await client.get(f"/component/{component_id}")
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


# =============================================================================
# Discovery Tools
# =============================================================================


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_list_discoveries(
    parent_id: Annotated[
        str | None,
        "Optional filter by parent ID (component or discovery)",
    ] = None,
    include_fields: Annotated[
        bool,
        "Whether to include discovery field values in the response",
    ] = False,
) -> str:
    """List all discoveries in Harvestr with optional filtering.

    Discoveries represent feature requests, bugs, or insights gathered from feedback.
    Returns a list of discovery objects with id, title, description, state, and more.
    """
    try:
        client = get_client()
        params = {}
        if parent_id:
            params["parentId"] = parent_id
        if include_fields:
            params["select"] = "discoveryfields"
        result = await client.get("/discovery", params=params if params else None)
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_get_discovery(
    discovery_id: Annotated[str, "The unique identifier of the discovery to retrieve"],
    include_fields: Annotated[
        bool,
        "Whether to include discovery field values in the response",
    ] = False,
) -> str:
    """Retrieve a specific discovery by ID.

    Returns the discovery object with details including id, title, description,
    discoveryStateId, parentId, parentType, assigneeId, tags, and timestamps.
    """
    try:
        client = get_client()
        params = {}
        if include_fields:
            params["select"] = "discoveryfields"
        result = await client.get(
            f"/discovery/{discovery_id}",
            params=params if params else None,
        )
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_get_discovery_state(
    discovery_id: Annotated[str, "The unique identifier of the discovery"],
) -> str:
    """Get the current state of a specific discovery.

    Returns the discovery state object with id, name, and timestamps.
    """
    try:
        client = get_client()
        result = await client.get(f"/discovery/{discovery_id}/discovery-state")
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_list_discovery_feedback(
    discovery_id: Annotated[str, "The unique identifier of the discovery"],
) -> str:
    """List all feedback associated with a specific discovery.

    Returns a list of feedback objects linked to this discovery.
    """
    try:
        client = get_client()
        result = await client.get(f"/discovery/{discovery_id}/feedback")
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


# =============================================================================
# Discovery State Tools
# =============================================================================


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_list_discovery_states() -> str:
    """List all discovery states in Harvestr.

    Discovery states represent the workflow stages for discoveries (e.g., New,
    In Progress, Done). Returns a list of state objects with id, name, and timestamps.
    """
    try:
        client = get_client()
        result = await client.get("/discovery-state")
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_get_discovery_state_by_id(
    state_id: Annotated[str, "The unique identifier of the discovery state"],
) -> str:
    """Retrieve a specific discovery state by ID.

    Returns the discovery state object with id, name, and timestamps.
    """
    try:
        client = get_client()
        result = await client.get(f"/discovery-state/{state_id}")
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


# =============================================================================
# Message Tools
# =============================================================================


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_list_messages() -> str:
    """List all messages in Harvestr.

    Messages represent customer communications or feedback entries.
    Returns a list of message objects with id, content, authorId, and timestamps.
    """
    try:
        client = get_client()
        result = await client.get("/message")
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_get_message(
    message_id: Annotated[str, "The unique identifier of the message to retrieve"],
) -> str:
    """Retrieve a specific message by ID.

    Returns the message object with details including id, content, authorId,
    and timestamps.
    """
    try:
        client = get_client()
        result = await client.get(f"/message/{message_id}")
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_list_message_feedback(
    message_id: Annotated[str, "The unique identifier of the message"],
) -> str:
    """List all feedback associated with a specific message.

    Returns a list of feedback objects linked to this message.
    """
    try:
        client = get_client()
        result = await client.get(f"/message/{message_id}/feedback")
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


# =============================================================================
# Feedback Tools
# =============================================================================


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_list_feedback(
    message_id: Annotated[
        str | None,
        "Optional filter by message ID",
    ] = None,
    discovery_id: Annotated[
        str | None,
        "Optional filter by discovery ID",
    ] = None,
) -> str:
    """List all feedback in Harvestr with optional filtering.

    Feedback represents the link between messages and discoveries, containing
    selections (highlighted text) and scores.
    Returns a list of feedback objects with id, starred, score, selections, and timestamps.
    """
    try:
        client = get_client()
        params = {}
        if message_id:
            params["messageId"] = message_id
        if discovery_id:
            params["discoveryId"] = discovery_id
        result = await client.get("/feedback", params=params if params else None)
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_get_feedback(
    feedback_id: Annotated[str, "The unique identifier of the feedback to retrieve"],
) -> str:
    """Retrieve a specific feedback by ID.

    Returns the feedback object with details including id, starred, score,
    messageId, discoveryId, selections, and timestamps.
    """
    try:
        client = get_client()
        result = await client.get(f"/feedback/{feedback_id}")
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


# =============================================================================
# Attribute Tools
# =============================================================================


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_list_user_attributes() -> str:
    """List all user attributes defined in Harvestr.

    User attributes are custom fields that can be set on users.
    Returns a list of attribute definitions with id, name, type, and timestamps.
    """
    try:
        client = get_client()
        result = await client.get("/attribute/user")
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
async def harvestr_list_company_attributes() -> str:
    """List all company attributes defined in Harvestr.

    Company attributes are custom fields that can be set on companies.
    Returns a list of attribute definitions with id, name, type, and timestamps.
    """
    try:
        client = get_client()
        result = await client.get("/attribute/company")
        return format_response(result)
    except HarvestrClientError as e:
        return f"Error: {e.message}"


# =============================================================================
# Server Entry Point
# =============================================================================


if __name__ == "__main__":
    mcp.run()
