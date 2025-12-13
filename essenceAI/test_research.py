import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

from agents import ResearchAgent

def test_research_agent():
    """Test research agent with API key."""
    print("\n" + "="*60)
    print("Testing Research Agent")
    print("="*60)

    try:
        agent = ResearchAgent(data_dir="data")
        print("✓ Research agent created")

        # Initialize
        print("\nInitializing research database...")
        if agent.initialize():
            print("✓ Research database initialized")

            # Test query
            result = agent.execute({
                'query': 'What are consumer acceptance factors for plant-based meat?',
                'domain': 'Plant-Based',
                'segment': 'High Essentialist'
            })

            if result['status'] == 'success':
                data = result['data']
                print(f"\n✓ Query executed successfully")
                print(f"  Citations: {len(data['citations'])}")
                print(f"  Answer preview: {data['answer'][:150]}...")

                if data['citations']:
                    print(f"\nFirst citation:")
                    citation = data['citations'][0]
                    print(f"  Source: {citation.get('source', 'N/A')}")
                    print(f"  Text: {citation.get('text', 'N/A')[:100]}...")
            else:
                print(f"✗ Query error: {result['error']}")
                return False
        else:
            print("⚠️  No PDFs found in data/ directory")
            print("   This is expected if you haven't added research papers yet")

        print("\n" + "="*60)
        print("✓ Research agent test completed!")
        print("="*60)
        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_research_agent()
