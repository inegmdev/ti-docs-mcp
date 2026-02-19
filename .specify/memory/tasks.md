# Task List for ti-docs-mcp

**Generated from plan.md (2026-02-11)**
**Status:** Ready for Implementation

---

## Phase 1: Foundation (Week 1-2) ✅ COMPLETE

### Project Setup
- [X] **[T1-001]** Create project structure (src/, tests/, config.yaml, pyproject.toml)
- [X] **[T1-002]** Initialize Python package (src/ti_docs_mcp/__init__.py)
- [X] **[T1-003]** Setup PyPI packaging (setup.py, pyproject.toml with metadata)
- [X] **[T1-004]** Add CLI entry point (console_scripts in pyproject.toml)

### MCP Server Skeleton
- [X] **[T1-005]** Initialize MCP server with mcp-python SDK
- [X] **[T1-006]** Implement stdio transport
- [X] **[T1-007]** Create tool definitions (5 tools with stub implementations)
- [X] **[T1-008]** Implement server main() function
- [X] **[T1-009]** Add error handling for MCP protocol errors

### Testing Setup
- [X] **[T1-010]** Setup pytest configuration
- [X] **[T1-011]** Create test skeleton (test_tools.py, test_server.py)
- [X] **[T1-012]** Add pytest-asyncio for async testing
- [X] **[T1-013]** Write unit tests for MCP server start/stop

---

## Phase 2: Index Layer (Week 2-3)

### Document Download
- [X] **[T2-001]** Implement TI doc downloader with httpx
- [X] **[T2-002]** Parse TI sitemap for URL discovery
- [X] **[T2-003]** Implement 4-second crawl delay (respect robots.txt)
- [X] **[T2-004]** Add retry logic for failed downloads
- [X] **[T2-005]** Filter by TDA4 product family

### Content Parsing
- [X] **[T2-006]** Parse HTML with BeautifulSoup (datasheets, user guides)
- [ ] **[T2-007]** Parse PDF with pypdf2 (app notes, reference designs)
- [X] **[T2-008]** Extract metadata (title, type, family, part_number, URLs)
- [X] **[T2-009]** Clean and normalize text content
- [X] **[T2-010]** Deduplicate documents by URL

### Vector Index
- [X] **[T2-011]** Integrate sentence-transformers for local embeddings (all-MiniLM-L6-v2)
- [X] **[T2-012]** Setup ChromaDB (or LanceDB) for vector storage
- [X] **[T2-013]** Implement batch embedding generation (100 docs/batch)
- [X] **[T2-014]** Store embeddings with metadata in vector DB
- [X] **[T2-015]** Implement index persistence (save/load from disk)

### CLI Index Management
- [X] **[T2-016]** Implement `ti-docs-mcp index` CLI command
- [X] **[T2-017]** Add `--family` flag for product family
- [ ] **[T2-018]** Add `--update` flag for incremental index
- [X] **[T2-019]** Add `--clear` flag to reset index
- [ ] **[T2-020]** Test indexing with TDA4 docs

---

## Phase 3: Tool Implementation (Week 3-4)

### Tool: ti_search
- [X] **[T3-001]** Implement `ti_search` tool with MCP decorator
- [X] **[T3-002]** Generate query embedding
- [X] **[T3-003]** Search vector DB with filters (document_type, product_family)
- [X] **[T3-004]** Rank results by relevance score
- [X] **[T3-005]** Limit to max_results parameter
- [X] **[T3-006]** Return structured response (title, url, type, snippet, score)
- [ ] **[T3-007]** Add input validation
- [ ] **[T3-008]** Write unit tests

### Tool: component_lookup
- [X] **[T3-009]** Implement `component_lookup` tool
- [X] **[T3-010]** Exact match search by part_number
- [X] **[T3-011]** Fallback to prefix match
- [X] **[T3-012]** Return component details (name, family, datasheet_url, user_guide_url, features)
- [X] **[T3-013]** Handle invalid part numbers with error
- [ ] **[T3-014]** Write unit tests

### Tool: product_info
- [X] **[T3-015]** Implement `product_info` tool
- [X] **[T3-016]** Search TDA4 product database by name
- [X] **[T3-017]** Return product overview (description, applications, variants)
- [X] **[T3-018]** Return related products
- [ ] **[T3-019]** Write unit tests

### Tool: sdk_search
- [X] **[T3-020]** Implement `sdk_search` tool
- [X] **[T3-021]** Filter SDK docs by sdk_name
- [X] **[T3-022]** Semantic search within SDK documents
- [X] **[T3-023]** Return function/API results (name, description, parameters, example, url)
- [X] **[T3-024]** Filter by api_version if provided
- [ ] **[T3-025]** Write unit tests

### Tool: ti_question
- [X] **[T3-026]** Implement `ti_question` tool (RAG stub for now)
- [X] **[T3-027]** Define response structure (answer, sources, confidence, related)
- [ ] **[T3-028]** Write unit tests (mock RAG)
- [X] **[T3-029]** Integrate GLM 4.7 in Phase 4

---

## Phase 4: RAG + GLM 4.7 Integration (Week 4-5)

### Query Processing
- [ ] **[T4-001]** Implement `embed_query()` function
- [ ] **[T4-002]** Call OpenAI embeddings API for query
- [ ] **[T4-003]** Handle API errors and rate limits
- [ ] **[T4-004]** Cache query embeddings (same query optimization)

