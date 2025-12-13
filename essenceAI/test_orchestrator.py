import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

from agents import AgentOrchestrator

def test_orchestrator():
    """Test full orchestrator workflow."""
    print("\n" + "="*60)
    print("Testing Agent Orchestrator")
    print("="*60)

    try:
        orchestrator = AgentOrchestrator(data_dir="data")
        print("✓ Orchestrator created")

        # Get agent status
        status = orchestrator.get_agent_status()
        print(f"\n✓ Agent status retrieved:")
        for agent_name, agent_status in status.items():
            if agent_name != 'research_initialized':
                print(f"  - {agent_status['name']}: {agent_status['actions_count']} actions")

        # Execute full analysis
        print("\nExecuting full analysis...")
        result = orchestrator.execute_full_analysis(
            product_description="Plant-based protein bar",
            domain="Plant-Based",
            segment="High Essentialist"
        )

        if result['status'] in ['success', 'partial']:
            print(f"✓ Analysis completed: {result['status']}")
            print(f"  Agents used: {', '.join(result['agents_used'])}")
            print(f"  Steps: {len(result['workflow']['steps'])}")

            if 'data' in result:
                data = result['data']
                if 'competitor_intelligence' in data:
                    print(f"  Competitors: {data['competitor_intelligence'].get('count', 0)}")
                if 'marketing_strategy' in data and data['marketing_strategy']:
                    print(f"  Strategy: {data['marketing_strategy']['segment']}")
        else:
            print(f"✗ Error: {result.get('message', 'Unknown error')}")
            return False

        print("\n" + "="*60)
        print("✓ Orchestrator test completed!")
        print("="*60)
        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_orchestrator()
