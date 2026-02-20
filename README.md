# ti-docs-mcp

TI Documentation MCP Server — Search Texas Instruments documentation with semantic queries

## Overview

ti-docs-mcp is an MCP (Model Context Protocol) server that provides intelligent search across Texas Instruments documentation. It uses semantic search and RAG (Retrieval-Augmented Generation) to answer technical questions about TI components, products, and SDKs.

## Features

- **🔍 Semantic Search** — Natural language queries across TI documentation with local embeddings
- **📦 Component Lookup** — Quick access to datasheets by part number
- **🏭 Product Information** — TDA4 (Jacinto) processor family details
- **📚 SDK Documentation** — Search SDK APIs with function signatures
- **🤖 Technical Q&A** — RAG-powered answers with GLM 4.7 integration

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

### Prerequisites

Set the GLM 4.7 API key environment variable:

```bash
export GLM_API_KEY="your-glm-api-key"
```

### Step 1: Index TI Documentation

Before using the MCP server, download and index TI documentation:

```bash
# Download and index TDA4 documents (default: 100 docs)
ti-docs-mcp index

# Download specific product family
ti-docs-mcp index --family TDA4

# Limit number of documents for faster testing
ti-docs-mcp index --max-docs 50

# Clear and rebuild index
ti-docs-mcp index --clear

# Use GPU for faster embeddings (if available)
ti-docs-mcp index --device cuda
```

**What happens during indexing:**
1. Discovers URLs from TI's sitemap (respects 4-second crawl delay)
2. Downloads HTML documentation from e2e.ti.com
3. Parses HTML and extracts metadata (title, type, family, URLs)
4. Generates local embeddings using `all-MiniLM-L6-v2` (384 dimensions)
5. Stores embeddings in ChromaDB vector database
6. Persists index to `~/.ti-docs-mcp/index`

### Step 2: Start MCP Server

```bash
# Start MCP server (stdio transport)
ti-docs-mcp
```

The server will load the index and expose 5 tools for MCP clients.

## MCP Tools

### Tool 1: `ti_search`

Search TI documentation using semantic queries.

**Inputs:**
- `query` (string, required) — Search query
- `document_types` (array, optional) — Filter by type: `["datasheet", "user_guide", "app_note", "reference_design"]`
- `product_family` (string, optional) — Filter by family (e.g., "TDA4", "MSP430")
- `max_results` (integer, optional, default: 10) — Maximum results

**Returns:**
```json
{
  "results": [
    {
      "title": "MSP430FR2355 Watchdog Timer",
      "url": "https://e2e.ti.com/...",
      "document_type": "user_guide",
      "snippet": "Configure the watchdog timer using WDTCTL register...",
      "relevance_score": 0.92
    }
  ]
}
```

**Example:**
```python
# From Python
import asyncio

async def search_docs():
    from mcp import Client
    
    client = Client(stdio_transport=True)
    result = await client.call_tool(
        "ti-docs-mcp",
        "ti_search",
        arguments={
            "query": "watchdog timer configuration",
            "document_types": ["user_guide", "datasheet"],
            "max_results": 5
        }
    )
    print(result)

asyncio.run(search_docs())
```

---

### Tool 2: `component_lookup`

Lookup a TI component by part number.

**Inputs:**
- `part_number` (string, required) — TI part number (e.g., "TDA4VP8", "MSP430FR2355")

**Returns:**
```json
{
  "part_number": "TDA4VP8",
  "name": "TDA4VP8 Jacinto Processor",
  "family": "TDA4",
  "package": "BGA",
  "description": "Automotive processor with vision acceleration...",
  "datasheet_url": "https://e2e.ti.com/...",
  "user_guide_url": "https://e2e.ti.com/...",
  "key_features": ["VPAC", "HSA", "EVE", "C7x"]
}
```

**Example:**
```python
await client.call_tool(
    "ti-docs-mcp",
    "component_lookup",
    arguments={"part_number": "TDA4VP8"}
)
```

---

### Tool 3: `product_info`

Get TDA4 product family information.

**Inputs:**
- `product_name` (string, required) — Product name (e.g., "TDA4", "Jacinto")

**Returns:**
```json
{
  "product_name": "TDA4",
  "category": "Automotive Processor",
  "description": "TDA4 product family - Jacinto processors for automotive applications",
  "applications": ["Automotive", "Industrial", "Robotics"],
  "variants": ["TDA4VP8", "TDA4VM", "TDA4VMQ", "AM68A", "AM62A"],
  "related_products": ["TDA4VP8", "TDA4VM", "AM68A", "AM62A"]
}
```

**Example:**
```python
await client.call_tool(
    "ti-docs-mcp",
    "product_info",
    arguments={"product_name": "TDA4"}
)
```

---

### Tool 4: `sdk_search`

Search SDK documentation.

**Inputs:**
- `sdk_name` (string, required) — SDK name (e.g., "C2000WARE", "MSPM0", "SYSCONFIG")
- `query` (string, required) — Search query within SDK
- `api_version` (string, optional) — Specific API version

