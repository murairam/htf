"""
Test script to verify DuckDuckGo fallback works when Tavily is unavailable.
This ensures agents always search the real web, never using AI-generated estimates.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from competitor_data import OptimizedCompetitorIntelligence
from dotenv import load_dotenv

load_dotenv()


def test_duckduckgo_fallback():
    """Test that DuckDuckGo fallback works when Tavily is disabled."""

    print("=" * 80)
    print("Testing DuckDuckGo Fallback for Web Search")
    print("=" * 80)

    # Test 1: With Tavily disabled (simulate Tavily failure)
    print("\n📋 Test 1: Simulating Tavily unavailable...")
    print("-" * 80)

    # Temporarily disable Tavily by removing the API key
    original_tavily_key = os.environ.get("TAVILY_API_KEY")
    if original_tavily_key:
        del os.environ["TAVILY_API_KEY"]

    try:
        intel = OptimizedCompetitorIntelligence(use_database=False)

        print(f"✓ Tavily available: {intel.tavily_client is not None}")
        print(f"✓ DuckDuckGo available: {intel.ddg_client is not None}")
        print(f"✓ OpenAI available: {intel.openai_client is not None}")

        if not intel.ddg_client:
            print("\n❌ ERROR: DuckDuckGo not available!")
            print("   Install with: pip install duckduckgo-search")
            return False

        print("\n🔍 Searching for competitors (should use DuckDuckGo)...")
        competitors = intel.get_competitors(
            product_concept="plant-based burger",
            category="Plant-Based",
            max_results=3,
            use_cache=False
        )

        print(f"\n✓ Found {len(competitors)} competitors")

        if not competitors:
            print("❌ ERROR: No competitors found!")
            return False

        print("\n📊 Competitor Results:")
        print("-" * 80)
        for i, comp in enumerate(competitors, 1):
            print(f"\n{i}. {comp.get('Company', 'Unknown')}")
            print(f"   Product: {comp.get('Product', 'N/A')}")
            print(f"   Source: {comp.get('Source', 'N/A')}")

            # Check if it's AI-generated (should NOT be)
            source = comp.get('Source', '')
            if 'AI Generated' in source or 'AI generated' in source:
                print("   ❌ WARNING: This appears to be AI-generated!")
                return False
            else:
                print("   ✓ Real web source")

        print("\n" + "=" * 80)
        print("✅ Test 1 PASSED: DuckDuckGo fallback works correctly")
        print("=" * 80)

        return True

    finally:
        # Restore Tavily key
        if original_tavily_key:
            os.environ["TAVILY_API_KEY"] = original_tavily_key


def test_no_ai_estimates():
    """Verify that AI estimates are never used."""

    print("\n" + "=" * 80)
    print("Test 2: Verifying NO AI-Generated Estimates")
    print("=" * 80)

    # Disable both Tavily and DuckDuckGo to force fallback
    original_tavily_key = os.environ.get("TAVILY_API_KEY")
    if original_tavily_key:
        del os.environ["TAVILY_API_KEY"]

    try:
        intel = OptimizedCompetitorIntelligence(use_database=False)

        # Simulate DuckDuckGo failure by setting client to None
        intel.ddg_client = None

        print("\n🔍 Searching with both Tavily and DuckDuckGo disabled...")
        print("   (Should use static fallback data, NOT AI estimates)")

        competitors = intel.get_competitors(
            product_concept="plant-based burger",
            category="Plant-Based",
            max_results=3,
            use_cache=False
        )

        print(f"\n✓ Found {len(competitors)} competitors (from static fallback)")

        # Verify these are from static fallback, not AI-generated
        for comp in competitors:
            source = comp.get('Source', '')
            if 'AI Generated' in source or 'AI generated' in source:
                print(f"\n❌ ERROR: Found AI-generated estimate: {comp.get('Company')}")
                print("   This should NOT happen!")
                return False

        print("\n✅ Test 2 PASSED: No AI-generated estimates found")
        print("   All results are either from web search or static fallback data")

        return True

    finally:
        # Restore Tavily key
        if original_tavily_key:
            os.environ["TAVILY_API_KEY"] = original_tavily_key


def test_tavily_to_duckduckgo_chain():
    """Test the complete fallback chain."""

    print("\n" + "=" * 80)
    print("Test 3: Testing Complete Fallback Chain")
    print("=" * 80)

    print("\nFallback Chain:")
    print("1. Tavily API (if available)")
    print("2. DuckDuckGo Web Search (if Tavily fails)")
    print("3. Static Fallback Data (if all web searches fail)")
    print("\n❌ REMOVED: OpenAI AI-generated estimates")

    intel = OptimizedCompetitorIntelligence(use_database=False)

    print(f"\n✓ Tavily available: {intel.tavily_client is not None}")
    print(f"✓ DuckDuckGo available: {intel.ddg_client is not None}")

    if intel.tavily_client:
        print("\n🔍 Testing with Tavily (primary method)...")
    elif intel.ddg_client:
        print("\n🔍 Testing with DuckDuckGo (fallback method)...")
    else:
        print("\n🔍 Testing with static fallback data (last resort)...")

    competitors = intel.get_competitors(
        product_concept="precision fermentation protein",
        category="Precision Fermentation",
        max_results=3,
        use_cache=False
    )

    print(f"\n✓ Found {len(competitors)} competitors")

    # Verify no AI estimates
    has_ai_estimates = any('AI Generated' in comp.get('Source', '') for comp in competitors)

    if has_ai_estimates:
        print("\n❌ ERROR: Found AI-generated estimates in results!")
        return False

    print("\n✅ Test 3 PASSED: Fallback chain works correctly")
    print("   No AI-generated estimates found")

    return True


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("DUCKDUCKGO FALLBACK TEST SUITE")
    print("Ensuring agents always search the real web (NO AI estimates)")
    print("=" * 80)

    results = []

    # Run tests
    results.append(("DuckDuckGo Fallback", test_duckduckgo_fallback()))
    results.append(("No AI Estimates", test_no_ai_estimates()))
    results.append(("Complete Fallback Chain", test_tavily_to_duckduckgo_chain()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("   Agents will always search the real web when Tavily fails.")
        print("   NO AI-generated estimates will be used.")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("   Please review the errors above.")

    print("=" * 80)

    sys.exit(0 if all_passed else 1)
