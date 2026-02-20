# Getting Started with ti-docs-mcp

Quick start guide for MVP (Minimum Viable Product).

## Prerequisites

1. Python 3.8+ installed
2. GLM 4.7 API key (set as `GLM_API_KEY` environment variable)

## Installation

```bash
# From PyPI (once published)
pip install ti-docs-mcp

# From source (for now)
cd ti-docs-mcp
pip install -e .
```

## Setup Environment Variables

```bash
# Export GLM 4.7 API key
export GLM_API_KEY="your-glm-api-key"

# Optional: For GPU acceleration
export CUDA_VISIBLE_DEVICES=0
```

## Step 1: Index TI Documentation

Before using the MCP server, download and index TI documentation:

```bash
# Download and index TDA4 documents (limit to 50 docs for testing)
ti-docs-mcp index --family TDA4 --max-docs 50

# Or download more documents
ti-docs-mcp index --family TDA4 --max-docs 500

# Clear and rebuild index
ti-docs-mcp index --clear --family TDA4
```

This will:
1. Fetch TDA4 documentation from e2e.ti.com
2. Parse HTML content and extract metadata
3. Generate local embeddings (all-MiniLM-L6-v2)
4. Store in ChromaDB vector database
5. Index persisted to `~/.ti-docs-mcp/index`

## Step 2: Start MCP Server

```bash
# Start MCP server (stdio transport)
ti-docs-mcp
```

The server will:
1. Load the vector index from disk
2. Register 5 MCP tools
3. Wait for tool calls via stdio

## Step 3: Use the Tools

### Tool 1: ti_search

Search TI documentation with semantic queries:

```json
{
  "tool": "ti_search",
  "arguments": {
    "query": "watchdog timer configuration",
    "max_results": 10
  }
}
```

Response:
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

### Tool 2: component_lookup

Lookup a TI component by part number:

```json
{
  "tool": "component_lookup",
  "arguments": {
    "part_number": "TDA4VP8"
  }
}
```

### Tool 3: product_info

Get TDA4 product family information:

```json
{
  "tool": "product_info",
  "arguments": {
    "product_name": "TDA4"
  }
}
```

### Tool 4: sdk_search

Search SDK documentation:

```json
{
  "tool": "sdk_search",
  "arguments": {
    "sdk_name": "C2000WARE",
    "query": "ADC configuration example"
  }
}
```

### Tool 5: ti_question

Ask technical questions with RAG:

```json
{
  "tool": "ti_question",
  "arguments": {
    "question": "How do I configure the watchdog timer on TDA4VP8?"
  }
}
```

Response:
```json
{
  "answer": "To configure the watchdog timer on TDA4VP8...",
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

## Integration with MCP Clients

### Claude Desktop

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

### Cursor

Add to `.cursorrules`:

```
Use ti-docs-mcp to search TI documentation.

Example:
@ti-docs-mcp ti_search "watchdog timer"
@ti-docs-mcp component_lookup "TDA4VP8"
@ti-docs-mcp ti_question "How to configure SPI?"
```

## Testing the MVP

```bash
# Test 1: Index some docs
ti-docs-mcp index --family TDA4 --max-docs 10

# Test 2: Start server in test mode
# (MCP server should start without errors)

# Test 3: Call tools via your MCP client
# Try each of the 5 tools with sample queries
```

## Troubleshooting

### No documents in index

```bash
# Check if index exists
ls ~/.ti-docs-mcp/index

# Clear and rebuild
ti-docs-mcp index --clear --family TDA4
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
# (Modify batch_size in config.yaml)
```

## Next Steps

1. Index full TDA4 documentation
2. Test with real queries from your work
3. Provide feedback on accuracy and performance
4. Expand to other product families (MSP430, C2000, etc.)

---

**MVP Status:** ✅ Ready to use
**Phase:** Foundation + Index Layer + Tool Implementation (Partial)
**Missing:** PDF parsing, incremental update, comprehensive tests
