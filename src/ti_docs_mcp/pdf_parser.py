"""
PDF Parser Module for ti-docs-mcp

Handles PDF document extraction using pymupdf4llm.
"""

import pymupdf4llm
from typing import Dict, Optional


def parse_pdf(url: str, content: str) -> Dict:
    """
    Parse PDF content and extract text and metadata.

    Args:
        url: URL of the PDF document
        content: PDF content (binary data)

    Returns:
        Dictionary with extracted text and metadata
    """
    try:
        # Use pymupdf4llm to convert PDF to markdown
        md_text = pymupdf4llm.to_markdown(content)

        # Extract metadata from markdown
        # First non-empty line is typically the title
        lines = md_text.split('\n')
        title = None
        for line in lines:
            stripped = line.strip()
            if stripped and not title:
                title = stripped
                break

        if not title:
            title = url.split('/')[-1].split('.')[0]

        return {
            'url': url,
            'title': title,
            'document_type': 'pdf',
            'content': md_text,
            'content_type': 'application/pdf'
        }

    except Exception as e:
        print(f"Warning: Failed to parse PDF {url}: {e}")
        return {
            'url': url,
            'title': url.split('/')[-1].split('.')[0],
            'document_type': 'pdf',
            'content': '',
            'content_type': 'application/pdf'
        }


def extract_metadata_from_pdf(text: str, url: str) -> Dict:
    """
    Extract metadata from PDF content.

    Args:
        text: Extracted PDF text
        url: Document URL

    Returns:
        Metadata dictionary
    """
    metadata = {
        'url': url
        'document_type': 'pdf'
    }

    # Try to extract document type from URL path
    url_lower = url.lower()
    if 'datasheet' in url_lower:
        metadata['document_type'] = 'datasheet'
    elif 'user' in url_lower and 'guide' in url_lower:
        metadata['document_type'] = 'user_guide'
    elif 'app' in url_lower and 'note' in url_lower:
        metadata['document_type'] = 'app_note'
    elif 'reference' in url_lower and 'design' in url_lower:
        metadata['document_type'] = 'reference_design'

    return metadata
