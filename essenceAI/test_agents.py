"""
Test script for Agent System
Demonstrates CompetitorAgent and CodeAgent functionality
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from agents import get_agent_manager, TaskStatus


def test_competitor_agent():
    """Test CompetitorAgent with various tasks."""
    print("\n" + "="*60)
    print("TESTING COMPETITOR AGENT")
    print("="*60)

    manager = get_agent_manager()

    # Test 1: Competitor Research
    print("\n[Test 1] Competitor Research Task")
    print("-" * 60)

    task1 = manager.create_task(
        task_type="competitor_research",
        description="Research competitors for plant-based burger market",
        parameters={
            "product_concept": "Plant-based burger for fast-food chains",
            "category": "Plant-Based",
            "max_results": 5
        },
        priority=8
    )

    print(f"Created task: {task1.task_id}")
    print(f"Description: {task1.description}")

    # Execute task
    result_task = manager.execute_task(task1.task_id)

    print(f"\nTask Status: {result_task.status.value}")
    if result_task.status == TaskStatus.COMPLETED:
        print(f"✅ Task completed successfully!")
        print(f"Found {result_task.result['count']} competitors")
        print("\nTop 3 Competitors:")
        for i, comp in enumerate(result_task.result['competitors'][:3], 1):
            print(f"  {i}. {comp['Company']} - {comp['Product']}")
            print(f"     Price: €{comp['Price (€/kg)']}/kg | CO₂: {comp['CO₂ (kg)']} kg")
    else:
        print(f"❌ Task failed: {result_task.error}")

    print("\nTask Logs:")
    for log in result_task.logs:
        print(f"  {log}")

    # Test 2: Market Analysis
    print("\n[Test 2] Market Analysis Task")
    print("-" * 60)

    task2 = manager.create_task(
        task_type="market_analysis",
        description="Analyze plant-based protein market",
        parameters={
            "product_concept": "Plant-based protein powder",
            "category": "Plant-Based",
            "max_results": 8
        },
        priority=7
    )

    print(f"Created task: {task2.task_id}")
    result_task2 = manager.execute_task(task2.task_id)

    print(f"\nTask Status: {result_task2.status.value}")
    if result_task2.status == TaskStatus.COMPLETED:
        print(f"✅ Market analysis completed!")
        analysis = result_task2.result
        print(f"\nMarket Size: {analysis['market_size']} competitors")
        print(f"Price Range: €{analysis['price_stats']['min']:.2f} - €{analysis['price_stats']['max']:.2f}/kg")
        print(f"Average Price: €{analysis['price_stats']['avg']:.2f}/kg")
        print(f"\nMarket Insights:")
        for insight in analysis['market_insights']:
            print(f"  • {insight}")

    # Test 3: Pricing Analysis
    print("\n[Test 3] Pricing Analysis Task")
    print("-" * 60)

    task3 = manager.create_task(
        task_type="pricing_analysis",
        description="Analyze pricing strategies in precision fermentation market",
        parameters={
            "product_concept": "Precision fermented cheese",
            "category": "Precision Fermentation",
            "max_results": 5
        },
        priority=6
    )

    print(f"Created task: {task3.task_id}")
    result_task3 = manager.execute_task(task3.task_id)

    print(f"\nTask Status: {result_task3.status.value}")
    if result_task3.status == TaskStatus.COMPLETED:
        print(f"✅ Pricing analysis completed!")
        pricing = result_task3.result
        print("\nPrice Segments:")
        for segment, data in pricing['price_segments'].items():
            print(f"  {segment.upper()}: {data['count']} competitors ({data['range']})")
        print(f"\nRecommendation: {pricing['pricing_strategy_recommendation']}")


def test_code_agent():
    """Test CodeAgent with various tasks."""
    print("\n" + "="*60)
    print("TESTING CODE AGENT")
    print("="*60)

    manager = get_agent_manager()

    # Test 1: Code Generation
    print("\n[Test 1] Code Generation Task")
    print("-" * 60)

    task1 = manager.create_task(
        task_type="generate_code",
        description="Generate Python function to calculate CO2 savings",
        parameters={
            "prompt": "Create a Python function that calculates CO2 savings when switching from traditional meat to plant-based alternatives. Include parameters for meat type, quantity, and alternative type.",
            "language": "python"
        },
        priority=7
    )

    print(f"Created task: {task1.task_id}")
    print(f"Description: {task1.description}")

    # Note: This will only work if BLACKBOX_API_KEY is set
    result_task = manager.execute_task(task1.task_id)

    print(f"\nTask Status: {result_task.status.value}")
    if result_task.status == TaskStatus.COMPLETED:
        print(f"✅ Code generated successfully!")
        print(f"\nGenerated Code ({result_task.result['language']}):")
        print("-" * 60)
        print(result_task.result['code'][:500] + "..." if len(result_task.result['code']) > 500 else result_task.result['code'])
    else:
        print(f"⚠️ Task failed: {result_task.error}")
        if "BLACKBOX_API_KEY" in str(result_task.error):
            print("\n💡 Tip: Set BLACKBOX_API_KEY in your .env file to test CodeAgent")

    # Test 2: Code Analysis
    print("\n[Test 2] Code Analysis Task")
    print("-" * 60)

    sample_code = """
