#!/usr/bin/env python3
"""
CLI entry point for ti-docs-mcp

Usage:
    ti-docs-mcp                    # Start MCP server (stdio transport)
    ti-docs-mcp index              # Download and index TI docs
    ti-docs-mcp index --help      # Show index command help
    ti-docs-mcp --help           # Show help
    ti-docs-mcp --version        # Show version
"""

import sys
import argparse
import asyncio

from ti_docs_mcp import __version__


def cmd_index(args):
    """Handle index command."""
    import asyncio
    from ti_docs_mcp.ingest import TIDocDownloader, TIDocParser, normalize_text, deduplicate_by_url
    from ti_docs_mcp.embeddings import get_text_model
    from ti_docs_mcp.index import get_documents_index

    async def run_index():
        # Initialize downloader using async context manager
        async with TIDocDownloader(
            sitemap_url="https://e2e.ti.com/sitemapindex-standard.xml",
            crawl_delay=4.0
        ) as downloader:
            # Discover URLs
            urls = await downloader.discover_urls()

            # Filter by product family
            if args.family:
                urls = downloader.filter_tda4_urls(urls, family=args.family)
            else:
                urls = downloader.filter_tda4_urls(urls)

            # Download documents
            downloaded = await downloader.download_batch(urls[:args.max_docs])

        # Parse documents (HTML only for now)
        parser = TIDocParser()
        parsed_docs = []

        for doc in downloaded:
            if doc['content_type'] == 'text/html':
                parsed = parser.parse_html(doc['content'], doc['url'])
                parsed['content'] = normalize_text(parsed['content'])
                parsed_docs.append(parsed)

        # Deduplicate
        parsed_docs = deduplicate_by_url(parsed_docs)

        # Clear index if requested
        if args.clear:
            index = get_documents_index()
            index.clear()

        # Generate embeddings
        model = get_text_model(device=args.device)
        embeddings = model.embed_batch([doc['content'] for doc in parsed_docs])

        # Store in vector database
        index = get_documents_index()
        index.add_documents(parsed_docs, embeddings)

        print(f"Indexing complete! {index.get_document_count()} documents in index.")

    asyncio.run(run_index())


def main():
    parser = argparse.ArgumentParser(
        prog="ti-docs-mcp",
        description="TI Documentation MCP Server - Search TI docs with semantic queries"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"ti-docs-mcp {__version__}"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Index command
    index_parser = subparsers.add_parser('index', help='Download and index TI documentation')
    index_parser.add_argument(
        '--family',
        default='TDA4',
        help='Product family to index (default: TDA4)'
    )
    index_parser.add_argument(
        '--max-docs',
        type=int,
        default=100,
        help='Maximum number of documents to download (default: 100)'
    )
    index_parser.add_argument(
        '--device',
        default='cpu',
        choices=['cpu', 'cuda'],
        help='Device to run embeddings on (default: cpu)'
    )
    index_parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear existing index before indexing'
    )

    args = parser.parse_args()

    # Handle commands
    if args.command == 'index':
        cmd_index(args)
    else:
        # Default: run MCP server
        from ti_docs_mcp.server import main as server_main
        server_main()


if __name__ == "__main__":
    main()