### Context Building
- [ ] **[T4-005]** Implement `build_context()` function
- [ ] **[T4-006]** Retrieve top N documents from vector DB
- [ ] **[T4-007]** Filter and deduplicate results
- [ ] **[T4-008]** Build context window (truncate to max_tokens)
- [ ] **[T4-009]** Include source URLs in context

### GLM 4.7 Integration
- [ ] **[T4-010]** Implement `glm_client.py` with Zai API
- [ ] **[T4-011]** Add API key configuration (env var + config file)
- [ ] **[T4-012]** Implement chat/completion API call
- [ ] **[T4-013]** Design prompt template (system + context + question)
- [ ] **[T4-014]** Parse GLM response for structured output
- [ ] **[T4-015]** Handle GLM errors (timeout, rate limit, invalid response)
- [ ] **[T4-016]** Connect to RAG: `ti_question` calls `build_context()` → `ask_glm()`

---

## Phase 5: Testing & Validation (Week 5-6)

### Unit Tests
- [ ] **[T5-001]** Unit tests for `ti_search` tool
- [ ] **[T5-002]** Unit tests for `component_lookup` tool
- [ ] **[T5-003]** Unit tests for `product_info` tool
- [ ] **[T5-004]** Unit tests for `sdk_search` tool
- [ ] **[T5-005]** Unit tests for `ti_question` tool
- [ ] **[T5-006]** Unit tests for embedding generation
- [ ] **[T5-007]** Unit tests for vector DB operations
- [ ] **[T5-008]** Unit tests for CLI commands
- [ ] **[T5-009]** Achieve >80% code coverage

### Integration Tests
- [ ] **[T5-010]** Test MCP server start/stop with stdio
- [ ] **[T5-011]** Test all 5 tools with MCP client
- [ ] **[T5-012]** Test tool error handling
- [ ] **[T5-013]** Test with real MCP client (Claude Desktop, etc.)
- [ ] **[T5-014]** Test concurrent requests

### Performance Benchmarks
- [ ] **[T5-015]** Benchmark `ti_search` latency (<500ms P95)
- [ ] **[T5-016]** Benchmark `component_lookup` latency (<200ms P95)
- [ ] **[T5-017]** Benchmark `ti_question` latency (<2s P95)
- [ ] **[T5-018]** Benchmark embedding generation time
- [ ] **[T5-019]** Optimize bottlenecks

### TDA4 Validation
- [ ] **[T5-020]** Test with TDA4-specific queries (e.g., "TDA4VP8", "Jacinto SDK")
- [ ] **[T5-021]** Validate datasheet retrieval works
- [ ] **[T5-022]** Validate SDK documentation search
- [ ] **[T5-023]** Test technical Q&A with TDA4 context
- [ ] **[T5-024]** Document any TDA4-specific issues

### Constitution Compliance
- [ ] **[T5-025]** Verify MCP protocol compliance
- [ ] **[T5-026]** Verify error-first design (all tools return errors)
- [ ] **[T5-027]** Verify input validation (all tools validate inputs)
- [ ] **[T5-028]** Verify no resource leaks (test with long-running server)
- [ ] **[T5-029]** Verify logging and observability

---

## Phase 6: Packaging & Documentation (Week 6)

### PyPI Packaging
- [ ] **[T6-001]** Finalize pyproject.toml (name, version, dependencies)
- [ ] **[T6-002]** Complete setup.py with entry points
- [ ] **[T6-003]** Add MANIFEST.in for package assets
- [ ] **[T6-004]** Test `pip install -e .` locally
- [ ] **[T6-005]** Build distribution packages (python -m build)
- [ ] **[T6-006]** Test twine upload to TestPyPI

### Documentation
- [ ] **[T6-007]** Write README.md with installation/usage
- [ ] **[T6-008]** Document all 5 tools with examples
- [ ] **[T6-009]** Write API documentation (optional: Sphinx/MkDocs)
- [ ] **[T6-010]** Write CHANGELOG.md for v1.0.0
- [ ] **[T6-011]** Create example MCP server config file
- [ ] **[T6-012]** Document environment variables (OPENAI_API_KEY, GLM_API_KEY)

### Final Validation
- [ ] **[T6-013]** End-to-end test with GLM 4.7 + MCP server
- [ ] **[T6-014]** Verify success metrics met
- [ ] **[T6-015]** Prepare for PyPI release

---

## Task Statistics

- **Total Tasks:** 115
- **Phase 1 (Foundation):** 13 tasks
- **Phase 2 (Index Layer):** 20 tasks
- **Phase 3 (Tool Implementation):** 29 tasks
- **Phase 4 (RAG + GLM 4.7):** 16 tasks
- **Phase 5 (Testing & Validation):** 29 tasks
- **Phase 6 (Packaging & Documentation):** 15 tasks

---

## Next Steps

1. **Start with Phase 1, Task T1-001:** Create project structure
2. **Work through tasks in order** (T1-001, T1-002, etc.)
3. **Mark tasks complete** as you finish each
4. **Use `/implement`** to automate execution (when available)
5. **Update spec** if requirements change

---

**Generated:** 2026-02-11 | **Status:** Ready for Implementation
