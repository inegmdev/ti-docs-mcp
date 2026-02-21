"""
RAG (Retrieval-Augmented Generation) Module for ti-docs-mcp

Handles context building and GLM 4.7 integration.
"""

from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
from functools import lru_cache
import httpx


class RAGRetriever:
    """Retrieval-Augmented Generation system"""

    def __init__(self, max_context_tokens: int = 4000):
        """
        Initialize RAG retriever.

        Args:
            max_context_tokens: Maximum tokens for context window (default: 4000)
        """
        self.max_context_tokens = max_context_tokens

    def build_context_window(self, documents: List[Dict]) -> str:
        """
        Build context window from retrieved documents.

        Args:
            documents: Retrieved documents

        Returns:
            Context string
        """
        # Simple concatenation for now
        # TODO: Implement smarter context building with summarization
        context_parts = []

        for i, doc in enumerate(documents):
            context_parts.append(f"[Source {i+1}: {doc['metadata'].get('title', 'Unknown')}]")
            context_parts.append(f"URL: {doc['metadata'].get('url', '')}")
            context_parts.append(f"{doc['text']}\n")

        # Truncate to max tokens
        context = "\n".join(context_parts)

        # Simple token counting (approximate: 4 chars per token)
        tokens = len(context)
        if tokens > self.max_context_tokens:
            # Truncate to max tokens
            # (This is approximate, for production use tiktoken or similar)
            context = context[:self.max_context_tokens]

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
            context: Retrieved context
            model: Model to use

        Returns:
            Dictionary with answer, sources, confidence, related_questions
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
                            "content": "You are a Texas Instruments technical expert. Answer questions using only the provided TI documentation context. Be concise and accurate."
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
            # TODO: Parse response to extract sources and confidence
            answer = data.get('choices', [{}])[0].get('message', {}).get('content', '')

            return {
                'answer': answer,
                'sources': [],
                'confidence': 0.8,  # Default confidence
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
        if context:
            prompt = f"""Using the following TI documentation context, answer the question.

Context:
{context}

Question: {question}

Provide:
1. Direct answer to the question
2. Source document references (include URLs)
3. Confidence score (0.0 to 1.0)
4. 3 related follow-up questions

Be concise and accurate."""
        else:
            prompt = f"""You are a Texas Instruments technical expert. Answer the question.

Question: {question}

Provide:
1. Direct answer to the question
2. If you don't know, say "I don't have enough information"
3. Be concise and accurate

Be concise and accurate."""

        return prompt


class RAGSystem:
    """Complete RAG system with retrieval and generation"""

    def __init__(self, retriever: RAGRetriever, glm_client: GLMClient):
        """
        Initialize RAG system.

        Args:
            retriever: Retrieval component
            glm_client: GLM API client
        """
        self.retriever = retriever
        self.glm_client = glm_client

    async def retrieve_documents(self, query: str, top_k: int = 10,
                            filters: Optional[Dict] = None) -> List[Dict]:
        """
        Retrieve relevant documents for query.

        Args:
            query: Search query
            top_k: Number of documents to retrieve
            filters: Metadata filters

        Returns:
            List of retrieved documents
        """
        # Retrieve from retriever (needs index and embedding model)
        return await self.retriever.retrieve_context(query, top_k=top_k, filters=filters)

    def build_context_window(self, documents: List[Dict]) -> str:
        """
        Build context window from retrieved documents.

        Args:
            documents: Retrieved documents

        Returns:
            Context string
        """
        # Use retriever's context builder
        return self.retriever.build_context_window(documents)

    def extract_source_citations(self, documents: List[Dict]) -> List[Dict]:
        """
        Extract source citations from documents.

        Args:
            documents: Retrieved documents

        Returns:
            List of source dictionaries
        """
        sources = []
        for doc in documents:
            sources.append({
                'title': doc.get('metadata', {}).get('title', 'Unknown'),
                'url': doc.get('metadata', {}).get('url', ''),
                'relevance': 1.0 - doc.get('distance', 0.0)
            })
        return sources

    async def generate_related_questions(self, question: str) -> List[str]:
        """
        Generate related follow-up questions.

        Args:
            question: User's question

        Returns:
            List of related questions
        """
        # TODO: Implement smarter related question generation
        # For now, return generic questions
        return [
            "What other TI components are related to this?",
            "Can you provide more details about the specific feature?",
            "Where can I find more information about this topic?"
        ]

    async def answer_question(self, question: str, context_scope: Optional[str] = None,
                         top_k: int = 10) -> Dict:
        """
        Answer a technical question using RAG.

        Args:
            question: User's question
            context_scope: Limit search to specific context
            top_k: Number of documents to retrieve

        Returns:
            Dictionary with answer, sources, confidence, related_questions
        """
        # Build filters based on context scope
        filters = {}
        if context_scope:
            filters['context_scope'] = context_scope

        # Retrieve relevant documents
        documents = await self.retrieve_documents(question, top_k=top_k, filters=filters)

        # Build context window
        context = self.build_context_window(documents)

        # Extract source citations
        sources = self.extract_source_citations(documents)

        # Ask GLM for answer
        result = await self.glm_client.ask(question, context)

        # Add sources to result
        # TODO: Properly parse GLM response to extract sources
        # For now, add document sources
        result['sources'] = sources

        # Calculate confidence based on retrieval quality
        # Better matches = higher confidence
        if documents:
            # Average distance to top documents (0 = best, 1 = worst)
            avg_distance = sum(doc['distance'] for doc in documents[:5]) / len(documents[:5])
            confidence = max(0.0, 1.0 - avg_distance)
            result['confidence'] = confidence
        else:
            result['confidence'] = 0.5

        # Generate related questions
        related_questions = await self.generate_related_questions(question)
        result['related_questions'] = related_questions

        return result