**Returns:**
```json
{
  "sdk_name": "C2000WARE",
  "function_name": "initADC",
  "description": "Initialize ADC module...",
  "parameters": ["adc_base", "clk_div", "adc_num", "adc_sample_time"],
  "example": "ADC_init(ADC_BASE, ADC_SAMPLE_TIME);",
  "documentation_url": "https://docs.ti.com/c2000ware",
  "api_version": "3.1.0"
}
```

**Example:**
```python
await client.call_tool(
    "ti-docs-mcp",
    "sdk_search",
    arguments={
        "sdk_name": "C2000WARE",
        "query": "ADC initialization"
    }
)
```

---

### Tool 5: `ti_question`

Ask technical questions using TI documentation with RAG.

**Inputs:**
- `question` (string, required) — Natural language technical question
- `context_scope` (string, optional) — Limit search to specific context ("component", "sdk", "product")

**Returns:**
```json
{
  "answer": "To configure the watchdog timer on TDA4VP8, use the WDTCTL register...",
  "sources": [
    {
      "title": "TDA4VP8 User Guide",
      "url": "https://e2e.ti.com/...",
      "relevance": 0.95
    }
  ],
  "confidence": 0.85,
  "related_questions": [
    "How do I disable the watchdog timer?",
    "What is the default watchdog interval?"
  ]
}
```

**Example:**
```python
await client.call_tool(
    "ti-docs-mcp",
    "ti_question",
    arguments={"question": "How do I configure the watchdog timer on TDA4VP8?"}
)
```

---

## Integration with AI Agents

### Gemini CLI

**Using with Gemini CLI:**

```bash
# 1. Start ti-docs-mcp MCP server in background
ti-docs-mcp &

# 2. Use Gemini CLI with MCP tools
gemini \
  --tool ti-docs-mcp \
  --prompt "Search TI documentation for watchdog timer configuration" \
  --message "Use ti_search tool to find relevant docs"

# Or use in interactive mode
gemini --tool ti-docs-mcp
# Then in Gemini, use natural language:
# "Search for watchdog timer documentation"
# "Look up TDA4VP8 part number"
# "How do I configure the SPI interface?"
```

**Gemini Configuration:**

Create or edit `~/.gemini/config`:

```toml
[mcp.servers.ti-docs-mcp]
enabled = true
command = ["ti-docs-mcp"]
args = ["stdio"]

[tools.ti-docs-mcp]
ti_search = { enabled = true, auto_approve = false }
component_lookup = { enabled = true, auto_approve = false }
product_info = { enabled = true, auto_approve = false }
sdk_search = { enabled = true, auto_approve = false }
ti_question = { enabled = true, auto_approve = false }
```

**Environment Variables:**

```bash
# For Gemini CLI
export GLM_API_KEY="your-glm-api-key"

# Gemini will auto-connect to ti-docs-mcp when enabled
```

---

### Claude Desktop

**Configuration:**

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ti-docs-mcp": {
      "command": "ti-docs-mcp"
    }
  }
}
```

**Usage:**

Claude will automatically load the MCP server. You can then:

```
Search TI documentation for "watchdog timer configuration"
```

Claude will call `ti_search` automatically.

---

### Cursor IDE

**Configuration:**

Add to `.cursorrules`:

```
Use ti-docs-mcp to search TI documentation.

Examples:
@ti-docs-mcp ti_search "watchdog timer"
@ti-docs-mcp component_lookup "TDA4VP8"
@ti-docs-mcp ti_question "How do I configure the watchdog timer?"

@ti-docs-mcp product_info "TDA4"
@ti-docs-mcp sdk_search "C2000WARE" "ADC initialization"
```

**Usage:**

Cursor will automatically recognize `@ti-docs-mcp` prefix and call the appropriate tool.

---

### Cline (VS Code Extension)

**Configuration:**

Add to `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "ti-docs-mcp": {
      "command": "ti-docs-mcp",
      "disabled": false
    }
  }
}
```

**Usage:**

Cline will automatically connect to the MCP server. Use in chat:

```
Search TI documentation for watchdog timer
```

---

### Continue.dev

**Configuration:**

Add to `config.json` in `.continue` directory:

```json
{
  "mcpServers": {
    "ti-docs-mcp": {
      "command": "ti-docs-mcp"
    }
  }
}
```

---

### Other MCP Clients

Any MCP-compatible client can connect to `ti-docs-mcp` via stdio:

```bash
# Start server
ti-docs-mcp

# Client will connect via stdio and can call any of the 5 tools
```

---

## Configuration

### Environment Variables

```bash
# GLM 4.7 API key (required for ti_question tool)
export GLM_API_KEY="your-glm-api-key"

# Optional: Custom index path
export TI_DOCS_INDEX_PATH="~/.ti-docs-mcp/index"

# Optional: Embedding model
export TI_DOCS_TEXT_MODEL="all-MiniLM-L6-v2"
export TI_DOCS_CODE_MODEL="microsoft/codebert-base"

