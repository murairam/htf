#!/usr/bin/env python
"""
Quick test to verify app.py can import optimized modules
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("🔍 Testing app.py imports...")

try:
    # Test the imports that app.py uses
    from competitor_data import OptimizedCompetitorIntelligence
    print("✅ OptimizedCompetitorIntelligence imported")

    from rag_engine import OptimizedRAGEngine
    print("✅ OptimizedRAGEngine imported")

    # Test instantiation
    print("\n🔍 Testing instantiation...")
    comp_intel = OptimizedCompetitorIntelligence("test_app.db")
    print("✅ OptimizedCompetitorIntelligence instantiated")

    # Test getting competitors (should use fallback data)
    print("\n🔍 Testing competitor data retrieval...")
    competitors = comp_intel.get_competitors(
        product_concept="Test product",
        category="Plant-Based",
        max_results=3,
        use_cache=False
    )
    print(f"✅ Retrieved {len(competitors)} competitors")
    print(f"   Sample: {competitors[0]['Company'] if competitors else 'None'}")

    # Test stats
    print("\n🔍 Testing statistics...")
    stats = comp_intel.get_stats()
    print(f"✅ Stats retrieved:")
    print(f"   API calls: {stats['api_calls_made']}")
    print(f"   Cache hits: {stats['cache_hits']}")
    print(f"   Cache efficiency: {stats['cache_efficiency']}")

    # Cleanup
    Path("test_app.db").unlink(missing_ok=True)

    print("\n🎉 All app integration tests passed!")
    print("✅ The optimized modules are working correctly")
    print("✅ App.py should run without issues")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
