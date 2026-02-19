# Tests for ti-docs-mcp

This directory contains tests for the TI Documentation MCP server.

## Test Structure

- `test_tools.py` - Tests for tool functions and their execution
- `test_server.py` - Tests for MCP server lifecycle and connection handling
- `conftest.py` - Shared pytest fixtures

## Running Tests

### Run all tests:
```bash
pytest
```

### Run with coverage:
```bash
pytest --cov=ti_docs_mcp --cov-report=html
```

### Run specific test file:
```bash
pytest tests/test_tools.py
```

### Run specific test:
```bash
pytest tests/test_tools.py::TestToolDiscovery::test_list_tools_returns_tools
```

### Run with verbose output:
```bash
pytest -v
```

### Run async tests only:
```bash
pytest -m asyncio
```

## Test Configuration

Tests are configured in `pyproject.toml`:

- Test discovery: `tests/` directory
- Async mode: `auto` (pytest-asyncio)
- Coverage: Enabled with HTML and terminal reports

## Writing Tests

### Async Tests:

```python
import pytest

@pytest.mark.asyncio
async def test_something_async():
    result = await some_async_function()
    assert result is not None
```

### Using Fixtures:

```python
def test_with_fixture(mock_client):
    assert mock_client is not None
```

### Creating New Tests:

1. Add a test class with descriptive name
2. Write individual test methods starting with `test_`
3. Mark async tests with `@pytest.mark.asyncio`
4. Use descriptive test names that explain what is being tested
5. Keep tests focused and independent

## Dependencies

Test dependencies are in `pyproject.toml` under `[project.optional-dependencies]`:

- `pytest>=8.0.0` - Test framework
- `pytest-asyncio>=0.23.0` - Async test support
- `pytest-cov>=4.1.0` - Coverage reporting
- `pyright>=1.1.0` - Type checking
- `ruff>=0.1.0` - Linting

Install dev dependencies:
```bash
pip install -e ".[dev]"
```
