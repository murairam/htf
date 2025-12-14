"""
Test script for competitor data completeness fix
Tests the improved extraction and validation logic
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from competitor_data import OptimizedCompetitorIntelligence
import json

def test_competitor_extraction():
    """Test competitor data extraction with various scenarios"""

    print("=" * 80)
    print("TESTING COMPETITOR DATA EXTRACTION FIX")
    print("=" * 80)

    # Initialize without database for fresh results
    comp_intel = OptimizedCompetitorIntelligence(use_database=False)

    # Test cases
    test_cases = [
        {
            "name": "Plant-Based Cheese",
            "product": "Plant-based artisan cheese for European market",
            "category": "Plant-Based",
            "max_results": 5
        },
        {
            "name": "Precision Fermentation Protein",
            "product": "Precision fermented whey protein for food manufacturers",
            "category": "Precision Fermentation",
            "max_results": 5
        },
        {
            "name": "General Sustainable Food",
            "product": "Sustainable food alternatives",
            "category": None,
            "max_results": 5
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST CASE {i}: {test_case['name']}")
        print(f"{'=' * 80}")
        print(f"Product: {test_case['product']}")
        print(f"Category: {test_case['category']}")
        print(f"Max Results: {test_case['max_results']}")
        print()

        try:
            # Get competitors
            competitors = comp_intel.get_competitors(
                product_concept=test_case['product'],
                category=test_case['category'],
                max_results=test_case['max_results'],
                use_cache=False
            )

            if not competitors:
                print("❌ No competitors found!")
                continue

            print(f"✅ Found {len(competitors)} competitors\n")

            # Analyze data completeness
            total = len(competitors)
            has_company = sum(1 for c in competitors if c.get('Company') and c['Company'] != 'Unknown')
            has_product = sum(1 for c in competitors if c.get('Product') and c['Product'] not in ['N/A', 'See source for details', 'See source for product details'])
            has_price = sum(1 for c in competitors if c.get('Price (€/kg)') is not None)
            has_co2 = sum(1 for c in competitors if c.get('CO₂ (kg)') is not None)
            has_claim = sum(1 for c in competitors if c.get('Marketing Claim') and c['Marketing Claim'] not in ['N/A', 'Visit source for details'])
            has_source = sum(1 for c in competitors if c.get('Source') and c['Source'] != 'N/A')

            print("DATA COMPLETENESS:")
            print(f"  Company Names:    {has_company}/{total} ({has_company/total*100:.1f}%)")
            print(f"  Product Info:     {has_product}/{total} ({has_product/total*100:.1f}%)")
            print(f"  Price Data:       {has_price}/{total} ({has_price/total*100:.1f}%)")
            print(f"  CO₂ Data:         {has_co2}/{total} ({has_co2/total*100:.1f}%)")
            print(f"  Marketing Claims: {has_claim}/{total} ({has_claim/total*100:.1f}%)")
            print(f"  Source URLs:      {has_source}/{total} ({has_source/total*100:.1f}%)")

            # Display competitors
            print("\nCOMPETITOR DETAILS:")
            print("-" * 80)
            for j, comp in enumerate(competitors, 1):
                print(f"\n{j}. {comp.get('Company', 'Unknown')}")
                print(f"   Product: {comp.get('Product', 'N/A')}")
                print(f"   Price: €{comp.get('Price (€/kg)', 'N/A')}/kg" if comp.get('Price (€/kg)') else "   Price: N/A")
                print(f"   CO₂: {comp.get('CO₂ (kg)', 'N/A')} kg" if comp.get('CO₂ (kg)') else "   CO₂: N/A")
                print(f"   Claim: {comp.get('Marketing Claim', 'N/A')[:80]}...")
                print(f"   Source: {comp.get('Source', 'N/A')[:60]}...")

            # Quality assessment
            print("\n" + "=" * 80)
            print("QUALITY ASSESSMENT:")

            if has_company == total and has_source == total:
                print("✅ All competitors have company names and sources")
            else:
                print(f"⚠️  Some competitors missing basic info")

            if has_price >= total * 0.5:
                print(f"✅ Good price data coverage ({has_price/total*100:.0f}%)")
            elif has_price > 0:
                print(f"⚠️  Limited price data ({has_price/total*100:.0f}%)")
            else:
                print("❌ No price data available")

            if has_co2 >= total * 0.5:
                print(f"✅ Good CO₂ data coverage ({has_co2/total*100:.0f}%)")
            elif has_co2 > 0:
                print(f"⚠️  Limited CO₂ data ({has_co2/total*100:.0f}%)")
            else:
                print("❌ No CO₂ data available")

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

    # Print statistics
    print("\n" + "=" * 80)
    print("OVERALL STATISTICS:")
    print("=" * 80)
    stats = comp_intel.get_stats()
    print(f"API Calls Made: {stats['api_calls_made']}")
    print(f"Cache Hits: {stats['cache_hits']}")
    print(f"Tavily Available: {stats['tavily_available']}")
    print(f"DuckDuckGo Available: {stats['duckduckgo_available']}")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_competitor_extraction()
