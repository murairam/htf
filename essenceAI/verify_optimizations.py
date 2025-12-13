#!/usr/bin/env python3
"""
Verification Script for Optimizations
Tests that all critical fixes are working correctly
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """Test that optimized modules can be imported."""
    print("🔍 Testing imports...")
    try:
        from competitor_data import OptimizedCompetitorIntelligence
        print("  ✓ OptimizedCompetitorIntelligence imported")

        from rag_engine import OptimizedRAGEngine
        print("  ✓ OptimizedRAGEngine imported")

        from database import EssenceAIDatabase
        print("  ✓ EssenceAIDatabase imported")

        from logger import get_logger
        print("  ✓ Logger imported")

        print("✅ All optimized modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_indexes():
    """Test that database indexes exist."""
    print("\n🔍 Testing database indexes...")
    try:
        from database import EssenceAIDatabase
        import sqlite3

        db = EssenceAIDatabase("test_verify.db")
        conn = db.conn
        cursor = conn.cursor()

        # Get list of indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]

        expected_indexes = [
            'idx_competitors_category',
            'idx_competitors_last_updated',
            'idx_analysis_cache_category_created',
            'idx_analysis_cache_created_at',
            'idx_product_urls_created_at'
        ]

        missing = [idx for idx in expected_indexes if idx not in indexes]

        if missing:
            print(f"❌ Missing indexes: {missing}")
            db.close()
            Path("test_verify.db").unlink(missing_ok=True)
            return False

        print(f"✅ All {len(expected_indexes)} indexes created successfully")
        db.close()
        Path("test_verify.db").unlink(missing_ok=True)
        return True

    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def test_context_manager():
    """Test that database context manager works."""
    print("\n🔍 Testing database context manager...")
    try:
        from database import EssenceAIDatabase

        # Test context manager
        with EssenceAIDatabase("test_context.db") as db:
            stats = db.get_stats()
            assert isinstance(stats, dict)

        # Verify connection is closed
        assert db.conn is None, "Connection should be None after context exit"

        print("✅ Context manager working correctly")
        Path("test_context.db").unlink(missing_ok=True)
        return True

    except Exception as e:
        print(f"❌ Context manager test error: {e}")
        return False

def test_logging():
    """Test that logging framework works."""
    print("\n🔍 Testing logging framework...")
    try:
        from logger import get_logger
        import logging

        logger = get_logger("test_logger")

        # Test different log levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        # Verify logger has handlers
        assert len(logger.handlers) > 0, "Logger should have handlers"

        print("✅ Logging framework working correctly")
        return True

    except Exception as e:
        print(f"❌ Logging test error: {e}")
        return False

def test_fallback_data():
    """Test that fallback data is optimized."""
    print("\n🔍 Testing fallback data optimization...")
    try:
        from competitor_data import OptimizedCompetitorIntelligence

        comp_intel = OptimizedCompetitorIntelligence("test_fallback.db")

        # Verify FALLBACK_DATA is a class variable (dict)
        assert hasattr(comp_intel, 'FALLBACK_DATA'), "Should have FALLBACK_DATA"
        assert isinstance(comp_intel.FALLBACK_DATA, dict), "FALLBACK_DATA should be dict"

        # Test O(1) lookup
        data = comp_intel._get_fallback_data("Plant-Based", 3)
        assert len(data) <= 3, "Should return max_results items"
        assert isinstance(data, list), "Should return list"

        print("✅ Fallback data optimized (O(1) lookup)")
        Path("test_fallback.db").unlink(missing_ok=True)
        return True

    except Exception as e:
        print(f"❌ Fallback data test error: {e}")
        return False

def test_exception_handling():
    """Test that specific exceptions are used."""
    print("\n🔍 Testing exception handling...")
    try:
        from competitor_data import OptimizedCompetitorIntelligence
        import inspect

        # Get source code
        source = inspect.getsource(OptimizedCompetitorIntelligence)

        # Check for specific exceptions (not bare except)
        specific_exceptions = [
            'json.JSONDecodeError',
            'ConnectionError',
            'TimeoutError',
            'ValueError',
            'TypeError'
        ]

        found = sum(1 for exc in specific_exceptions if exc in source)

        if found < 3:
            print(f"⚠️  Only found {found} specific exception types")
            return False

        print(f"✅ Using specific exception handling ({found} types found)")
        return True

    except Exception as e:
        print(f"❌ Exception handling test error: {e}")
        return False

def main():
    """Run all verification tests."""
    print("=" * 60)
    print("🚀 OPTIMIZATION VERIFICATION SUITE")
    print("=" * 60)

    tests = [
        ("Module Imports", test_imports),
        ("Database Indexes", test_database_indexes),
        ("Context Manager", test_context_manager),
        ("Logging Framework", test_logging),
        ("Fallback Data", test_fallback_data),
        ("Exception Handling", test_exception_handling),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\n🎯 Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All optimizations verified successfully!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
