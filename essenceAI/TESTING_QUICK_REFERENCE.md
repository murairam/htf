# 🧪 Agent Testing - Quick Reference

## 🚀 Quick Start

```bash
# Verify everything works
python3 test_agent_setup.py

# Run all tests
./run_all_tests.sh

# Or run tests individually
python3 test_marketing.py
python3 test_segment_comparison.py
```

## 📋 Test Commands

### Verification Tests (No API Keys Needed)

```bash
# Setup verification (5 tests)
python3 test_agent_setup.py

# Marketing agent tests
python3 test_marketing.py
python3 test_segment_comparison.py

# Unit tests (22 tests pass without API keys)
pytest tests/test_agents.py::TestBaseAgent -v
pytest tests/test_agents.py::TestMarketingAgent -v
pytest tests/test_agents.py::TestAgentConfig -v
pytest tests/test_agents.py::TestIntegration -v
```

### Full Test Suite

```bash
# Run all unit tests (31 total)
pytest tests/test_agents.py -v

# Run with coverage
pytest tests/test_agents.py --cov=src/agents --cov-report=term-missing

# Run specific test
pytest tests/test_agents.py::TestMarketingAgent::test_execute_success -v
```

### Interactive Testing

```bash
# Start Python REPL
python3

# Then run:
from agents import MarketingAgent
agent = MarketingAgent()
result = agent.execute({
    'product_description': 'Test product',
    'segment': 'High Essentialist',
    'domain': 'Plant-Based'
})
print(result['data']['messaging']['primary_message'])
```

## 📊 Expected Results

### Without API Keys
- ✅ 5/5 verification tests pass
- ✅ 22/31 unit tests pass
- ✅ All Marketing Agent tests pass
- ⚠️ 9 tests fail (require API keys - expected)

### With API Keys
- ✅ 5/5 verification tests pass
- ✅ 31/31 unit tests pass
- ✅ All agent tests pass

## 🎯 Test Files

| File | Purpose | API Key Required |
|------|---------|------------------|
| `test_agent_setup.py` | Verify setup | ❌ No |
| `test_marketing.py` | Test marketing agent | ❌ No |
| `test_segment_comparison.py` | Test segment comparison | ❌ No |
| `tests/test_agents.py` | Full unit test suite | ⚠️ Partial |
| `run_all_tests.sh` | Run all tests | ⚠️ Partial |

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'agents'"
```bash
cd essenceAI
python3 test_agent_setup.py
```

### "OPENAI_API_KEY not found"
**Expected** - Some tests require API keys. This is normal.
- 22 tests pass without API keys
- 31 tests pass with API keys

### Run specific test class
```bash
pytest tests/test_agents.py::TestMarketingAgent -v
```

## ✅ Success Checklist

- [ ] `python3 test_agent_setup.py` shows 5/5 passed
- [ ] `python3 test_marketing.py` completes successfully
- [ ] `python3 test_segment_comparison.py` works
- [ ] At least 22 unit tests pass
- [ ] No import errors

## 🎓 Test Examples

### Test 1: Quick Verification
```bash
python3 test_agent_setup.py
```
**Expected:** 5/5 tests passed

### Test 2: Marketing Agent
```bash
python3 test_marketing.py
```
**Expected:** All 3 segments tested successfully

### Test 3: Unit Tests
```bash
pytest tests/test_agents.py::TestMarketingAgent -v
```
**Expected:** 7/7 tests passed

### Test 4: Full Suite
```bash
./run_all_tests.sh
```
**Expected:** 7/7 tests passed (without API keys)

## 📚 Documentation

- **Full Guide:** `AGENT_TESTING_GUIDE.md`
- **Quick Start:** `AGENTS_QUICKSTART.md`
- **API Docs:** `AGENTS_README.md`

## 🎉 Quick Win

Run this to see it working:
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
"
```

---

**Need help?** Check `AGENT_TESTING_GUIDE.md` for detailed instructions.
