"""
Product URL Parser
Extracts product information from e-commerce URLs (Carrefour, Amazon, etc.)
"""

import re
import requests
from typing import Dict, Optional
from urllib.parse import urlparse
import json


class ProductParser:
    """
    Parse product information from URLs.
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def parse_url(self, url: str) -> Dict:
        """
        Parse product URL and extract information.

        Args:
            url: Product URL

        Returns:
            Dictionary with product information
        """
        domain = urlparse(url).netloc.lower()

        # Detect retailer
        if 'carrefour' in domain:
            return self._parse_carrefour(url)
        elif 'amazon' in domain:
            return self._parse_amazon(url)
        elif any(x in domain for x in ['auchan', 'leclerc', 'intermarche']):
            return self._parse_generic(url)
        else:
            return self._parse_generic(url)

    def _parse_carrefour(self, url: str) -> Dict:
        """Parse Carrefour product page."""
        try:
            # Try to fetch the page
            response = requests.get(url, headers=self.headers, timeout=10)
            html = response.text

            # Extract product name from title or meta tags
            product_name = self._extract_between(html, '<title>', '</title>')
            if product_name:
                product_name = product_name.split('|')[0].strip()

            # Try to extract price
            price_match = re.search(r'€\s*(\d+[,.]?\d*)', html)
            price = float(price_match.group(1).replace(',', '.')) if price_match else None

            # Try to extract brand
            brand_match = re.search(r'"brand":\s*"([^"]+)"', html)
            brand = brand_match.group(1) if brand_match else None

            # Detect category from URL or content
            category = self._detect_category(url, html)

            return {
                'url': url,
                'retailer': 'Carrefour',
                'product_name': product_name or 'Unknown Product',
                'brand': brand,
                'price': price,
                'category': category,
                'raw_html_snippet': html[:500] if html else None
            }

        except Exception as e:
            print(f"⚠️ Could not parse Carrefour URL: {e}")
            return self._fallback_parse(url)

    def _parse_amazon(self, url: str) -> Dict:
        """Parse Amazon product page."""
        try:
            # Extract ASIN from URL
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
            asin = asin_match.group(1) if asin_match else None

            # Try to fetch page
            response = requests.get(url, headers=self.headers, timeout=10)
            html = response.text

            # Extract product title
            title_match = re.search(r'<span id="productTitle"[^>]*>([^<]+)</span>', html)
            product_name = title_match.group(1).strip() if title_match else None

            # Extract price
            price_match = re.search(r'€\s*(\d+[,.]?\d*)', html)
            price = float(price_match.group(1).replace(',', '.')) if price_match else None

            category = self._detect_category(url, html)

            return {
                'url': url,
                'retailer': 'Amazon',
                'product_name': product_name or 'Unknown Product',
                'asin': asin,
                'price': price,
                'category': category,
                'raw_html_snippet': html[:500] if html else None
            }

        except Exception as e:
            print(f"⚠️ Could not parse Amazon URL: {e}")
            return self._fallback_parse(url)

    def _parse_generic(self, url: str) -> Dict:
        """Generic parser for other retailers."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            html = response.text

            # Extract title
            product_name = self._extract_between(html, '<title>', '</title>')
            if product_name:
                product_name = product_name.split('|')[0].split('-')[0].strip()

            # Try to find price
            price_match = re.search(r'€\s*(\d+[,.]?\d*)', html)
            price = float(price_match.group(1).replace(',', '.')) if price_match else None

            category = self._detect_category(url, html)
            retailer = urlparse(url).netloc.split('.')[0].title()

            return {
                'url': url,
                'retailer': retailer,
                'product_name': product_name or 'Unknown Product',
                'price': price,
                'category': category,
                'raw_html_snippet': html[:500] if html else None
            }

        except Exception as e:
            print(f"⚠️ Could not parse URL: {e}")
            return self._fallback_parse(url)

    def _fallback_parse(self, url: str) -> Dict:
        """Fallback when parsing fails - extract from URL."""
        path = urlparse(url).path

        # Try to extract product name from URL path
        parts = [p for p in path.split('/') if p and not p.isdigit()]
        product_name = parts[-1].replace('-', ' ').replace('_', ' ').title() if parts else 'Unknown'

        return {
            'url': url,
            'retailer': urlparse(url).netloc,
            'product_name': product_name,
            'price': None,
            'category': self._detect_category(url, ''),
            'parsing_method': 'fallback'
        }

    def _detect_category(self, url: str, html: str) -> str:
        """
        Detect product category from URL and content.
        """
        text = (url + ' ' + html).lower()

        # Check for sustainable food categories
        if any(word in text for word in ['vegan', 'plant-based', 'vegetal', 'vegetarien']):
            return 'Plant-Based'
        elif any(word in text for word in ['ferment', 'precision', 'biotech']):
            return 'Precision Fermentation'
        elif any(word in text for word in ['algae', 'algue', 'spiruline', 'spirulina']):
            return 'Algae'
        elif any(word in text for word in ['cheese', 'fromage', 'dairy', 'lait']):
            return 'Dairy Alternative'
        elif any(word in text for word in ['burger', 'steak', 'meat', 'viande']):
            return 'Meat Alternative'
        else:
            return 'Other'

    def _extract_between(self, text: str, start: str, end: str) -> Optional[str]:
        """Extract text between two markers."""
        try:
            start_idx = text.find(start)
            if start_idx == -1:
                return None
            start_idx += len(start)
            end_idx = text.find(end, start_idx)
            if end_idx == -1:
                return None
            return text[start_idx:end_idx].strip()
        except:
            return None

    def create_product_concept(self, parsed_data: Dict) -> str:
        """
        Create a product concept description from parsed data.

        Args:
            parsed_data: Parsed product information

        Returns:
            Product concept string for analysis
        """
        parts = []

        if parsed_data.get('product_name'):
            parts.append(parsed_data['product_name'])

        if parsed_data.get('brand'):
            parts.append(f"by {parsed_data['brand']}")

        if parsed_data.get('category'):
            parts.append(f"({parsed_data['category']})")

        if parsed_data.get('price'):
            parts.append(f"- €{parsed_data['price']}")

        concept = ' '.join(parts)

        # Add context
        if parsed_data.get('retailer'):
            concept += f" | Available at {parsed_data['retailer']}"

        return concept


# Example usage
if __name__ == "__main__":
    parser = ProductParser()

    # Test with example URLs
    test_urls = [
        "https://www.carrefour.fr/p/steak-vegetal-3760074380145",
        "https://www.amazon.fr/dp/B08XYZ1234"
    ]

    for url in test_urls:
        print(f"\nParsing: {url}")
        result = parser.parse_url(url)
        print(json.dumps(result, indent=2))
