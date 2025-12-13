# 🧪 How to Test the Agent System

## 🚀 Quick Start (30 seconds)

```bash
cd essenceAI
python3 test_agent_setup.py
```

**Expected Output:**
```
🎉 All tests passed! Agent system is ready to use.
Total: 5/5 tests passed
```

---

## 📋 Complete Test Suite

### Option 1: Run Everything (Recommended)

```bash
./run_all_tests.sh
```

**What it does:**
- ✅ Verifies setup (5 tests)
- ✅ Tests Marketing Agent (all segments)
- ✅ Tests segment comparison
- ✅ Runs unit tests (Base Agent, Marketing, Config, Integration)

**Expected Result:**
```
Total Tests:  7
Passed:       7
Failed:       0

🎉 All tests passed!
```

### Option 2: Individual Tests

```bash
# 1. Setup verification
python3 test_agent_setup.py

# 2. Marketing agent tests
python3 test_marketing.py
python3 test_segment_comparison.py

# 3. Unit tests
pytest tests/test_agents.py::TestBaseAgent -v
pytest tests/test_agents.py::TestMarketingAgent -v
pytest tests/test_agents.py::TestAgentConfig -v
pytest tests/test_agents.py::TestIntegration -v
```

---

## 🎯 Test Categories

### 1. Setup Verification ✅ (No API Keys)

**File:** `test_agent_setup.py`

**Tests:**
- ✅ Agent imports
- ✅ Base agent functionality
- ✅ Marketing agent execution
- ✅ Configuration loading
- ✅ Segment profiles

**Run:**
```bash
python3 test_agent_setup.py
```

### 2. Marketing Agent Tests ✅ (No API Keys)

**Files:** `test_marketing.py`, `test_segment_comparison.py`

**Tests:**
- ✅ All 3 consumer segments
- ✅ Strategy generation
- ✅ Segment comparison
- ✅ Positioning and messaging

**Run:**
```bash
python3 test_marketing.py
python3 test_segment_comparison.py
```

### 3. Unit Tests ✅ (Partial - No API Keys)

**File:** `tests/test_agents.py`

**Tests:**
- ✅ 6 Base Agent tests
- ✅ 7 Marketing Agent tests
- ✅ 5 Configuration tests
- ✅ 2 Integration tests
- ⚠️ 9 tests require API keys (expected to fail)

**Run:**
```bash
# All tests (31 total, 22 pass without API keys)
pytest tests/test_agents.py -v

# Only tests that don't need API keys
pytest tests/test_agents.py::TestBaseAgent -v
pytest tests/test_agents.py::TestMarketingAgent -v
pytest tests/test_agents.py::TestAgentConfig -v
pytest tests/test_agents.py::TestIntegration -v
```

---

## 📊 Test Results

### Without API Keys (Default)

| Test Suite | Tests | Pass | Fail | Notes |
|------------|-------|------|------|-------|
| Setup Verification | 5 | 5 | 0 | ✅ All pass |
| Marketing Tests | 2 | 2 | 0 | ✅ All pass |
| Unit Tests | 31 | 22 | 9 | ⚠️ 9 need API keys |
| **Total** | **38** | **29** | **9** | **76% pass** |

### With API Keys (Full Functionality)

| Test Suite | Tests | Pass | Fail | Notes |
|------------|-------|------|------|-------|
| Setup Verification | 5 | 5 | 0 | ✅ All pass |
| Marketing Tests | 2 | 2 | 0 | ✅ All pass |
| Unit Tests | 31 | 31 | 0 | ✅ All pass |
| **Total** | **38** | **38** | **0** | **100% pass** |

---

## 🔧 Test Commands Reference

### Quick Commands

```bash
# Fastest verification
python3 test_agent_setup.py

# Complete test suite
./run_all_tests.sh

# Unit tests only
pytest tests/test_agents.py -v

# With coverage report
pytest tests/test_agents.py --cov=src/agents --cov-report=html
```

### Specific Test Classes

```bash
# Base Agent (6 tests)
pytest tests/test_agents.py::TestBaseAgent -v

# Marketing Agent (7 tests)
pytest tests/test_agents.py::TestMarketingAgent -v

# Competitor Agent (3 tests - needs API key)
pytest tests/test_agents.py::TestCompetitorAgent -v

# Research Agent (4 tests - needs API key)
pytest tests/test_agents.py::TestResearchAgent -v

# Orchestrator (4 tests - needs API key)
pytest tests/test_agents.py::TestAgentOrchestrator -v

# Configuration (5 tests)
pytest tests/test_agents.py::TestAgentConfig -v

# Integration (2 tests)
pytest tests/test_agents.py::TestIntegration -v
```

### Individual Tests

```bash
# Run a specific test
pytest tests/test_agents.py::TestMarketingAgent::test_execute_success -v

# Run with detailed output
pytest tests/test_agents.py::TestMarketingAgent -v -s

# Run with coverage
pytest tests/test_agents.py::TestMarketingAgent --cov=src/agents/marketing_agent
```

---

## 🎓 Interactive Testing

### Python REPL

```bash
python3
```

