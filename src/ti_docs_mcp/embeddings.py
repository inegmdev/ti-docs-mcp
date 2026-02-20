"""
Embeddings Module for ti-docs-mcp

Handles local embedding generation using sentence-transformers.
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np


class EmbeddingModel:
    """Local embedding model using sentence-transformers"""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', device: str = 'cpu'):
        """
        Initialize embedding model.

        Args:
            model_name: Name of the sentence-transformers model
            device: Device to run model on ('cpu' or 'cuda')
        """
        print(f"Loading embedding model: {model_name}")
        self.model_name = model_name
        self.model = SentenceTransformer(model_name, device=device)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Dimension: {self.dimension}, Device: {device}")

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str], batch_size: int = 32, show_progress: bool = True) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            batch_size: Batch size for encoding
            show_progress: Show progress bar

        Returns:
            List of embedding vectors
        """
        print(f"Generating embeddings for {len(texts)} texts...")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for search query.

        Args:
            query: Search query text

        Returns:
            Query embedding vector
        """
        return self.embed_text(query)


class CodeEmbeddingModel:
    """Code-aware embedding model using CodeBERT"""

    def __init__(self, model_name: str = 'microsoft/codebert-base', device: str = 'cpu'):
        """
        Initialize code embedding model.

        Args:
            model_name: Name of the code embedding model
            device: Device to run model on ('cpu' or 'cuda')
        """
        print(f"Loading code embedding model: {model_name}")
        self.model_name = model_name
        self.model = SentenceTransformer(model_name, device=device)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Code model loaded. Dimension: {self.dimension}, Device: {device}")

    def embed_code(self, code: str) -> List[float]:
        """
        Generate embedding for code snippet.

        Args:
            code: Code to embed

        Returns:
            Embedding vector as list of floats
        """
        embedding = self.model.encode(code, convert_to_numpy=True)
        return embedding.tolist()

    def embed_code_batch(self, codes: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple code snippets.

        Args:
            codes: List of code snippets to embed
            batch_size: Batch size for encoding

        Returns:
            List of embedding vectors
        """
        print(f"Generating embeddings for {len(codes)} code snippets...")
        embeddings = self.model.encode(
            codes,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings.tolist()


# Global model instances (lazy loading)
_text_model = None
_code_model = None


def get_text_model(device: str = 'cpu') -> EmbeddingModel:
    """
    Get or create text embedding model instance.

    Args:
        device: Device to run model on

    Returns:
        Text embedding model instance
    """
    global _text_model
    if _text_model is None:
        _text_model = EmbeddingModel(device=device)
    return _text_model


def get_code_model(device: str = 'cpu') -> CodeEmbeddingModel:
    """
    Get or create code embedding model instance.

    Args:
        device: Device to run model on

    Returns:
        Code embedding model instance
    """
    global _code_model
    if _code_model is None:
        _code_model = CodeEmbeddingModel(device=device)
    return _code_model
