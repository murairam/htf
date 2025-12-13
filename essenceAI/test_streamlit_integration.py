"""
Quick test to verify Streamlit app integration
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")

    try:
        from agents.orchestrator import AgentOrchestrator
        print("✅ AgentOrchestrator imported successfully")
    except Exception as e:
        print(f"❌ Failed to import AgentOrchestrator: {e}")
        return False

    try:
        from agents.research_agent import ResearchAgent
        print("✅ ResearchAgent imported successfully")
    except Exception as e:
        print(f"❌ Failed to import ResearchAgent: {e}")
        return False

    try:
        from agents.competitor_agent import CompetitorAgent
        print("✅ CompetitorAgent imported successfully")
    except Exception as e:
        print(f"❌ Failed to import CompetitorAgent: {e}")
        return False

    try:
        from agents.marketing_agent import MarketingAgent
        print("✅ MarketingAgent imported successfully")
    except Exception as e:
        print(f"❌ Failed to import MarketingAgent: {e}")
        return False

    return True

def test_orchestrator_initialization():
    """Test that orchestrator can be initialized"""
    print("\nTesting orchestrator initialization...")

    try:
        from agents.orchestrator import AgentOrchestrator

        data_dir = Path(__file__).parent / "data"
        persist_dir = Path(__file__).parent / ".storage"

        orchestrator = AgentOrchestrator(
            data_dir=str(data_dir),
            persist_dir=str(persist_dir)
        )
        print("✅ AgentOrchestrator initialized successfully")

        # Test get_agent_status
        status = orchestrator.get_agent_status()
        print(f"✅ Agent status retrieved: {len(status)} agents")

        return True
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_syntax():
    """Test that app.py has valid syntax"""
    print("\nTesting app.py syntax...")

    try:
        app_path = Path(__file__).parent / "src" / "app.py"
        with open(app_path, 'r') as f:
            code = f.read()

        compile(code, str(app_path), 'exec')
        print("✅ app.py syntax is valid")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in app.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking app.py: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("STREAMLIT INTEGRATION TEST SUITE")
    print("="*60)

    results = []

    # Test 1: Imports
    results.append(("Imports", test_imports()))

    # Test 2: Orchestrator
    results.append(("Orchestrator Initialization", test_orchestrator_initialization()))

    # Test 3: App Syntax
    results.append(("App Syntax", test_app_syntax()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(result[1] for result in results)

    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Integration is ready!")
        print("\nTo run the app:")
        print("  cd essenceAI")
        print("  streamlit run src/app.py")
    else:
        print("❌ SOME TESTS FAILED - Please review errors above")
    print("="*60)

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
