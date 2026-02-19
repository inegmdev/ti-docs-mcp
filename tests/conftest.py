"""
Shared pytest fixtures for ti-docs-mcp tests.
"""

import pytest
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def event_loop_policy():
    """
    Fixture to set up the event loop policy for async tests.
    This is needed for pytest-asyncio to work correctly.
    """
    import asyncio
    policy = asyncio.DefaultEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)
    return policy


@pytest.fixture
async def async_client():
    """
    Fixture that provides an async client mock with basic connection methods.
    """
    class AsyncClientMock:
        def __init__(self):
            self.connected = False
            self.session = None

        async def connect(self):
            """Mock connection method."""
            self.connected = True

        async def disconnect(self):
            """Mock disconnection method."""
            self.connected = False

        async def send_request(self, method: str, params: dict = None) -> dict:
            """Mock send request method."""
            return {"result": "ok"}

    client = AsyncClientMock()
    yield client
    # Cleanup after test
    if client.connected:
        await client.disconnect()


@pytest.fixture
def mock_tool_registry():
    """
    Fixture that provides a mock tool registry.
    """
    registry = {
        "test_tool": {
            "name": "test_tool",
            "description": "A test tool",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "arg": {"type": "string"}
                },
                "required": ["arg"]
            }
        }
    }
    return registry


@pytest.fixture
def sample_request():
    """
    Fixture that provides a sample MCP request.
    """
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }


@pytest.fixture
def sample_response():
    """
    Fixture that provides a sample MCP response.
    """
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "tools": []
        }
    }


@pytest.fixture
def error_response():
    """
    Fixture that provides a sample MCP error response.
    """
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": -32601,
            "message": "Method not found"
        }
    }
