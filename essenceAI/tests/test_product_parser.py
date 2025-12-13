"""
Unit tests for product URL parser
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from product_parser import ProductParser


@pytest.fixture
def parser():
    """Create a product parser instance"""
    return ProductParser()


def test_detect_category_plant_based(parser):
    """Test category detection for plant-based products"""
    text = "vegan burger plant-based meat alternative"
    category = parser._detect_category("", text)
    assert category == "Plant-Based"


def test_detect_category_fermentation(parser):
    """Test category detection for precision fermentation"""
    text = "precision fermented cheese biotech dairy"
    category = parser._detect_category("", text)
    assert category == "Precision Fermentation"


def test_detect_category_algae(parser):
    """Test category detection for algae products"""
    text = "spirulina algae protein powder"
    category = parser._detect_category("", text)
    assert category == "Algae"


def test_fallback_parse(parser):
    """Test fallback parsing when URL fetch fails"""
    url = "https://example.com/products/vegan-burger-deluxe"
    result = parser._fallback_parse(url)

    assert result['url'] == url
    assert 'Vegan Burger Deluxe' in result['product_name']
    assert result['parsing_method'] == 'fallback'


def test_extract_between(parser):
    """Test text extraction helper"""
    text = "<title>Test Product | Store</title>"
    result = parser._extract_between(text, "<title>", "</title>")
    assert result == "Test Product | Store"

    # Test when markers not found
    result = parser._extract_between(text, "<notfound>", "</notfound>")
    assert result is None


def test_create_product_concept(parser):
    """Test creating product concept from parsed data"""
    parsed_data = {
        'product_name': 'Vegan Burger',
        'brand': 'Beyond Meat',
        'category': 'Plant-Based',
        'price': 5.99,
        'retailer': 'Carrefour'
    }

    concept = parser.create_product_concept(parsed_data)

    assert 'Vegan Burger' in concept
    assert 'Beyond Meat' in concept
    assert 'Plant-Based' in concept
    assert '€5.99' in concept
    assert 'Carrefour' in concept


def test_create_product_concept_minimal(parser):
    """Test creating concept with minimal data"""
    parsed_data = {
        'product_name': 'Test Product'
    }

    concept = parser.create_product_concept(parsed_data)
    assert 'Test Product' in concept


def test_parse_url_structure(parser):
    """Test that parse_url returns correct structure"""
    # This will use fallback since we can't actually fetch
    url = "https://www.carrefour.fr/p/steak-vegetal-test"
    result = parser.parse_url(url)

    assert 'url' in result
    assert 'product_name' in result
    assert 'retailer' in result
    assert 'category' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
