# 🤖 essenceAI Agent System

A multi-agent framework for autonomous market intelligence tasks in the sustainable food sector.

## 📋 Overview

The essenceAI agent system provides specialized AI agents that work together to deliver comprehensive market intelligence:

- **Research Agent**: Analyzes scientific papers and extracts research-backed insights
- **Competitor Agent**: Gathers and analyzes real-time competitor intelligence
- **Marketing Agent**: Generates marketing strategies based on consumer psychology
- **Agent Orchestrator**: Coordinates multiple agents for complex workflows

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Orchestrator                        │
│              (Coordinates multi-agent workflows)             │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐     ┌──────────────┐
│   Research   │      │  Competitor  │     │  Marketing   │
│    Agent     │      │    Agent     │     │    Agent     │
├──────────────┤      ├──────────────┤     ├──────────────┤
│ • RAG Engine │      │ • Tavily API │     │ • Psychology │
│ • Citations  │      │ • OpenAI     │     │ • Segments   │
│ • PDFs       │      │ • Real-time  │     │ • Strategy   │
└──────────────┘      └──────────────┘     └──────────────┘
```

## 🚀 Quick Start

### 1. Basic Setup

```python
from agents import AgentOrchestrator

# Initialize orchestrator
orchestrator = AgentOrchestrator(data_dir="data", persist_dir=".storage")

# Initialize research database (first time only)
orchestrator.initialize_research()
```

### 2. Run Full Analysis

```python
# Execute complete market intelligence analysis
result = orchestrator.execute_full_analysis(
    product_description="Precision fermented artisan cheese",
    domain="Precision Fermentation",
    segment="Skeptic"
)

if result['status'] == 'success':
    data = result['data']
    print(f"Competitors found: {data['competitor_intelligence']['count']}")
    print(f"Research citations: {len(data['research_insights']['citations'])}")
    print(f"Marketing strategy: {data['marketing_strategy']['segment']}")
```

### 3. Quick Analysis (One-liner)

```python
from agents.orchestrator import quick_analysis

result = quick_analysis(
    product_description="Algae-based protein bar",
    domain="Algae",
    segment="High Essentialist"
)
```

## 🎯 Individual Agents

### Research Agent

Analyzes scientific papers using RAG (Retrieval-Augmented Generation).

```python
from agents import ResearchAgent

# Initialize
research_agent = ResearchAgent(data_dir="data")
research_agent.initialize()

# Query research papers
result = research_agent.execute({
    'query': 'What are consumer acceptance factors for plant-based meat?',
    'domain': 'Plant-Based',
    'segment': 'High Essentialist'
})

# Specialized methods
acceptance = research_agent.analyze_consumer_acceptance("Plant-Based", "Skeptic")
insights = research_agent.get_marketing_insights("Algae", "Non-Consumer")
barriers = research_agent.identify_barriers("Precision Fermentation")
```

**Key Features:**
- ✅ Cites scientific sources
- ✅ Extracts research insights
- ✅ Analyzes consumer acceptance
- ✅ Identifies barriers

### Competitor Agent

Gathers real-time market intelligence.

```python
from agents import CompetitorAgent

competitor_agent = CompetitorAgent()

# Basic competitor analysis
result = competitor_agent.execute({
    'product_description': 'Plant-based burger',
    'domain': 'Plant-Based',
    'max_competitors': 10
})

# Specialized analyses
pricing = competitor_agent.analyze_pricing("Plant-based burger", "Plant-Based")
sustainability = competitor_agent.analyze_sustainability("Algae protein", "Algae")
gaps = competitor_agent.find_market_gaps("Fermented cheese", "Precision Fermentation")
```

**Key Features:**
- ✅ Real-time competitor data
- ✅ Pricing analysis
- ✅ Sustainability metrics (CO2)
- ✅ Market gap identification

### Marketing Agent

Generates marketing strategies based on consumer psychology.

```python
from agents import MarketingAgent

marketing_agent = MarketingAgent()

# Generate strategy for specific segment
result = marketing_agent.execute({
    'product_description': 'Precision fermented ice cream',
    'segment': 'High Essentialist',
    'domain': 'Precision Fermentation',
    'competitor_data': {},  # Optional
    'research_insights': {}  # Optional
})

