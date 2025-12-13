#!/usr/bin/env python3
"""
Upload PDFs to Weaviate Cloud (no prompts, automatic)
"""

import sys
from pathlib import Path
sys.path.append('src')

from rag_engine_weaviate import WeaviateRAGEngine
import time

print("=" * 70)
print("  Uploading PDFs to Weaviate Cloud")
print("=" * 70)
print()

try:
    print("🚀 Connecting to Weaviate...")
    with WeaviateRAGEngine(data_dir='data') as engine:
        print("   ✓ Connected")
        print()

        print("📤 Uploading embeddings (5-10 min due to rate limits)...")
        start_time = time.time()

        result = engine.initialize_index(force_reload=True)

        elapsed = time.time() - start_time
        print(f"   ✓ Complete in {elapsed:.1f}s")
        print()

        print("🔍 Testing query...")
        answer, citations = engine.get_cited_answer("What are acceptance factors for plant-based meat?")
        print(f"   ✓ Query works: {len(answer)} chars")
        print()

        print("=" * 70)
        print("  ✅ Success! Embeddings stored in Weaviate Cloud")
        print("=" * 70)

    print("🔌 Connection closed automatically")

except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
