# Implementation Plan for ti-docs-mcp

**Version:** 1.0.0
**Status:** Draft
**Created:** 2026-02-11

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MCP Client (e.g., GLM 4.7)                │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ stdio
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                    ti-docs-mcp Server                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │ Tool Layer  │  │   RAG Layer  │  │ Index Layer │  │
│  │              │  │              │  │             │  │
│  │ • ti_search │  │ • Retrieval  │  │ • Vector    │  │
│  │ • component │  │ • Context    │  │   Index     │  │
│  │ • product  │  │   Building  │  │             │  │
│  │ • sdk_search│  │              │  │ • Embedding │  │
│  │ • ti_quest  │  │             │  │   Model     │  │
│  └──────────────┘  └──────────────┘  └─────────────┘  │
│                                              │            │
│                                        ┌───────▼────────┐   │
│                                        │  TI Docs      │   │
│                                        │  (Local)      │   │
│                                        │ • Datasheets  │   │
│                                        │ • User Guides  │   │
│                                        │ • App Notes    │   │
│                                        │ • SDK Docs     │   │
│                                        └────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Language** | Python 3.8+ | Rich ecosystem, good for CLI/ML, PyPI deployment |
| **MCP Protocol** | mcp-python SDK | Official Python SDK for MCP servers |
| **Embeddings (Text)** | sentence-transformers (all-MiniLM-L6-v2) | Local, fast, zero API cost, good semantic quality |
| **Embeddings (Code)** | microsoft/codebert-base | Local, code-aware embeddings for SDK search |
| **Vector Store** | ChromaDB | Lightweight, Python-native, persistent, HNSW indexing |
| **Reranker (Optional)** | ms-marco-MiniLM-L-6-v2 | Better relevance for Q&A (cross-encoder) |
| **PDF Parsing** | pymupdf4llm (or pdfplumber) | Fast, handles tables, structure preservation |
| **HTML Parsing** | BeautifulSoup4 | Robust HTML parsing, widely used |
| **CLI Framework** | Click or Typer | Type hints, auto-generated help, rich CLI |
| **Packaging** | setuptools (PyPI) | Standard Python packaging |
| **Testing** | pytest + pytest-asyncio | Async testing for MCP |
| **Type Hints** | mypy | Static type checking |
| **Linting** | ruff | Fast Python linter |

**Key Benefits of Local Embeddings:**
- **Privacy:** No data sent to external APIs
- **Cost:** Zero API costs for embeddings
- **Offline:** Works without internet connection
- **Performance:** Fast inference (~50ms per document)
- **Control:** Full control over model versions

**RAG Strategy by Data Type:**
- **HTML/PDF:** ChromaDB + semantic chunking (512 tokens, 50 overlap)
- **Code:** ChromaDB + function-level chunking (AST-aware)
- **See [RAG_STRATEGY.md](../../RAG_STRATEGY.md)** for detailed implementation

---

## Component Design

### 1. Tool Layer (MCP Tools)

Each tool is an async function decorated with MCP `@tool`.

#### 1.1 ti_search Tool
```python
@mcp.tool()
async def ti_search(
    query: str,
    document_types: Optional[List[str]] = None,
    product_family: Optional[str] = None,
    max_results: int = 10
) -> List[SearchResult]:
    """Search TI documentation using semantic queries."""
    # 1. Generate embedding for query
    # 2. Search vector index with filters
    # 3. Rank and return top results
    pass
```

**Implementation:**
- Generate query embedding using OpenAI embeddings API
- Filter by `document_types` and `product_family` if provided
- Top-k search in vector database
- Return with relevance scores

#### 1.2 component_lookup Tool
```python
@mcp.tool()
async def component_lookup(part_number: str) -> ComponentDetails:
    """Lookup TI component by part number."""
    # 1. Search component database by exact match
    # 2. Return component details with URLs
    pass
```

**Implementation:**
- Exact match search in component index
- Fallback to prefix match if exact not found
- Return metadata from parsed component pages

#### 1.3 product_info Tool
```python
@mcp.tool()
async def product_info(product_name: str) -> ProductDetails:
    """Get TDA4 product information."""
    # 1. Search product database by name
    # 2. Return variants and applications
    pass
```

#### 1.4 sdk_search Tool
```python
@mcp.tool()
async def sdk_search(
    sdk_name: str,
    query: str,
    api_version: Optional[str] = None
) -> List[SDKResult]:
    """Search SDK documentation."""
    # 1. Filter SDK docs by name
    # 2. Semantic search within SDK docs
    # 3. Return function/API results
    pass
```