# Compare across all segments
comparison = marketing_agent.compare_segments(
    product="Plant-based chicken nuggets",
    domain="Plant-Based"
)
```

**Key Features:**
- ✅ Segment-specific strategies
- ✅ Positioning & messaging
- ✅ Channel recommendations
- ✅ Tactical guidance

**Available Segments:**
- **High Essentialist**: Values sensory mimicry
- **Skeptic**: Values naturalness and transparency
- **Non-Consumer**: Fears unfamiliar foods

## 🎼 Orchestrator Workflows

### Full Analysis

Complete market intelligence using all agents.

```python
result = orchestrator.execute_full_analysis(
    product_description="Algae-based omega-3 supplement",
    domain="Algae",
    segment="Skeptic"
)
```

**Workflow:**
1. Competitor Agent → Gather market data
2. Research Agent → Extract scientific insights
3. Marketing Agent → Generate strategy

### Competitor Deep Dive

Comprehensive competitor analysis.

```python
result = orchestrator.execute_competitor_analysis(
    product_description="Plant-based yogurt",
    domain="Plant-Based",
    include_pricing=True,
    include_sustainability=True,
    include_gaps=True
)
```

### Research Deep Dive

Comprehensive research analysis.

```python
result = orchestrator.execute_research_analysis(
    domain="Precision Fermentation",
    segment="High Essentialist",
    include_acceptance=True,
    include_barriers=True,
    include_marketing=True
)
```

### Segment Comparison

Compare strategies across all consumer segments.

```python
result = orchestrator.execute_segment_comparison(
    product_description="Fermented dairy alternative",
    domain="Precision Fermentation"
)
```

## 📊 Response Format

All agents return standardized responses:

```python
{
    'status': 'success',  # or 'error'
    'agent': 'AgentName',
    'message': 'Task completed successfully',
    'data': {
        # Agent-specific results
    },
    'timestamp': '2025-12-13T10:30:00'
}
```

## 🔧 Configuration

### Agent Configuration

```python
from agents.agent_config import AgentConfig

config = AgentConfig(
    data_dir="data",
    persist_dir=".storage",
    llm_provider="openai",  # or "anthropic"
    temperature=0.1,
    max_competitors=10,
    max_citations=5,
    verbose=True
)
```

### Environment Variables

Create a `.env` file:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional
TAVILY_API_KEY=tvly-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# LLM Provider
LLM_PROVIDER=openai  # or "anthropic"
```

## 📚 Examples

See `examples/agent_usage_examples.py` for comprehensive examples:

```bash
cd essenceAI
python examples/agent_usage_examples.py
```

**Available Examples:**
1. Individual Agents
2. Full Analysis with Orchestrator
3. Deep Dive Competitor Analysis
4. Segment Comparison
5. Quick Analysis Function
6. Agent Status and Capabilities
7. Custom Workflow

## 🧪 Testing

Run agent tests:

```bash
cd essenceAI
pytest tests/test_agents.py -v
```

## 🎯 Use Cases

### 1. Product Launch Planning

```python
# Analyze market before launching new product
result = orchestrator.execute_full_analysis(
    product_description="Precision fermented mozzarella for pizza chains",
    domain="Precision Fermentation",
    segment="High Essentialist"
)

# Get competitor landscape
competitors = result['data']['competitor_intelligence']

# Get research-backed strategy
strategy = result['data']['marketing_strategy']
```

### 2. Competitive Intelligence

```python
# Monitor competitor landscape
result = orchestrator.execute_competitor_analysis(
    product_description="Plant-based protein powder",
    domain="Plant-Based",
    include_pricing=True,
    include_sustainability=True,
    include_gaps=True
)

# Identify market opportunities
gaps = result['market_gaps']['data']
```

### 3. Marketing Strategy Development

```python
# Compare strategies across segments
result = orchestrator.execute_segment_comparison(
    product_description="Algae-based snack bar",
    domain="Algae"
)

# Choose best segment to target
for segment, strategy in result['data'].items():
    print(f"{segment}: {strategy['positioning']}")
```

### 4. Research Insights

