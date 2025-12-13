"""
Agent Configuration
Configuration settings and utilities for the agent system
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class AgentType(Enum):
    """Available agent types."""
    RESEARCH = "research"
    COMPETITOR = "competitor"
    MARKETING = "marketing"
    ORCHESTRATOR = "orchestrator"


class WorkflowType(Enum):
    """Predefined workflow types."""
    FULL_ANALYSIS = "full_analysis"
    COMPETITOR_ONLY = "competitor_only"
    RESEARCH_ONLY = "research_only"
    MARKETING_ONLY = "marketing_only"
    SEGMENT_COMPARISON = "segment_comparison"


@dataclass
class AgentConfig:
    """Configuration for agent system."""
    
    # Data directories
    data_dir: str = "data"
    persist_dir: str = ".storage"
    
    # LLM settings
    llm_provider: str = "openai"  # "openai" or "anthropic"
    temperature: float = 0.1
    
    # Agent-specific settings
    max_competitors: int = 10
    max_citations: int = 5
    
    # Workflow settings
    enable_parallel_execution: bool = False  # Future enhancement
    timeout_seconds: int = 300
    
    # Logging
    verbose: bool = True
    log_file: str = "agent_logs.txt"


# Default consumer segments
CONSUMER_SEGMENTS = [
    "High Essentialist",
    "Skeptic",
    "Non-Consumer"
]

# Default domains
FOOD_DOMAINS = [
    "Precision Fermentation",
    "Plant-Based",
    "Algae"
]

# Workflow templates
WORKFLOW_TEMPLATES = {
    WorkflowType.FULL_ANALYSIS: {
        "name": "Full Market Intelligence Analysis",
        "description": "Complete analysis using all agents",
        "agents": ["competitor", "research", "marketing"],
        "required_params": ["product_description"],
        "optional_params": ["domain", "segment"]
    },
    WorkflowType.COMPETITOR_ONLY: {
        "name": "Competitor Intelligence Only",
        "description": "Focus on competitor analysis",
        "agents": ["competitor"],
        "required_params": ["product_description"],
        "optional_params": ["domain"]
    },
    WorkflowType.RESEARCH_ONLY: {
        "name": "Research Analysis Only",
        "description": "Focus on scientific research insights",
        "agents": ["research"],
        "required_params": ["domain"],
        "optional_params": ["segment"]
    },
    WorkflowType.MARKETING_ONLY: {
        "name": "Marketing Strategy Only",
        "description": "Focus on marketing strategy generation",
        "agents": ["marketing"],
        "required_params": ["product_description", "segment"],
        "optional_params": ["domain"]
    },
    WorkflowType.SEGMENT_COMPARISON: {
        "name": "Segment Comparison",
        "description": "Compare strategies across all segments",
        "agents": ["marketing"],
        "required_params": ["product_description"],
        "optional_params": ["domain"]
    }
}


def get_workflow_template(workflow_type: WorkflowType) -> Dict[str, Any]:
    """
    Get a workflow template by type.
    
    Args:
        workflow_type: Type of workflow
        
    Returns:
        Workflow template dictionary
    """
    return WORKFLOW_TEMPLATES.get(workflow_type, {})


def validate_task_params(task: Dict[str, Any], required_params: List[str]) -> tuple[bool, str]:
    """
    Validate that a task has all required parameters.
    
    Args:
        task: Task dictionary
        required_params: List of required parameter names
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    missing = [param for param in required_params if param not in task or not task[param]]
    
    if missing:
        return False, f"Missing required parameters: {', '.join(missing)}"
    
    return True, ""


def get_agent_capabilities() -> Dict[str, Dict[str, Any]]:
    """
    Get capabilities of all available agents.
    
    Returns:
        Dictionary mapping agent types to their capabilities
    """
    return {
        "research": {
            "name": "Research Agent",
            "description": "Analyzes scientific papers and extracts research-backed insights",
            "capabilities": [
                "Query research papers with citations",
                "Analyze consumer acceptance factors",
                "Extract marketing insights from research",
                "Identify barriers to adoption"
            ],
            "requires_initialization": True,
            "data_source": "Research PDFs via RAG"
        },
        "competitor": {
            "name": "Competitor Agent",
            "description": "Gathers and analyzes real-time competitor intelligence",
            "capabilities": [
                "Fetch competitor data from web",
                "Analyze pricing landscape",
                "Evaluate sustainability metrics",
                "Identify market gaps"
            ],
            "requires_initialization": False,
            "data_source": "Tavily API + OpenAI"
        },
        "marketing": {
            "name": "Marketing Agent",
            "description": "Generates marketing strategies based on consumer psychology",
            "capabilities": [
                "Generate segment-specific strategies",
                "Create positioning and messaging",
                "Recommend marketing channels",
                "Compare strategies across segments"
            ],
            "requires_initialization": False,
            "data_source": "Consumer psychology research + market data"
        },
        "orchestrator": {
            "name": "Agent Orchestrator",
            "description": "Coordinates multiple agents for complex workflows",
            "capabilities": [
                "Execute multi-agent workflows",
                "Coordinate data flow between agents",
                "Manage task sequencing",
                "Aggregate results from multiple agents"
            ],
            "requires_initialization": False,
            "data_source": "Coordinates other agents"
        }
    }


def get_example_tasks() -> Dict[str, Dict[str, Any]]:
    """
    Get example tasks for each agent type.
    
    Returns:
        Dictionary of example tasks
    """
    return {
        "research": {
            "basic_query": {
                "query": "What are the key consumer acceptance factors for plant-based meat alternatives?",
                "domain": "Plant-Based",
                "segment": "High Essentialist"
            },
            "acceptance_analysis": {
                "domain": "Precision Fermentation",
                "segment": "Skeptic"
            },
            "marketing_insights": {
                "domain": "Algae",
                "segment": "Non-Consumer"
            }
        },
        "competitor": {
            "basic_analysis": {
                "product_description": "Plant-based burger for fast-food chains",
                "domain": "Plant-Based",
                "max_competitors": 10
            },
            "pricing_analysis": {
                "product_description": "Precision fermented cheese",
                "domain": "Precision Fermentation"
            },
            "sustainability_analysis": {
                "product_description": "Algae-based protein powder",
                "domain": "Algae"
            }
        },
        "marketing": {
            "strategy_generation": {
                "product_description": "Precision fermented artisan cheese for European market",
                "segment": "High Essentialist",
                "domain": "Precision Fermentation"
            },
            "segment_comparison": {
                "product_description": "Plant-based chicken nuggets",
                "domain": "Plant-Based"
            }
        },
        "orchestrator": {
            "full_analysis": {
                "product_description": "Algae-based protein bar for athletes",
                "domain": "Algae",
                "segment": "Skeptic"
            },
            "competitor_focus": {
                "product_description": "Plant-based yogurt",
                "domain": "Plant-Based",
                "include_pricing": True,
                "include_sustainability": True,
                "include_gaps": True
            }
        }
    }


# Export configuration
DEFAULT_CONFIG = AgentConfig()