#### 1.5 ti_question Tool
```python
@mcp.tool()
async def ti_question(
    question: str,
    context_scope: Optional[str] = None
) -> QuestionAnswer:
    """Answer technical questions using TI documentation."""
    # 1. Retrieve relevant docs (RAG)
    # 2. Build prompt with context
    # 3. Call GLM 4.7 to generate answer
    # 4. Return answer with sources
    pass
```

**Implementation:**
- Use query embedding to find relevant docs (top 5-10)
- Build context window with retrieved snippets
- Call GLM 4.7 API with context + question
- Parse response for answer + confidence
- Include source URLs in response

---

### 2. RAG Layer (Retrieval)

#### 2.1 Query Embedding Generation
```python
async def embed_query(text: str) -> List[float]:
    """Generate embedding for query text."""
    response = await openai.Embedding.acreate(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding
```

#### 2.2 Context Building
```python
async def build_context(
    query_embedding: List[float],
    max_tokens: int = 4000
) -> List[DocumentSnippet]:
    """Build context from retrieved documents."""
    # 1. Search vector store for top N results
    # 2. Filter and deduplicate
    # 3. Truncate to max_tokens
    pass
```

#### 2.3 GLM 4.7 Integration
```python
async def ask_glm(
    question: str,
    context: List[DocumentSnippet]
) -> QuestionAnswer:
    """Ask GLM 4.7 with RAG context."""
    # 1. Build prompt with context
    # 2. Call GLM 4.7 API
    # 3. Parse and return structured response
    pass
```

**Prompt Template:**
```
You are a Texas Instruments technical expert. Answer the question using only the provided TI documentation context.

Context:
{context_snippets}

Question: {question}

Provide:
1. Direct answer
2. Confidence score (0.0-1.0)
3. Source document references
4. Related follow-up questions
```

---

### 3. Index Layer (Vector Store + Embeddings)

#### 3.1 Document Ingestion Pipeline
```python
async def ingest_ti_docs(
    source_dir: str,
    batch_size: int = 100
) -> None:
    """Download, parse, and index TI documentation."""
    # 1. Download TI docs (respect robots.txt, 4s delay)
    # 2. Parse HTML/PDF content
    # 3. Extract metadata (title, type, family, URLs)
    # 4. Generate embeddings in batches
    # 5. Store in vector database
    pass
```

#### 3.2 Vector Database Schema
```python
@dataclass
class Document:
    id: str
    title: str
    content: str
    url: str
    document_type: str  # datasheet, user_guide, app_note, reference_design
    product_family: str  # TDA4, etc.
    part_number: Optional[str]
    embedding: List[float]
    created_at: datetime
```

#### 3.3 Indexing Strategy
1. **Download Phase:**
   - Fetch TDA4 family docs from e2e.ti.com
   - Respect 4-second crawl delay
   - Use sitemap for discovery

2. **Parse Phase:**
   - Extract text from HTML (BeautifulSoup)
   - Extract PDF text (pymupdf4llm or pdfplumber)
   - Clean and normalize content
   - Preserve structure (headings, code blocks, tables)

3. **Chunking Phase (Per Data Type):**
   - **HTML/PDF:** Semantic chunking (512 tokens, 50 overlap) using LangChain RecursiveCharacterTextSplitter
   - **Code:** Function-level chunking (AST-aware) for SDK docs
   - Preserve context and document structure

4. **Embed Phase (Local Models):**
   - **Text:** Use sentence-transformers `all-MiniLM-L6-v2` (384 dims, fast)
   - **Code:** Use `microsoft/codebert-base` (768 dims, code-aware)
   - Generate embeddings locally (no API calls)
   - Cache embeddings to disk for fast reload

5. **Index Phase:**
   - Store in ChromaDB with HNSW indexing
   - Create metadata filters (document_type, product_family, language)
   - Persist to disk for fast startup
   - Optional reranking with `ms-marco-MiniLM-L-6-v2` for Q&A

---

### 4. Index Management

#### 4.1 CLI Commands
```bash
# Download and index TI docs
ti-docs-mcp index --family TDA4 --source e2e.ti.com

# Update index (incremental)
ti-docs-mcp index --update

# Search index directly (for testing)
ti-docs-mcp search "watchdog timer"

# Clear index
ti-docs-mcp index --clear
```

#### 4.2 Index Storage
```
~/.ti-docs-mcp/
├── index/                    # ChromaDB/LanceDB storage
│   ├── data.bin
│   └── metadata.json
├── embeddings/              # Cached embeddings
│   └── embeddings.pkl
├── docs/                    # Downloaded TI docs (optional)
│   ├── datasheets/
│   ├── user_guides/
│   └── app_notes/
└── config.yaml               # CLI config
```

