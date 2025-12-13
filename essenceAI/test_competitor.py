import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

from agents import CompetitorAgent

def test_competitor_agent():
    """Test competitor agent with API key."""
    print("\n" + "="*60)
    print("Testing Competitor Agent")
    print("="*60)

    try:
        agent = CompetitorAgent()
        print("✓ Competitor agent created")

        # Test basic execution
        result = agent.execute({
            'product_description': 'Plant-based burger',
            'domain': 'Plant-Based',
            'max_competitors': 5
        })

        if result['status'] == 'success':
            data = result['data']
            print(f"\n✓ Competitors found: {data['count']}")

            if data['count'] > 0:
                print(f"\nFirst competitor:")
                comp = data['competitors'][0]
                print(f"  Name: {comp.get('name', 'N/A')}")
                print(f"  Price: ${comp.get('price_usd', 0):.2f}")
                print(f"  CO2: {comp.get('co2_kg_per_kg', 0):.2f} kg/kg")

            if 'statistics' in data:
                stats = data['statistics']
                if 'price_stats' in stats:
                    print(f"\nPrice Statistics:")
                    print(f"  Min: ${stats['price_stats']['min']:.2f}")
                    print(f"  Max: ${stats['price_stats']['max']:.2f}")
                    print(f"  Avg: ${stats['price_stats']['avg']:.2f}")
        else:
            print(f"✗ Error: {result['error']}")
            return False

        print("\n" + "="*60)
        print("✓ Competitor agent test completed!")
        print("="*60)
        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_competitor_agent()
