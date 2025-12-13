# 🚀 Getting Started with Agents

Complete guide to set up and test the essenceAI agent system.

---

## 📋 Table of Contents

1. [Installation](#-installation)
2. [Testing](#-testing)
3. [Quick Examples](#-quick-examples)
4. [Documentation](#-documentation)
5. [Troubleshooting](#-troubleshooting)

---

## 📦 Installation

### Step 1: Install Dependencies

```bash
cd essenceAI
pip install -r requirements.txt
```

Or with pip3:
```bash
python3 -m pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
python3 test_agent_setup.py
```

**Expected Output:**
```
🎉 All tests passed! Agent system is ready to use.
Total: 5/5 tests passed
```

✅ **Installation complete!** See `INSTALL.md` for detailed instructions.

---

## 🧪 Testing

### Quick Test (30 seconds)

```bash
python3 test_agent_setup.py
```

### Complete Test Suite

```bash
./run_all_tests.sh
```

### Individual Tests

```bash
# Marketing agent
python3 test_marketing.py

# Segment comparison
python3 test_segment_comparison.py

# Unit tests
pytest tests/test_agents.py -v
```

✅ **Testing complete!** See `HOW_TO_TEST.md` for detailed testing guide.

---

## 🎯 Quick Examples

### Example 1: Marketing Strategy (No API Key)

```python
from agents import MarketingAgent

agent = MarketingAgent()

result = agent.execute({
    'product_description': 'Plant-based burger for fast-food chains',
    'segment': 'High Essentialist',
    'domain': 'Plant-Based'
})

print(result['data']['messaging']['primary_message'])
# Output: Plant-based burger for fast-food chains - Indistinguishable from traditional products
```

### Example 2: Compare All Segments

```python
from agents import MarketingAgent

agent = MarketingAgent()

result = agent.compare_segments(
    product='Precision fermented cheese',
    domain='Precision Fermentation'
)

for segment, strategy in result['data'].items():
    print(f"\n{segment}:")
    print(f"  Focus: {strategy['segment_profile']['messaging_focus']}")
    print(f"  Top Tactic: {strategy['tactics'][0]['tactic']}")
```

### Example 3: Full Analysis (Requires API Keys)

```python
from agents.orchestrator import quick_analysis

result = quick_analysis(
    product_description="Algae-based protein bar",
    domain="Algae",
    segment="Skeptic"
)

if result['status'] == 'success':
    data = result['data']
    print(f"Competitors: {data['competitor_intelligence']['count']}")
    print(f"Strategy: {data['marketing_strategy']['segment']}")
```

✅ **More examples:** See `examples/agent_usage_examples.py`

---

## 📚 Documentation

### Quick References

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **INSTALL.md** | Installation guide | First time setup |
| **HOW_TO_TEST.md** | Testing guide | Verify everything works |
| **AGENTS_QUICKSTART.md** | 5-minute quick start | Learn basics fast |
| **AGENTS_README.md** | Complete documentation | Full API reference |
| **TESTING_QUICK_REFERENCE.md** | Test commands | Quick command lookup |

### Documentation Flow

```
1. INSTALL.md          → Install dependencies
2. HOW_TO_TEST.md      → Verify installation
3. AGENTS_QUICKSTART.md → Learn basics
4. AGENTS_README.md    → Deep dive
```

---

## 🎓 Learning Path

### Level 1: Beginner (5 minutes)

1. Install dependencies: `pip install -r requirements.txt`
2. Verify setup: `python3 test_agent_setup.py`
3. Try Marketing Agent: `python3 test_marketing.py`

### Level 2: Intermediate (15 minutes)

1. Read: `AGENTS_QUICKSTART.md`
2. Run examples: `python3 examples/agent_usage_examples.py`
3. Try interactive testing (see below)

### Level 3: Advanced (30 minutes)

1. Read: `AGENTS_README.md`
2. Set up API keys in `.env`
3. Build custom workflows

---

## 🎮 Interactive Testing

### Python REPL

```bash
python3
```

```python
# Import agents
from agents import MarketingAgent, AgentOrchestrator
from agents.agent_config import get_agent_capabilities

# Test Marketing Agent
agent = MarketingAgent()
result = agent.execute({
    'product_description': 'Your product',
    'segment': 'High Essentialist',
    'domain': 'Plant-Based'
})

print(result['data']['messaging']['primary_message'])

# Explore capabilities
capabilities = get_agent_capabilities()
for agent_type, info in capabilities.items():
    print(f"\n{info['name']}:")
    for cap in info['capabilities']:
        print(f"  - {cap}")

# Get segment profiles
profiles = agent.get_segment_profiles()
for segment, profile in profiles.items():
    print(f"\n{segment}: {profile['description']}")
```

---

## 🔑 Optional: API Keys Setup

For full functionality (Competitor and Research agents):

### Create .env file

```bash
cd essenceAI
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-openai-key-here
TAVILY_API_KEY=tvly-your-tavily-key-here
LLM_PROVIDER=openai
EOF
```

### Get API Keys

- **OpenAI:** https://platform.openai.com/api-keys
- **Tavily:** https://tavily.com (free tier: 1000 requests/month)

---

## 🐛 Troubleshooting

### Issue: "No module named 'llama_index'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "No module named 'agents'"

**Solution:**
```bash
cd essenceAI
python3 test_agent_setup.py
```

### Issue: Tests fail

**Check:**
1. Dependencies installed? `pip install -r requirements.txt`
2. In correct directory? `cd essenceAI`
3. Python version? `python3 --version` (need 3.9+)

### Issue: "OPENAI_API_KEY not found"

**This is expected!** Some features require API keys.

**Without API keys:**
- ✅ Marketing Agent works
- ✅ 22/31 tests pass
- ⚠️ Competitor Agent needs API key
- ⚠️ Research Agent needs API key

**To fix:** Create `.env` file with API keys (see above)

---

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] `python3 test_agent_setup.py` passes (5/5)
- [ ] `python3 test_marketing.py` works
- [ ] Can import agents: `from agents import MarketingAgent`
- [ ] (Optional) API keys configured

---

## 🎯 What Works Without API Keys

These features work **immediately** without any API keys:

### ✅ Marketing Agent
- Generate marketing strategies
- Compare segments
- Get positioning and messaging
- Recommend channels and tactics

### ✅ Base Agent
- Action logging
- History tracking
- Status reporting

### ✅ Configuration
- Agent capabilities
- Workflow templates
- Segment profiles

### 🔑 Requires API Keys

- **Competitor Agent** - Real-time market data
- **Research Agent** - Scientific paper analysis
- **Full Orchestrator** - Complete workflows

---

## 🚀 Quick Commands

```bash
# Install
pip install -r requirements.txt

# Verify
python3 test_agent_setup.py

# Test marketing
python3 test_marketing.py

# Run all tests
./run_all_tests.sh

# Run examples
python3 examples/agent_usage_examples.py

# Interactive
python3
>>> from agents import MarketingAgent
>>> agent = MarketingAgent()
>>> result = agent.execute({'product_description': 'Test', 'segment': 'High Essentialist', 'domain': 'Plant-Based'})
>>> print(result['status'])
```

---

## 📖 Next Steps

### After Installation

1. ✅ Verify: `python3 test_agent_setup.py`
2. ✅ Test: `python3 test_marketing.py`
3. ✅ Learn: Read `AGENTS_QUICKSTART.md`
4. ✅ Explore: Run `python3 examples/agent_usage_examples.py`

### After Testing

1. ✅ Read full docs: `AGENTS_README.md`
2. ✅ (Optional) Add API keys
3. ✅ Build your own workflows
4. ✅ Integrate with your application

---

## 🎊 You're Ready!

If you see this:
```
🎉 All tests passed! Agent system is ready to use.
```

**Congratulations! Your agent system is fully set up and working.** 🚀

### What You Can Do Now

1. **Generate marketing strategies** for any product
2. **Compare consumer segments** to find best target
3. **Get positioning and messaging** recommendations
4. **Build custom workflows** with multiple agents
5. **(With API keys)** Get real-time competitor data
6. **(With API keys)** Analyze scientific research papers

---

## 🆘 Need Help?

| Issue | Document |
|-------|----------|
| Installation problems | `INSTALL.md` |
| Testing issues | `HOW_TO_TEST.md` |
| Usage questions | `AGENTS_QUICKSTART.md` |
| API reference | `AGENTS_README.md` |
| Quick commands | `TESTING_QUICK_REFERENCE.md` |

---

**Ready to start?**

```bash
python3 test_agent_setup.py
```

🎉 **Welcome to the essenceAI Agent System!**
