#!/usr/bin/env python3
"""
Quick test script to verify agent system setup
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all agent modules can be imported."""
    print("🔍 Testing agent imports...")
    
    try:
        from agents import (
            BaseAgent,
            ResearchAgent,
            CompetitorAgent,
            MarketingAgent,
            AgentOrchestrator
        )
        print("✓ All agent classes imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_marketing_agent():
    """Test marketing agent (doesn't require API keys)."""
    print("\n🎯 Testing Marketing Agent...")
    
    try:
        from agents import MarketingAgent
        
        agent = MarketingAgent()
        print(f"✓ Marketing agent created: {agent.name}")
        
        # Test execution
        result = agent.execute({
            'product_description': 'Test plant-based burger',
            'segment': 'High Essentialist',
            'domain': 'Plant-Based'
        })
        
        if result['status'] == 'success':
            print(f"✓ Strategy generated for {result['data']['segment']}")
            print(f"  - Primary message: {result['data']['messaging']['primary_message'][:60]}...")
            print(f"  - Channels: {len(result['data']['channels'])}")
            print(f"  - Tactics: {len(result['data']['tactics'])}")
            return True
        else:
            print(f"✗ Execution failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"✗ Marketing agent test failed: {e}")
        return False


def test_agent_config():
    """Test agent configuration."""
    print("\n⚙️  Testing Agent Configuration...")
    
    try:
        from agents.agent_config import (
            AgentConfig,
            get_agent_capabilities,
            get_workflow_template,
            WorkflowType,
            CONSUMER_SEGMENTS,
            FOOD_DOMAINS
        )
        
        config = AgentConfig()
        print(f"✓ Default config created")
        print(f"  - Data dir: {config.data_dir}")
        print(f"  - LLM provider: {config.llm_provider}")
        print(f"  - Max competitors: {config.max_competitors}")
        
        capabilities = get_agent_capabilities()
        print(f"✓ Agent capabilities loaded: {len(capabilities)} agents")
        
        template = get_workflow_template(WorkflowType.FULL_ANALYSIS)
        print(f"✓ Workflow template loaded: {template['name']}")
        
        print(f"✓ Consumer segments: {', '.join(CONSUMER_SEGMENTS)}")
        print(f"✓ Food domains: {', '.join(FOOD_DOMAINS)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_segment_profiles():
    """Test segment profiles."""
    print("\n👥 Testing Consumer Segment Profiles...")
    
    try:
        from agents import MarketingAgent
        
        agent = MarketingAgent()
        profiles = agent.get_segment_profiles()
        
        print(f"✓ Found {len(profiles)} consumer segments:")
        for segment, profile in profiles.items():
            print(f"\n  📊 {segment}:")
            print(f"     - {profile['description']}")
            print(f"     - Focus: {profile['messaging_focus']}")
            print(f"     - Key factors: {', '.join(profile['key_factors'][:2])}")
        
        return True
        
    except Exception as e:
        print(f"✗ Segment profile test failed: {e}")
        return False


def test_base_agent():
    """Test base agent functionality."""
    print("\n🤖 Testing Base Agent Functionality...")
    
    try:
        from agents.base_agent import BaseAgent
        
        class TestAgent(BaseAgent):
            def execute(self, task):
                return self._create_success_response(task, "Test completed")
        
        agent = TestAgent("TestAgent", "Test description")
        print(f"✓ Test agent created: {agent.name}")
        
        # Test logging
        agent.log_action("test_action", {"key": "value"})
        print(f"✓ Action logged: {len(agent.get_history())} actions")
        
        # Test status
        status = agent.get_status()
        print(f"✓ Status retrieved: {status['name']}")
        
        # Test execution
        result = agent.execute({"test": "data"})
        print(f"✓ Execution successful: {result['status']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Base agent test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 80)
    print("  essenceAI Agent System - Setup Verification")
    print("=" * 80)
    
    tests = [
        ("Imports", test_imports),
        ("Base Agent", test_base_agent),
        ("Marketing Agent", test_marketing_agent),
        ("Agent Configuration", test_agent_config),
        ("Segment Profiles", test_segment_profiles)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("  Test Summary")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All tests passed! Agent system is ready to use.")
        print("\n  Next steps:")
        print("  1. Set up your .env file with API keys")
        print("  2. Run: python examples/agent_usage_examples.py")
        print("  3. Check AGENTS_README.md for full documentation")
    else:
        print("\n  ⚠️  Some tests failed. Check the output above for details.")
    
    print("=" * 80 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
