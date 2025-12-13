"""
Unit tests for competitor intelligence module
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from competitor_data import OptimizedCompetitorIntelligence


@pytest.fixture
def test_db_path():
    """Provide test database path"""
    db_path = "test_competitors.db"
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def intel(test_db_path):
    """Create intelligence instance with test database"""
    return OptimizedCompetitorIntelligence(db_path=test_db_path)


def test_initialization(intel):
    """Test that intelligence module initializes correctly"""
    assert intel.db is not None
    assert intel.api_calls_made == 0
    assert intel.cache_hits == 0


def test_fallback_data_structure(intel):
    """Test fallback data has correct structure"""
    data = intel._get_fallback_data("Plant-Based", 3)

    assert len(data) == 3
    assert all('Company' in item for item in data)
    assert all('Product' in item for item in data)
    assert all('Price (€/kg)' in item for item in data)
    assert all('CO₂ (kg)' in item for item in data)
    assert all('Marketing Claim' in item for item in data)


def test_fallback_data_categories(intel):
    """Test fallback data for all categories"""
    categories = ["Precision Fermentation", "Plant-Based", "Algae"]

    for category in categories:
        data = intel._get_fallback_data(category, 3)
        assert len(data) > 0
        assert len(data) <= 3


def test_format_competitors(intel):
    """Test formatting database rows to competitor format"""
    db_rows = [
        {
            'company_name': 'Test Company',
            'product_type': 'Test Product',
            'price_per_kg': 25.50,
            'co2_emission': 2.3,
            'marketing_claim': 'Test Claim'
        }
    ]

    formatted = intel._format_competitors(db_rows)

    assert len(formatted) == 1
    assert formatted[0]['Company'] == 'Test Company'
    assert formatted[0]['Product'] == 'Test Product'
    assert formatted[0]['Price (€/kg)'] == 25.50


def test_cache_competitors(intel):
    """Test caching competitor data"""
    competitors = [
        {
            'Company': 'Test Co',
            'Product': 'Test Product',
            'Price (€/kg)': 25.0,
            'CO₂ (kg)': 2.0,
            'Marketing Claim': 'Test'
        }
    ]

    intel._cache_competitors(competitors, 'Plant-Based')

    # Verify it was cached
    cached = intel.db.get_competitors('Plant-Based', limit=10)
    assert len(cached) >= 1


def test_get_competitors_with_cache(intel):
    """Test getting competitors uses cache"""
    # First call - should make API call (or use fallback)
    competitors1 = intel.get_competitors(
        product_concept="Test product",
        category="Plant-Based",
        max_results=3,
        use_cache=True
    )

    initial_api_calls = intel.api_calls_made

    # Second call - should use cache
    competitors2 = intel.get_competitors(
        product_concept="Test product",
        category="Plant-Based",
        max_results=3,
        use_cache=True
    )

    # API calls should not increase
    assert intel.api_calls_made == initial_api_calls
    assert intel.cache_hits > 0


def test_get_competitors_without_cache(intel):
    """Test getting competitors without cache"""
    competitors = intel.get_competitors(
        product_concept="Test product",
        category="Plant-Based",
        max_results=3,
        use_cache=False
    )

    assert len(competitors) > 0
    assert len(competitors) <= 3


def test_get_stats(intel):
    """Test getting usage statistics"""
    # Make some requests
    intel.get_competitors("Test", "Plant-Based", max_results=2)
    intel.get_competitors("Test", "Plant-Based", max_results=2)  # Should hit cache

    stats = intel.get_stats()

    assert 'api_calls_made' in stats
    assert 'cache_hits' in stats
    assert 'cache_efficiency' in stats
    assert 'total_competitors' in stats


def test_stats_calculation(intel):
    """Test cache efficiency calculation"""
    # Simulate some API calls and cache hits
    intel.api_calls_made = 2
    intel.cache_hits = 8

    stats = intel.get_stats()

    # 8 cache hits out of 10 total = 80% efficiency
    assert '80.0%' in stats['cache_efficiency']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
