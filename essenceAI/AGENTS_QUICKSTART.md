# 🚀 Agent System Quick Start

Get started with the essenceAI agent system in 5 minutes!

## ✅ Verification

First, verify the agent system is set up correctly:

```bash
cd essenceAI
python3 test_agent_setup.py
```

You should see: `🎉 All tests passed! Agent system is ready to use.`

## 🎯 Quick Examples

### 1. Marketing Agent (No API Key Required)

The Marketing Agent works without any API keys!

```python
from agents import MarketingAgent

# Create agent
agent = MarketingAgent()

# Generate strategy
result = agent.execute({
    'product_description': 'Plant-based burger for fast-food chains',
    'segment': 'High Essentialist',
    'domain': 'Plant-Based'
})

# Access results
if result['status'] == 'success':
    strategy = result['data']
    print(f"Segment: {strategy['segment']}")
    print(f"Message: {strategy['messaging']['primary_message']}")
    print(f"Channels: {[c['channel'] for c in strategy['channels']]}")
```

**Available Segments:**
- `High Essentialist` - Values sensory mimicry
- `Skeptic` - Values naturalness and transparency
- `Non-Consumer` - Fears unfamiliar foods

### 2. Compare All Segments

```python
from agents import MarketingAgent

agent = MarketingAgent()

# Compare strategies across all segments
result = agent.compare_segments(
    product='Precision fermented cheese',
    domain='Precision Fermentation'
)

for segment, strategy in result['data'].items():
    print(f"\n{segment}:")
    print(f"  Focus: {strategy['segment_profile']['messaging_focus']}")
    print(f"  Top tactic: {strategy['tactics'][0]['tactic']}")
```

### 3. Full Analysis (Requires API Keys)

For competitor intelligence and research analysis, you'll need API keys.

**Setup `.env` file:**

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional (for better competitor data)
TAVILY_API_KEY=tvly-your-key-here

# LLM Provider
LLM_PROVIDER=openai
```

**Run full analysis:**

```python
from agents.orchestrator import quick_analysis

result = quick_analysis(
    product_description="Algae-based protein bar for athletes",
    domain="Algae",
    segment="Skeptic"
)

if result['status'] == 'success':
    data = result['data']
    print(f"Competitors: {data['competitor_intelligence']['count']}")
    print(f"Research citations: {len(data['research_insights']['citations'])}")
    print(f"Marketing strategy: {data['marketing_strategy']['segment']}")
```

## 📚 Available Agents

### 1. Marketing Agent ✅ (No API Key)
- Generate segment-specific strategies
- Compare strategies across segments
- Get positioning and messaging
- Recommend channels and tactics

### 2. Competitor Agent 🔑 (Requires OPENAI_API_KEY)
- Gather real-time competitor data
- Analyze pricing landscape
- Evaluate sustainability metrics
- Identify market gaps

### 3. Research Agent 🔑 (Requires OPENAI_API_KEY + PDFs)
- Analyze scientific papers
- Extract research insights
- Provide cited recommendations
- Identify consumer acceptance factors

### 4. Agent Orchestrator 🔑 (Coordinates all agents)
- Execute multi-agent workflows
- Coordinate data flow
- Aggregate results

## 🎮 Interactive Examples

Run the comprehensive examples:

```bash
cd essenceAI
python3 examples/agent_usage_examples.py
```

This will demonstrate:
1. Individual agent usage
2. Full analysis workflow
3. Deep dive competitor analysis
4. Segment comparison
5. Custom workflows

## 📖 Documentation

- **Full Documentation**: See `AGENTS_README.md`
- **API Reference**: See `AGENTS_README.md` → API Reference section
- **Configuration**: See `src/agents/agent_config.py`

## 🧪 Testing

Run the test suite:

```bash
cd essenceAI
pytest tests/test_agents.py -v
```

Note: Some tests require API keys. Tests that don't require API keys will pass.

## 🎯 Common Use Cases

### Use Case 1: Product Launch Planning

```python
from agents import MarketingAgent