---

### 5. MCP Server

#### 5.1 Server Entry Point
```python
async def main():
    """Start MCP server via stdio."""
    # 1. Load index from disk
    # 2. Initialize embedding client
    # 3. Register tools with MCP
    # 4. Start stdio transport
    pass

if __name__ == "__main__":
    mcp.run(main())
```

#### 5.2 MCP Protocol Compliance
- Tool definitions with JSON Schema
- Error responses with proper error codes
- Progress reporting for long operations
- Cancellation support

---

## Project Structure

```
ti-docs-mcp/
├── src/
│   └── ti_docs_mcp/
│       ├── __init__.py
│       ├── cli.py              # CLI commands
│       ├── server.py           # MCP server main
│       ├── tools.py           # MCP tool definitions
│       ├── rag.py             # RAG logic
│       ├── index.py           # Vector store operations
│       ├── ingest.py          # Doc download/parse
│       ├── embeddings.py       # Embedding generation
│       └── glm_client.py      # GLM 4.7 API client
├── tests/
│   ├── test_tools.py
│   ├── test_rag.py
│   ├── test_index.py
│   └── test_cli.py
├── config.yaml               # Default configuration
├── pyproject.toml           # Project metadata
├── setup.py                # PyPI packaging
└── README.md               # User documentation
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
**Goal:** Setup project structure and basic MCP server

**Tasks:**
- [ ] Create project structure (src, tests, config)
- [ ] Setup PyPI packaging (pyproject.toml, setup.py)
- [ ] Initialize MCP server with stdio transport
- [ ] Implement skeleton tool definitions (5 tools)
- [ ] Setup testing framework (pytest)
- [ ] Write unit tests for MCP protocol compliance

**Deliverables:**
- Working MCP server that responds to tool calls (stub responses)
- CLI entry point with help text
- Basic test suite

---

### Phase 2: Index Layer (Week 2-3)
**Goal:** Document ingestion and vector indexing

**Tasks:**
- [ ] Implement TI doc downloader (respect 4s delay)
- [ ] Parse HTML/PDF content
- [ ] Extract metadata (title, type, family, URLs)
- [ ] Integrate OpenAI embeddings API
- [ ] Setup ChromaDB (or LanceDB)
- [ ] Implement batch embedding generation
- [ ] Implement index storage and loading
- [ ] CLI: `ti-docs-mcp index` command

**Deliverables:**
- Working index pipeline
- Indexed TDA4 documentation
- CLI for index management

---

### Phase 3: Tool Implementation (Week 3-4)
**Goal:** Implement all 5 MCP tools

**Tasks:**
- [ ] Implement `ti_search` with vector search
- [ ] Implement `component_lookup` with exact match
- [ ] Implement `product_info` for TDA4 family
- [ ] Implement `sdk_search` with semantic search
- [ ] Implement `ti_question` with RAG
- [ ] Add error handling for all tools
- [ ] Add input validation

**Deliverables:**
- All 5 tools working
- Structured error responses
- Integration tests for each tool

---

### Phase 4: RAG + GLM 4.7 Integration (Week 4-5)
**Goal:** Question answering with GLM 4.7

**Tasks:**
- [ ] Implement query embedding
- [ ] Implement context building from retrieved docs
- [ ] Integrate GLM 4.7 API client
- [ ] Implement prompt template and generation
- [ ] Parse GLM response for structured output
- [ ] Handle GLM API errors and rate limits

**Deliverables:**
- Working `ti_question` tool
- Accurate answers with source citations
- Confidence scoring

---

### Phase 5: Testing & Validation (Week 5-6)
**Goal:** Comprehensive testing and validation

**Tasks:**
- [ ] Unit tests for all components
- [ ] Integration tests with MCP client
- [ ] Benchmark query performance
- [ ] Test with TDA4-specific queries
- [ ] Validate against constitution (protocol compliance, errors)
- [ ] Manual testing with GLM 4.7

**Deliverables:**
- >80% code coverage
- Performance benchmarks (search <500ms, QA <2s)
- Validated against success metrics

---

### Phase 6: Packaging & Documentation (Week 6)
**Goal:** PyPI package and user docs

**Tasks:**
- [ ] Finalize PyPI package metadata
- [ ] Write README with installation/usage examples
- [ ] Write CHANGELOG for v1.0.0
- [ ] Document all tools with examples
- [ ] Create example MCP server config
- [ ] Test PyPI installation locally

**Deliverables:**
- Publishable PyPI package
- Complete documentation
- Example configuration files

---

## Configuration

### config.yaml
```yaml
# MCP Server
mcp:
  name: "ti-docs-mcp"
  version: "1.0.0"

