# Harvestr MCP Server - Development Guide

## Project Overview

This is an MCP (Model Context Protocol) server for [Harvestr.io](https://harvestr.io/), built with [FastMCP](https://gofastmcp.com/). It exposes Harvestr's product management API as MCP tools that can be used by AI assistants like Claude.

## Architecture

```
src/harvestr_mcp/
├── __init__.py      # Package exports
├── server.py        # MCP server and tool definitions (FastMCP)
├── client.py        # Async HTTP client for Harvestr API
└── types.py         # Pydantic models for API entities
```

### Key Components

- **FastMCP**: The MCP framework used to define tools. Tools are decorated with `@mcp.tool()` which wraps functions as `FunctionTool` objects.
- **HarvestrClient**: Async HTTP client using `httpx` with automatic auth header injection.
- **Pydantic Models**: Type-safe data models with camelCase/snake_case field aliasing.

## FastMCP Specifics

FastMCP wraps tool functions in `FunctionTool` objects. When testing:
- Access the underlying function via `tool.fn` attribute
- Tools use annotations for hints: `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`

```python
@mcp.tool(annotations={"readOnlyHint": True, ...})
async def harvestr_list_users() -> str:
    ...
```

## Running Locally

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Set API token
export HARVESTR_API_TOKEN="your-token"

# Run server (stdio)
fastmcp run src/harvestr_mcp/server.py:mcp

# Run server (HTTP)
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
```

### Test Guidelines

1. **No classes** - Use flat test functions, classes add unnecessary indentation
2. **No redundant docstrings** - Function names should be descriptive enough
3. **Use parametrize** - Reduce repetition for similar test cases
4. **Mock at the right level** - Patch `server_module.get_client` not `client_module.get_client` since server.py imports `get_client` directly

Example:
```python
@pytest.mark.asyncio
@pytest.mark.parametrize("tool,endpoint", [
    (harvestr_list_users, "/user"),
    (harvestr_list_companies, "/company"),
])
async def test_list_endpoints(tool, endpoint, mock_client):
    mock_client.get.return_value = [{"id": "123"}]
    with patch.object(server_module, "get_client", return_value=mock_client):
        result = await get_fn(tool)()
    assert mock_client.get.called
```

## Code Style

- Use `ruff` for linting and formatting
- Line length: 100 characters
- Python 3.10+ type hints

```bash
ruff check --fix .
ruff format .
```

## API Reference

The server exposes tools for:
- **Users**: List, get, update attributes
- **Companies**: CRUD operations, segments, attributes
- **Components**: Browse product hierarchy
- **Discoveries**: Feature requests, bugs, states, feedback
- **Messages**: Customer communications
- **Feedback**: Links between messages and discoveries
- **Attributes**: Custom field definitions

All tools return JSON strings via `format_response()` and handle errors by returning `"Error: {message}"`.
