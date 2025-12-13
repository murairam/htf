#!/usr/bin/env python3
"""
Test script to verify the RAG engine rate limit fix
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rag_engine_optimized import OptimizedRAGEngine

def main():
    print("=" * 60)
    print("Testing Optimized RAG Engine with Rate Limit Handling")
    print("=" * 60)
    
    # Initialize engine
    print("\n1. Initializing OptimizedRAGEngine...")
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
        engine = OptimizedRAGEngine(data_dir=str(data_dir))
        print("   ✓ Engine initialized")
        
        # Try to build index
        print("\n2. Building index (this may take a few minutes)...")
        print("   Using text-embedding-3-small model")
        print("   Chunk size: 400 tokens")
        print("   Batch size: 10")
        
        success = engine.initialize_index(force_reload=True)
        
        if success:
            print("\n✅ SUCCESS! Index built without rate limit errors")
            
            # Test a simple query
            print("\n3. Testing query...")
            answer, citations = engine.get_cited_answer(
                "What are the main factors affecting consumer acceptance of plant-based meat?"
            )
            
            print(f"\n   Answer: {answer[:200]}...")
            print(f"   Citations: {len(citations)} sources found")
            
            return True
        else:
            print("\n❌ Failed to build index")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
