"""
Unit tests for database module
"""

import pytest
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database import EssenceAIDatabase


@pytest.fixture
def test_db():
    """Create a test database"""
    db_path = "test_essenceai.db"
    db = EssenceAIDatabase(db_path)
    yield db
    # Cleanup
    db.close()
    if os.path.exists(db_path):
        os.remove(db_path)


def test_database_initialization(test_db):
    """Test database tables are created"""
    stats = test_db.get_stats()
    assert 'total_competitors' in stats
    assert 'cached_analyses' in stats
    assert 'product_urls' in stats


def test_add_competitor(test_db):
    """Test adding competitor data"""
    competitor = {
        'company_name': 'Test Company',
        'category': 'Plant-Based',
        'product_type': 'Test Product',
        'price_per_kg': 25.50,
        'co2_emission': 2.3,
        'marketing_claim': 'Test Claim',
        'source_url': 'https://test.com'
    }

    row_id = test_db.add_competitor(competitor)
    assert row_id > 0

    # Verify it was added
    competitors = test_db.get_competitors('Plant-Based', limit=10)
    assert len(competitors) == 1
    assert competitors[0]['company_name'] == 'Test Company'


def test_get_competitors_by_category(test_db):
    """Test retrieving competitors by category"""
    # Add multiple competitors
    for i in range(3):
        test_db.add_competitor({
            'company_name': f'Company {i}',
            'category': 'Plant-Based',
            'product_type': f'Product {i}',
            'price_per_kg': 20.0 + i,
            'co2_emission': 2.0 + i * 0.1,
            'marketing_claim': f'Claim {i}'
        })

    competitors = test_db.get_competitors('Plant-Based', limit=10)
    assert len(competitors) == 3


def test_cache_analysis(test_db):
    """Test caching analysis results"""
    result = {
        'competitors': ['Company A', 'Company B'],
        'strategy': 'Test strategy'
    }

    test_db.cache_analysis(
        product_concept='Test Product',
        category='Plant-Based',
        segment='Skeptic',
        result=result
    )

    # Retrieve cached result
    cached = test_db.get_cached_analysis(
        product_concept='Test Product',
        category='Plant-Based',
        segment='Skeptic',
        max_age_hours=24
    )

    assert cached is not None
    assert cached['strategy'] == 'Test strategy'


def test_cache_expiration(test_db):
    """Test that old cache is not returned"""
    result = {'test': 'data'}

    test_db.cache_analysis(
        product_concept='Old Product',
        category='Plant-Based',
        segment='Skeptic',
        result=result
    )

    # Try to get with 0 hour max age (should not return)
    cached = test_db.get_cached_analysis(
        product_concept='Old Product',
        category='Plant-Based',
        segment='Skeptic',
        max_age_hours=0
    )

    assert cached is None


def test_add_product_url(test_db):
    """Test storing product URL data"""
    parsed_data = {
        'product_name': 'Test Product',
        'brand': 'Test Brand',
        'category': 'Plant-Based',
        'price': 4.99
    }

    row_id = test_db.add_product_url(
        url='https://test.com/product',
        parsed_data=parsed_data
    )

    assert row_id > 0

    # Retrieve it
    product = test_db.get_product_by_url('https://test.com/product')
    assert product is not None
    assert product['product_name'] == 'Test Product'
    assert product['parsed_data']['brand'] == 'Test Brand'


def test_database_stats(test_db):
    """Test getting database statistics"""
    # Add some data
    test_db.add_competitor({
        'company_name': 'Test',
        'category': 'Plant-Based',
        'price_per_kg': 25.0,
        'co2_emission': 2.0
    })

    test_db.cache_analysis('Product', 'Plant-Based', 'Skeptic', {'test': 'data'})

    stats = test_db.get_stats()
    assert stats['total_competitors'] >= 1
    assert stats['cached_analyses'] >= 1


def test_clear_old_cache(test_db):
    """Test clearing old cache entries"""
    # Add some cache entries
    for i in range(5):
        test_db.cache_analysis(
            f'Product {i}',
            'Plant-Based',
            'Skeptic',
            {'data': i}
        )

    stats_before = test_db.get_stats()

    # Clear cache older than 7 days (should not delete anything recent)
    test_db.clear_old_cache(days=7)

    stats_after = test_db.get_stats()
    assert stats_after['cached_analyses'] == stats_before['cached_analyses']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
