# ti-docs-mcp

TI Documentation MCP Server — Search Texas Instruments documentation with semantic queries

## Overview

ti-docs-mcp is an MCP (Model Context Protocol) server that provides intelligent search across Texas Instruments documentation. It uses semantic search and RAG (Retrieval-Augmented Generation) to answer technical questions about TI components, products, and SDKs.

## Features

- **🔍 Semantic Search** — Natural language queries across TI documentation
- **📦 Component Lookup** — Quick access to datasheets by part number
- **🏭 Product Information** — TDA4 (Jacinto) processor family details
- **📚 SDK Documentation** — Search SDK APIs with function signatures
- **🤖 Technical Q&A** — RAG-powered answers with source citations

## Installation

### From PyPI (Recommended)

```bash
pip install ti-docs-mcp
```

### From Source

```bash
git clone https://github.com/openclaw/ti-docs-mcp.git
cd ti-docs-mcp
pip install -e .
```

## Usage

### As MCP Server

Start the server via stdio transport:

```bash
ti-docs-mcp
```

The server will connect to your MCP client (e.g., Claude Desktop, Cursor, etc.) and expose 5 tools:

1. **ti_search** — Semantic search across TI documentation
2. **component_lookup** — Component lookup by part number
3. **product_info** — TDA4 product family information
4. **sdk_search** — SDK documentation search
5. **ti_question** — Technical Q&A with RAG

### Example: Semantic Search

```
Search for MSP430 watchdog timer configuration
```

## Configuration

Set environment variables for API keys:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export GLM_API_KEY="your-glm-api-key"
```

## Requirements

- Python 3.8+
- MCP Client (Claude Desktop, Cursor, etc.)

## Project Status

**Current Version:** 1.0.0 (Alpha)

**Implemented:**
- ✅ MCP server with stdio transport
- ✅ 5 tool stubs with basic implementations
- ✅ Installable package structure

**In Development:**
- ⏳ TI documentation indexing (TDA4 family)
- ⏳ Vector database with OpenAI embeddings
- ⏳ RAG layer with GLM 4.7 integration
- ⏳ CLI commands for index management

## Development Roadmap

See [specification](.specify/memory/spec.md) for full details on planned features.

## License

MIT License — see LICENSE file for details.

## Contributing

This project uses Spec-Driven Development. See the [Spec Kit documentation](https://speckit.org) for workflows.

## Support

For issues and questions, please open an issue on GitHub.
