# Clarification Questions for ti-docs-mcp Specification

The following questions are designed to identify ambiguities, missing details, and potential risks in the specification. Please answer each question to refine the specification before planning.

---

## Technical Implementation

### 1. Data Source and Content Access
**Question:** How will the MCP server access TI documentation content?

**Options:**
- A) Scrape e2e.ti.com web pages dynamically
- B) Use TI's official search API (if available)
- C) Download and index TI documentation locally
- D) Hybrid approach (cache locally, fetch live when needed)

**Considerations:**
- Scraping may violate TI's terms of service
- API may not exist or be rate-limited
- Local indexing requires storage and update strategy
- Hybrid balances freshness with performance

---

### 2. Search Technology
**Question:** What search mechanism will power semantic search?

**Options:**
- A) TI.com's built-in search API results
- B) Embedding-based vector search (index TI docs locally)
- C) Full-text search with keyword matching
- D) Hybrid (embedding + full-text + TI API)

**Considerations:**
- Embedding-based provides semantic understanding but requires embedding generation
- Full-text is simpler but less accurate for natural language
- Hybrid provides best results but more complex
- Need to decide which embedding model to use (OpenAI, local, etc.)

---

### 3. Authentication and Rate Limiting
**Question:** Does e2e.ti.com require authentication for API or scraping?

**Details Needed:**
- Is TI search publicly accessible without login?
- Are there documented rate limits?
- Do we need API keys or tokens?
- How to handle rate limit errors (exponential backoff, queue, fail)?

---

### 4. Caching Strategy
**Question:** How should search results be cached?

**Options:**
- A) In-memory cache (fast, lost on restart)
- B) Persistent cache (SQLite, Redis, file-based)
- C) No caching (always fetch live)
- D) Time-based TTL (e.g., cache for 24 hours)

**Considerations:**
- Caching improves performance and reduces TI server load
- TI documentation may change (need cache invalidation)
- Storage requirements for persistent cache

---

### 5. Component Lookup Source
**Question:** For the `component_lookup` tool, where will component data come from?

**Options:**
- A) TI's product API (if available)
- B) Parse datasheet HTML pages
- C) Scrape product landing pages
- D) TI's public parts database export (if exists)

**Considerations:**
- Product pages may have structured data (JSON-LD, microdata)
- Need consistent data format across different TI product families
- Datasheets may be PDF (harder to parse)

---

### 6. SDK Documentation Source
**Question:** Where will SDK documentation be sourced from?

**Options:**
- A) TI's SDK documentation website (docs.ti.com)
- B) Local SDK installations (scan user's SDK directories)
- C) Downloaded SDK documentation archives
- D) TI's GitHub repositories (SDK examples and code)

**Considerations:**
- SDKs vary by platform (MSPWARE, C2000WARE, SYSCONFIG)
- Users may have SDKs installed locally (better context)
- Online docs are more comprehensive but require network

---

## Architecture and Integration

### 7. MCP Transport Protocol
**Question:** Which MCP transport protocols should be supported?

**Current Spec:** stdio (required), HTTP (optional)

**Clarification Needed:**
- Will HTTP transport be implemented in v1.0 or deferred?
- If HTTP, how will authentication be handled (API keys)?
- Should we support SSE (Server-Sent Events) for streaming?

---

### 8. GLM 4.7 Integration
**Question:** How does GLM 4.7 factor into the implementation?

**Details Needed:**
- Is GLM 4.7 the consumer of the MCP server?
- Does GLM 4.7 need specific response formats or schemas?
- Any GLM-specific constraints (token limits, context windows)?

---

### 9. Deployment Model
**Question:** How will users deploy and run the MCP server?

**Options:**
- A) Standalone executable (run as process, connect via stdio)
- B) Docker container (run with `docker run`, port exposed)
- C) Node.js/npm package (install globally, run CLI)
- D) Python package (PyPI, install via pip)

**Considerations:**
- Standalone executable is most portable
- Docker simplifies dependencies but adds overhead
- npm/PyPI enables easy installation for developers

---

## Scope and Features