# Optional: Device (cpu/cuda)
export TI_DOCS_DEVICE="cuda"
```

### Configuration File

Create `~/.ti-docs-mcp/config.yaml`:

```yaml
# MCP Server
mcp:
  name: "ti-docs-mcp"
  version: "1.0.0"

# Vector Store
vector_store:
  type: "chromadb"
  path: "~/.ti-docs-mcp/index"
  hnsw_space: "cosine"

# Embeddings (Local Models)
embeddings:
  text_model: "all-MiniLM-L6-v2"
  code_model: "microsoft/codebert-base"
  device: "cpu"  # or "cuda" for GPU
  batch_size: 100

# GLM 4.7
glm:
  api_key: "${GLM_API_KEY}"
  model: "glm-4.7"
  timeout: 30

# TI Documentation
ti_docs:
  product_family: "TDA4"
  sitemap_url: "https://e2e.ti.com/sitemapindex-standard.xml"
  crawl_delay: 4
  max_results: 50

# Chunking
chunking:
  text:
    chunk_size: 512
    chunk_overlap: 50
  code:
    chunk_size: 512
    chunk_overlap: 50
```

---

## Development

### Project Structure

```
ti-docs-mcp/
├── src/ti_docs_mcp/
│   ├── __init__.py
│   ├── cli.py              # CLI entry point with index command
│   ├── server.py           # MCP server with 5 tools
│   ├── ingest.py           # Document download & parsing
│   ├── embeddings.py        # Local embedding generation
│   ├── index.py            # ChromaDB vector operations
│   └── rag.py              # RAG system with GLM 4.7
├── tests/
│   ├── test_server.py       # MCP server tests
│   └── test_tools.py       # Tool implementation tests
├── .specify/memory/
│   ├── spec.md             # Full specification
│   ├── plan.md             # Implementation plan
│   ├── tasks.md            # Task breakdown
│   └── clarify.md          # Clarification answers
├── config.yaml             # Default configuration
└── pyproject.toml          # Package metadata
```

### Adding a New Tool

1. Define the tool in `server.py`:

```python
@mcp.tool()
async def my_new_tool(param: str) -> dict:
    """
    Tool description here.

    Args:
        param: Parameter description

    Returns:
        Tool response
    """
    # Your implementation
    return {"result": "value"}
```

2. Document in `.specify/memory/spec.md`
3. Update task list in `.specify/memory/tasks.md`
4. Implement with embeddings and vector search
5. Test with MCP client

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_server.py

# Run with coverage
pytest --cov=src/ti_docs_mcp
```

---

## Troubleshooting

### No documents in index

```bash
# Check if index exists
ls ~/.ti-docs-mcp/index

# Clear and rebuild
ti-docs-mcp index --clear
```

### GLM API key error

```bash
# Set API key
export GLM_API_KEY="your-key"

# Verify
echo $GLM_API_KEY
```

### Slow embedding generation

```bash
# Use GPU if available
ti-docs-mcp index --device cuda

# Or reduce batch size
```

### MCP client can't connect

Ensure the MCP server is running:

```bash
# Start server in foreground (for debugging)
ti-docs-mcp
```

---

## Performance

- **Embedding Generation:** ~50ms per document (all-MiniLM-L6-v2, CPU)
- **Vector Search:** <50ms (ChromaDB HNSW index)
- **Component Lookup:** <100ms (exact match search)
- **Semantic Search:** <200ms (includes embedding generation)
- **Technical Q&A:** <2s (depends on GLM 4.7 response time)

---

## Requirements

- Python 3.8+
- 4GB RAM minimum (for embeddings and vector DB)
- Disk space: ~100MB for 1000 documents (ChromaDB + embeddings)

---

## Project Status

**Current Version:** 1.0.0 (Alpha - MVP)

**Implemented:**
- ✅ MCP server with stdio transport
- ✅ 5 tools with real implementations
- ✅ Local embeddings (all-MiniLM-L6-v2)
- ✅ ChromaDB vector database
- ✅ RAG system with GLM 4.7 integration
- ✅ Document download and parsing (HTML)
- ✅ CLI index command

**In Development:**
- ⏳ PDF parsing (pymupdf4llm)
- ⏳ Incremental index updates
- ⏳ Input validation
- ⏳ Unit tests
- ⏳ Performance optimization

---

## License

MIT License — see LICENSE file for details.

## Contributing

This project uses Spec-Driven Development. See [Spec Kit documentation](https://speckit.org) for workflows.

## Acknowledgments

- [MCP Protocol](https://modelcontextprotocol.io)
- [sentence-transformers](https://www.sbert.net/) for local embeddings
- [ChromaDB](https://www.trychroma.com/) for vector database
- [GLM 4.7](https://zai.io/) for RAG question answering

## Support

For issues, questions, or contributions, please visit:
- GitHub Issues: https://github.com/openclaw/ti-docs-mcp/issues
- Discord: https://discord.com/clawd
- Documentation: https://docs.openclaw.ai
