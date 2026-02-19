# RAG Layer Test Strategy
**Version:** 1.0
**Created:** 2026-02-12
**Author:** Tester 2 (@tester2)

---

## Overview

This document defines the test strategy for the RAG (Retrieval-Augmented Generation) layer, which is Phase 4 of the ti-docs-mcp project. The RAG layer is responsible for query embedding, context building, and GLM 4.7 integration for the `ti_question` tool.

**Components Under Test:**
1. Query Embedding Generation
2. Context Building
3. GLM 4.7 Integration
4. Vector Search Operations
5. Error Handling and Edge Cases

---

## Test Objectives

### Primary Objectives
- Ensure query embeddings are generated correctly
- Verify context building retrieves and formats relevant documents
- Validate GLM 4.7 integration produces accurate answers
- Test performance meets SLA requirements (<2s for ti_question)

### Secondary Objectives
- Ensure graceful degradation on API failures
- Validate error handling for malformed inputs
- Test with various question types (simple, complex, multi-part)

---

## Test Environment

### Dependencies
- OpenAI API for embeddings (text-embedding-3-small)
- GLM 4.7 API for question answering
- Vector database (ChromaDB/LanceDB)
- Mock embeddings and GLM responses for offline testing

### Test Data
- Sample TI documentation snippets
- Mock vector database with indexed TDA4 documents
- Known question-answer pairs for validation
- Edge case questions (ambiguous, out-of-scope, malformed)

---

## Test Cases

### 1. Query Embedding Tests (T4-001 to T4-004)

#### TC-RAG-001: Valid Query Embedding
**Description:** Generate embedding for a valid technical question
**Input:** "How do I configure the watchdog timer on TDA4?"
**Expected Output:** 1536-dimensional vector (text-embedding-3-small)
**Validation:**
- Vector dimension is 1536
- Vector values are floats between -1 and 1
- No API errors
- Response time <500ms

**Test Code:**
```python
@pytest.mark.asyncio
async def test_valid_query_embedding():
    query = "How do I configure the watchdog timer on TDA4?"
    embedding = await embed_query(query)
    assert len(embedding) == 1536
    assert all(isinstance(x, float) for x in embedding)
    assert all(-1 <= x <= 1 for x in embedding)
```

#### TC-RAG-002: Empty Query Embedding
**Description:** Handle empty query string
**Input:** ""
**Expected Behavior:** Raise ValueError or return error
**Validation:**
- Appropriate error raised
- Error message is clear
- No API call made

#### TC-RAG-003: Long Query Embedding
**Description:** Handle very long queries (>1000 chars)
**Input:** 1500-character technical question
**Expected Output:** Valid embedding (truncated if needed)
**Validation:**
- Embedding generated successfully
- API call succeeds
- Performance acceptable

#### TC-RAG-004: Special Characters in Query
**Description:** Handle queries with special characters
**Input:** "What's the difference between UART/I²C/SPI on TDA4?"
**Expected Output:** Valid embedding
**Validation:**
- Special characters handled correctly
- No encoding errors
- Embedding dimension correct

---

### 2. Context Building Tests (T4-005 to T4-009)

#### TC-RAG-005: Basic Context Building
**Description:** Build context from top 5 relevant documents
**Input:**
- Query embedding for "TDA4 watchdog timer configuration"
- Vector DB with 100+ TDA4 documents
- max_tokens=4000
**Expected Output:**
- 3-5 document snippets
- Total tokens <4000
- Includes metadata (title, url, document_type)
**Validation:**
- Snippets are relevant to query
- No duplicate documents
- Token count respects limit
- Source URLs are valid

#### TC-RAG-006: Empty Vector DB
**Description:** Handle empty vector database
**Input:**
- Query embedding
- Empty vector DB
**Expected Behavior:** Return empty context or graceful error
**Validation:**
- Appropriate error raised
- Error message indicates empty DB
- No crashes

#### TC-RAG-007: Context with No Relevant Docs
**Description:** Query with no matching documents
**Input:**
- Query embedding for "Apple iPhone specs"
- TDA4-only vector DB
**Expected Output:** Empty context or low-confidence indication
**Validation:**
- Context is empty
- Warning or error logged
- No spurious results

#### TC-RAG-008: Context Token Limit Truncation
**Description:** Verify context truncation when exceeding max_tokens
**Input:**
- Query with 50+ relevant documents
- max_tokens=1000
**Expected Output:** Truncated context within limit
**Validation:**
- Token count <=1000
- Most relevant documents included
- Truncation is graceful (no mid-sentence cutoffs if possible)

