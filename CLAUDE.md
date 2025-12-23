# Harvestr MCP Server - Development Guide

## Project Overview

This is an MCP (Model Context Protocol) server for [Harvestr.io](https://harvestr.io/), a product management platform for managing customer feedback, discoveries, and components. Built with [FastMCP](https://gofastmcp.com/), it exposes Harvestr's REST API as MCP tools for AI assistants like Claude.

## Architecture

```
src/harvestr_mcp/
├── __init__.py      # Package exports (mcp server instance)
├── server.py        # MCP server with 24 tool definitions (FastMCP)
├── client.py        # Async HTTP client for Harvestr API (httpx)
└── types.py         # Pydantic models with camelCase/snake_case aliasing

tests/
├── __init__.py
├── conftest.py      # Shared fixtures (client singleton reset)
├── test_client.py   # HTTP client tests (96 lines)
├── test_server.py   # MCP tool tests (88 lines)
└── test_types.py    # Pydantic model tests (132 lines)
```

### Key Components

| Component | Description |
|-----------|-------------|
| `FastMCP` | MCP framework - tools decorated with `@mcp.tool()` become `FunctionTool` objects |
| `HarvestrClient` | Async HTTP client using `httpx` with token auth via `X-Harvestr-Private-App-Token` header |
| Pydantic Models | Type-safe models with `Field(alias="camelCase")` and `populate_by_name=True` config |

### FastMCP Tool Pattern

Tools use annotations for MCP hints and return JSON strings:

```python
@mcp.tool(
    annotations={
        "readOnlyHint": True,      # Doesn't modify data
        "destructiveHint": False,   # Safe operation
        "idempotentHint": True,     # Same result on retry
        "openWorldHint": False,     # Closed system
    }
)
async def harvestr_list_users() -> str:
    try:
        client = get_client()
        result = await client.get("/user")
        return format_response(result)  # Returns JSON string
    except HarvestrClientError as e:
        return f"Error: {e.message}"
```

## Available Tools (24 total)

### Users (4 tools)
- `harvestr_list_users` - List all users
- `harvestr_get_user` - Get user by ID
- `harvestr_list_user_attribute_values` - Get user's attribute values
- `harvestr_update_user_attribute_values` - Update user's attribute values

### Companies (6 tools)
- `harvestr_list_companies` - List companies (filter by externalUid)
- `harvestr_create_company` - Create new company
- `harvestr_get_company` - Get company by ID
- `harvestr_update_company` - Update company
- `harvestr_list_company_attribute_values` - Get company's attribute values
- `harvestr_update_company_attribute_values` - Update company's attribute values

### Components (2 tools)
- `harvestr_list_components` - List components (filter by parentId)
- `harvestr_get_component` - Get component by ID

### Discoveries (4 tools)
- `harvestr_list_discoveries` - List discoveries (filter by parentId, include fields)
- `harvestr_get_discovery` - Get discovery by ID
- `harvestr_get_discovery_state` - Get discovery's current state
- `harvestr_list_discovery_feedback` - List feedback for discovery

### Discovery States (2 tools)
- `harvestr_list_discovery_states` - List all discovery states
- `harvestr_get_discovery_state_by_id` - Get state by ID

### Messages (3 tools)
- `harvestr_list_messages` - List all messages
- `harvestr_get_message` - Get message by ID
- `harvestr_list_message_feedback` - List feedback for message

### Feedback (2 tools)
- `harvestr_list_feedback` - List feedback (filter by messageId, discoveryId)
- `harvestr_get_feedback` - Get feedback by ID

### Attributes (2 tools)
- `harvestr_list_user_attributes` - List user attribute definitions
- `harvestr_list_company_attributes` - List company attribute definitions

## Running Locally

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Set API token
export HARVESTR_API_TOKEN="your-token"

# Run server (stdio - for MCP clients)
fastmcp run src/harvestr_mcp/server.py:mcp

# Run server (HTTP - for remote access)
fastmcp run src/harvestr_mcp/server.py:mcp --transport http --port 8000

# Test with MCP Inspector
npx @modelcontextprotocol/inspector fastmcp run src/harvestr_mcp/server.py:mcp
```

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific file
pytest tests/test_server.py

# Run with coverage
pytest --cov=harvestr_mcp
```

### Test Conventions

1. **Flat test functions** - No test classes, avoid unnecessary nesting
2. **Descriptive function names** - No redundant docstrings needed
3. **Use `@pytest.mark.parametrize`** - Reduce repetition for similar cases
4. **Mock at import location** - Patch `server_module.get_client` not `client_module.get_client`
5. **Use `get_fn()` helper** - Extract underlying function from FunctionTool wrapper

### Example Test Pattern

```python
from unittest.mock import AsyncMock, patch
import harvestr_mcp.server as server_module

def get_fn(tool):
    """Get the underlying async function from a FunctionTool."""
    return tool.fn if hasattr(tool, "fn") else tool

@pytest.fixture
def mock_client():
    return AsyncMock(spec=HarvestrClient)

@pytest.mark.asyncio
@pytest.mark.parametrize("tool,endpoint,fixture_name", [
    (harvestr_list_users, "/user", "sample_user"),
    (harvestr_list_companies, "/company", "sample_company"),
])
async def test_list_endpoints(tool, endpoint, fixture_name, mock_client, request):
    sample_data = request.getfixturevalue(fixture_name)
    mock_client.get.return_value = [sample_data]

    with patch.object(server_module, "get_client", return_value=mock_client):
        result = await get_fn(tool)()

    assert mock_client.get.called
```

### Test File Organization

| File | Tests |
|------|-------|
| `test_client.py` | Client init, headers, HTTP methods, response handling, singleton |
| `test_server.py` | Tool execution, parametrized endpoint tests, error handling |
| `test_types.py` | Pydantic model parsing, camelCase aliasing, optional fields |

## Code Style

- **Formatter/Linter**: Ruff
- **Line length**: 100 characters
- **Python version**: 3.10+

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### Style Guidelines

- Use Python 3.10+ type hints (`str | None` not `Optional[str]`)
- Use `Field(alias="camelCase")` with `model_config = {"populate_by_name": True}` for Pydantic models
- All tool functions return `str` (JSON via `format_response()` or `"Error: {message}"`)
- Use `Annotated[type, "description"]` for tool parameter documentation

## API Patterns

### Client Singleton

```python
from harvestr_mcp.client import get_client

client = get_client()  # Returns global HarvestrClient instance
result = await client.get("/endpoint")
result = await client.post("/endpoint", data={"key": "value"})
result = await client.patch("/endpoint", data={"key": "value"})
```

### Error Handling

All tools catch `HarvestrClientError` and return error strings:

```python
try:
    result = await client.get("/endpoint")
    return format_response(result)
except HarvestrClientError as e:
    return f"Error: {e.message}"
```

### Pydantic Models

Models support both camelCase (API) and snake_case (Python):

```python
class Company(BaseModel):
    id: str
    client_id: str = Field(alias="clientId")
    external_uid: str | None = Field(default=None, alias="externalUid")

    model_config = {"populate_by_name": True}

# Both work:
Company(clientId="c-1", ...)  # From API
Company(client_id="c-1", ...)  # In Python
```

## Dependencies

### Core
- `fastmcp>=2.0.0` - MCP framework
- `httpx>=0.27.0` - Async HTTP client
- `pydantic>=2.0.0` - Data validation

### Development
- `pytest>=8.0.0` - Testing framework
- `pytest-asyncio>=0.23.0` - Async test support (mode: auto)
- `ruff>=0.4.0` - Linting and formatting

## Common Pitfalls

1. **Client singleton not reset in tests** - Use `conftest.py` fixture that resets `client_module._client = None`
2. **Mocking wrong import location** - Patch where it's imported (server_module), not where it's defined
3. **FunctionTool wrapper** - Use `tool.fn` to access underlying function for direct testing
4. **API token missing** - Always set `HARVESTR_API_TOKEN` env var before running

## Claude Desktop Configuration

```json
{
  "mcpServers": {
    "harvestr": {
      "command": "uv",
      "args": ["run", "fastmcp", "run", "/path/to/harvestr-mcp/src/harvestr_mcp/server.py:mcp"],
      "env": {
        "HARVESTR_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

## External Resources

- [Harvestr API Docs](https://developers.harvestr.io/api/)
- [FastMCP Documentation](https://gofastmcp.com/)
- [MCP Specification](https://modelcontextprotocol.io/)
