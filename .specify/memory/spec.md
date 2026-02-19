# ti-docs-mcp Specification

## Overview

**Project Name:** TI Documentation MCP Server

**Purpose:** An MCP (Model Context Protocol) server that provides tools for searching Texas Instruments documentation and answering technical questions about TI components, products, and SDKs.

**Target Users:** Engineers, developers, and researchers working with TI hardware and software.

---

## Problem Statement

TI documentation across e2e.ti.com is vast and fragmented:
- Multiple documentation types (datasheets, user guides, app notes)
- Component specifications scattered across product pages
- SDKs and libraries have separate documentation
- Search across all sources is difficult and time-consuming

Current solutions:
- Manual browsing through e2e.ti.com (slow, requires context switching)
- Using general search engines (noisy results, not TI-specific)
- Downloading PDFs manually (inefficient for quick lookups)

---

## Solution

An MCP server that exposes tools for:
1. **Semantic search** across TI documentation
2. **Component lookup** by part number or name
3. **Product information** retrieval
4. **SDK documentation** search
5. **Question answering** based on TI documentation context

The server acts as a bridge between AI models and TI's documentation ecosystem.

**Key Technical Decisions:**
- **Local Embeddings:** Uses `sentence-transformers` for offline privacy and zero API costs
- **Vector Database:** ChromaDB for fast, lightweight semantic search
- **RAG Strategy:** Optimized chunking per data type (HTML, PDF, code)
- **Models:**
  - Text: `all-MiniLM-L6-v2` (fast, 384 dims) or `all-mpnet-base-v2` (better accuracy, 768 dims)
  - Code: `microsoft/codebert-base` (code-aware embeddings)

See **[RAG_STRATEGY.md](../../RAG_STRATEGY.md)** for detailed implementation details.

---

## Core Capabilities

### 1. e2e.ti.com Search Tool
Search TI's documentation portal using semantic queries.

**Inputs:**
- `query` (string, required): Search query (natural language or technical terms)
- `document_types` (array of strings, optional): Filter by type (datasheet, user_guide, app_note, reference_design)
- `product_family` (string, optional): Filter by product family (e.g., MSP430, TMS320, AM263x)
- `max_results` (integer, optional): Maximum results to return (default: 10, max: 50)

**Outputs:**
- Array of search results with:
  - `title`: Document title
  - `url`: Direct link to document
  - `document_type`: Type (datasheet, user_guide, etc.)
  - `snippet`: Relevant excerpt
  - `relevance_score`: Match confidence (0-1)

**Example:**
```json
{
  "tool": "ti_search",
  "result": [
    {
      "title": "MSP430FR2355 Datasheet",
      "url": "https://e2e.ti.com/.../msp430fr2355-ds",
      "document_type": "datasheet",
      "snippet": "The MSP430FR2355 device combines...",
      "relevance_score": 0.92
    }
  ]
}
```

### 2. Component Lookup Tool
Retrieve detailed information about a specific TI component.

**Inputs:**
- `part_number` (string, required): TI part number (e.g., MSP430FR2355, TMS320F28335)

**Outputs:**
- Component details:
  - `part_number`: Part number
  - `name`: Device name
  - `description`: Brief description
  - `family`: Product family
  - `package`: Package type
  - `datasheet_url`: Link to datasheet
  - `user_guide_url`: Link to user guide
  - `key_features`: List of key features

### 3. Product Information Tool
Get high-level information about a TI product family or series.

**Inputs:**
- `product_name` (string, required): Product name (e.g., MSP430, TMS320, AM263x, CC13x2)

**Outputs:**
- Product details:
  - `name`: Product name
  - `category`: Microcontroller, DSP, Analog, Power, etc.
  - `description`: Product overview
  - `applications`: Typical applications
  - `variants`: Available device variants
  - `related_products`: Related TI products

### 4. SDK Documentation Search Tool
Search within TI SDK documentation and examples.

**Inputs:**
- `sdk_name` (string, required): SDK name (e.g., MSPM0, C2000WARE, SYSCONFIG)
- `query` (string, required): Search query within SDK
- `api_version` (string, optional): Specific API version