#### TC-RAG-009: Context Deduplication
**Description:** Remove duplicate documents from context
**Input:**
- Query with 10 results, 3 duplicates
**Expected Output:** 7 unique documents
**Validation:**
- No duplicate URLs in context
- No duplicate content
- Relevant documents preserved

---

### 3. GLM 4.7 Integration Tests (T4-010 to T4-016)

#### TC-RAG-010: Basic Question Answering
**Description:** Answer a simple technical question
**Input:**
- Question: "What is the clock speed of TDA4VP?"
- Context: Relevant TDA4 datasheet snippets
**Expected Output:**
- Answer: "The TDA4VP operates at up to 1.8 GHz"
- Confidence: >0.8
- Sources: 2-3 document references
**Validation:**
- Answer is accurate (compared to known truth)
- Confidence score is reasonable
- Sources are relevant
- Response time <2s

#### TC-RAG-011: Multi-Part Question
**Description:** Answer a question with multiple parts
**Input:**
- Question: "What are the power modes and current consumption of TDA4VP?"
- Context: Power management documentation
**Expected Output:**
- Answer covers all power modes
- Includes current consumption values
- Structured format (bullet points or table)
**Validation:**
- All question parts addressed
- Values are accurate
- Sources for each part provided

#### TC-RAG-012: Out-of-Scope Question
**Description:** Handle question outside TI documentation scope
**Input:**
- Question: "What's the weather in Austin?"
- Context: TDA4 documentation
**Expected Output:**
- Answer: "I cannot answer this based on TI documentation"
- Confidence: <0.3
- Sources: None
**Validation:**
- Low confidence score
- No incorrect answers
- Appropriate refusal

#### TC-RAG-013: Ambiguous Question
**Description:** Clarify ambiguous questions
**Input:**
- Question: "What is the SPI speed?"
- Context: Multiple TDA4 documents with different SPI speeds
**Expected Output:**
- Answer asks for clarification or provides multiple values
- Confidence: Moderate (0.5-0.7)
**Validation:**
- Clarification requested or multiple options provided
- Not a single potentially incorrect answer
- Sources for each option

#### TC-RAG-014: GLM API Error Handling
**Description:** Handle GLM API failures
**Input:**
- Question: Any valid question
- Mock: GLM API timeout or 500 error
**Expected Behavior:**
- Retry with exponential backoff (up to 3 times)
- If still failing, return graceful error
- Log error appropriately
**Validation:**
- Retry logic works
- User gets meaningful error
- No crash or infinite loop
- Error logged

#### TC-RAG-015: Rate Limit Handling
**Description:** Handle GLM API rate limits (HTTP 429)
**Input:**
- Rapid sequence of questions
- Mock: GLM API returns 429
**Expected Behavior:**
- Wait for Retry-After header or default backoff
- Resubmit request
**Validation:**
- Requests retry after appropriate delay
- User receives delayed but correct response
- No excessive retries

#### TC-RAG-016: Malformed GLM Response
**Description:** Handle invalid GLM API responses
**Input:**
- Question: Any valid question
- Mock: Malformed JSON response
**Expected Behavior:**
- Log error
- Return fallback error message
- Not crash
**Validation:**
- Error handled gracefully
- User sees helpful error
- Service continues

---

### 4. Vector Search Tests (T2-011 to T2-015)

#### TC-RAG-017: Semantic Search Accuracy
**Description:** Test semantic search finds relevant documents
**Input:**
- Query: "TDA4VP interrupt latency"
- Vector DB: 200 TDA4 documents
**Expected Output:**
- Top 5 results include interrupt-related docs
- Relevance scores >0.7 for top 3
**Validation:**
- Manual review of top 5 results
- Relevance scores reasonable
- Documents contain relevant content

#### TC-RAG-018: Search with Filters
**Description:** Test search with document_type filter
**Input:**
- Query: "Watchdog timer"
- Filter: document_type="datasheet"
**Expected Output:**
- Only datasheets in results
- Relevant watchdog timer datasheets
**Validation:**
- All results are datasheets
- Results contain watchdog timer info
- Relevance scores good

#### TC-RAG-019: Product Family Filter
**Description:** Test search with product_family filter
**Input:**
- Query: "GPIO configuration"
- Filter: product_family="TDA4"
**Expected Output:**
- Only TDA4 documents
- GPIO-related content
**Validation:**
- All results from TDA4 family
- GPIO configuration present
- No other families

