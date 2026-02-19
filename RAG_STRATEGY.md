# RAG System Strategy - ti-docs-mcp

**Created:** 2026-02-19
**Purpose:** Define optimal RAG systems and local embedding models for TI documentation

---

## Overview

This document defines the RAG strategy for ti-docs-mcp, including:
1. Optimal RAG systems for each data type (HTML, PDF, code)
2. Local embedding model recommendations
3. Chunking strategies per data type
4. Embedding and indexing workflows

---

## RAG System Selection by Data Type

### 1. HTML Documentation (Datasheets, User Guides, App Notes)

**Vector Database:** ChromaDB
- **Why:** Lightweight, Python-native, excellent for small-to-medium datasets
- **Features:** Built-in HNSW indexing, metadata filtering, persistent storage
- **Best for:** Text-heavy documentation, quick startup, low resource usage

**Alternative:** Qdrant
- **Why:** Faster search, better filtering, production-ready
- **When:** Need higher performance or larger dataset (>100K documents)

**Chunking Strategy:**
- **Method:** Sentence/semantic chunking with overlap
- **Chunk size:** 512 tokens
- **Overlap:** 50 tokens
- **Preserve:** Headings, code blocks, tables
- **Tool:** LangChain `RecursiveCharacterTextSplitter` with `separators=["\n\n", "\n", ". ", " ", ""]`

**Reranking (Optional):** Cross-encoder `ms-marco-MiniLM-L-6-v2`
- **Why:** Improves relevance after initial retrieval
- **When:** Need top-N precision for Q&A

---

### 2. PDF Documents (App Notes, Reference Designs)

**Vector Database:** ChromaDB (same as HTML)
- **Why:** Consistency with HTML docs, easy to search across both
- **Note:** PDF content is extracted and treated as text after parsing

**PDF Parsing Strategy:**
- **Tool:** `pdfplumber` (better layout preservation) OR `pymupdf4llm` (fast, handles tables)
- **Extraction:** Extract text with structure preservation (headings, tables, code blocks)
- **Images:** OCR for diagrams (optional, using `easyocr` or `tesseract`)

**Chunking Strategy:**
- **Method:** Structure-aware chunking
- **Chunk size:** 512 tokens (same as HTML)
- **Overlap:** 50 tokens
- **Preserve:** Page numbers, section headers, figure captions

---

### 3. Code Examples and SDK APIs

**Vector Database:** ChromaDB with Code-Aware Indexing
- **Why:** Same vector DB for unified search, but with code-specific metadata
- **Enhancement:** Add AST-level metadata (function name, class, parameters)

**Specialized Option (Future):** Sourcegraph CodeGraph or CodeSearchnet
- **When:** Need semantic code understanding across large codebases

**Chunking Strategy:**
- **Method:** Function/class-level chunking
- **Chunk size:** Whole function (100-500 tokens)
- **Preserve:** Function signature, docstring, imports, return statements
- **Metadata:** file_path, language, function_name, parameters

**Reranking:** Code-aware cross-encoder (e.g., `codet5-base`)
- **Why:** Better understanding of code semantics

---

## Local Embedding Models

### General Text (Documentation)

| Model | Dimensions | Speed | Performance | Use Case |
|-------|-----------|-------|-------------|----------|
| **all-MiniLM-L6-v2** | 384 | ⚡ Very Fast | ✅ Good | Default choice, best speed/accuracy |
| **all-mpnet-base-v2** | 768 | 🚀 Fast | ✅ Excellent | Better accuracy for technical Q&A |
| **bge-small-en-v1.5** | 384 | ⚡ Very Fast | ✅ Good | Good for technical content |
| **e5-small-v2** | 384 | ⚡ Very Fast | ✅ Good | Good for bilingual (EN/CN) |

**Recommended Default:** `all-MiniLM-L6-v2`
- Fast inference (~50ms per document)
- Good semantic quality
- Small model size (~80MB)
- Works well for technical documentation

**For Better Accuracy:** `all-mpnet-base-v2`
- Better semantic understanding
- Slightly slower (~100ms per document)
- Larger model size (~420MB)
- Use when accuracy > speed

### Code-Specific Embeddings

| Model | Type | Dimensions | Speed | Performance | Use Case |
|-------|------|-----------|-------|-------------|----------|
| **microsoft/codebert-base** | CodeBERT | 768 | 🚀 Fast | ✅ Good | Default for code |
| **Salesforce/codet5-base** | CodeT5 | 768 | 🚀 Fast | ✅ Excellent | Better code understanding |
| **microsoft/unixcoder-base** | UniXcoder | 768 | 🚀 Fast | ✅ Good | Unified code + text |