```python
# Extract research insights for specific domain
result = orchestrator.execute_research_analysis(
    domain="Precision Fermentation",
    segment="Skeptic",
    include_acceptance=True,
    include_barriers=True,
    include_marketing=True
)

# Get cited recommendations
insights = result['research_insights']['data']
```

## 🔍 Agent Status & History

### Check Agent Status

```python
status = orchestrator.get_agent_status()
print(status)
```

### View Workflow History

```python
history = orchestrator.get_workflow_history()
for workflow in history:
    print(f"Workflow {workflow['id']}: {workflow['product']}")
    print(f"  Steps: {len(workflow['steps'])}")
```

### Clear History

```python
orchestrator.clear_history()
```

## 🚧 Advanced Usage

### Custom Workflow

Build your own multi-agent workflow:

```python
from agents import ResearchAgent, CompetitorAgent, MarketingAgent

# Initialize agents
research = ResearchAgent(data_dir="data")
competitor = CompetitorAgent()
marketing = MarketingAgent()

# Step 1: Research
research.initialize()
research_result = research.analyze_consumer_acceptance("Plant-Based", "Skeptic")

# Step 2: Competitors
competitor_result = competitor.execute({
    'product_description': 'Plant-based burger',
    'domain': 'Plant-Based'
})

# Step 3: Marketing
marketing_result = marketing.execute({
    'product_description': 'Plant-based burger',
    'segment': 'Skeptic',
    'domain': 'Plant-Based',
    'competitor_data': competitor_result.get('data', {}),
    'research_insights': research_result.get('data', {})
})
```

### Parallel Execution (Future)

```python
# Coming soon: Parallel agent execution
config = AgentConfig(enable_parallel_execution=True)
```

## 📖 API Reference

### BaseAgent

All agents inherit from `BaseAgent`:

```python
class BaseAgent(ABC):
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]
    def log_action(self, action: str, details: Dict[str, Any])
    def get_history(self) -> List[Dict[str, Any]]
    def clear_history()
    def get_status() -> Dict[str, Any]
```

### ResearchAgent

```python
class ResearchAgent(BaseAgent):
    def initialize(self, force_reload: bool = False) -> bool
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]
    def analyze_consumer_acceptance(self, domain: str, segment: Optional[str]) -> Dict
    def get_marketing_insights(self, domain: str, segment: str) -> Dict
    def identify_barriers(self, domain: str) -> Dict
    def get_available_papers(self) -> List[str]
```

### CompetitorAgent

```python
class CompetitorAgent(BaseAgent):
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]
    def analyze_pricing(self, product: str, domain: Optional[str]) -> Dict
    def analyze_sustainability(self, product: str, domain: Optional[str]) -> Dict
    def find_market_gaps(self, product: str, domain: Optional[str]) -> Dict
```

### MarketingAgent

```python
class MarketingAgent(BaseAgent):
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]
    def get_segment_profiles(self) -> Dict[str, Dict[str, Any]]
    def compare_segments(self, product: str, domain: Optional[str]) -> Dict
```

### AgentOrchestrator

```python
class AgentOrchestrator:
    def initialize_research(self, force_reload: bool = False) -> bool
    def execute_full_analysis(self, product: str, domain: Optional[str], segment: Optional[str]) -> Dict
    def execute_competitor_analysis(self, product: str, domain: Optional[str], ...) -> Dict
    def execute_research_analysis(self, domain: str, segment: Optional[str], ...) -> Dict
    def execute_segment_comparison(self, product: str, domain: Optional[str]) -> Dict
    def get_agent_status(self) -> Dict[str, Any]
    def get_workflow_history(self) -> List[Dict[str, Any]]
    def clear_history()
```

## 🤝 Contributing

To add a new agent:

1. Create a new file in `src/agents/`
2. Inherit from `BaseAgent`
3. Implement the `execute()` method
4. Add to `__init__.py`
5. Update orchestrator if needed

## 📝 License

Part of the essenceAI project - Built for Hack the Fork 2025

## 🆘 Support

For issues or questions:
- Check `examples/agent_usage_examples.py`
- Review `tests/test_agents.py`
- See main `README.md` for project setup

---

**Built with ❤️ for sustainable food innovation**
