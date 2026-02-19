# Clarification Questions for ti-docs-mcp Specification

**All questions have been answered!** ✅

---

## All Questions Answered

### 1. Data Source ✅
**Decision:** Download and index TI documentation locally

**Rationale:** Optimizes performance, reduces dependency on TI.com uptime, allows faster semantic search without network latency.

---

### 2. Search Technology ✅
**Decision:** Embedding-based vector search with local models

**Rationale:**
- Provides semantic understanding (natural language queries)
- More accurate than keyword search
- Uses local `sentence-transformers` models (no API costs)
- Fast inference (~50ms per document)
- Privacy: No data sent to external APIs

**Model:** `all-MiniLM-L6-v2` (text), `microsoft/codebert-base` (code)

---

### 3. Authentication ✅
**Decision:** Not required (local indexing)

**Rationale:** Since we're downloading and indexing locally, no live API calls to TI.com during runtime. Local embedding models run on the user's machine.

---

### 4. Caching ✅
**Decision:** Persistent local index (ChromaDB)

**Rationale:**
- Fast search response times
- Works offline after initial indexing
- ChromaDB provides persistent storage with HNSW indexing
- Can be updated incrementally

---

### 5. Component Data ✅
**Decision:** Scrape product landing pages + parse structured data

**Rationale:**
- TI doesn't provide a public product API
- Product pages have structured data (JSON-LD, microdata)
- Parse HTML with BeautifulSoup4
- Extract metadata (name, family, package, features, URLs)

**Implementation:**
- Parse product page HTML structure
- Extract datasheet and user guide URLs
- Store metadata in vector database
- Index component descriptions for semantic search

---

### 6. SDK Source ✅
**Decision:** Online docs (docs.ti.com) + GitHub repositories

**Rationale:**
- Online docs are comprehensive and up-to-date
- TI GitHub repos have code examples and SDK source
- Users can also point to local SDK installations via CLI
- Multiple sources provide best coverage

**Implementation:**
- Primary: docs.ti.com for SDK documentation
- Secondary: TI GitHub for code examples
- Optional: User-provided local SDK paths
- Parse both documentation and code files

---

### 7. MCP Transport ✅
**Decision:** stdio transport only (initially)

**Rationale:** stdio is required by MCP spec and sufficient for most use cases. HTTP can be added in future if needed.

---

### 8. GLM 4.7 Integration ✅
**Decision:** RAG (retrieve relevant docs with local embeddings) + pass to GLM 4.7

**Rationale:**
- Local embeddings provide context retrieval (fast, offline)
- GLM 4.7 provides strong reasoning and answer generation
- Combines contextual retrieval with GLM 4.7's capabilities
- RAG architecture: Query → Local Embeddings → Vector Search → Context → GLM 4.7

**Workflow:**
1. User asks question via `ti_question` tool
2. Generate query embedding locally (all-MiniLM-L6-v2)
3. Search vector database (ChromaDB) for relevant docs
4. Build context from top-N retrieved documents
5. Pass context + question to GLM 4.7
6. GLM 4.7 generates answer with citations

---

### 9. Deployment Model ✅
**Decision:** PyPI package with CLI

**Rationale:** Easy installation with `pip install ti-docs-mcp`, works across platforms (Windows, macOS, Linux).

---

### 10. Product Families ✅
**Decision:** Jacinto TDA4 Family only (initially)

**Rationale:** Focused scope, easier to validate. Can expand to other families later (MSP430, C2000, etc.) by updating product_family filter.

---

### 11. Document Types Priority ✅
**Decision:** All 4 types equal priority, index all together

**Rationale:**
- Datasheets, user guides, app notes, and reference designs are all valuable
- ChromaDB can handle mixed document types with metadata filters
- Users can filter by document_type if needed
- Prioritizing would create blind spots

**Implementation:**
- Index all 4 document types during ingestion
- Add `document_type` metadata field to each chunk
- Allow filtering by `document_type` in search queries
- Return mixed results by default (relevance-ranked)

---

