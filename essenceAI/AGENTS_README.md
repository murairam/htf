# Agent System Documentation

## Overview

The essenceAI agent system provides intelligent automation for market research, competitor analysis, and technical tasks. It consists of specialized agents that can work independently or be coordinated for complex workflows.

## Architecture

### Components

1. **Blackbox AI Client** (`src/blackbox_client.py`)
   - API wrapper for Blackbox AI
   - Handles code generation, analysis, and data processing
   - Implements caching to reduce API costs

2. **Agent System** (`src/agents.py`)
   - Base agent framework
   - Specialized agent implementations
   - Task management and coordination

3. **Agent Manager**
   - Coordinates multiple agents
   - Manages task queue and execution
   - Tracks system statistics

## Available Agents

### 1. CompetitorAgent

**Purpose:** Market research and competitor analysis

**Capabilities:**
- `competitor_research`: Find and analyze competitors
- `market_analysis`: Comprehensive market landscape analysis
- `pricing_analysis`: Pricing strategy analysis and recommendations
- `competitor_comparison`: Compare specific competitors

**Example Usage:**
```python
from agents import get_agent_manager

manager = get_agent_manager()

# Create competitor research task
task = manager.create_task(
    task_type="competitor_research",
    description="Research plant-based burger competitors",
    parameters={
        "product_concept": "Plant-based burger for fast-food",
        "category": "Plant-Based",
        "max_results": 10
    },
    priority=8
)

# Execute task
result = manager.execute_task(task.task_id)

# Access results
if result.status == TaskStatus.COMPLETED:
    competitors = result.result['competitors']
    print(f"Found {len(competitors)} competitors")
```

### 2. CodeAgent

**Purpose:** Code generation and technical automation

**Capabilities:**
- `generate_code`: Generate code from natural language descriptions
- `analyze_code`: Review code for best practices and issues
- `optimize_code`: Suggest code optimizations
- `debug_code`: Debug code and identify issues
- `data_processing`: Process and analyze data

**Example Usage:**
```python
# Generate code
task = manager.create_task(
    task_type="generate_code",
    description="Create CO2 calculator function",
    parameters={
        "prompt": "Create a Python function to calculate CO2 savings",
        "language": "python"
    }
)

result = manager.execute_task(task.task_id)
generated_code = result.result['code']

# Analyze code
task = manager.create_task(
    task_type="analyze_code",
    description="Review pricing function",
    parameters={
        "code": my_code,
        "analysis_type": "review"  # or "optimize", "debug", "explain"
    }
)
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key  # Optional
BLACKBOX_API_KEY=your_blackbox_key  # Required for CodeAgent
```

**Getting API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Tavily: https://tavily.com (optional, for real-time web search)
- Blackbox AI: https://www.blackbox.ai/api

### 3. Test the System

```bash
python test_agents.py
```

## Task Management

### Creating Tasks

```python
from agents import get_agent_manager

manager = get_agent_manager()

task = manager.create_task(
    task_type="competitor_research",  # Task type
    description="Research competitors",  # Human-readable description
    parameters={  # Task-specific parameters
        "product_concept": "...",
        "category": "Plant-Based"
    },
    priority=5  # 1-10, higher = more important
)
```

### Task Status

Tasks go through these states:
- `PENDING`: Created but not started
- `RUNNING`: Currently being executed
- `COMPLETED`: Successfully finished
- `FAILED`: Execution failed
- `CANCELLED`: Manually cancelled

### Accessing Results

```python
# Execute task
result = manager.execute_task(task.task_id)

# Check status
if result.status == TaskStatus.COMPLETED:
    # Access result data
    data = result.result

    # View logs
    for log in result.logs:
        print(log)
else:
    # Handle error
    print(f"Error: {result.error}")
```

## System Statistics

```python
# Get overall system stats
stats = manager.get_system_stats()
print(f"Total agents: {stats['total_agents']}")
print(f"Tasks completed: {stats['tasks_completed']}")

# Get agent-specific stats
for agent_stat in stats['agents']:
    print(f"{agent_stat['name']}: {agent_stat['tasks_completed']} completed")
```

