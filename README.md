# Harvestr MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for [Harvestr.io](https://harvestr.io/) - a product management platform for managing customer feedback, discoveries, and components.

Built with [FastMCP](https://gofastmcp.com/) for clean, Pythonic MCP development.

## Features

- **Companies**: List, create, update, and manage companies and their attributes
- **Components**: Browse product components and their hierarchy
- **Discoveries**: Access feature requests, bugs, and insights with state tracking
- **Feedback**: Manage customer feedback linked to messages and discoveries
- **Messages**: Access customer communications
- **Users**: List users and manage their attributes
- **Attributes**: Access custom field definitions for users and companies

## Installation

### Using uv (recommended)

```bash
uv pip install -e .
```

### Using pip

```bash
pip install -e .
```

## Configuration

### API Token

Create a Harvestr API token:

1. Go to Harvestr Settings > Integrations > API Access Token
2. Create a new token
3. Set the `HARVESTR_API_TOKEN` environment variable:

```bash
export HARVESTR_API_TOKEN="your-api-token-here"
```

> **Security Note**: Treat your API token like a password. Never commit it to version control or share it publicly.

## Usage

### Running the Server

#### Stdio Transport (for local use with MCP clients)

```bash
# Using the FastMCP CLI
fastmcp run src/harvestr_mcp/server.py:mcp

# Or directly with Python
python -m harvestr_mcp.server
```

#### HTTP Transport (for remote access)

```bash
fastmcp run src/harvestr_mcp/server.py:mcp --transport http --port 8000
```

### Using with Claude Desktop

Add to your Claude Desktop configuration (`~/.config/claude/claude_desktop_config.json` on Linux/Mac or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

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

### Using with FastMCP Client

```python
import asyncio
from fastmcp import Client

async def main():
    async with Client("http://localhost:8000/mcp") as client:
        # List all companies
        companies = await client.call_tool("harvestr_list_companies")
        print(companies)

        # Get a specific discovery
        discovery = await client.call_tool(
            "harvestr_get_discovery",
            {"discovery_id": "abc123", "include_fields": True}
        )
        print(discovery)

asyncio.run(main())
```

## Available Tools

### Users

| Tool | Description |
|------|-------------|
| `harvestr_list_users` | List all users |
| `harvestr_get_user` | Retrieve a specific user by ID |
| `harvestr_list_user_attribute_values` | List attribute values for a user |
| `harvestr_update_user_attribute_values` | Update attribute values for a user |

### Companies

| Tool | Description |
|------|-------------|
| `harvestr_list_companies` | List all companies (optional: filter by externalUid) |
| `harvestr_create_company` | Create a new company |
| `harvestr_get_company` | Retrieve a specific company by ID |
| `harvestr_update_company` | Update a company |
| `harvestr_list_company_attribute_values` | List attribute values for a company |
| `harvestr_update_company_attribute_values` | Update attribute values for a company |

### Components

| Tool | Description |
|------|-------------|
| `harvestr_list_components` | List all components (optional: filter by parentId) |
| `harvestr_get_component` | Retrieve a specific component by ID |

### Discoveries

| Tool | Description |
|------|-------------|
| `harvestr_list_discoveries` | List all discoveries (optional: filter by parentId, include fields) |
| `harvestr_get_discovery` | Retrieve a specific discovery by ID |
| `harvestr_get_discovery_state` | Get the current state of a discovery |
| `harvestr_list_discovery_feedback` | List all feedback for a discovery |

### Discovery States

| Tool | Description |
|------|-------------|
| `harvestr_list_discovery_states` | List all discovery states |
| `harvestr_get_discovery_state_by_id` | Retrieve a specific discovery state by ID |

### Messages

| Tool | Description |
|------|-------------|
| `harvestr_list_messages` | List all messages |
| `harvestr_get_message` | Retrieve a specific message by ID |
| `harvestr_list_message_feedback` | List all feedback for a message |

### Feedback

| Tool | Description |
|------|-------------|
| `harvestr_list_feedback` | List all feedback (optional: filter by messageId, discoveryId) |
| `harvestr_get_feedback` | Retrieve a specific feedback by ID |

### Attributes

| Tool | Description |
|------|-------------|
| `harvestr_list_user_attributes` | List all user attribute definitions |
| `harvestr_list_company_attributes` | List all company attribute definitions |

## Development

### Running Tests

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest
```

### Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector fastmcp run src/harvestr_mcp/server.py:mcp
```

### Code Formatting

```bash
ruff check --fix .
ruff format .
```

## API Documentation

For detailed API documentation, see the [Harvestr API Docs](https://developers.harvestr.io/api/).

## License

MIT License - see [LICENSE](LICENSE) for details.