# Vector Store
vector_store:
  type: "chromadb"
  path: "~/.ti-docs-mcp/index"
  hnsw_space: "cosine"  # cosine, l2, ip

# Embeddings (Local Models)
embeddings:
  text_model: "all-MiniLM-L6-v2"  # 384 dims, fast
  # Alternative for better accuracy: "all-mpnet-base-v2" (768 dims)
  code_model: "microsoft/codebert-base"  # 768 dims, code-aware
  device: "cpu"  # or "cuda" for GPU acceleration
  batch_size: 100

# Optional Reranker (Better Relevance for Q&A)
reranker:
  enabled: false  # Set to true for better Q&A accuracy
  model: "ms-marco-MiniLM-L-6-v2"

# GLM 4.7
glm:
  api_key: "${GLM_API_KEY}"
  base_url: "https://api.zai.io"  # actual URL
  model: "glm-4.7"
  timeout: 30  # seconds

# TI Documentation
ti_docs:
  product_family: "TDA4"
  sitemap_url: "https://e2e.ti.com/sitemapindex-standard.xml"
  crawl_delay: 4  # seconds
  max_results: 50

# Chunking
chunking:
  text:
    chunk_size: 512  # tokens
    chunk_overlap: 50
    method: "semantic"  # semantic, fixed, structure
  code:
    chunk_size: 512  # tokens
    chunk_overlap: 50
    method: "ast_aware"  # function-level, preserve code structure

# Indexing
indexing:
  download_dir: "~/.ti-docs-mcp/docs"
  cache_embeddings: true
  incremental: true
```

---

## Dependencies

### Runtime Dependencies
```toml
[tool.poetry.dependencies]
python = "^3.8"
mcp = "^0.1.0"
sentence-transformers = "^2.2.0"  # Local embeddings
chromadb = "^0.4.0"
beautifulsoup4 = "^4.12.0"
pymupdf4llm = "^0.0.5"  # PDF parsing (fast, handles tables)
pdfplumber = "^3.0.0"  # Alternative PDF parser
httpx = "^0.24.0"
pyyaml = "^6.0.0"
click = "^8.1.0"
langchain = "^0.1.0"  # For chunking utilities

# Optional for code parsing
asttokens = "^2.4.0"

# Optional for GPU acceleration
# torch = { version = "^2.0.0", extras = ["cuda"] }  # For CUDA support
```

### Development Dependencies
```toml
[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
mypy = "^1.7.0"
ruff = "^0.1.0"
```

---

## Testing Strategy

### Unit Tests
- Each tool function tested with mock data
- Embedding generation tested with sample queries
- Vector store operations tested
- Error handling tested for all edge cases

### Integration Tests
- Test full MCP message flow (request → response)
- Test with real MCP client (e.g., Claude Desktop)
- Test all 5 tools with real data

### Benchmark Tests
- Measure query latency (target: <500ms P95)
- Measure QA latency (target: <2s P95)
- Measure embedding generation time

---

## Known Risks & Mitigations

| Risk | Impact | Mitigation |
|-------|---------|------------|
| **TI robots.txt changes** | Indexing blocked | Monitor, respect crawl delay, use sitemap |
| **Index size** | Slow startup, high memory | Implement lazy loading, limit initial index |
| **TDA4 documentation missing** | Poor search results | Validate TI has TDA4 docs, handle gracefully |
| **GLM 4.7 API changes** | QA failures | Document API version, test regularly |
| **Local model performance** | Slow embedding on CPU | Support GPU acceleration with CUDA, use smaller models |
| **Code parsing failures** | Missing code chunks | Fallback to fixed-size chunking, log errors |

---

## Success Criteria

- [ ] All 5 MCP tools implemented and working
- [ ] Index contains TDA4 documentation (datasheets, user guides, app notes)
- [ ] Semantic search returns relevant results (>80% top-3 accuracy)
- [ ] Question answering produces accurate answers (>70% correct)
- [ ] Performance targets met (<500ms search, <2s QA)
- [ ] Local embeddings working (~50ms per document)
- [ ] PyPI package installable with `pip install ti-docs-mcp`
- [ ] Tested with GLM 4.7 and MCP client
- [ ] Constitution compliance verified

---

**Version:** 1.1 | **Status:** Draft | **Created:** 2026-02-11 | **Updated:** 2026-02-19

**Next Step:** Generate task list from this plan (`/tasks`)