**Outputs:**
- SDK documentation results:
  - `function_name`: Relevant function or API
  - `description`: Function description
  - `parameters`: Parameter list with descriptions
  - `example`: Code example (if available)
  - `documentation_url`: Link to full documentation

### 5. Technical Question Answering Tool
Answer technical questions using TI documentation as context.

**Inputs:**
- `question` (string, required): Natural language technical question
- `context_scope` (string, optional): Limit search to specific context (component, sdk, product)

**Outputs:**
- Answer with:
  - `answer`: Direct answer to question
  - `sources`: Array of source documents used
  - `confidence`: Confidence score (0-1)
  - `related_questions`: Suggested follow-up questions

**Example:**
```
Question: "How do I configure the watchdog timer on MSP430FR2355?"

Answer:
"Configure the watchdog timer (WDT) using the WDTCTL register.
Set WDTPW to 0x5A and WDTHOLD to 1 to hold the WDT.
For 250ms interval, set WDTIS to 4."

Sources:
- MSP430FR2355 User Guide (Section 8.2.1)
- MSP430FR2355 Code Examples (example_wdt.c)
```

---

## Non-Functional Requirements

### Performance
- Search queries respond within 500ms (P95)
- Component lookup responds within 200ms (P95)
- Question answering responds within 2s (P95)

### Reliability
- 99% uptime for TI.com connectivity
- Graceful degradation when e2e.ti.com is slow or unavailable
- Fallback to cached results when possible

### Compatibility
- Compatible with GLM 4.7 model
- Supports stdio transport (required by MCP)
- Supports HTTP transport (optional, for web clients)
- Follows MCP Tool Protocol v1.0

### Security
- No user authentication required (public TI documentation)
- Respect TI.com robots.txt
- Rate limit requests to avoid overloading TI servers
- Cache with appropriate TTL to reduce load

---

## User Stories

### US-1: Component Datasheet Lookup
**As a** hardware engineer
**I want to** quickly find a component's datasheet
**So that** I can verify specifications without browsing TI.com

**Acceptance Criteria:**
- Enter part number → Get datasheet link and key specs
- Works for common part numbers (MSP430*, TMS320*, AM263x*)
- Returns error for invalid part numbers

### US-2: SDK API Search
**As a** firmware developer
**I want to** search SDK documentation for API functions
**So that** I can find function signatures and examples quickly

**Acceptance Criteria:**
- Search by SDK name and query
- Returns function description, parameters, and code examples
- Links to full documentation

### US-3: Technical Question Answering
**As a** developer debugging an issue
**I want to** ask a technical question and get an answer with sources
**So that** I can resolve issues without reading full manuals

**Acceptance Criteria:**
- Natural language question returns direct answer
- Answer includes source document references
- Confidence score helps assess reliability
- Suggests follow-up questions

### US-4: Product Information Discovery
**As a** new TI user
**I want to** explore a product family and its variants
**So that** I can select the right device for my application

**Acceptance Criteria:**
- Search by product name returns overview
- Shows device variants and key features
- Links to datasheets and user guides

### US-5: Multi-Source Search
**As a** researcher
**I want to** search across datasheets, user guides, and app notes
**So that** I get comprehensive results from all TI documentation

**Acceptance Criteria:**
- Single query searches all document types
- Can filter by document type
- Results sorted by relevance

---

## Out of Scope (Initial Version)

- TI account login and private documents
- Order management or inventory lookup
- Pricing and availability information
- Design tools integration (WEBENCH, Power Designer)
- Forum or community support search (E2E community)
- Non-TI documentation support

---

## Success Metrics

- **Search Accuracy:** >80% of searches return relevant results in top 3
- **Question Answering:** >70% of technical questions are answered correctly
- **Response Time:** 95% of queries respond within SLA
- **User Satisfaction:** Qualitative feedback from initial users

---

**Clarification Status:** All 19 questions answered ✅

See **[clarify.md](./clarify.md)** for detailed decisions on:
- Data sources (download + index locally)
- Local embedding models (sentence-transformers)
- Component data sources (scrape + parse)
- SDK sources (online + GitHub + local)
- Error handling strategies
- Benchmark queries

---

**Version:** 1.1 | **Status:** Draft | **Created:** 2026-02-11 | **Updated:** 2026-02-19
