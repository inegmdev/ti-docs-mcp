#!/usr/bin/env python3
"""
CLI entry point for ti-docs-mcp

Usage:
    ti-docs-mcp                    # Start MCP server (stdio transport)
    ti-docs-mcp --help           # Show help
    ti-docs-mcp --version        # Show version
"""

import sys
import argparse

from ti_docs_mcp import __version__


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
    
    args = parser.parse_args()
    
    # Import and run MCP server
    from ti_docs_mcp.server import main as server_main
    server_main()


if __name__ == "__main__":
    main()
