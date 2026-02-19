"""
Vector Index Module for ti-docs-mcp

Handles ChromaDB operations for storing and searching embeddings.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any
from pathlib import Path


class VectorIndex:
    """Vector database index using ChromaDB"""

    def __init__(self, path: str = "~/.ti-docs-mcp/index", collection_name: str = "ti_documents"):
        """
        Initialize vector database.

        Args:
            path: Path to store index data
            collection_name: Name of the collection
        """
        self.path = Path(path).expanduser()
        self.collection_name = collection_name

        print(f"Initializing ChromaDB at: {self.path}")

        # Create persistent client
        self.client = chromadb.PersistentClient(
            path=str(self.path),
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"Loaded existing collection: {collection_name}")
            print(f"Collection count: {self.collection.count()}")
        except chromadb.errors.NotFoundException:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"Created new collection: {collection_name}")

    def add_documents(self, documents: List[Dict], embeddings: List[List[float]]):
        """
        Add documents to the index.

        Args:
            documents: List of document dictionaries with metadata
            embeddings: List of embedding vectors
        """
        print(f"Adding {len(documents)} documents to index...")

        ids = [doc.get('id', f"doc_{i}") for i, doc in enumerate(documents)]

        # Prepare metadata (filter out 'content' and 'embedding')
        metadatas = []
        for doc in documents:
            metadata = {k: v for k, v in doc.items()
                       if k not in ['content', 'embedding', 'id']}
            metadatas.append(metadata)

        # Prepare documents (text content for retrieval)
        docs = [doc.get('content', '') for doc in documents]

        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=docs,
            metadatas=metadatas
        )

        print(f"Added {len(documents)} documents. Total count: {self.collection.count()}")

    def search(self, query_embedding: List[float], n_results: int = 10,
              where: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Search for similar documents.

        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Metadata filters (e.g., {"document_type": "datasheet"})

        Returns:
            Dictionary with search results
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )

        return results

    def get_document_count(self) -> int:
        """
        Get total number of documents in index.

        Returns:
            Document count
        """
        return self.collection.count()

    def clear(self):
        """Clear all documents from the index."""
        print("Clearing index...")
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        print("Index cleared")

    def delete_collection(self):
        """Delete the entire collection."""
        print(f"Deleting collection: {self.collection_name}")
        self.client.delete_collection(name=self.collection_name)
        self.collection = None
        print("Collection deleted")


class CodeIndex(VectorIndex):
    """Vector index for code snippets"""

    def __init__(self, path: str = "~/.ti-docs-mcp/index"):
        """
        Initialize code vector index.

        Args:
            path: Path to store index data
        """
        super().__init__(path=path, collection_name="ti_code")


# Global index instances (lazy loading)
_documents_index = None
_code_index = None


def get_documents_index() -> VectorIndex:
    """
    Get or create documents index instance.

    Returns:
        Vector index instance
    """
    global _documents_index
    if _documents_index is None:
        _documents_index = VectorIndex()
    return _documents_index


def get_code_index() -> CodeIndex:
    """
    Get or create code index instance.

    Returns:
        Code index instance
    """
    global _code_index
    if _code_index is None:
        _code_index = CodeIndex()
    return _code_index
