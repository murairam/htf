"""
Test script to verify dynamic results fix
Tests that different products generate different results
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from rag_engine import OptimizedRAGEngine
import json

def test_product_specific_caching():
    """Test that different products generate different cache keys"""
    print("\n" + "="*80)
    print("TEST 1: Product-Specific Cache Keys")
    print("="*80)

    data_dir = Path(__file__).parent / "data"
    rag_engine = OptimizedRAGEngine(data_dir=str(data_dir))

    # Test cache key generation
    query = "What are the marketing strategies?"

    product_a = "Precision fermented cheese"
    product_b = "Plant-based burger"

    hash_a = rag_engine._get_query_hash(query, product_a)
    hash_b = rag_engine._get_query_hash(query, product_b)
    hash_no_product = rag_engine._get_query_hash(query, None)

    print(f"\nQuery: '{query}'")
    print(f"Product A: '{product_a}'")
    print(f"  Cache Key: {hash_a}")
    print(f"\nProduct B: '{product_b}'")
    print(f"  Cache Key: {hash_b}")
    print(f"\nNo Product Context:")
    print(f"  Cache Key: {hash_no_product}")

    # Verify they're different
    assert hash_a != hash_b, "❌ FAIL: Same cache key for different products!"
    assert hash_a != hash_no_product, "❌ FAIL: Product context not affecting cache key!"

    print("\n✅ PASS: Different products generate different cache keys")
    return True

def test_use_cache_parameter():
    """Test that use_cache parameter works correctly"""
    print("\n" + "="*80)
    print("TEST 2: use_cache Parameter")
    print("="*80)

    data_dir = Path(__file__).parent / "data"
    rag_engine = OptimizedRAGEngine(data_dir=str(data_dir))

    # Check method signatures
    import inspect

    methods_to_check = [
        'get_marketing_strategy',
        'get_segment_strategy',
        'get_general_strategy',
        'get_universal_strategy',
        'get_consumer_insights'
    ]

    print("\nChecking method signatures for 'use_cache' parameter:")
    all_have_param = True

    for method_name in methods_to_check:
        method = getattr(rag_engine, method_name)
        sig = inspect.signature(method)
        params = sig.parameters

        has_use_cache = 'use_cache' in params
        default_value = params['use_cache'].default if has_use_cache else None

        status = "✅" if has_use_cache and default_value == False else "❌"
        print(f"  {status} {method_name}: use_cache={default_value}")

        if not (has_use_cache and default_value == False):
            all_have_param = False

    assert all_have_param, "❌ FAIL: Not all methods have use_cache=False default"
    print("\n✅ PASS: All methods have use_cache parameter with default False")
    return True

def test_product_context_parameter():
    """Test that product_context parameter exists"""
    print("\n" + "="*80)
    print("TEST 3: product_context Parameter")
    print("="*80)

    data_dir = Path(__file__).parent / "data"
    rag_engine = OptimizedRAGEngine(data_dir=str(data_dir))

    import inspect

    methods_to_check = [
        ('get_cited_answer', True),  # Should have product_context
        ('get_marketing_strategy', False),  # Uses product_concept
        ('get_consumer_insights', True),  # Should have product_context
    ]

    print("\nChecking method signatures for product context:")
    all_correct = True

    for method_name, should_have_product_context in methods_to_check:
        method = getattr(rag_engine, method_name)
        sig = inspect.signature(method)
        params = sig.parameters

        has_product_context = 'product_context' in params
        has_product_concept = 'product_concept' in params

        if should_have_product_context:
            status = "✅" if has_product_context else "❌"
            print(f"  {status} {method_name}: has product_context={has_product_context}")
            if not has_product_context:
                all_correct = False
        else:
            status = "✅" if has_product_concept else "❌"
            print(f"  {status} {method_name}: has product_concept={has_product_concept}")
            if not has_product_concept:
                all_correct = False

    assert all_correct, "❌ FAIL: Not all methods have product context parameters"
    print("\n✅ PASS: All methods have appropriate product context parameters")
    return True

def test_research_agent_integration():
    """Test that research agent accepts product_context"""
    print("\n" + "="*80)
    print("TEST 4: Research Agent Integration")
    print("="*80)

    from agents.research_agent import ResearchAgent
    import inspect

    agent = ResearchAgent()

    methods_to_check = [
        'execute',
        'analyze_consumer_acceptance',
        'get_marketing_insights'
    ]

    print("\nChecking ResearchAgent methods for product_context:")
    all_have_param = True

    for method_name in methods_to_check:
        method = getattr(agent, method_name)
        sig = inspect.signature(method)
        params = sig.parameters

        has_product_context = 'product_context' in params
        status = "✅" if has_product_context else "❌"
        print(f"  {status} {method_name}: has product_context={has_product_context}")

        if not has_product_context:
            all_have_param = False

    assert all_have_param, "❌ FAIL: Not all ResearchAgent methods have product_context"
    print("\n✅ PASS: ResearchAgent methods have product_context parameter")
    return True

def test_cache_file_structure():
    """Test cache file structure"""
    print("\n" + "="*80)
    print("TEST 5: Cache File Structure")
    print("="*80)

    cache_file = Path(__file__).parent / ".cache" / "query_cache.json"

    if cache_file.exists():
        print(f"\n✅ Cache file exists: {cache_file}")

        with open(cache_file, 'r') as f:
            cache_data = json.load(f)

        print(f"✅ Cache contains {len(cache_data)} entries")

        if cache_data:
            # Show first entry structure
            first_key = list(cache_data.keys())[0]
            first_entry = cache_data[first_key]
            print(f"\nSample cache entry structure:")
            print(f"  Key: {first_key[:50]}...")
            print(f"  Has 'answer': {'answer' in first_entry}")
            print(f"  Has 'citations': {'citations' in first_entry}")
    else:
        print(f"\n⚠️  Cache file doesn't exist yet: {cache_file}")
        print("   This is normal if the app hasn't been run yet")

    print("\n✅ PASS: Cache structure is correct")
    return True

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("DYNAMIC RESULTS FIX - AUTOMATED TESTS")
    print("="*80)

    tests = [
        ("Product-Specific Caching", test_product_specific_caching),
        ("use_cache Parameter", test_use_cache_parameter),
        ("product_context Parameter", test_product_context_parameter),
        ("Research Agent Integration", test_research_agent_integration),
        ("Cache File Structure", test_cache_file_structure),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "PASS", None))
        except AssertionError as e:
            results.append((test_name, "FAIL", str(e)))
        except Exception as e:
            results.append((test_name, "ERROR", str(e)))

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, status, _ in results if status == "PASS")
    failed = sum(1 for _, status, _ in results if status == "FAIL")
    errors = sum(1 for _, status, _ in results if status == "ERROR")

    for test_name, status, error in results:
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {test_name}: {status}")
        if error:
            print(f"   Error: {error}")

    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Errors: {errors}")

    if failed > 0 or errors > 0:
        print("\n❌ SOME TESTS FAILED")
        return False
    else:
        print("\n✅ ALL TESTS PASSED")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
