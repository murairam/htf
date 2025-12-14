"""
essenceAI Agent System
Multi-agent framework for autonomous market intelligence tasks
"""

from .base_agent import BaseAgent
from .research_agent import ResearchAgent
from .competitor_agent import CompetitorAgent
from .marketing_agent import MarketingAgent
from .orchestrator import AgentOrchestrator

__all__ = [
    'BaseAgent',
    'ResearchAgent',
    'CompetitorAgent',
    'MarketingAgent',
    'AgentOrchestrator'
]
