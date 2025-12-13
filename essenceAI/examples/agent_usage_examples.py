"""
Agent System Usage Examples
Demonstrates how to use the essenceAI agent system
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from agents import (
    ResearchAgent,
    CompetitorAgent,
    MarketingAgent,
    AgentOrchestrator
)
from agents.orchestrator import quick_analysis
from agents.agent_config import get_example_tasks, get_agent_capabilities
import json


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_result(result: dict, indent: int = 0):
    """Pretty print a result dictionary."""
    spacing = "  " * indent
    if isinstance(result, dict):
        for key, value in result.items():
            if isinstance(value, (dict, list)):
                print(f"{spacing}{key}:")
                print_result(value, indent + 1)
            else:
                print(f"{spacing}{key}: {value}")
    elif isinstance(result, list):
        for i, item in enumerate(result):
            print(f"{spacing}[{i}]:")
            print_result(item, indent + 1)
    else:
        print(f"{spacing}{result}")


def example_1_individual_agents():
    """Example 1: Using individual agents separately."""
    print_section("Example 1: Using Individual Agents")

    # 1. Competitor Agent
    print("📊 Using Competitor Agent:")
    competitor_agent = CompetitorAgent()

    result = competitor_agent.execute({
        'product_description': 'Plant-based burger for fast-food chains',
        'domain': 'Plant-Based',
        'max_competitors': 5
    })

    if result['status'] == 'success':
        print(f"✓ Found {result['data']['count']} competitors")
        print(f"  Average price: ${result['data']['statistics']['price_stats']['avg']:.2f}")
        print(f"  Average CO2: {result['data']['statistics']['co2_stats']['avg']:.2f} kg/kg")

    # 2. Marketing Agent
    print("\n🎯 Using Marketing Agent:")
    marketing_agent = MarketingAgent()

    result = marketing_agent.execute({
        'product_description': 'Plant-based burger for fast-food chains',
        'segment': 'High Essentialist',
        'domain': 'Plant-Based'
    })

    if result['status'] == 'success':
        strategy = result['data']
        print(f"✓ Strategy generated for {strategy['segment']}")
        print(f"  Primary message: {strategy['messaging']['primary_message']}")
        print(f"  Key channels: {', '.join([c['channel'] for c in strategy['channels'][:3]])}")

    # 3. Research Agent (requires initialization)
    print("\n📚 Using Research Agent:")
    # Use absolute path to data directory
    data_path = Path(__file__).parent.parent / "data"
    research_agent = ResearchAgent(data_dir=str(data_path))

    print("  Initializing research database...")
    if research_agent.initialize():
        result = research_agent.execute({
            'query': 'What are consumer acceptance factors for plant-based meat?',
            'domain': 'Plant-Based',
            'segment': 'High Essentialist'
        })

        if result['status'] == 'success':
            print(f"✓ Research completed")
            print(f"  Citations found: {len(result['data']['citations'])}")
            print(f"  Answer preview: {result['data']['answer'][:150]}...")
    else:
        print("  ⚠ Research database not available (no PDFs found)")


def example_2_orchestrator_full_analysis():
    """Example 2: Using orchestrator for full analysis."""
    print_section("Example 2: Full Analysis with Orchestrator")

    # Use absolute path to data directory
    data_path = Path(__file__).parent.parent / "data"
    orchestrator = AgentOrchestrator(data_dir=str(data_path))

    # Initialize research (optional)
    print("🔄 Initializing research database...")
    orchestrator.initialize_research()

    # Execute full analysis
    print("\n🚀 Executing full market intelligence analysis...")
    result = orchestrator.execute_full_analysis(
        product_description="Precision fermented artisan cheese for European gourmet market",
        domain="Precision Fermentation",
        segment="Skeptic"
    )

    if result['status'] == 'success':
        data = result['data']
        print("\n✓ Analysis Complete!")
        print(f"\n📊 Competitor Intelligence:")
        print(f"  - Competitors found: {data['competitor_intelligence']['count']}")

        if data['research_insights']:
            print(f"\n📚 Research Insights:")
            print(f"  - Citations: {len(data['research_insights']['citations'])}")

        if data['marketing_strategy']:
            print(f"\n🎯 Marketing Strategy:")
            print(f"  - Target segment: {data['marketing_strategy']['segment']}")
            print(f"  - Primary message: {data['marketing_strategy']['messaging']['primary_message']}")


def example_3_competitor_deep_dive():
    """Example 3: Deep dive competitor analysis."""
    print_section("Example 3: Deep Dive Competitor Analysis")

    orchestrator = AgentOrchestrator()

    print("🔍 Executing comprehensive competitor analysis...")
    result = orchestrator.execute_competitor_analysis(
        product_description="Algae-based protein powder for athletes",
        domain="Algae",
        include_pricing=True,
        include_sustainability=True,
        include_gaps=True
    )

    print("\n✓ Analysis Complete!")

    if result['competitors']['status'] == 'success':
        print(f"\n📊 Base Competitor Data:")
        print(f"  - Competitors: {result['competitors']['data']['count']}")

    if 'pricing_analysis' in result and result['pricing_analysis']['status'] == 'success':
        pricing = result['pricing_analysis']['data']
        print(f"\n💰 Pricing Analysis:")
        print(f"  - Min: ${pricing['min_price']:.2f}")
        print(f"  - Max: ${pricing['max_price']:.2f}")
        print(f"  - Avg: ${pricing['avg_price']:.2f}")

    if 'sustainability_analysis' in result and result['sustainability_analysis']['status'] == 'success':
        sustainability = result['sustainability_analysis']['data']
        print(f"\n🌱 Sustainability Analysis:")
        print(f"  - Best CO2: {sustainability['min_co2']:.2f} kg/kg")
        print(f"  - Avg CO2: {sustainability['avg_co2']:.2f} kg/kg")

    if 'market_gaps' in result and result['market_gaps']['status'] == 'success':
        gaps = result['market_gaps']['data']
        print(f"\n🎯 Market Gaps:")
        print(f"  - Premium gap exists: {gaps['premium_segment']['exists']}")
        print(f"  - Budget gap exists: {gaps['budget_segment']['exists']}")


def example_4_segment_comparison():
    """Example 4: Compare strategies across segments."""
    print_section("Example 4: Segment Comparison")

    orchestrator = AgentOrchestrator()

    print("🔍 Comparing marketing strategies across all segments...")
    result = orchestrator.execute_segment_comparison(
        product_description="Plant-based chicken nuggets for families",
        domain="Plant-Based"
    )

    if result['status'] == 'success':
        print("\n✓ Comparison Complete!")

        for segment, strategy in result['data'].items():
            print(f"\n📊 {segment}:")
            print(f"  - Focus: {strategy['segment_profile']['messaging_focus']}")
            print(f"  - Key factors: {', '.join(strategy['segment_profile']['key_factors'][:2])}")
            print(f"  - Top tactic: {strategy['tactics'][0]['tactic']}")


def example_5_quick_analysis():
    """Example 5: Using the quick_analysis convenience function."""
    print_section("Example 5: Quick Analysis Function")

    # Use absolute path to data directory
    data_path = Path(__file__).parent.parent / "data"
    print("🚀 Running quick analysis...")
    result = quick_analysis(
        product_description="Algae-based omega-3 supplement",
        domain="Algae",
        segment="Skeptic",
        data_dir=str(data_path),
        initialize_research=True
    )

    if result['status'] == 'success':
        print("\n✓ Quick Analysis Complete!")
        print(f"  - Workflow ID: {result['workflow']['id']}")
        print(f"  - Agents used: {', '.join(result['agents_used'])}")
        print(f"  - Steps completed: {len(result['workflow']['steps'])}")


def example_6_agent_status():
    """Example 6: Check agent status and capabilities."""
    print_section("Example 6: Agent Status and Capabilities")

    orchestrator = AgentOrchestrator()

    print("📊 Agent Status:")
    status = orchestrator.get_agent_status()
    for agent_name, agent_status in status.items():
        if agent_name != 'research_initialized':
            print(f"\n  {agent_status['name']}:")
            print(f"    - Description: {agent_status['description']}")
            print(f"    - Actions performed: {agent_status['actions_count']}")

    print("\n\n📋 Agent Capabilities:")
    capabilities = get_agent_capabilities()
    for agent_type, info in capabilities.items():
        print(f"\n  {info['name']}:")
        print(f"    - {info['description']}")
        print(f"    - Capabilities:")
        for cap in info['capabilities']:
            print(f"      • {cap}")


def example_7_custom_workflow():
    """Example 7: Building a custom workflow."""
    print_section("Example 7: Custom Workflow")

    print("🔧 Building custom workflow...")

    # Initialize agents
    competitor_agent = CompetitorAgent()
    marketing_agent = MarketingAgent()

    product = "Precision fermented ice cream"
    domain = "Precision Fermentation"

    # Step 1: Get competitor data
    print("\n1️⃣ Gathering competitor intelligence...")
    competitor_result = competitor_agent.execute({
        'product_description': product,
        'domain': domain,
        'max_competitors': 8
    })

    # Step 2: Analyze pricing
    print("2️⃣ Analyzing pricing strategy...")
    pricing_result = competitor_agent.analyze_pricing(product, domain)

    # Step 3: Generate strategies for multiple segments
    print("3️⃣ Generating multi-segment strategies...")
    strategies = {}
    for segment in ["High Essentialist", "Skeptic", "Non-Consumer"]:
        result = marketing_agent.execute({
            'product_description': product,
            'segment': segment,
            'domain': domain,
            'competitor_data': competitor_result.get('data', {})
        })
        if result['status'] == 'success':
            strategies[segment] = result['data']

    print("\n✓ Custom Workflow Complete!")
    print(f"  - Competitors analyzed: {competitor_result['data']['count'] if competitor_result['status'] == 'success' else 0}")
    print(f"  - Strategies generated: {len(strategies)}")

    if pricing_result['status'] == 'success':
        print(f"  - Price range: ${pricing_result['data']['min_price']:.2f} - ${pricing_result['data']['max_price']:.2f}")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("  essenceAI Agent System - Usage Examples")
    print("=" * 80)

    examples = [
        ("Individual Agents", example_1_individual_agents),
        ("Full Analysis with Orchestrator", example_2_orchestrator_full_analysis),
        ("Deep Dive Competitor Analysis", example_3_competitor_deep_dive),
        ("Segment Comparison", example_4_segment_comparison),
        ("Quick Analysis Function", example_5_quick_analysis),
        ("Agent Status and Capabilities", example_6_agent_status),
        ("Custom Workflow", example_7_custom_workflow)
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nRunning Example 1 (Individual Agents)...")
    print("To run other examples, call them directly from this script.\n")

    # Run first example by default
    example_1_individual_agents()

    print("\n" + "=" * 80)
    print("  Examples completed! Check the code for more usage patterns.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