### 12. Question Answering Mechanism ✅
**Decision:** RAG (local embeddings) + pass to GLM 4.7

**Rationale:**
- Local embeddings provide fast context retrieval (~50ms)
- GLM 4.7 provides accurate answer generation
- Combines speed with accuracy
- Reduces token usage (only relevant context sent to GLM)

**Workflow:**
1. Receive question via `ti_question` tool
2. Generate query embedding locally
3. Search vector database for relevant documents
4. Build context window (top 5-10 chunks, truncated to max_tokens)
5. Call GLM 4.7 with context + question
6. Return answer with sources and confidence

---

### 13. Invalid Part Numbers ✅
**Decision:** Return error with suggestions (similar parts)

**Rationale:**
- Provides helpful error message
- Suggests similar valid part numbers (prefix match)
- Avoids frustrating "not found" errors
- Maintains good UX

**Implementation:**
- Exact match search for component_lookup
- If not found, try prefix match (e.g., "TDA4VP" → "TDA4VP8")
- Return top 3 suggestions with similarity scores
- Include error message: "Part number not found. Did you mean: X, Y, Z?"

---

### 14. Network Failures ✅
**Decision:** Return cached results only (with stale data warning)

**Rationale:**
- Graceful degradation
- Better UX than hard failure
- Local index is persistent and reliable
- Warn users that data may be stale

**Implementation:**
- Check if vector database exists and has data
- If yes, search local index only
- Add metadata flag: `"source": "cached", "stale": true`
- Return results with warning: "TI.com unavailable. Results from cached index (may be stale)."

---

### 15. Ambiguous Queries ✅
**Decision:** Return top N results with confidence scores + metadata filtering

**Rationale:**
- Avoids blocking the user with clarification questions
- Confidence scores help users assess results
- Metadata (document_type, product_family) helps disambiguate
- Users can refine queries based on results

**Implementation:**
- Return top 10 results with relevance scores
- Include document_type and product_family in results
- If confidence < 0.6, add metadata note: "Low confidence. Try adding product_family filter."
- Don't require product_family parameter (optional)

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
- Avoid copyright issues (don't serve full TI docs, just snippets + links)

**Implementation:**
- Store full document text in local index (for search)
- Only return snippets + metadata in tool responses
- Always include `url` field pointing to TI.com
- Never rehost or serve complete TI documentation

---

### 18. Benchmark Queries ✅
**Decision:** TDA4-specific benchmark queries

**Benchmark Queries (TDA4 Focus):**
1. "TDA4VP8 watchdog timer configuration"
2. "Jacinto 7 SDK example code for SPI"
3. "TDA4VM power management low power modes"
4. "AM68A (TDA4) R5F core boot sequence"
5. "TDA4VP8 Vision Processing Unit (VPAC) API"
6. "Jacinto 7 CAN-FD driver configuration"
7. "TDA4VM PCIe endpoint mode setup"
8. "AM62A (TDA4) safety mechanism lockstep"
9. "TDA4VP8 ethernet MAC/MDIO initialization"
10. "Jacinto 7 secure boot flow"

**Success Criteria:**
- Top 3 results contain relevant document
- Answer includes correct citation to source
- Confidence score > 0.7 for correct answers
- Response time < 500ms for search, < 2s for QA

---

### 19. User Feedback Collection ✅
**Decision:** Manual review + implicit metrics (initially)

**Rationale:**
- Manual review is practical for early development
- Implicit metrics (query patterns, click-through) provide data
- No explicit feedback mechanism needed in v1.0
- Can add explicit feedback (thumbs up/down) in v2.0

**Implementation:**
- Log all queries and results to local file
- Track click-through rate to TI.com URLs
- Periodic manual review of search logs
- Document common queries that fail or return poor results

**Metrics to Track:**
- Query latency (search, QA)
- Result relevance (manual spot-check)
- Click-through rate to TI.com
- Common failed queries (no results or low confidence)

---

**Created:** 2026-02-11 | **Status:** All Questions Answered ✅ | **Updated:** 2026-02-19