**Recommended Default:** `microsoft/codebert-base`
- Well-tested for code search
- Good balance of speed/accuracy
- Supports multiple programming languages

**For Better Accuracy:** `Salesforce/codet5-base`
- Better code understanding (T5-based)
- Good for code + documentation combined

### Multilingual (Future)

| Model | Dimensions | Speed | Performance | Languages |
|-------|-----------|-------|-------------|-----------|
| **paraphrase-multilingual-MiniLM-L12-v2** | 384 | ⚡ Fast | ✅ Good | 50+ languages |
| **bge-m3** | 1024 | 🚀 Moderate | ✅ Excellent | 100+ languages |

---

## Chunking Methods

### 1. Fixed-Size Chunking with Overlap

**Description:** Split text into fixed-size chunks with overlap

**Pros:**
- Simple and predictable
- Easy to implement
- Consistent vector sizes

**Cons:**
- May break sentences/paragraphs
- Can lose context

**Best For:**
- Large documents where speed matters
- Initial indexing when content structure is unknown

**Implementation:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " ", ""]
)
```

---

### 2. Sentence/Semantic Chunking

**Description:** Split at sentence boundaries, preserve semantic meaning

**Pros:**
- Preserves context better
- Natural language flow
- Better for Q&A

**Cons:**
- Variable chunk sizes
- Slightly slower to process

**Best For:**
- Documentation and technical content
- Q&A and retrieval

**Implementation:**
```python
from sentence_transformers import SentenceSplitter

splitter = SentenceSplitter(
    chunk_size=512,
    chunk_overlap=50
)
```

---

### 3. Code-Aware Chunking

**Description:** Chunk at function/class level, preserve code structure

**Pros:**
- Preserves code semantics
- Better for code search
- Maintains function context

**Cons:**
- Requires AST parsing
- Language-specific logic

**Best For:**
- SDK APIs and code examples
- Function documentation

**Implementation:**
```python
import ast

def chunk_code_file(code: str, language: str) -> list:
    """Parse code and extract functions/classes as chunks."""
    tree = ast.parse(code)
    chunks = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            # Extract function/class as chunk
            chunk = ast.get_source_segment(code, node)
            chunks.append(chunk)
    
    return chunks
```

---

### 4. Structure-Aware Chunking (Hybrid)

**Description:** Use structure (headings, sections) to guide chunking

**Pros:**
- Preserves document hierarchy
- Better context for each section
- Natural boundaries

**Cons:**
- Requires parsing structure
- More complex implementation

**Best For:**
- HTML documentation with headings
- PDF documents with sections

**Implementation:**
```python
from bs4 import BeautifulSoup

def chunk_html_structure(html: str) -> list:
    """Parse HTML and chunk by headings."""
    soup = BeautifulSoup(html, 'html.parser')
    chunks = []
    current_section = ""
    
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'pre']):
        if tag.name.startswith('h'):
            # New section, save previous
            if current_section:
                chunks.append(current_section)
            current_section = tag.get_text() + "\n"
        else:
            current_section += tag.get_text() + "\n"
    
    if current_section:
        chunks.append(current_section)
    
    return chunks
```

---

## Embedding & Indexing Workflow

### 1. Installation

```bash
# Core dependencies
pip install sentence-transformers chromadb langchain pdfplumber pymupdf4llm

# Optional: OCR for PDF images
pip install easyocr

# Optional: Code parsing
pip install asttokens
```

---

### 2. Initialize Embedding Model

```python
from sentence_transformers import SentenceTransformer

# General text embedding model
text_model = SentenceTransformer('all-MiniLM-L6-v2')

# Code-specific embedding model
code_model = SentenceTransformer('microsoft/codebert-base')
```

---

### 3. Initialize Vector Database

```python
import chromadb
from chromadb.config import Settings

# Create persistent client
client = chromadb.PersistentClient(
    path="~/.ti-docs-mcp/index",
    settings=Settings(anonymized_telemetry=False)
)

# Create collection for documents
docs_collection = client.create_collection(
    name="ti_documents",
    metadata={"hnsw:space": "cosine"}
)

