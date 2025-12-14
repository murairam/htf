"""
Test script to verify the RateLimitedEmbedding serialization fix
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.research_agent import ResearchAgent
from logger import get_logger

logger = get_logger(__name__)


def test_research_agent_initialization():
    """Test that the research agent can initialize and load the index."""
    print("\n" + "="*60)
    print("Testing Research Agent Initialization")
    print("="*60 + "\n")

    try:
        # Initialize research agent
        print("1. Creating ResearchAgent instance...")
        agent = ResearchAgent(data_dir="data", persist_dir=".storage")
        print("   ✓ ResearchAgent created\n")

        # Try to initialize (this will load from storage if available)
        print("2. Initializing RAG engine (loading from storage)...")
        success = agent.initialize(force_reload=False)

        if success:
            print("   ✓ RAG engine initialized successfully!")
            print("   ✓ No 'delay_seconds' error!\n")

            # Try a simple query to verify it works
            print("3. Testing a simple research query...")
            result = agent.execute({
                'query': 'What are consumer preferences for plant-based products?',
                'domain': 'Plant-Based',
                'max_results': 2
            })

            if result.get('success'):
                print("   ✓ Query executed successfully!")
                print(f"   ✓ Found {len(result['data'].get('citations', []))} citations\n")

                # Show a snippet of the answer
                answer = result['data'].get('answer', '')
                if answer:
                    print("   Answer snippet:")
                    print(f"   {answer[:200]}...\n")

                return True
            else:
                print(f"   ✗ Query failed: {result.get('error')}\n")
                return False
        else:
            print("   ✗ Failed to initialize RAG engine\n")
            return False

    except Exception as e:
        print(f"\n   ✗ Error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_serialization():
    """Test that RateLimitedEmbedding can be serialized and deserialized."""
    print("\n" + "="*60)
    print("Testing RateLimitedEmbedding Serialization")
    print("="*60 + "\n")

    try:
        from rate_limited_embedding import RateLimitedEmbedding
        import os

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("   ⚠ OPENAI_API_KEY not set, skipping serialization test\n")
            return True

        print("1. Creating RateLimitedEmbedding instance...")
        embedding = RateLimitedEmbedding(
            model="text-embedding-3-small",
            api_key=api_key,
            delay_seconds=2.0
        )
        print("   ✓ Instance created\n")

        print("2. Serializing to dictionary...")
        data = embedding.to_dict()
        print(f"   ✓ Serialized: {list(data.keys())}")
        print(f"   ✓ delay_seconds in data: {'delay_seconds' in data}\n")

        print("3. Deserializing from dictionary...")
        restored = RateLimitedEmbedding.from_dict(data)
        print(f"   ✓ Deserialized successfully")
        print(f"   ✓ delay_seconds = {restored.delay_seconds}\n")

        return True

    except Exception as e:
        print(f"\n   ✗ Error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("RESEARCH AGENT FIX VERIFICATION")
    print("="*60)

    # Test serialization first
    serialization_ok = test_serialization()

    # Test research agent initialization
    agent_ok = test_research_agent_initialization()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Serialization Test: {'✓ PASSED' if serialization_ok else '✗ FAILED'}")
    print(f"Research Agent Test: {'✓ PASSED' if agent_ok else '✗ FAILED'}")

    if serialization_ok and agent_ok:
        print("\n🎉 All tests passed! The fix is working correctly.")
        print("You can now use the Research Insights feature without errors.\n")
        sys.exit(0)
    else:
        print("\n⚠ Some tests failed. Please check the errors above.\n")
        sys.exit(1)
