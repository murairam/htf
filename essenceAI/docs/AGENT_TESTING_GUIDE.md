# 🧪 Agent System Testing Guide

Complete guide to testing the essenceAI agent system.

## 📋 Table of Contents

1. [Quick Verification](#quick-verification)
2. [Unit Tests](#unit-tests)
3. [Manual Testing](#manual-testing)
4. [Integration Testing](#integration-testing)
5. [Testing Without API Keys](#testing-without-api-keys)
6. [Testing With API Keys](#testing-with-api-keys)

---

## 🚀 Quick Verification

### Step 1: Verify Setup

```bash
cd essenceAI
python3 test_agent_setup.py
```

**Expected Output:**
```
================================================================================
  essenceAI Agent System - Setup Verification
================================================================================
🔍 Testing agent imports...
✓ All agent classes imported successfully

🤖 Testing Base Agent Functionality...
✓ Test agent created: TestAgent
✓ Action logged: 1 actions
✓ Status retrieved: TestAgent
✓ Execution successful: success

🎯 Testing Marketing Agent...
✓ Marketing agent created: MarketingAgent
✓ Strategy generated for High Essentialist
  - Primary message: Test plant-based burger - Indistinguishable from traditional...
  - Channels: 3
  - Tactics: 3

⚙️  Testing Agent Configuration...
✓ Default config created
  - Data dir: data
  - LLM provider: openai
  - Max competitors: 10
✓ Agent capabilities loaded: 4 agents
✓ Workflow template loaded: Full Market Intelligence Analysis
✓ Consumer segments: High Essentialist, Skeptic, Non-Consumer
✓ Food domains: Precision Fermentation, Plant-Based, Algae

👥 Testing Consumer Segment Profiles...
✓ Found 3 consumer segments:

  📊 High Essentialist:
     - Values sensory mimicry and authentic taste/texture
     - Focus: Indistinguishable from traditional products
     - Key factors: Taste similarity, Texture match

  📊 Skeptic:
     - Values naturalness and transparency about origins
     - Focus: Natural, simple, transparent production
     - Key factors: Natural ingredients, Minimal processing

  📊 Non-Consumer:
     - Fears unfamiliar and heavily processed foods
     - Focus: Familiar formats, trusted brands, gradual introduction
     - Key factors: Familiarity, Simplicity

================================================================================
  Test Summary
================================================================================
  ✓ PASS: Imports
  ✓ PASS: Base Agent
  ✓ PASS: Marketing Agent
  ✓ PASS: Agent Configuration
  ✓ PASS: Segment Profiles

  Total: 5/5 tests passed

  🎉 All tests passed! Agent system is ready to use.
```

---

## 🧪 Unit Tests

### Run All Tests

```bash
cd essenceAI
pytest tests/test_agents.py -v
```

### Run Specific Test Classes

```bash
# Test Marketing Agent only
pytest tests/test_agents.py::TestMarketingAgent -v

# Test Base Agent only
pytest tests/test_agents.py::TestBaseAgent -v

# Test Configuration only
pytest tests/test_agents.py::TestAgentConfig -v

# Test Integration tests
pytest tests/test_agents.py::TestIntegration -v
```

### Run Tests with Coverage

```bash
pytest tests/test_agents.py --cov=src/agents --cov-report=term-missing
```

### Expected Results

**Without API Keys:**
- ✅ 22 tests pass (BaseAgent, MarketingAgent, Config, Integration)
- ⚠️ 9 tests fail (require API keys - expected)

**With API Keys:**
- ✅ All 31 tests should pass

---

## 🎯 Manual Testing

### Test 1: Marketing Agent (No API Keys Required)

Create a test file `test_marketing.py`:

```python
from agents import MarketingAgent

def test_marketing_agent():
    """Test marketing agent with all segments."""
    agent = MarketingAgent()
    
    segments = ['High Essentialist', 'Skeptic', 'Non-Consumer']
    
    for segment in segments:
        print(f"\n{'='*60}")
        print(f"Testing {segment}")
        print('='*60)
        
        result = agent.execute({
            'product_description': 'Plant-based burger for fast-food chains',
            'segment': segment,
            'domain': 'Plant-Based'
        })
        
        if result['status'] == 'success':
            data = result['data']
            print(f"✓ Status: {result['status']}")
            print(f"✓ Segment: {data['segment']}")
            print(f"✓ Primary Message: {data['messaging']['primary_message']}")
            print(f"✓ Channels: {len(data['channels'])}")
            print(f"✓ Tactics: {len(data['tactics'])}")
            print(f"✓ Key Messages: {len(data['key_messages'])}")
            
            # Show first tactic
            print(f"\nFirst Tactic:")
            print(f"  - {data['tactics'][0]['tactic']}")
            print(f"  - Goal: {data['tactics'][0]['goal']}")
        else:
            print(f"✗ Error: {result['error']}")
            return False
    
    print(f"\n{'='*60}")
    print("✓ All segments tested successfully!")
    print('='*60)
    return True

if __name__ == "__main__":
    test_marketing_agent()
```

Run it:
```bash
python3 test_marketing.py
```

### Test 2: Segment Comparison

Create `test_segment_comparison.py`:

```python
from agents import MarketingAgent

def test_segment_comparison():
    """Compare strategies across all segments."""
    agent = MarketingAgent()
    
    product = "Precision fermented artisan cheese"
    domain = "Precision Fermentation"
    
    print(f"\n{'='*60}")
    print(f"Comparing Segments for: {product}")
    print('='*60)
    
    result = agent.compare_segments(product, domain)
    
    if result['status'] == 'success':
        for segment, strategy in result['data'].items():
            print(f"\n📊 {segment}:")
            print(f"   Focus: {strategy['segment_profile']['messaging_focus']}")
            print(f"   Key Factors: {', '.join(strategy['segment_profile']['key_factors'][:2])}")
            print(f"   Top Tactic: {strategy['tactics'][0]['tactic']}")
            print(f"   Channels: {', '.join([c['channel'] for c in strategy['channels'][:2]])}")
        
        print(f"\n{'='*60}")
        print("✓ Segment comparison completed!")
        print('='*60)
        return True
    else:
        print(f"✗ Error: {result['error']}")
        return False

if __name__ == "__main__":
    test_segment_comparison()
```

Run it:
```bash
python3 test_segment_comparison.py
```

### Test 3: Agent History and Status

Create `test_agent_tracking.py`:

```python
from agents import MarketingAgent

def test_agent_tracking():
    """Test agent history and status tracking."""
    agent = MarketingAgent()
    
    print(f"\n{'='*60}")
    print("Testing Agent History and Status")
    print('='*60)
    
    # Initial status
    status = agent.get_status()
    print(f"\nInitial Status:")
    print(f"  Name: {status['name']}")
    print(f"  Description: {status['description']}")
    print(f"  Actions: {status['actions_count']}")
    
    # Execute multiple tasks
    print(f"\nExecuting 3 tasks...")
    for i in range(3):
        agent.execute({
            'product_description': f'Product {i+1}',
            'segment': 'High Essentialist',
            'domain': 'Plant-Based'
        })
    
    # Check history
    history = agent.get_history()
    print(f"\n✓ History tracked: {len(history)} actions")
    
    for i, action in enumerate(history):
        print(f"\nAction {i+1}:")
        print(f"  Timestamp: {action['timestamp']}")
        print(f"  Action: {action['action']}")
        print(f"  Product: {action['details']['product']}")
    
    # Final status
    status = agent.get_status()
    print(f"\nFinal Status:")
    print(f"  Actions: {status['actions_count']}")
    
    # Clear history
    agent.clear_history()
    print(f"\n✓ History cleared: {len(agent.get_history())} actions")
    
    print(f"\n{'='*60}")
    print("✓ Agent tracking test completed!")
    print('='*60)
    return True

if __name__ == "__main__":
    test_agent_tracking()
```

Run it:
```bash
python3 test_agent_tracking.py
```

---

## 🔗 Integration Testing

### Test 4: Multi-Agent Workflow (Requires API Keys)

Create `test_integration.py`:

```python
import os
from agents import MarketingAgent, CompetitorAgent

def test_integration():
    """Test integration between multiple agents."""
    
    # Check if API keys are available
    has_api_key = os.getenv('OPENAI_API_KEY') is not None
    
    print(f"\n{'='*60}")
    print("Testing Multi-Agent Integration")
    print('='*60)
    
    # Marketing Agent (always works)
    print("\n1️⃣ Testing Marketing Agent...")
    marketing = MarketingAgent()
    
    marketing_result = marketing.execute({
        'product_description': 'Plant-based protein powder',
        'segment': 'High Essentialist',
        'domain': 'Plant-Based'
    })
    
    if marketing_result['status'] == 'success':
        print("✓ Marketing Agent: SUCCESS")
        print(f"  Strategy: {marketing_result['data']['segment']}")
    else:
        print(f"✗ Marketing Agent: FAILED - {marketing_result['error']}")
        return False
    
    # Competitor Agent (requires API key)
    if has_api_key:
        print("\n2️⃣ Testing Competitor Agent...")
        try:
            competitor = CompetitorAgent()
            
            competitor_result = competitor.execute({
                'product_description': 'Plant-based protein powder',
                'domain': 'Plant-Based',
                'max_competitors': 5
            })
            
            if competitor_result['status'] == 'success':
                print("✓ Competitor Agent: SUCCESS")
                print(f"  Competitors found: {competitor_result['data']['count']}")
            else:
                print(f"⚠️  Competitor Agent: {competitor_result['error']}")
        except Exception as e:
            print(f"⚠️  Competitor Agent: {str(e)}")
    else:
        print("\n2️⃣ Skipping Competitor Agent (no API key)")
    
    print(f"\n{'='*60}")
    print("✓ Integration test completed!")
    print('='*60)
    return True

if __name__ == "__main__":
    test_integration()
```

Run it:
```bash
python3 test_integration.py
```

---

## 🔓 Testing Without API Keys

These tests work **without any API keys**:

### Quick Test Script

```bash
# Run verification
python3 test_agent_setup.py

# Run unit tests (22 will pass)
pytest tests/test_agents.py::TestBaseAgent -v
pytest tests/test_agents.py::TestMarketingAgent -v
pytest tests/test_agents.py::TestAgentConfig -v
pytest tests/test_agents.py::TestIntegration -v

# Run manual tests
python3 test_marketing.py
python3 test_segment_comparison.py
python3 test_agent_tracking.py
```

### Interactive Python Test

```bash
python3
```

```python
# Import agent
from agents import MarketingAgent

# Create agent
agent = MarketingAgent()

# Test execution
result = agent.execute({
    'product_description': 'Algae-based protein bar',
    'segment': 'Skeptic',
    'domain': 'Algae'
})

# Check result
print(f"Status: {result['status']}")
print(f"Message: {result['data']['messaging']['primary_message']}")

# Get segment profiles
profiles = agent.get_segment_profiles()
print(f"Available segments: {list(profiles.keys())}")

# Compare segments
comparison = agent.compare_segments('Test product', 'Plant-Based')
print(f"Comparison status: {comparison['status']}")
print(f"Segments compared: {len(comparison['data'])}")
```

---

## 🔑 Testing With API Keys

### Setup API Keys

Create `.env` file:
```bash
cd essenceAI
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-actual-key-here
TAVILY_API_KEY=tvly-your-key-here
LLM_PROVIDER=openai
EOF
```

### Test Competitor Agent

Create `test_competitor.py`:

```python
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
```

Run it:
```bash
python3 test_competitor.py
```

### Test Research Agent

Create `test_research.py`:

```python
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
```

Run it:
```bash
python3 test_research.py
```

### Test Full Orchestrator

Create `test_orchestrator.py`:

```python
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
```

Run it:
```bash
python3 test_orchestrator.py
```

---

## 📊 Test Summary

### Test Coverage

| Component | Tests | No API Key | With API Key |
|-----------|-------|------------|--------------|
| Base Agent | 6 | ✅ All pass | ✅ All pass |
| Marketing Agent | 7 | ✅ All pass | ✅ All pass |
| Competitor Agent | 3 | ⚠️ 2 fail | ✅ All pass |
| Research Agent | 4 | ⚠️ 3 fail | ✅ All pass |
| Orchestrator | 4 | ⚠️ 4 fail | ✅ All pass |
| Configuration | 5 | ✅ All pass | ✅ All pass |
| Integration | 2 | ✅ All pass | ✅ All pass |
| **Total** | **31** | **22 pass** | **31 pass** |

### Quick Test Commands

```bash
# Verify setup (always works)
python3 test_agent_setup.py

# Run all unit tests
pytest tests/test_agents.py -v

# Run tests that don't need API keys
pytest tests/test_agents.py::TestBaseAgent -v
pytest tests/test_agents.py::TestMarketingAgent -v
pytest tests/test_agents.py::TestAgentConfig -v

# Run with coverage
pytest tests/test_agents.py --cov=src/agents --cov-report=html

# View coverage report
open htmlcov/index.html  # or browse to htmlcov/index.html
```

---

## 🎯 Recommended Testing Workflow

### 1. Initial Setup
```bash
python3 test_agent_setup.py
```

### 2. Unit Tests
```bash
pytest tests/test_agents.py -v
```

### 3. Manual Testing (No API Keys)
```bash
python3 test_marketing.py
python3 test_segment_comparison.py
python3 test_agent_tracking.py
```

### 4. Integration Testing (With API Keys)
```bash
# Set up .env first
python3 test_competitor.py
python3 test_research.py
python3 test_orchestrator.py
```

### 5. Run Examples
```bash
python3 examples/agent_usage_examples.py
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'agents'"
**Solution:**
```bash
cd essenceAI
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python3 test_agent_setup.py
```

### Issue: "OPENAI_API_KEY not found"
**Solution:**
```bash
# Create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### Issue: Tests fail with API key errors
**Expected:** Some tests require API keys. This is normal.
- 22 tests pass without API keys
- 31 tests pass with API keys

### Issue: "No PDF files found"
**Solution:** Research agent needs PDFs in `data/` directory
```bash
# Check if PDFs exist
ls -la data/*.pdf

# If no PDFs, research agent will skip initialization (expected)
```

---

## ✅ Success Criteria

Your agent system is working correctly if:

1. ✅ `python3 test_agent_setup.py` shows 5/5 tests passed
2. ✅ Marketing Agent tests all pass
3. ✅ At least 22 unit tests pass (without API keys)
4. ✅ Agent imports work without errors
5. ✅ Configuration loads successfully

---

**Ready to test? Start with:**
```bash
python3 test_agent_setup.py
```

🎉 **Happy Testing!**