agent = MarketingAgent()

# Test different segments
for segment in ['High Essentialist', 'Skeptic', 'Non-Consumer']:
    result = agent.execute({
        'product_description': 'Your product here',
        'segment': segment,
        'domain': 'Plant-Based'
    })
    
    if result['status'] == 'success':
        print(f"\n{segment} Strategy:")
        print(f"  Message: {result['data']['messaging']['primary_message']}")
        print(f"  Top 3 tactics:")
        for tactic in result['data']['tactics'][:3]:
            print(f"    - {tactic['tactic']}: {tactic['goal']}")
```

### Use Case 2: Market Research (With API Keys)

```python
from agents import CompetitorAgent

agent = CompetitorAgent()

# Analyze competitors
result = agent.execute({
    'product_description': 'Plant-based protein powder',
    'domain': 'Plant-Based',
    'max_competitors': 10
})

if result['status'] == 'success':
    data = result['data']
    print(f"Found {data['count']} competitors")
    print(f"Price range: ${data['statistics']['price_stats']['min']:.2f} - ${data['statistics']['price_stats']['max']:.2f}")
    print(f"Avg CO2: {data['statistics']['co2_stats']['avg']:.2f} kg/kg")

# Analyze pricing
pricing = agent.analyze_pricing('Plant-based protein powder', 'Plant-Based')
if pricing['status'] == 'success':
    print(f"\nPricing Analysis:")
    print(f"  Average: ${pricing['data']['avg_price']:.2f}")
    print(f"  Median: ${pricing['data']['median_price']:.2f}")
```

### Use Case 3: Research Insights (With API Keys + PDFs)

```python
from agents import ResearchAgent

agent = ResearchAgent(data_dir="data")

# Initialize (first time only)
agent.initialize()

# Get consumer acceptance insights
result = agent.analyze_consumer_acceptance(
    domain="Precision Fermentation",
    segment="Skeptic"
)

if result['status'] == 'success':
    print(f"Answer: {result['data']['answer'][:200]}...")
    print(f"\nCitations:")
    for citation in result['data']['citations'][:3]:
        print(f"  - {citation['source']}: {citation['text'][:100]}...")
```

## 🔧 Troubleshooting

### "OPENAI_API_KEY not found"
- Create a `.env` file in the `essenceAI` directory
- Add your OpenAI API key: `OPENAI_API_KEY=sk-your-key-here`

### "No module named 'agents'"
- Make sure you're in the `essenceAI` directory
- Check that `src/agents/` exists
- Try: `python3 test_agent_setup.py` to verify setup

### "RAG engine not initialized"
- Call `agent.initialize()` before using ResearchAgent
- Make sure you have PDF files in the `data/` directory

### Tests failing
- Some tests require API keys (expected)
- Run `python3 test_agent_setup.py` for tests that don't require API keys
- Marketing Agent tests should always pass

## 🎓 Learning Path

1. **Start Simple**: Use Marketing Agent (no API keys needed)
   ```bash
   python3 test_agent_setup.py
   ```

2. **Add API Keys**: Set up `.env` file for Competitor Agent

3. **Add Research**: Place PDFs in `data/` folder for Research Agent

4. **Use Orchestrator**: Combine all agents for full analysis

5. **Build Custom**: Create your own workflows

## 📞 Support

- Check `AGENTS_README.md` for detailed documentation
- Review `examples/agent_usage_examples.py` for code examples
- Run `python3 test_agent_setup.py` to verify setup
- See main `README.md` for project setup

---

**Ready to start? Try this:**

```python
from agents import MarketingAgent

agent = MarketingAgent()
result = agent.execute({
    'product_description': 'Your innovative food product',
    'segment': 'High Essentialist',
    'domain': 'Plant-Based'
})

print(result['data']['messaging']['primary_message'])
```

🎉 **That's it! You're ready to use the agent system!**
