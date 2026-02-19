"""
RAG (Retrieval-Augmented Generation) Module for ti-docs-mcp

Handles context building and GLM 4.7 integration.
"""

from typing import List, Dict, Optional
import httpx


class RAGRetriever:
    """Retrieval-Augmented Generation system"""

    def __init__(self, embedding_model, vector_index, max_context_tokens: int = 4000):
        """
        Initialize RAG retriever.

        Args:
            embedding_model: Embedding model instance
            vector_index: Vector database index
            max_context_tokens: Maximum tokens for context window
        """
        self.embedding_model = embedding_model
        self.vector_index = vector_index
        self.max_context_tokens = max_context_tokens

    def retrieve_context(self, query: str, top_k: int = 10,
                      filters: Optional[Dict] = None) -> List[Dict]:
        """
        Retrieve relevant documents for query.

        Args:
            query: Search query
            top_k: Number of documents to retrieve
            filters: Metadata filters for search

        Returns:
            List of retrieved documents with metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_model.embed_query(query)

        # Search vector database
        results = self.vector_index.search(
            query_embedding=query_embedding,
            n_results=top_k,
            where=filters
        )

        # Format results
        documents = []
        for i in range(len(results['ids'][0])):
            documents.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })

        return documents

    def build_context_window(self, documents: List[Dict]) -> str:
        """
        Build context window from retrieved documents.

        Args:
            documents: Retrieved documents

        Returns:
            Context string
        """
        # Simple concatenation for now
        # TODO: Implement smarter context building with truncation
        context_parts = []

        for i, doc in enumerate(documents):
            context_parts.append(f"[Source {i+1}: {doc['metadata'].get('title', 'Unknown')}]")
            context_parts.append(f"URL: {doc['metadata'].get('url', '')}")
            context_parts.append(f"{doc['text']}\n")

        context = "\n".join(context_parts)
        return context


class GLMClient:
    """GLM 4.7 API client for RAG"""

    def __init__(self, api_key: str, base_url: str = "https://api.zai.io"):
        """
        Initialize GLM client.

        Args:
            api_key: API key for Zai
            base_url: Base URL for API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
        )

    async def ask(self, question: str, context: str,
                model: str = "glm-4.7") -> Dict:
        """
        Ask GLM 4.7 a question with context.

        Args:
            question: User's question
            context: Retrieved context from documents
            model: Model to use

        Returns:
            Dictionary with answer, sources, confidence
        """
        # Build prompt
        prompt = self._build_prompt(question, context)

        try:
            # Call GLM API
            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a Texas Instruments technical expert. Answer questions using only the provided TI documentation context."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                }
            )

            response.raise_for_status()
            data = response.json()

            # Extract answer
            answer = data['choices'][0]['message']['content']

            # TODO: Parse response to extract sources and confidence
            # For now, return basic structure
            return {
                'answer': answer,
                'sources': [],
                'confidence': 0.8,
                'related_questions': []
            }

        except httpx.HTTPError as e:
            raise RuntimeError(f"GLM API call failed: {e}")

    def _build_prompt(self, question: str, context: str) -> str:
        """
        Build prompt with context.

        Args:
            question: User's question
            context: Retrieved context

        Returns:
            Prompt string
        """
        prompt = f"""Using the following TI documentation context, answer the question.

Context:
{context}

Question: {question}

Provide:
1. Direct answer to the question
2. Source document references (include URLs)
3. Confidence score (0.0-1.0)
4. 2-3 related follow-up questions
"""
        return prompt


class RAGSystem:
    """Complete RAG system with retrieval and generation"""

    def __init__(self, embedding_model, vector_index, glm_client: GLMClient):
        """
        Initialize RAG system.

        Args:
            embedding_model: Embedding model instance
            vector_index: Vector database index
            glm_client: GLM API client
        """
        self.retriever = RAGRetriever(embedding_model, vector_index)
        self.glm_client = glm_client

    async def answer_question(self, question: str, context_scope: Optional[str] = None,
                         top_k: int = 10) -> Dict:
        """
        Answer a technical question using RAG.

        Args:
            question: User's question
            context_scope: Optional scope filter (e.g., "component", "sdk")
            top_k: Number of documents to retrieve

        Returns:
            Dictionary with answer, sources, confidence, related_questions
        """
        # Build filters based on scope
        filters = None
        if context_scope:
            filters = {"product_family": "TDA4"}

        # Retrieve relevant documents
        documents = self.retriever.retrieve_context(question, top_k=top_k, filters=filters)

        if not documents:
            return {
                'answer': 'No relevant documentation found for this question.',
                'sources': [],
                'confidence': 0.0,
                'related_questions': []
            }

        # Build context window
        context = self.retriever.build_context_window(documents)

        # Ask GLM for answer
        result = await self.glm_client.ask(question, context)

        # Add sources from retrieved documents
        result['sources'] = [
            {'title': doc['metadata'].get('title', ''),
             'url': doc['metadata'].get('url', ''),
             'relevance': 1.0 - doc['distance']}
            for doc in documents[:5]
        ]

        return result
