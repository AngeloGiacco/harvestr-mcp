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

## Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A Harvestr.io account with API access

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/your-org/harvestr-mcp.git
cd harvestr-mcp

# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

### 2. Get Your Harvestr API Token

1. Log in to your [Harvestr.io](https://harvestr.io/) account
2. Navigate to **Settings** > **Integrations** > **API Access Token**
3. Click **Create new token** and copy the generated token

### 3. Configure the API Token

Set your API token as an environment variable:

```bash
# Linux/macOS
export HARVESTR_API_TOKEN="your-api-token-here"

# Windows (PowerShell)
$env:HARVESTR_API_TOKEN="your-api-token-here"

# Windows (CMD)
set HARVESTR_API_TOKEN=your-api-token-here
```

For persistent configuration, add the export to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
echo 'export HARVESTR_API_TOKEN="your-api-token-here"' >> ~/.bashrc
source ~/.bashrc
```

> **Security Note**: Treat your API token like a password. Never commit it to version control or share it publicly.

### 4. Run the Server

```bash
# Using FastMCP CLI (recommended)
fastmcp run src/harvestr_mcp/server.py:mcp

# Or using Python directly
python -m harvestr_mcp.server
```

### 5. Test with MCP Inspector (Optional)

To interactively test the server's tools:

```bash
npx @modelcontextprotocol/inspector fastmcp run src/harvestr_mcp/server.py:mcp
```

This opens a web interface where you can explore and test all available tools.

## Installation

### Using uv (recommended)

```bash
uv pip install -e .
```

### Using pip

```bash
pip install -e .
```

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

### Setting Up for Development

```bash
# Clone and enter the repository
git clone https://github.com/your-org/harvestr-mcp.git
cd harvestr-mcp

# Install with dev dependencies using uv (recommended)
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

### Running Tests

The test suite uses pytest with pytest-asyncio for async test support:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_client.py

# Run specific test class
pytest tests/test_server.py::TestUserTools

# Run with coverage (if installed)
pytest --cov=harvestr_mcp
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py      # Shared fixtures and test configuration
├── test_client.py   # Tests for the Harvestr API client
├── test_types.py    # Tests for Pydantic models
└── test_server.py   # Tests for MCP server tools
```

### Testing with MCP Inspector

For interactive testing of the server:

```bash
npx @modelcontextprotocol/inspector fastmcp run src/harvestr_mcp/server.py:mcp
```

### Code Formatting

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

## API Documentation

For detailed API documentation, see the [Harvestr API Docs](https://developers.harvestr.io/api/).

## License

MIT License - see [LICENSE](LICENSE) for details.
