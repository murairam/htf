"""
Agents Module - Main entry point
This file provides backward compatibility by importing from the modular implementation.

DEPRECATED: Direct use of this monolithic file is deprecated.
Please use the modular agents package:
  - from agents.base_agent import BaseAgent
  - from agents.marketing_agent import MarketingAgent
  - from agents.research_agent import ResearchAgent
  - from agents.competitor_agent import CompetitorAgent
  - from agents.orchestrator import AgentOrchestrator
"""

import warnings

# Import from modular agents package
from .agents.base_agent import BaseAgent
from .agents.marketing_agent import MarketingAgent
from .agents.research_agent import ResearchAgent
from .agents.competitor_agent import CompetitorAgent
from .agents.orchestrator import AgentOrchestrator

# Show deprecation warning
warnings.warn(
    "Importing from 'agents' module is deprecated. "
    "Please use 'from agents.marketing_agent import MarketingAgent' instead.",
    DeprecationWarning,
    stacklevel=2
)

# For backward compatibility, expose all agents
__all__ = [
    'BaseAgent',
    'MarketingAgent',
    'ResearchAgent',
    'CompetitorAgent',
    'AgentOrchestrator'
]