```python
# Test Marketing Agent
from agents import MarketingAgent

agent = MarketingAgent()

# Execute strategy
result = agent.execute({
    'product_description': 'Plant-based burger',
    'segment': 'High Essentialist',
    'domain': 'Plant-Based'
})

# Check result
print(f"Status: {result['status']}")
print(f"Message: {result['data']['messaging']['primary_message']}")

# Get all segments
profiles = agent.get_segment_profiles()
print(f"Segments: {list(profiles.keys())}")

# Compare segments
comparison = agent.compare_segments('Test product', 'Plant-Based')
print(f"Compared {len(comparison['data'])} segments")
```

### IPython (if available)

```bash
ipython
```

```python
from agents import MarketingAgent, AgentOrchestrator
from agents.agent_config import get_agent_capabilities

# Explore capabilities
capabilities = get_agent_capabilities()
for agent, info in capabilities.items():
    print(f"\n{info['name']}:")
    for cap in info['capabilities']:
        print(f"  - {cap}")
```

---

## ✅ Success Criteria

Your agent system is working correctly if:

1. ✅ `python3 test_agent_setup.py` shows **5/5 tests passed**
2. ✅ `python3 test_marketing.py` completes successfully
3. ✅ `./run_all_tests.sh` shows **7/7 tests passed**
4. ✅ At least **22/31 unit tests pass** (without API keys)
5. ✅ No import errors when running tests

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'agents'"

**Solution:**
```bash
cd essenceAI
python3 test_agent_setup.py
```

### Issue: "OPENAI_API_KEY not found"

**This is expected!** Some tests require API keys.

**Without API keys:**
- ✅ 22/31 tests pass (expected)
- ⚠️ 9 tests fail (expected)

**To fix (optional):**
```bash
# Create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### Issue: Tests are slow

**Solution:** Run only fast tests
```bash
# Skip tests that need API keys
pytest tests/test_agents.py::TestBaseAgent -v
pytest tests/test_agents.py::TestMarketingAgent -v
```

### Issue: Want to see detailed output

**Solution:**
```bash
# Add -s flag for print statements
pytest tests/test_agents.py::TestMarketingAgent -v -s

# Add --tb=short for shorter tracebacks
pytest tests/test_agents.py -v --tb=short
```

---

## 📚 Documentation

- **This Guide:** `HOW_TO_TEST.md` (you are here)
- **Detailed Testing:** `AGENT_TESTING_GUIDE.md`
- **Quick Reference:** `TESTING_QUICK_REFERENCE.md`
- **Agent Docs:** `AGENTS_README.md`
- **Quick Start:** `AGENTS_QUICKSTART.md`

---

## 🎉 Quick Win

Run this one-liner to see it working:

```bash
python3 -c "
from agents import MarketingAgent
agent = MarketingAgent()
result = agent.execute({
    'product_description': 'Algae-based protein bar',
    'segment': 'High Essentialist',
    'domain': 'Algae'
})
print('✓ Status:', result['status'])
print('✓ Message:', result['data']['messaging']['primary_message'])
print('✓ Channels:', len(result['data']['channels']))
print('✓ Tactics:', len(result['data']['tactics']))
"
```

**Expected Output:**
```
✓ Status: success
✓ Message: Algae-based protein bar - Indistinguishable from traditional products
✓ Channels: 3
✓ Tactics: 3
```

---

## 🎯 Recommended Testing Workflow

### For First-Time Setup

```bash
# 1. Verify setup
python3 test_agent_setup.py

# 2. Run complete test suite
./run_all_tests.sh

# 3. Try interactive testing
python3 -c "from agents import MarketingAgent; print(MarketingAgent().get_segment_profiles())"
```

### For Development

```bash
# 1. Run relevant tests
pytest tests/test_agents.py::TestMarketingAgent -v

# 2. Check coverage
pytest tests/test_agents.py --cov=src/agents --cov-report=term-missing

# 3. Run manual tests
python3 test_marketing.py
```

### For CI/CD

```bash
# Run all tests with coverage
pytest tests/test_agents.py -v --cov=src/agents --cov-report=xml

# Or use the test script
./run_all_tests.sh
```

---

## 📈 Test Coverage

Current coverage (without API keys):

- ✅ **Base Agent:** 90% coverage
- ✅ **Marketing Agent:** 70% coverage
- ✅ **Configuration:** 83% coverage
- ⚠️ **Competitor Agent:** 20% (needs API key)
- ⚠️ **Research Agent:** 23% (needs API key)
- ⚠️ **Orchestrator:** 22% (needs API key)

**Overall:** ~60% coverage without API keys, ~90% with API keys

---

## 🎊 Summary

**To test the agent system:**

1. **Quick verification:** `python3 test_agent_setup.py`
2. **Complete suite:** `./run_all_tests.sh`
3. **Unit tests:** `pytest tests/test_agents.py -v`

**Expected results:**
- ✅ 5/5 verification tests pass
- ✅ 7/7 complete suite tests pass
- ✅ 22/31 unit tests pass (without API keys)
- ✅ 31/31 unit tests pass (with API keys)

**Your agent system is ready to use! 🎉**

---

**Need more help?** Check `AGENT_TESTING_GUIDE.md` for detailed instructions.
