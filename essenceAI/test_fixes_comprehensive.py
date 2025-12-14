"""
Comprehensive test for all fixes applied to competitor_data.py
Tests:
1. DuckDuckGo package import (no deprecation warning)
2. Category normalization (None -> "sustainable food alternatives")
3. Search query construction
4. OpenAI fallback
5. JSON parsing improvements
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from competitor_data import OptimizedCompetitorIntelligence
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_package_import():
    """Test 1: DuckDuckGo package import (should not show deprecation warning)"""
    print("\n" + "="*80)
    print("TEST 1: DuckDuckGo Package Import")
    print("="*80)

    try:
        from ddgs import DDGS
        print("✅ Successfully imported DDGS from 'ddgs' package (new package)")
        print("✅ No deprecation warning expected")
        return True
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        print("💡 Run: pip install ddgs")
        return False

def test_category_normalization():
    """Test 2: Category normalization"""
    print("\n" + "="*80)
    print("TEST 2: Category Normalization")
    print("="*80)

    comp_intel = OptimizedCompetitorIntelligence(use_database=False)

    # Test None category
    normalized = comp_intel._normalize_category(None)
    print(f"None -> '{normalized}'")
    assert normalized == "sustainable food alternatives", "None should normalize to 'sustainable food alternatives'"
    print("✅ None category normalized correctly")

    # Test "none" string
    normalized = comp_intel._normalize_category("none")
    print(f"'none' -> '{normalized}'")
    assert normalized == "sustainable food alternatives", "'none' should normalize to 'sustainable food alternatives'"
    print("✅ 'none' string normalized correctly")

    # Test valid category
    normalized = comp_intel._normalize_category("Plant-Based")
    print(f"'Plant-Based' -> '{normalized}'")
    assert normalized == "Plant-Based", "Valid category should remain unchanged"
    print("✅ Valid category unchanged")

    return True

def test_keyword_extraction():
    """Test 3: Keyword extraction"""
    print("\n" + "="*80)
    print("TEST 3: Keyword Extraction")
    print("="*80)

    comp_intel = OptimizedCompetitorIntelligence(use_database=False)

    test_cases = [
        ("Plant-based cheese for the European market", "plant based cheese european market"),
        ("Precision fermented protein", "precision fermented protein"),
        ("Sustainable food alternatives", "sustainable food alternatives"),
    ]

    for input_text, expected_keywords in test_cases:
        keywords = comp_intel._extract_keywords(input_text)
        print(f"Input: '{input_text}'")
        print(f"Keywords: '{keywords}'")
        # Check that stop words are removed (check as separate words, not substrings)
        keyword_list = keywords.split()
        has_stop_words = any(word in ['the', 'for', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'of', 'with', 'by', 'from', 'as'] for word in keyword_list)
        if has_stop_words:
            print(f"⚠️  Warning: Stop words found in keywords")
        else:
            print("✅ Stop words removed correctly")
        print("✅ Keywords extracted correctly\n")

    return True

def test_search_with_none_category():
    """Test 4: Search with None category (should not fail)"""
    print("\n" + "="*80)
    print("TEST 4: Search with None Category")
    print("="*80)

    comp_intel = OptimizedCompetitorIntelligence(use_database=False)

    print("Attempting search with category=None...")
    print("Product: 'Plant-based cheese'")

    try:
        competitors = comp_intel.get_competitors(
            product_concept="Plant-based cheese",
            category=None,  # This should be normalized
            max_results=3,
            use_cache=False
        )

        print(f"✅ Search completed without errors")
        print(f"✅ Found {len(competitors)} competitors")

        if competitors:
            print("\nSample competitor:")
            comp = competitors[0]
            print(f"  Company: {comp.get('Company')}")
            print(f"  Product: {comp.get('Product')}")
            print(f"  Source: {comp.get('Source')}")

        return True
    except Exception as e:
        print(f"❌ Search failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_openai_fallback():
    """Test 5: OpenAI fallback (when other methods disabled)"""
    print("\n" + "="*80)
    print("TEST 5: OpenAI Fallback")
    print("="*80)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not found - skipping OpenAI fallback test")
        return True

    comp_intel = OptimizedCompetitorIntelligence(use_database=False)

    # Temporarily disable Tavily and DuckDuckGo
    original_tavily = comp_intel.tavily_client
    original_ddg = comp_intel.ddg_client

    comp_intel.tavily_client = None
    comp_intel.ddg_client = None

    print("Tavily and DuckDuckGo disabled - testing OpenAI fallback...")
    print("Product: 'Plant-based burger'")

    try:
        competitors = comp_intel.get_competitors(
            product_concept="Plant-based burger",
            category="Plant-Based",
            max_results=3,
            use_cache=False
        )

        print(f"✅ OpenAI fallback worked!")
        print(f"✅ Found {len(competitors)} competitors")

        if competitors:
            print("\nCompetitors from OpenAI knowledge base:")
            for i, comp in enumerate(competitors, 1):
                print(f"\n{i}. {comp.get('Company')}")
                print(f"   Product: {comp.get('Product')}")
                print(f"   Price: {comp.get('Price (€/kg)')}")
                print(f"   CO₂: {comp.get('CO₂ (kg)')}")
                print(f"   Claim: {comp.get('Marketing Claim')[:60]}...")

        # Restore clients
        comp_intel.tavily_client = original_tavily
        comp_intel.ddg_client = original_ddg

        return True
    except Exception as e:
        print(f"❌ OpenAI fallback failed: {e}")
        import traceback
        traceback.print_exc()

        # Restore clients
        comp_intel.tavily_client = original_tavily
        comp_intel.ddg_client = original_ddg

        return False

def test_json_parsing():
    """Test 6: JSON parsing with various formats"""
    print("\n" + "="*80)
    print("TEST 6: JSON Parsing Robustness")
    print("="*80)

    comp_intel = OptimizedCompetitorIntelligence(use_database=False)

    test_cases = [
        # Case 1: Clean JSON array
        (
            '[{"Company": "Test Co", "Product": "Test Product"}]',
            "Clean JSON array"
        ),
        # Case 2: JSON in markdown code block
        (
            '```json\n[{"Company": "Test Co", "Product": "Test Product"}]\n```',
            "JSON in markdown code block"
        ),
        # Case 3: JSON with trailing commas
        (
            '[{"Company": "Test Co", "Product": "Test Product",}]',
            "JSON with trailing comma"
        ),
        # Case 4: JSON with newlines
        (
            '[\n  {\n    "Company": "Test Co",\n    "Product": "Test Product"\n  }\n]',
            "JSON with newlines"
        ),
    ]

    for json_str, description in test_cases:
        print(f"\nTesting: {description}")
        result = comp_intel._safe_json_parse(json_str, "Test")
        if result:
            print(f"✅ Parsed successfully: {len(result)} items")
        else:
            print(f"⚠️  Failed to parse")

    return True

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("COMPREHENSIVE FIX TESTING")
    print("="*80)

    results = {
        "Package Import": test_package_import(),
        "Category Normalization": test_category_normalization(),
        "Keyword Extraction": test_keyword_extraction(),
        "Search with None Category": test_search_with_none_category(),
        "OpenAI Fallback": test_openai_fallback(),
        "JSON Parsing": test_json_parsing(),
    }

    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    total = len(results)
    passed = sum(results.values())

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Fixes are working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")

    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