def calculate_price(quantity, base_price):
    total = quantity * base_price
    if quantity > 100:
        total = total * 0.9
    return total
"""

    task2 = manager.create_task(
        task_type="analyze_code",
        description="Review pricing calculation function",
        parameters={
            "code": sample_code,
            "analysis_type": "review"
        },
        priority=5
    )

    print(f"Created task: {task2.task_id}")
    result_task2 = manager.execute_task(task2.task_id)

    print(f"\nTask Status: {result_task2.status.value}")
    if result_task2.status == TaskStatus.COMPLETED:
        print(f"✅ Code analysis completed!")
        print(f"\nAnalysis:")
        print(result_task2.result['analysis'][:300] + "..." if len(result_task2.result['analysis']) > 300 else result_task2.result['analysis'])
    else:
        print(f"⚠️ Task failed: {result_task2.error}")


def test_system_stats():
    """Display system statistics."""
    print("\n" + "="*60)
    print("SYSTEM STATISTICS")
    print("="*60)

    manager = get_agent_manager()
    stats = manager.get_system_stats()

    print(f"\nTotal Agents: {stats['total_agents']}")
    print(f"Total Tasks: {stats['total_tasks']}")
    print(f"  ✅ Completed: {stats['tasks_completed']}")
    print(f"  ❌ Failed: {stats['tasks_failed']}")
    print(f"  🔄 Running: {stats['tasks_running']}")
    print(f"  ⏳ Pending: {stats['tasks_pending']}")

    print("\nAgent Details:")
    for agent_stat in stats['agents']:
        print(f"\n  {agent_stat['name']} ({agent_stat['agent_id']})")
        print(f"    Tasks Completed: {agent_stat['tasks_completed']}")
        print(f"    Tasks Failed: {agent_stat['tasks_failed']}")
        print(f"    Status: {'🔴 Busy' if agent_stat['is_busy'] else '🟢 Available'}")


def test_quality_agent():
    """Test QualityAgent with various tasks."""
    print("\n" + "="*60)
    print("TESTING QUALITY AGENT")
    print("="*60)

    manager = get_agent_manager()

    # Test 1: Code Quality Check
    print("\n[Test 1] Code Quality Check Task")
    print("-" * 60)

    sample_code = """
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price']
    return total

