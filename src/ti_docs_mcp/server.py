"""
MCP Server for ti-docs-mcp

MCP server with 5 tools for TI documentation search and Q&A.
"""

import os
from typing import List, Optional
import asyncio

# Try FastMCP import, fall back to stdio_server
try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("ti-docs-mcp")
    HAS_FASTMCP = True
except ImportError:
    from mcp.server import stdio_server, Server
    from mcp.server.models import InitializationOptions
    HAS_FASTMCP = False

# Import our modules
from ti_docs_mcp.embeddings import get_text_model, get_code_model
from ti_docs_mcp.index import get_documents_index, get_code_index
from ti_docs_mcp.rag import RAGSystem, GLMClient


def register_tools(mcp_instance):
    """Register all tools with MCP server."""

    @mcp_instance.tool()
    async def ti_search(
        query: str,
        document_types: Optional[List[str]] = None,
        product_family: Optional[str] = None,
        max_results: int = 10
    ) -> list:
        """
        Search TI documentation using semantic queries.

        Args:
            query: Search query (natural language or technical terms)
            document_types: Filter by type (datasheet, user_guide, app_note, reference_design)
            product_family: Filter by product family (e.g., TDA4, MSP430)
            max_results: Maximum results to return (default: 10)

        Returns:
            List of search results with title, url, document_type, snippet, score
        """
        # Get index and model
        index = get_documents_index()
        model = get_text_model()

        # Generate query embedding
        query_embedding = model.embed_query(query)

        # Build filters
        where = {}
        if document_types:
            where['document_type'] = {"$in": document_types}
        if product_family:
            where['product_family'] = product_family

        # Search vector database
        results = index.search(
            query_embedding=query_embedding,
            n_results=max_results,
            where=where if where else None
        )

        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            text = results['documents'][0][i]
            snippet = text[:200] + '...' if len(text) > 200 else text
            formatted_results.append({
                'title': results['metadatas'][0][i].get('title', 'Unknown'),
                'url': results['metadatas'][0][i].get('url', ''),
                'document_type': results['metadatas'][0][i].get('document_type', 'document'),
                'snippet': snippet,
                'relevance_score': 1.0 - results['distances'][0][i]  # Convert distance to score
            })

        return formatted_results


    @mcp_instance.tool()
    async def component_lookup(part_number: str) -> dict:
        """
        Lookup TI component by part number.

        Args:
            part_number: TI part number (e.g., TDA4VP8, MSP430FR2355)

        Returns:
            Component details with name, family, datasheet_url, user_guide_url, features
        """
        # Get index and model
        index = get_documents_index()
        model = get_text_model()

        # Generate query embedding
        query_embedding = model.embed_query(part_number)

        # Search for exact match
        results = index.search(
            query_embedding=query_embedding,
            n_results=1,
            where={'part_number': part_number}
        )

        # If no exact match, try prefix match
        if not results['ids'][0]:
            results = index.search(
                query_embedding=query_embedding,
                n_results=5,
                where={'part_number': {'$contains': part_number}}
            )

        if not results['ids'][0]:
            return {
                'part_number': part_number,
                'error': 'Component not found',
                'suggestions': []
            }

        # Return top result
        metadata = results['metadatas'][0][0]
        return {
            'part_number': part_number,
            'name': metadata.get('title', 'Unknown'),
            'family': metadata.get('product_family', 'TDA4'),
            'package': metadata.get('package', 'Unknown'),
            'description': metadata.get('content', '')[:200] + '...' if len(metadata.get('content', '')) > 200 else metadata.get('content', ''),
            'datasheet_url': metadata.get('url', ''),
            'user_guide_url': metadata.get('user_guide_url', ''),
            'key_features': metadata.get('features', [])
        }


    @mcp_instance.tool()
    async def product_info(product_name: str) -> dict:
        """
        Get TDA4 product information.

        Args:
            product_name: Product name (e.g., TDA4, Jacinto)

        Returns:
            Product overview with description, applications, variants, related_products
        """
        # Get index and model
        index = get_documents_index()
        model = get_text_model()

        # Generate query embedding
        query_embedding = model.embed_query(product_name)

        # Search for documents about this product
        results = index.search(
            query_embedding=query_embedding,
            n_results=20,
            where={'product_family': product_name}
        )

        if not results['ids'][0]:
            return {
                'product_name': product_name,
                'error': 'Product information not found'
            }

        # Extract information from results
        variants = list(set([
            meta.get('title', '').split()[0] if meta.get('title') else 'Unknown'
            for meta in results['metadatas'][0]
        ]))

        # TODO: Parse applications from documents
        applications = ['Automotive', 'Industrial', 'Robotics']  # Placeholder

        # TODO: Find related products
        related_products = ['TDA4VP8', 'TDA4VM', 'AM68A', 'AM62A']  # Placeholder

        return {
            'product_name': product_name,
            'category': 'Automotive Processor',
            'description': f'{product_name} product family - Jacinto processors for automotive applications.',
            'applications': applications,
            'variants': variants[:10],  # Top 10 variants
            'related_products': related_products
        }


    @mcp_instance.tool()
    async def sdk_search(
        sdk_name: str,
        query: str,
        api_version: Optional[str] = None
    ) -> list:
        """
        Search SDK documentation.

        Args:
            sdk_name: SDK name (e.g., C2000WARE, MSPM0, SYSCONFIG)
            query: Search query within SDK
            api_version: Specific API version

        Returns:
            List of SDK documentation results with function_name, description, parameters, example, url
        """
        # TODO: Implement code index and search
        # For MVP, return placeholder
        return [
            {
                'sdk_name': sdk_name,
                'function_name': f'{sdk_name}_API',
                'description': f'SDK documentation for {sdk_name}',
                'parameters': [],
                'example': f'// {sdk_name} example code\n// TODO: Implement code search',
                'documentation_url': f'https://docs.ti.com/{sdk_name.lower()}',
                'api_version': api_version
            }
        ]


    @mcp_instance.tool()
    async def ti_question(question: str, context_scope: Optional[str] = None) -> dict:
        """
        Answer technical questions using TI documentation.

        Args:
            question: Natural language technical question
            context_scope: Limit search to specific context (component, sdk, product)

        Returns:
            Answer with sources and confidence score
        """
        # Get API key from environment
        api_key = os.getenv('GLM_API_KEY')
        if not api_key:
            return {
                'question': question,
                'answer': 'GLM 4.7 API key not configured. Set GLM_API_KEY environment variable.',
                'sources': [],
                'confidence': 0.0,
                'related_questions': []
            }

        # Initialize RAG system
        try:
            model = get_text_model()
            index = get_documents_index()
            glm_client = GLMClient(api_key=api_key)

            rag = RAGSystem(
                embedding_model=model,
                vector_index=index,
                glm_client=glm_client
            )

            # Answer question
            result = await rag.answer_question(
                question=question,
                context_scope=context_scope,
                top_k=10
            )

            return result

        except Exception as e:
            return {
                'question': question,
                'answer': f'Error answering question: {str(e)}',
                'sources': [],
                'confidence': 0.0,
                'related_questions': []
            }


async def main():
    """Main entry point for MCP server via stdio."""
    print("Starting ti-docs-mcp MCP server...")

    # Load index on startup
    try:
        index = get_documents_index()
        print(f"Index loaded: {index.get_document_count()} documents")
    except Exception as e:
        print(f"Warning: Could not load index: {e}")
        print("Run 'ti-docs-mcp index' to create an index.")

    # Register tools and run server
    if HAS_FASTMCP:
        # Tools already registered via decorators
        mcp.run()
    else:
        # Use stdio_server as async context manager
        async with stdio_server() as (read_stream, write_stream):
            # Create and configure MCP server with streams
            # Create server instance
            server = Server(
                "ti-docs-mcp",
                "1.0.0",
                InitializationOptions(
                    server_name="ti-docs-mcp"
                )
            )

            # Register tools with server
            register_tools(server)

            # Run server with acquired streams
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ti-docs-mcp"
                )
            )


# Export for CLI
if HAS_FASTMCP:
    server = mcp


if __name__ == "__main__":
    asyncio.run(main())
