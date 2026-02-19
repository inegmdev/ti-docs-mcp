"""
ti-docs-mcp package setup
"""

from setuptools import setup, find_packages

setup(
    name="ti-docs-mcp",
    version="1.0.0",
    description="TI Documentation MCP Server - Search Texas Instruments documentation with semantic queries",
    long_description="""
        ti-docs-mcp is an MCP (Model Context Protocol) server that provides 
        intelligent search across Texas Instruments documentation. It uses semantic search 
        and RAG (Retrieval-Augmented Generation) to answer technical questions about 
        TI components, products, and SDKs.
        """,
    author="OpenClaw <openclaw@example.com>",
    url="https://github.com/openclaw/ti-docs-mcp",
    packages=find_packages(where="ti_docs_mcp"),
    python_requires=">=3.8",
    install_requires=[
        "mcp>=0.9.0",
        "openai>=1.0.0",
        "httpx>=0.24.0",
        "beautifulsoup4>=4.12.0",
        "pypdf2>=3.0.0",
        "pyyaml>=6.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ti-docs-mcp=ti_docs_mcp.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Scientific/Engineering :: Embedded Systems",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
    ],
    keywords="mcp,model-context-protocol,texas-instruments,documentation,semantic-search,rag,glm",
)
