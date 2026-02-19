# Specification Review - ti-docs-mcp

**Created:** 2026-02-19
**Status:** Ready for Review

## Purpose

This document summarizes the ti-docs-mcp specification for review before starting implementation.

## Project Overview

**ti-docs-mcp** is a Model Context Protocol (MCP) server that provides tools for searching Texas Instruments documentation and answering technical questions about TI components, products, and SDKs.

## Core Capabilities (5 Tools)

### 1. ti_search
Search TI documentation using semantic queries.

**Inputs:**
- query (string, required)
- document_types (array, optional)
- product_family (string, optional)
- max_results (integer, optional, default: 10)

**Outputs:**
- title, url, document_type, snippet, relevance_score

### 2. component_lookup
Lookup TI component by part number.

**Inputs:**
- part_number (string, required)

**Outputs:**
- name, description, family, package, datasheet_url, user_guide_url, key_features

### 3. product_info
Get TDA4 product information.

**Inputs:**
- product_name (string, required)

**Outputs:**
- category, description, applications, variants, related_products

### 4. sdk_search
Search SDK documentation.

**Inputs:**
- sdk_name (string, required)
- query (string, required)
- api_version (string, optional)

**Outputs:**
- function_name, description, parameters, example, documentation_url

### 5. ti_question
Answer technical questions using TI documentation.

**Inputs:**
- question (string, required)
- context_scope (string, optional)

**Outputs:**
- answer, sources, confidence, related_questions

## Non-Functional Requirements

- **Performance:** Search <500ms, Component lookup <200ms, QA <2s (P95)
- **Reliability:** 99% uptime, graceful degradation
- **Compatibility:** GLM 4.7, MCP stdio transport
- **Security:** No auth required, respect robots.txt, rate limiting

## Implementation Phases

1. **Foundation** (Week 1-2) - Project setup, MCP server skeleton, testing
2. **Index Layer** (Week 2-3) - Document ingestion, embeddings, vector DB
3. **Tool Implementation** (Week 3-4) - Implement 5 tools with actual logic
4. **RAG + GLM 4.7** (Week 4-5) - Query processing, context building, GLM integration
5. **Testing & Validation** (Week 5-6) - Unit/integration tests, benchmarks
6. **Packaging & Documentation** (Week 6) - PyPI package, README, docs

## Technology Stack

- **Language:** Python 3.8+
- **MCP Protocol:** mcp-python SDK
- **Embeddings (Text):** sentence-transformers (all-MiniLM-L6-v2) - Local, fast, zero API cost
- **Embeddings (Code):** microsoft/codebert-base - Local, code-aware
- **Vector Store:** ChromaDB with HNSW indexing
- **Reranker (Optional):** ms-marco-MiniLM-L-6-v2 - For better Q&A accuracy
- **PDF Parsing:** pymupdf4llm or pdfplumber
- **CLI:** Click or Typer
- **Testing:** pytest + pytest-asyncio
- **LLM:** GLM 4.7 (via Zai API)

**Key Benefits:**
- **Privacy:** No data sent to external APIs for embeddings
- **Cost:** Zero API costs for embeddings
- **Offline:** Works without internet
- **Fast:** ~50ms per document embedding

**See [RAG_STRATEGY.md](./RAG_STRATEGY.md)** for detailed RAG system design per data type

## Current Status

**Phase 1 Complete:**
- ✅ Project structure
- ✅ MCP server skeleton
- ✅ 5 tool stubs (placeholder responses)
- ✅ CLI entry point
- ✅ Basic test setup

**Next Steps:**
- Start Phase 2: Document ingestion and indexing

## Review Questions

1. Are the 5 tool specifications correct and complete?
2. Does the implementation plan and architecture make sense?
3. Are the 115 tasks in the task list comprehensive?
4. Any missing requirements or capabilities?

## Clarification Status ✅

All 19 clarification questions have been answered:
- Data source, search tech, authentication, caching
- Component data, SDK sources, transport, GLM integration
- Document types, QA mechanism, error handling
- Network failures, ambiguous queries, ToS compliance
- Licensing, benchmark queries, user feedback

**See [clarify.md](.specify/memory/clarify.md)** for detailed decisions.

---

**See detailed specs in:**
- `.specify/memory/spec.md` - Full specification
- `.specify/memory/plan.md` - Implementation plan
- `.specify/memory/clarify.md` - All 19 questions answered
- `.specify/memory/tasks.md` - 115 detailed tasks