## Advanced Usage

### Custom Task Parameters

#### CompetitorAgent Parameters

**competitor_research:**
```python
{
    "product_concept": str,  # Product description
    "category": str,  # "Plant-Based", "Precision Fermentation", "Algae"
    "max_results": int  # Number of competitors to find
}
```

**market_analysis:**
```python
{
    "product_concept": str,
    "category": str,
    "max_results": int
}
```

**pricing_analysis:**
```python
{
    "product_concept": str,
    "category": str,
    "max_results": int
}
```

**competitor_comparison:**
```python
{
    "product_concept": str,
    "category": str,
    "competitor_names": List[str]  # Specific companies to compare
}
```

#### CodeAgent Parameters

**generate_code:**
```python
{
    "prompt": str,  # Code generation prompt
    "language": str  # "python", "javascript", etc.
}
```

**analyze_code:**
```python
{
    "code": str,  # Code to analyze
    "analysis_type": str  # "review", "optimize", "debug", "explain"
}
```

**data_processing:**
```python
{
    "data": Any,  # Data to process (dict, list, etc.)
    "task": str  # Processing task description
}
```

## Caching

Both agents implement intelligent caching:

- **CompetitorAgent**: Caches competitor data in SQLite database (24h default)
- **CodeAgent**: Caches Blackbox AI responses to disk

This reduces API costs by 80-90% for repeated queries.

### Clear Cache

```python
# Clear Blackbox AI cache
from blackbox_client import get_blackbox_client
client = get_blackbox_client()
client.clear_cache()

# Clear competitor cache
from competitor_data import OptimizedCompetitorIntelligence
intel = OptimizedCompetitorIntelligence()
# Cache is automatically managed by database
```

## Error Handling

Agents handle errors gracefully:

```python
result = manager.execute_task(task_id)

if result.status == TaskStatus.FAILED:
    print(f"Task failed: {result.error}")

    # Check logs for details
    for log in result.logs:
        print(log)
```

Common errors:
- Missing API keys
- Network issues
- Invalid parameters
- Rate limits

## Performance Tips

1. **Use Caching**: Enable caching for repeated queries
2. **Batch Tasks**: Create multiple tasks and execute in sequence
3. **Set Priorities**: Higher priority tasks execute first
4. **Monitor Stats**: Track API usage to optimize costs

## Integration with Streamlit App

The agent system can be integrated into the main Streamlit app:

```python
import streamlit as st
from agents import get_agent_manager

# Initialize manager
manager = get_agent_manager()

# Create task from user input
if st.button("Analyze Competitors"):
    task = manager.create_task(
        task_type="competitor_research",
        description=f"Research {product_concept}",
        parameters={
            "product_concept": product_concept,
            "category": category,
            "max_results": 10
        }
    )

    # Execute and show results
    with st.spinner("Analyzing competitors..."):
        result = manager.execute_task(task.task_id)

    if result.status == TaskStatus.COMPLETED:
        st.success("Analysis complete!")
        st.json(result.result)
```

## Troubleshooting

### "BLACKBOX_API_KEY not found"
- Add your Blackbox AI API key to `.env` file
- CodeAgent requires this key to function

### "No available agent can handle this task"
- Check task_type matches available agent capabilities
- Ensure agent is not busy with another task

### "API connection error"
- Check internet connection
- Verify API keys are valid
- Check API service status

### Cache issues
- Delete `.cache` directory to clear all caches
- Check disk space for cache storage

## Future Enhancements

Planned features:
- [ ] More specialized agents (MarketingAgent, ResearchAgent)
- [ ] Multi-agent coordination for complex workflows
- [ ] Task dependencies and pipelines
- [ ] Real-time progress updates
- [ ] Agent learning from past tasks
- [ ] Custom agent creation API

## Support

For issues or questions:
1. Check this documentation
2. Review `test_agents.py` for examples
3. Check logs in `logs/` directory
4. Review task logs for specific errors

## License

Part of essenceAI - Hack the Fork 2025