### 10. Supported Product Families
**Question:** Which TI product families should be supported initially?

**Options:**
- A) All TI product families (broad scope, more work)
- B) Focus on specific families (e.g., MSP430, TMS320, C2000)
- C) User-configurable families (start with top 5, expand later)

**Considerations:**
- Different families have different documentation structures
- Testing effort scales with number of families
- Which families are most important to your use case?

---

### 11. Document Types Priority
**Question:** Which document types are highest priority?

**Current Spec:** datasheet, user_guide, app_note, reference_design

**Clarification Needed:**
- Are all 4 types equally important?
- Should some be indexed/searched before others?
- Are there other document types to include (e.g., errata, design guides)?

---

### 12. Question Answering Mechanism
**Question:** How should the `ti_question` tool work internally?

**Options:**
- A) RAG (Retrieval-Augmented Generation) with local LLM
- B) Pass query to GLM 4.7 with retrieved context
- C) Rule-based extraction from matched documents
- D) Hybrid (RAG for complex, rule-based for simple)

**Considerations:**
- RAG provides best answers but requires LLM integration
- Passing to GLM 4.7 may require tool call overhead
- Rule-based is fast but inflexible

---

## Error Handling and Edge Cases

### 13. Invalid Part Numbers
**Question:** How should the server handle invalid or non-existent part numbers?

**Options:**
- A) Return error with suggestions (similar valid parts)
- B) Return empty results with clear message
- C) Redirect to TI search page for that part number
- D) All of the above (suggestions + message + link)

---

### 14. Network Failures
**Question:** How should the server behave when e2e.ti.com is unavailable?

**Options:**
- A) Fail gracefully with error message
- B) Return cached results only (stale data warning)
- C) Queue requests and retry
- D) Degrade functionality (disable search, keep cached lookups)

---

### 15. Ambiguous Queries
**Question:** What happens when a search query is too ambiguous?

**Example:** User searches for "timer" (could be watchdog timer, PWM timer, RTC)

**Options:**
- A) Return results for all matches (let user filter)
- B) Ask clarification question (narrow down by context)
- C) Return top 3 results with confidence scores
- D) Require product_family parameter for disambiguation

---

## Compliance and Legal

### 16. TI Terms of Service
**Question:** Have you verified that scraping TI.com is allowed?

**Details Needed:**
- Does TI's robots.txt allow crawling?
- Are there API usage terms?
- Should we request permission for heavy usage?

---

### 17. Content Licensing
**Question:** How should TI documentation content be handled?

**Details Needed:**
- Can we cache/store TI documentation locally?
- Can we serve TI documentation through our own API?
- Should we always link back to TI.com (avoid rehosting)?

---

## Success Metrics Refinement

### 18. Benchmark Queries
**Question:** What benchmark queries should validate the system?

**Examples:**
- "MSP430 watchdog timer configuration"
- "TMS320F28335 ADC example code"
- "AM263x CAN bootloader"
- "CC13x2 low power modes"

**Clarification Needed:**
- Provide 5-10 representative queries from your domain
- What counts as a "correct" answer for each?

---

### 19. User Feedback Collection
**Question:** How will success metrics be measured in practice?

**Options:**
- A) Explicit user feedback (thumbs up/down on answers)
- B) Implicit metrics (click-through rate to TI.com, query reformulation)
- C) Manual review of search logs
- D) A/B testing with baseline (TI.com search)

---

## Open Questions Summary

Please answer these questions to proceed:

1. ~~**Data Source:** How to access TI content?~~ ✅ **Download and index locally**
2. ~~**Search Tech:** Embedding, full-text, hybrid, or TI API?~~ ✅ **Embedding-based**
3. ~~**Auth:** Does TI require authentication/API keys?~~ ✅ **None (local indexing)**
4. ~~**Caching:** In-memory, persistent, or none?** ✅ **Persistent (local index)**
5. **Component Data:** Product API, scrape pages, or database export?
6. **SDK Source:** Online docs, local SDKs, GitHub, or archives?
7. ~~**Transport:** stdio only, or HTTP in v1.0?** ✅ **stdio only (initially)**
8. ~~**GLM Role:** Is GLM 4.7 the consumer or integrated?** ✅ **RAG + pass to GLM 4.7**
9. ~~**Deployment:** Executable, Docker, npm, or PyPI?** ✅ **PyPI package (CLI)**
10. ~~**Product Families:** All families, specific focus, or configurable?** ✅ **Jacinto TDA4 Family only**
11. **Doc Types:** All 4 types equally, or prioritize some?
12. ~~**QA Mechanism:** RAG, pass to GLM, rule-based, or hybrid?** ✅ **RAG + pass to GLM 4.7**
13. **Invalid Parts:** Error, suggestions, redirect, or all?
14. **Network Fail:** Fail, cache-only, queue, or degrade?
15. **Ambiguity:** Return all, ask clarification, top 3, or require filter?
16. ~~**ToS:** Have you checked TI.com terms?** ✅ **Checked (see below)**
17. ~~**Licensing:** Can we cache/serve TI docs, or always link?** ✅ **Cache locally for search, always link to TI.com**
18. **Benchmarks:** Provide 5-10 example queries to test
19. **Feedback:** Explicit, implicit, manual review, or A/B?

---

## Answered Questions

### 1. Data Source ✅
**Decision:** Download and index TI documentation locally

**Rationale:** Optimizes performance, reduces dependency on TI.com uptime, allows faster semantic search without network latency.

---

### 2. Search Technology ✅
**Decision:** Embedding-based vector search

**Rationale:** Provides semantic understanding (natural language queries), more accurate than keyword search. Will use embeddings to search local TI document index.

---

### 3. Authentication ✅
**Decision:** Not required (local indexing)

**Rationale:** Since we're downloading and indexing locally, no live API calls to TI.com during runtime.

---

### 4. Caching ✅
**Decision:** Persistent local index

**Rationale:** Fast search response times, works offline after initial indexing.

---

### 7. MCP Transport ✅
**Decision:** stdio transport only (initially)

**Rationale:** stdio is required by MCP spec and sufficient for most use cases. HTTP can be added in future.

---

### 8. GLM 4.7 Integration ✅
**Decision:** RAG (retrieve relevant docs) + pass to GLM 4.7

**Rationale:** Combines contextual retrieval with GLM 4.7's strong reasoning for accurate answers.

---

### 9. Deployment Model ✅
**Decision:** PyPI package with CLI

**Rationale:** Easy installation with `pip install ti-docs-mcp`, works across platforms.

---

### 10. Product Families ✅
**Decision:** Jacinto TDA4 Family only (initially)

**Rationale:** Focused scope, easier to validate. Can expand to other families later.

---

### 12. Question Answering ✅
**Decision:** RAG + pass to GLM 4.7

**Rationale:** RAG retrieves relevant TI docs, GLM 4.7 generates answer with proper reasoning and citations.

---

### 16. TI.com Terms of Service ✅
**Checked robots.txt:** https://e2e.ti.com/robots.txt

**Key Findings:**
- `Crawl-delay: 4` — TI wants 4 seconds between requests
- `Disallow: /api/` — API endpoints are blocked
- `Sitemap: https://e2e.ti.com/sitemapindex-standard.xml` — Public docs have sitemap
- Most documentation URLs are NOT disallowed

**Interpretation:**
- TI allows crawling of public documentation if robots.txt is respected
- 4-second crawl delay must be honored if fetching live
- API endpoints are off-limits (use sitemap and page scraping instead)
- robots.txt is advisory — actual policy in ToS (ToS URL not easily accessible)

**Recommendation:**
- Respect 4-second delay if fetching live
- Use sitemap for structured discovery
- Don't access `/api/` endpoints
- Always link back to original TI.com documents
- Local indexing for personal/development use is generally acceptable

---

### 17. Content Licensing ✅
**Decision:** Cache locally for search, always link to TI.com

**Rationale:**
- Local cache enables fast search
- Always link back to original TI.com documents (don't rehost)
- Proper attribution in all responses

---

**Created:** 2026-02-11 | **Status:** Partially Answered (Q1-2,3-4,7-10,12,16-17)
