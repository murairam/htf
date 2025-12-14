"""
EssenceAI Module
Imported and adapted from essenceAI/src/ for unified service.
"""

# Re-export main components
try:
    from .agents.orchestrator import AgentOrchestrator
    from .agents.research_agent import ResearchAgent
    from .agents.competitor_agent import CompetitorAgent
    from .agents.marketing_agent import MarketingAgent
    from .rag_engine import OptimizedRAGEngine
    __all__ = [
        'AgentOrchestrator',
        'ResearchAgent',
        'CompetitorAgent',
        'MarketingAgent',
        'OptimizedRAGEngine'
    ]
except ImportError as e:
    # Handle case where dependencies are not available
    __all__ = []
    _import_error = e

