# Changelog

All notable changes to ti-docs-mcp will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/0.3.0/).

## [Unreleased]

### Added
- Initial project structure and MCP server setup
- 5 MCP tool stubs (ti_search, component_lookup, product_info, sdk_search, ti_question)
- Index layer implementation (document ingestion, embeddings, vector database)
- PDF parsing support with pymupdf4llm
- Input validation for all tools
- Incremental index updates with --update flag
- PyPI publishing preparation (LICENSE, MANIFEST.in, updated pyproject.toml)
- GitHub Actions workflow for automatic PyPI publishing

### Changed
- Fixed stdio_server() usage as async context manager
- Fixed document ID collisions using URL-based SHA256 hashes
- Fixed XXE vulnerability using defusedxml.ElementTree
- Fixed XML sitemap parsing to use element.text properly
- Fixed httpx resource leaks with async context manager
- Fixed FastMCP tool registration (now registers before mcp.run())
- Added comprehensive README with MCP integration guides
- Added config.yaml with default settings
- Updated all dependencies (local models, ChromaDB, httpx, etc.)

### Fixed
- Incorrect SentenceSplitter import in RAG_STRATEGY.md (changed to LangChain)
- Resource leaks in TIDocDownloader (added async context manager)

## [1.0.0] - 2026-02-20

### Added
- Foundation: Project structure, MCP server skeleton, testing setup
- Index Layer: Document download, HTML/PDF parsing, embeddings, ChromaDB
- Tool Implementation: All 5 tools with real implementations
- Input Validation: Comprehensive validation module for all tool inputs
- Incremental Updates: Index tracking with JSON database, --update flag support
- PyPI Preparation: LICENSE, MANIFEST.in, updated pyproject.toml
- GitHub Actions: Automated build and publish workflow
- Documentation: Comprehensive README with integration guides
- Security: Fixed XXE vulnerability, resource leaks, XML parsing issues

### Changed
- Security: Replaced xml.etree.ElementTree with defusedxml.ElementTree (XXE protection)
- Performance: Added stable document IDs (SHA256 hashes) to prevent re-processing
- Security: Added async context manager to httpx client (proper resource cleanup)
- Reliability: Fixed XML sitemap parsing (proper element.text usage)
- Reliability: Fixed FastMCP tool registration (tools now register before run)
- Performance: Implemented incremental index updates (only process new/changed docs)
- Documentation: Added config.yaml for default settings
- Documentation: Updated README with PyPI installation, MCP integration guides
- Features: Added PDF parsing support with pymupdf4llm
- Features: Added input validation to all 5 tools
- Features: Added --update flag to index command

### Fixed
- Security: XXE vulnerability in XML parsing (defusedxml)
- Resource Leaks: httpx client now properly closed (async context manager)
- Resource Leaks: FastMCP tool registration now calls register_tools() before run()
- Bug: Document IDs now use SHA256 hashes (prevents collisions, idempotent)
- Bug: XML sitemap now parses <loc> as element.text (not attribute)
- Bug: stdio_server() now used as async context manager with streams
- Dependencies: Removed openai (using local models only)
- Dependencies: Added pymupdf4llm for PDF parsing
- Dependencies: Added defusedxml for XXE protection
- Dependencies: Added sentence-transformers for local embeddings
- Dependencies: Added chromadb for vector database
- Dependencies: Added httpx for HTTP client
- Dependencies: Added beautifulsoup4 for HTML parsing
- Dependencies: Added pyyaml for config file
- Dependencies: Added numpy for array operations

### Security
- XXE Protection: All XML parsing uses defusedxml.ElementTree
- Local Models: No external API keys, no data exfiltration risk
- Resource Management: All HTTP clients use async context managers
- Credential Storage: GLM 4.7 API key from environment variable only

### Known Issues
- GitHub Actions workflow created but not yet committed/pushed
- Git issues with file detection in some commands (files not being tracked properly)

---

## [0.1.0] - TBD

---

## [0.0.0-alpha] - 2026-02-20

### Added
- Initial release of ti-docs-mcp MCP server
- Support for TI (Texas Instruments) documentation search
- Semantic search using local sentence-transformers embeddings
- Vector database using ChromaDB
- 5 MCP tools: ti_search, component_lookup, product_info, sdk_search, ti_question
- Document ingestion from e2e.ti.com with sitemap discovery
- HTML and PDF document parsing
- Local embedding models: all-MiniLM-L6-v2 (text), microsoft/codebert-base (code)
- RAG system with GLM 4.7 integration for question answering
- Input validation for all tools
- Incremental index updates with --update flag
- CLI command: `ti-docs-mcp index` for document ingestion
- GitHub Actions workflow for automated PyPI publishing
- MIT License
- Python 3.8+ support
- PyPI package: `ti-docs-mcp`

### Notes
- This is the initial alpha release
- All features from specification are implemented
- Ready for testing and feedback
- Performance targets: <500ms search, <2s Q&A
- Security: XXE protection, proper resource management, no API key leakage
