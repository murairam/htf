#!/usr/bin/env python3
"""
Test script for Weaviate-based RAG engine
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rag_engine_weaviate import WeaviateRAGEngine

def main():
    print("=" * 60)
    print("Testing Weaviate RAG Engine")
    print("=" * 60)
    
    # Check environment variables
    print("\n1. Checking environment variables...")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    weaviate_url = os.getenv("WEAVIATE_URL")
    weaviate_key = os.getenv("WEAVIATE_API_KEY")
    
    if not openai_key:
        print("❌ OPENAI_API_KEY not set")
        print("\nSet it with:")
        print("  export OPENAI_API_KEY='your-key'")
        return False
    else:
        print(f"✓ OPENAI_API_KEY: {openai_key[:8]}...")
    
    if not weaviate_url:
        print("❌ WEAVIATE_URL not set")
        print("\nGet a free cluster at: https://console.weaviate.cloud")
        print("Then set it with:")
        print("  export WEAVIATE_URL='https://your-cluster.weaviate.network'")
        return False
    else:
        print(f"✓ WEAVIATE_URL: {weaviate_url}")
    
    if not weaviate_key:
        print("⚠️  WEAVIATE_API_KEY not set (optional for some clusters)")
    else:
        print(f"✓ WEAVIATE_API_KEY: {weaviate_key[:8]}...")
    
    # Initialize engine
    print("\n2. Initializing WeaviateRAGEngine...")
    data_dir = Path(__file__).parent / "data"
    
    if not data_dir.exists():
        print(f"❌ Error: Data directory not found: {data_dir}")
        return False
    
    # Count PDFs
    pdf_files = list(data_dir.glob("*.pdf"))
    print(f"   Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        size_mb = pdf.stat().st_size / (1024 * 1024)
        print(f"   - {pdf.name} ({size_mb:.1f} MB)")
    
    try:
        engine = WeaviateRAGEngine(data_dir=str(data_dir))
        print("   ✓ Engine initialized")
        
        # Try to build/load index
        print("\n3. Building/loading index from Weaviate...")
        print("   (First time: 5-10 min with rate limiting)")
        print("   (Subsequent: <1 second from Weaviate)")
        print()
        
        success = engine.initialize_index(force_reload=False)
        
        if success:
            print("\n✅ SUCCESS! Index ready")
            
            # Test a simple query
            print("\n4. Testing query...")
            answer, citations = engine.get_cited_answer(
                "What are the main factors affecting consumer acceptance of plant-based meat?"
            )
            
            print(f"\n   Answer: {answer[:200]}...")
            print(f"   Citations: {len(citations)} sources found")
            
            print("\n" + "=" * 60)
            print("✅ Weaviate setup working perfectly!")
            print("=" * 60)
            print("\n💡 Next time you run this, it will load instantly!")
            print("💡 No more rate limit issues!")
            
            return True
        else:
            print("\n❌ Failed to build/load index")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        
        if "weaviate" in str(e).lower():
            print("\n💡 Tip: Make sure weaviate-client is installed:")
            print("   pip install weaviate-client")
        
        if "WEAVIATE_URL" in str(e):
            print("\n💡 Tip: Set up Weaviate Cloud:")
            print("   1. Go to https://console.weaviate.cloud")
            print("   2. Create free sandbox cluster")
            print("   3. Copy cluster URL and API key")
            print("   4. Set environment variables")
        
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