#### TC-RAG-020: Vector DB Persistence
**Description:** Test index save/load from disk
**Input:**
- Create index with 50 documents
- Save to disk
- Load from disk
**Expected Output:**
- Index loads correctly
- All 50 documents present
- Search works after load
**Validation:**
- Document count matches
- Search returns expected results
- No data corruption

#### TC-RAG-021: Vector DB Query Performance
**Description:** Measure search latency
**Input:**
- 1000 queries
- Vector DB with 1000 documents
**Expected Output:**
- P95 latency <100ms
- P99 latency <200ms
**Validation:**
- Performance measured
- Meets target
- No outliers >500ms

---

### 5. Integration Tests (ti_question Tool)

#### TC-RAG-022: End-to-End Question Answering
**Description:** Full ti_question tool flow
**Input:**
- Question: "How do I enable ECC on TDA4VP DDR?"
**Expected Output:**
- Valid answer with steps
- Sources: User guide section, datasheet
- Confidence: >0.8
- Total time <2s
**Validation:**
- Answer is accurate
- Sources cited
- Performance target met
- No errors

#### TC-RAG-023: Follow-Up Questions
**Description:** Test related questions
**Input:**
- Q1: "What is ECC?"
- Q2: "How do I configure ECC on TDA4?"
**Expected Output:**
- Q1: General ECC explanation
- Q2: TDA4-specific configuration
**Validation:**
- Context changes appropriately
- Answers are accurate
- Sources relevant to each question

#### TC-RAG-024: Question with context_scope
**Description:** Test context_scope parameter
**Input:**
- Question: "What is the clock frequency?"
- context_scope: "TDA4VP"
**Expected Output:**
- Answer specific to TDA4VP
- Not generic or other TDA4 variants
**Validation:**
- Context filter works
- Answer is scoped correctly
- Sources from TDA4VP only

#### TC-RAG-025: Concurrent Questions
**Description:** Test multiple concurrent requests
**Input:**
- 10 concurrent questions
**Expected Behavior:**
- All 10 questions answered
- No race conditions
- No crashes
**Validation:**
- All requests succeed
- Answers are accurate
- No interleaved responses

---

## Test Fixtures

### Mock Data Fixtures

#### fixture: mock_tda4_documents
```python
@pytest.fixture
def mock_tda4_documents():
    """Sample TDA4 documents for testing."""
    return [
        {
            "id": "doc_001",
            "title": "TDA4VP Datasheet",
            "url": "https://e2e.ti.com/.../tda4vp-ds",
            "document_type": "datasheet",
            "product_family": "TDA4",
            "part_number": "TDA4VP",
            "content": "The TDA4VP is a high-performance automotive processor..."
        },
        {
            "id": "doc_002",
            "title": "TDA4VP User Guide",
            "url": "https://e2e.ti.com/.../tda4vp-ug",
            "document_type": "user_guide",
            "product_family": "TDA4",
            "part_number": "TDA4VP",
            "content": "This user guide describes the TDA4VP architecture..."
        },
        # ... more documents
    ]
```

#### fixture: mock_embeddings
```python
@pytest.fixture
def mock_embeddings():
    """Mock embeddings for testing (1536-dimensional vectors)."""
    import numpy as np
    return {
        "watchdog_timer": np.random.randn(1536).tolist(),
        "gpio_config": np.random.randn(1536).tolist(),
        "ecc_ddr": np.random.randn(1536).tolist(),
    }
```

#### fixture: mock_glm_response
```python
@pytest.fixture
def mock_glm_response():
    """Mock GLM 4.7 API response."""
    return {
        "id": "glm_response_001",
        "object": "chat.completion",
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "The TDA4VP operates at up to 1.8 GHz"
            }
        }],
        "usage": {
            "prompt_tokens": 1000,
            "completion_tokens": 20,
            "total_tokens": 1020
        }
    }
```

### Vector DB Fixture

#### fixture: test_vector_db
```python
@pytest.fixture
async def test_vector_db(mock_tda4_documents):
    """Create temporary vector DB with test data."""
    # Initialize vector DB
    # Add mock documents with embeddings
    # Return DB instance
    # Cleanup after test
    pass
```

---

## Mock Data Preparation

### TI Documentation Mock Data

Create representative mock data files in `tests/fixtures/mock_docs/`:

