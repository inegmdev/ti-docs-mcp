"""
Document Ingestion Module for ti-docs-mcp

Handles downloading, parsing, and preparing TI documentation for indexing.
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import time
from pathlib import Path


class TIDocDownloader:
    """Download TI documentation from e2e.ti.com"""

    def __init__(self, sitemap_url: str, crawl_delay: float = 4.0):
        """
        Initialize downloader.

        Args:
            sitemap_url: URL to TI sitemap
            crawl_delay: Delay between requests in seconds (default: 4.0)
        """
        self.sitemap_url = sitemap_url
        self.crawl_delay = crawl_delay
        self.client = None  # Will be created in __aenter__ for lazy initialization

    async def __aenter__(self):
        """Async context manager entry - initialize httpx client."""
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; ti-docs-mcp/1.0)'
                }
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - close httpx client."""
        if self.client is not None:
            await self.client.aclose()
            self.client = None

    async def discover_urls(self) -> List[str]:
        """
        Discover documentation URLs from sitemap.

        Returns:
            List of documentation URLs
        """
        print(f"Fetching sitemap: {self.sitemap_url}")

        try:
            response = await self.client.get(self.sitemap_url)
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to fetch sitemap: {e}")

        # Parse sitemap XML
        root = ET.fromstring(response.text)
        urls = []

        # Handle both sitemap index and regular sitemap
        if root.tag.endswith('sitemapindex'):
            # Sitemap index - fetch all child sitemaps
            sitemap_ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
            for sitemap in root.findall(f'.//{sitemap_ns}sitemap'):
                # Use .text attribute or findtext() to get text content
                sitemap_url = sitemap.text
                if sitemap_url:
                    print(f"Fetching sub-sitemap: {sitemap_url}")
                    try:
                        sub_response = await self.client.get(sitemap_url)
                        sub_response.raise_for_status()
                        sub_root = ET.fromstring(sub_response.text)
                        for url in sub_root.findall(f'.//{sitemap_ns}loc'):
                            urls.append(url.text)
                    except httpx.HTTPError as e:
                        print(f"Warning: Failed to fetch sub-sitemap {sitemap_url}: {e}")
        else:
            # Regular sitemap
            sitemap_ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
            for url in root.findall(f'.//{sitemap_ns}loc'):
                urls.append(url.text)

        print(f"Discovered {len(urls)} URLs from sitemap")
        return urls

    def filter_tda4_urls(self, urls: List[str], family: str = "TDA4") -> List[str]:
        """
        Filter URLs by product family.

        Args:
            urls: List of URLs to filter
            family: Product family to filter (default: TDA4)

        Returns:
            Filtered list of URLs
        """
        # Filter URLs that contain the family name
        filtered = [u for u in urls if family.lower() in u.lower()]

        print(f"Filtered to {len(filtered)} URLs for family: {family}")
        return filtered

    async def download_document(self, url: str, retries: int = 3) -> Optional[Dict]:
        """
        Download a single document.

        Args:
            url: URL to download
            retries: Number of retry attempts

        Returns:
            Dictionary with url, content, content_type, or None on failure
        """
        for attempt in range(retries):
            try:
                await asyncio.sleep(self.crawl_delay)  # Respect robots.txt
                response = await self.client.get(url)
                response.raise_for_status()

                content_type = response.headers.get('content-type', '').split(';')[0]

                return {
                    'url': url,
                    'content': response.text,
                    'content_type': content_type
                }

            except httpx.HTTPError as e:
                print(f"Attempt {attempt + 1}/{retries} failed for {url}: {e}")
                if attempt == retries - 1:
                    print(f"Failed to download {url} after {retries} attempts")
                    return None
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)

        return None

    async def download_batch(self, urls: List[str]) -> List[Dict]:
        """
        Download multiple documents in parallel.

        Args:
            urls: List of URLs to download

        Returns:
            List of downloaded documents
        """
        print(f"Downloading {len(urls)} documents...")
        results = []

        tasks = [self.download_document(url) for url in urls]
        downloaded = await asyncio.gather(*tasks)

        for doc in downloaded:
            if doc:
                results.append(doc)

        print(f"Successfully downloaded {len(results)} documents")
        return results


class TIDocParser:
    """Parse TI documentation (HTML and PDF)"""

    def parse_html(self, content: str, url: str) -> Dict:
        """
        Parse HTML content.

        Args:
            content: HTML content
            url: Source URL

        Returns:
            Dictionary with metadata and text
        """
        soup = BeautifulSoup(content, 'html.parser')

        # Extract metadata
        title = self._extract_title(soup)
        document_type = self._extract_document_type(url, title)
        product_family = self._extract_product_family(url, title)

        # Extract text content
        text = soup.get_text(separator=' ', strip=True)

        return {
            'url': url,
            'title': title,
            'document_type': document_type,
            'product_family': product_family,
            'content': text,
            'content_type': 'text/html'
        }

    def parse_pdf(self, content: str, url: str) -> Dict:
        """
        Parse PDF content.

        Args:
            content: PDF content (binary)
            url: Source URL

        Returns:
            Dictionary with metadata and text
        """
        # TODO: Implement PDF parsing with pymupdf4llm
        # For now, return basic metadata
        return {
            'url': url,
            'title': Path(urlparse(url).path).stem,
            'document_type': 'unknown',
            'product_family': 'TDA4',
            'content': '',  # Will be filled by PDF parser
            'content_type': 'application/pdf'
        }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from HTML"""
        # Try h1 first
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)

        # Try title tag
        title = soup.find('title')
        if title:
            return title.get_text(strip=True)

        return "Untitled"

    def _extract_document_type(self, url: str, title: str) -> str:
        """Extract document type from URL or title"""
        url_lower = url.lower()
        title_lower = title.lower()

        if 'datasheet' in url_lower or 'datasheet' in title_lower:
            return 'datasheet'
        elif 'user' in url_lower and 'guide' in url_lower:
            return 'user_guide'
        elif 'application' in url_lower or 'app note' in title_lower:
            return 'app_note'
        elif 'reference' in url_lower or 'design' in url_lower:
            return 'reference_design'
        else:
            return 'document'

    def _extract_product_family(self, url: str, title: str) -> str:
        """Extract product family from URL or title"""
        # Simple heuristic - look for family names
        families = ['TDA4', 'TDA4VP', 'TDA4VM', 'AM68', 'AM62', 'AM69',
                   'Jacinto', 'J721S2', 'J721E', 'J720']

        url_lower = url.lower()
        title_lower = title.lower()

        for family in families:
            if family.lower() in url_lower or family.lower() in title_lower:
                return family

        return 'TDA4'  # Default


def normalize_text(text: str) -> str:
    """
    Clean and normalize text content.

    Args:
        text: Text to normalize

    Returns:
        Normalized text
    """
    # Remove extra whitespace
    text = ' '.join(text.split())

    # Remove non-printable characters
    text = ''.join(c for c in text if c.isprintable() or c in '\n\r\t')

    return text


def deduplicate_by_url(documents: List[Dict]) -> List[Dict]:
    """
    Deduplicate documents by URL.

    Args:
        documents: List of documents

    Returns:
        Deduplicated list
    """
    seen = set()
    deduplicated = []

    for doc in documents:
        url = doc['url']
        if url not in seen:
            seen.add(url)
            deduplicated.append(doc)

    print(f"Deduplicated: {len(documents)} -> {len(deduplicated)} documents")
    return deduplicated
