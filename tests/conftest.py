"""Shared pytest configuration."""

import pytest


@pytest.fixture(autouse=True)
def reset_client_singleton():
    """Reset the global client singleton before each test."""
    import harvestr_mcp.client as client_module
    client_module._client = None
    yield
    client_module._client = None
