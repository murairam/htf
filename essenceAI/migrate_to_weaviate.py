#!/usr/bin/env python3
"""
Migrate existing local vector index to Weaviate Cloud
This is a ONE-TIME script to upload your embeddings
"""

import sys
from pathlib import Path
sys.path.append('src')

from rag_engine_weaviate import WeaviateRAGEngine
import time

def main():
    print("=" * 70)
    print("  Migrating to Weaviate Cloud")
    print("=" * 70)
    print()
    print("This will:")
    print("  1. Connect to your Weaviate cluster")
    print("  2. Upload embeddings from your PDFs")
    print("  3. Store them in the cloud (one-time cost)")
    print()
    print("⏱️  Estimated time: 5-10 minutes (with rate limiting)")
    print("💰 Cost: ~$0.003 (one-time, for embeddings)")
    print()

    input("Press Enter to continue or Ctrl+C to cancel... ")
    print()

    try:
        print("🚀 Step 1/3: Connecting to Weaviate...")
        engine = WeaviateRAGEngine(data_dir='data')
        print("   ✓ Connected successfully")
        print()

        print("📤 Step 2/3: Uploading embeddings...")
        print("   (This may take several minutes due to rate limiting)")
        start_time = time.time()

        result = engine.initialize_index(force_reload=True)

        elapsed = time.time() - start_time
        print(f"   ✓ Upload complete in {elapsed:.1f} seconds")
        print()

        print("🔍 Step 3/3: Testing query...")
        answer, citations = engine.get_cited_answer("What are acceptance factors for plant-based meat?")
        print(f"   ✓ Query successful")
        print(f"   ✓ Answer length: {len(answer)} chars")
        print(f"   ✓ Citations: {len(citations)}")
        print()

        print("=" * 70)
        print("  ✅ Migration Complete!")
        print("=" * 70)
        print()
        print("Your embeddings are now stored in Weaviate Cloud!")
        print()
        print("Benefits:")
        print("  ✓ Instant loading (no more rebuilding)")
        print("  ✓ No rate limits (embeddings already created)")
        print("  ✓ Cloud accessible (work from anywhere)")
        print()
        print("Next steps:")
        print("  1. Test: python3 test_research.py")
        print("  2. Update agents to use Weaviate (optional)")
        print()

        return True

    except Exception as e:
        print()
        print("=" * 70)
        print("  ❌ Migration Failed")
        print("=" * 70)
        print()
        print(f"Error: {str(e)}")
        print()
        print("Troubleshooting:")
        print("  1. Check WEAVIATE_URL in .env (should start with https://)")
        print("  2. Check WEAVIATE_API_KEY in .env")
        print("  3. Verify cluster is running in Weaviate console")
        print()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