def get_user_data(user_id):
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    return db.execute(query)
"""

    task1 = manager.create_task(
        task_type="check_code_quality",
        description="Check code quality for pricing calculator",
        parameters={
            "code": sample_code,
            "language": "python"
        },
        priority=8
    )

    print(f"Created task: {task1.task_id}")
    result_task = manager.execute_task(task1.task_id)

    print(f"\nTask Status: {result_task.status.value}")
    if result_task.status == TaskStatus.COMPLETED:
        print(f"✅ Quality check completed!")
        print(f"Total Issues: {result_task.result['total_issues']}")
        print(f"Critical Issues: {result_task.result['critical_issues']}")
        print(f"High Issues: {result_task.result['high_issues']}")
    else:
        print(f"⚠️ Task failed: {result_task.error}")
        if "BLACKBOX_API_KEY" in str(result_task.error):
            print("\n💡 Tip: Set BLACKBOX_API_KEY in your .env file to test QualityAgent")

    # Test 2: Find Bugs
    print("\n[Test 2] Bug Detection Task")
    print("-" * 60)

    buggy_code = """
def divide_numbers(a, b):
    return a / b

def get_first_item(items):
    return items[0]

def process_data(data):
    result = []
    for i in range(len(data) + 1):
        result.append(data[i])
    return result
"""

    task2 = manager.create_task(
        task_type="find_bugs",
        description="Find bugs in utility functions",
        parameters={
            "code": buggy_code,
            "context": "These are utility functions used in production"
        },
        priority=9
    )

    print(f"Created task: {task2.task_id}")
    result_task2 = manager.execute_task(task2.task_id)

    print(f"\nTask Status: {result_task2.status.value}")
    if result_task2.status == TaskStatus.COMPLETED:
        print(f"✅ Bug detection completed!")
        print(f"\nBug Analysis Preview:")
        print(result_task2.result['bug_analysis'][:300] + "...")
    else:
        print(f"⚠️ Task failed: {result_task2.error}")

    # Test 3: Analyze Logs
    print("\n[Test 3] Log Analysis Task")
    print("-" * 60)

    sample_logs = """
2025-01-15 10:23:45 INFO Starting application
2025-01-15 10:23:46 INFO Database connected
2025-01-15 10:24:12 ERROR Failed to fetch user data: Connection timeout
2025-01-15 10:24:15 WARNING Retry attempt 1/3
2025-01-15 10:24:18 ERROR Failed to fetch user data: Connection timeout
2025-01-15 10:24:21 WARNING Retry attempt 2/3
2025-01-15 10:24:24 ERROR Failed to fetch user data: Connection timeout
2025-01-15 10:24:27 ERROR Max retries exceeded
2025-01-15 10:25:00 INFO Request processed successfully
2025-01-15 10:25:30 ERROR NullPointerException in payment processing
2025-01-15 10:26:00 WARNING High memory usage: 85%
"""

    task3 = manager.create_task(
        task_type="analyze_logs",
        description="Analyze application logs for issues",
        parameters={
            "logs": sample_logs
        },
        priority=7
    )

    print(f"Created task: {task3.task_id}")
    result_task3 = manager.execute_task(task3.task_id)

    print(f"\nTask Status: {result_task3.status.value}")
    if result_task3.status == TaskStatus.COMPLETED:
        print(f"✅ Log analysis completed!")
        print(f"Analyzed {result_task3.result['log_size']} characters of logs")
    else:
        print(f"⚠️ Task failed: {result_task3.error}")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("AGENT SYSTEM TEST SUITE")
    print("="*60)
    print("\nThis script demonstrates the agent system capabilities:")
    print("  • CompetitorAgent: Market research and analysis")
    print("  • CodeAgent: Code generation and analysis")
    print("  • QualityAgent: Code quality, bug detection, log analysis")
    print("\nNote: CodeAgent and QualityAgent require BLACKBOX_API_KEY in .env file")

    try:
        # Test CompetitorAgent (works without Blackbox API)
        test_competitor_agent()

        # Test CodeAgent (requires Blackbox API key)
        test_code_agent()

        # Test QualityAgent (requires Blackbox API key)
        test_quality_agent()

        # Show system statistics
        test_system_stats()

        print("\n" + "="*60)
        print("TEST SUITE COMPLETED")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