1. **datasheets/**
   - `tda4vp_datasheet.json` - Key specs, clock, power
   - `tda4vm_datasheet.json` - VM variant specs

2. **user_guides/**
   - `tda4vp_user_guide.json` - Architecture, peripherals
   - `tda4_bringup_guide.json` - Boot, initialization

3. **app_notes/**
   - `ecc_implementation.json` - ECC configuration
   - `watchdog_timer_usage.json` - WDT examples

4. **sdk_docs/**
   - `mcplus_sdk_api.json` - SDK function references
   - `psil_sdk_examples.json` - Code examples

### Question-Answer Pairs

Create validation dataset in `tests/fixtures/qa_pairs.json`:

```json
{
  "qa_pairs": [
    {
      "question": "What is the clock speed of TDA4VP?",
      "expected_answer": "1.8 GHz",
      "min_confidence": 0.9,
      "sources": ["TDA4VP Datasheet"]
    },
    {
      "question": "How do I configure ECC on DDR?",
      "expected_answer_contains": ["ECC", "DDR", "configuration"],
      "min_confidence": 0.8,
      "sources": ["TDA4VP User Guide"]
    }
  ]
}
```

---

## Test Execution

### Unit Tests
```bash
# Run all RAG tests
pytest tests/test_rag.py -v

# Run with coverage
pytest tests/test_rag.py --cov=ti_docs_mcp.rag --cov-report=html

# Run specific test category
pytest tests/test_rag.py -k "embedding"
pytest tests/test_rag.py -k "context_building"
pytest tests/test_rag.py -k "glm"
```

### Integration Tests
```bash
# Run with real vector DB (requires index)
pytest tests/test_rag.py --vector-db=/path/to/index -v

# Run with real GLM API (requires API key)
pytest tests/test_rag.py --use-real-glm -v
```

### Performance Tests
```bash
# Run benchmarks
pytest tests/test_rag.py -k "performance" --benchmark-only

# Generate benchmark report
pytest tests/test_rag.py -k "performance" --benchmark-json=benchmark.json
```

---

## Success Criteria

### Functional Criteria
- [ ] All 25 test cases pass
- [ ] Query embeddings generate correctly (100%)
- [ ] Context building works for all scenarios
- [ ] GLM 4.7 integration produces accurate answers (>70% correct)
- [ ] Error handling covers all edge cases

### Performance Criteria
- [ ] Query embedding <500ms (P95)
- [ ] Context building <500ms (P95)
- [ ] GLM 4.7 API call <1.5s (P95)
- [ ] Total ti_question response <2s (P95)
- [ ] Vector search <100ms (P95)

### Reliability Criteria
- [ ] 99% of valid questions return answers
- [ ] 0 crashes on malformed input
- [ ] Graceful degradation on API failures
- [ ] No race conditions with concurrent requests

---

## Open Questions & Dependencies

### Dependencies on Other Team Members
- **@dev1-3**: Need embedding API and vector store APIs to implement tests
- **@test-lead**: Review and approve test strategy
- **@pm**: Clarify acceptance criteria for accuracy targets

### Open Questions
1. Should we use real GLM API for testing or mock everything?
   - Recommendation: Mock for unit tests, use real for integration tests
2. How many sample documents needed for meaningful testing?
   - Recommendation: 50-100 representative documents
3. Should we test with real TI documentation or only mock data?
   - Recommendation: Both - mock data for speed, real docs for validation

---

## Timeline

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Week 1 | Create fixtures, mock data | 2-3 days |
| Week 1 | Implement embedding tests | 1-2 days |
| Week 2 | Implement context building tests | 2-3 days |
| Week 2 | Implement GLM integration tests | 2-3 days |
| Week 2-3 | Integration testing | 2-3 days |
| Week 3 | Performance testing | 1-2 days |

**Total Estimated:** ~10-15 days

---

## Next Steps

1. **Immediate (Today):**
   - Create test fixture files
   - Prepare mock data directory structure
   - Coordinate with @dev1-3 on API availability

2. **This Week:**
   - Implement embedding tests (TC-RAG-001 to TC-RAG-004)
   - Implement context building tests (TC-RAG-005 to TC-RAG-009)
   - Create mock vector DB with sample documents

3. **Next Week:**
   - Implement GLM integration tests (TC-RAG-010 to TC-RAG-016)
   - Implement vector search tests (TC-RAG-017 to TC-RAG-021)
   - Begin integration tests (TC-RAG-022 to TC-RAG-025)

---

**Status:** Draft - Ready for Review by @test-lead
**Last Updated:** 2026-02-12