# Create collection for code
code_collection = client.create_collection(
    name="ti_code",
    metadata={"hnsw:space": "cosine"}
)
```

---

### 4. Embed and Index Documents

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup

def ingest_html_document(html_content: str, url: str, metadata: dict):
    """Ingest HTML document into vector database."""
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    
    # Chunk text
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_text(text)
    
    # Generate embeddings
    embeddings = text_model.encode(chunks, show_progress_bar=True)
    
    # Store in vector database
    ids = [f"{url}_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            **metadata,
            "url": url,
            "chunk_index": i,
            "chunk_count": len(chunks)
        }
        for i in range(len(chunks))
    ]
    
    docs_collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=chunks,
        metadatas=metadatas
    )

def ingest_pdf_document(pdf_path: str, url: str, metadata: dict):
    """Ingest PDF document into vector database."""
    import pymupdf4llm
    
    # Extract text from PDF with structure
    md_text = pymupdf4llm.to_markdown(pdf_path)
    
    # Chunk text
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_text(md_text)
    
    # Generate embeddings
    embeddings = text_model.encode(chunks, show_progress_bar=True)
    
    # Store in vector database
    ids = [f"{url}_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            **metadata,
            "url": url,
            "source_file": pdf_path,
            "chunk_index": i,
            "chunk_count": len(chunks)
        }
        for i in range(len(chunks))
    ]
    
    docs_collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=chunks,
        metadatas=metadatas
    )

def ingest_code_file(code: str, file_path: str, language: str, metadata: dict):
    """Ingest code file into vector database."""
    import ast
    
    # Parse code and extract functions
    try:
        tree = ast.parse(code)
    except:
        # Fallback to fixed-size chunking if parsing fails
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50
        )
        chunks = splitter.split_text(code)
    else:
        # Extract functions as chunks
        chunks = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                chunk = ast.get_source_segment(code, node)
                if chunk:
                    chunks.append(chunk)
    
    # Generate embeddings
    embeddings = code_model.encode(chunks, show_progress_bar=True)
    
    # Store in vector database
    ids = [f"{file_path}_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            **metadata,
            "file_path": file_path,
            "language": language,
            "chunk_index": i,
            "chunk_count": len(chunks)
        }
        for i in range(len(chunks))
    ]
    
    code_collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=chunks,
        metadatas=metadatas
    )
```

---

### 5. Search and Retrieve

```python
def search_documents(query: str, max_results: int = 10, filters: dict = None):
    """Search documents with optional filters."""
    # Generate query embedding
    query_embedding = text_model.encode(query)
    
    # Search vector database
    results = docs_collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=max_results,
        where=filters  # e.g., {"document_type": "datasheet", "product_family": "TDA4"}
    )
    
    return results

def search_code(query: str, max_results: int = 10, language: str = None):
    """Search code with optional language filter."""
    # Generate query embedding
    query_embedding = code_model.encode(query)
    
    # Search vector database
    results = code_collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=max_results,
        where={"language": language} if language else None
    )
    
    return results
```

---

### 6. Reranking (Optional, for Better Accuracy)

```python
from sentence_transformers import CrossEncoder

# Load reranker
reranker = CrossEncoder('ms-marco-MiniLM-L-6-v2')

def rerank_results(query: str, results: list):
    """Rerank search results for better relevance."""
    # Prepare query-document pairs
    pairs = [(query, doc['document']) for doc in results]
    
    # Compute scores
    scores = reranker.predict(pairs)
    
    # Sort by score
    ranked_results = sorted(
        zip(results, scores),
        key=lambda x: x[1],
        reverse=True
    )
    
    return [result for result, score in ranked_results]
```

---

## Summary: Recommended Stack

| Component | Recommendation | Rationale |
|-----------|---------------|-----------|
| **Vector DB** | ChromaDB | Lightweight, Python-native, easy to use |
| **Text Embedding** | `all-MiniLM-L6-v2` | Fast, good quality, small size |
| **Code Embedding** | `microsoft/codebert-base` | Well-tested for code search |
| **Text Chunking** | Semantic chunking (512 tokens, 50 overlap) | Preserves context, natural flow |
| **Code Chunking** | Function-level (AST-aware) | Preserves code semantics |
| **Reranker** | `ms-marco-MiniLM-L-6-v2` (optional) | Better relevance for Q&A |
| **PDF Parsing** | `pymupdf4llm` | Fast, handles tables, Markdown output |
| **HTML Parsing** | `BeautifulSoup4` | Robust, widely used |

---

## Performance Benchmarks

| Operation | Latency | Throughput |
|-----------|---------|------------|
| Embedding (all-MiniLM) | ~50ms/doc | ~20 docs/s |
| Embedding (all-mpnet) | ~100ms/doc | ~10 docs/s |
| Embedding (CodeBERT) | ~80ms/doc | ~12 docs/s |
| Vector Search (HNSW) | ~10ms | ~100 queries/s |
| Reranking (CrossEncoder) | ~20ms | ~50 queries/s |

---

## Next Steps

1. **Update plan.md** - Reflect local embedding models and RAG system changes
2. **Update dependencies** - Add sentence-transformers, chromadb, pdfplumber, pymupdf4llm
3. **Update tasks.md** - Revise tasks for local embedding implementation
4. **Update PR** - Commit changes and push to specs branch

---

**Version:** 1.1 | **Status:** Draft | **Created:** 2026-02-19
