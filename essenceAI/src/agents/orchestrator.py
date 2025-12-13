"""
Agent Orchestrator
Coordinates multiple agents to execute complex multi-step tasks
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent
from agents.research_agent import ResearchAgent
from agents.competitor_agent import CompetitorAgent
from agents.marketing_agent import MarketingAgent


class AgentOrchestrator:
    """
    Orchestrates multiple agents to execute complex workflows.
    Manages agent coordination, data flow, and task sequencing.
    """

    def __init__(self, data_dir: str = "data", persist_dir: str = ".storage"):
        """
        Initialize the orchestrator with all available agents.

        Args:
            data_dir: Directory for research PDFs
            persist_dir: Directory for RAG index storage
        """
        self.research_agent = ResearchAgent(data_dir=data_dir, persist_dir=persist_dir)
        self.competitor_agent = CompetitorAgent()
        self.marketing_agent = MarketingAgent()

        self.agents = {
            'research': self.research_agent,
            'competitor': self.competitor_agent,
            'marketing': self.marketing_agent
        }

        self.workflow_history: List[Dict[str, Any]] = []

    def initialize_research(self, force_reload: bool = False) -> bool:
        """
        Initialize the research agent's RAG engine.

        Args:
            force_reload: Force rebuild of the index

        Returns:
            True if successful
        """
        return self.research_agent.initialize(force_reload=force_reload)

    def execute_full_analysis(
        self,
        product_description: str,
        domain: Optional[str] = None,
        segment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a complete market intelligence analysis using all agents.

        Workflow:
        1. Competitor Agent: Gather market intelligence
        2. Research Agent: Extract scientific insights
        3. Marketing Agent: Generate strategy based on data

        Args:
            product_description: Product to analyze
            domain: Optional domain filter
            segment: Optional target segment

        Returns:
            Comprehensive analysis results from all agents
        """
        workflow_id = len(self.workflow_history)
        workflow = {
            'id': workflow_id,
            'product': product_description,
            'domain': domain,
            'segment': segment,
            'steps': []
        }

        try:
            # Step 1: Competitor Intelligence
            print("🔍 Step 1: Gathering competitor intelligence...")
            competitor_result = self.competitor_agent.execute({
                'product_description': product_description,
                'domain': domain,
                'max_competitors': 10
            })
            workflow['steps'].append({
                'agent': 'competitor',
                'status': competitor_result['status'],
                'data': competitor_result
            })

            if competitor_result['status'] != 'success':
                return self._create_workflow_result(workflow, 'partial',
                    "Competitor analysis failed, continuing with available data")

            # Step 2: Research Insights
            print("📚 Step 2: Analyzing research papers...")
            if self.research_agent.index_initialized:
                research_query = f"What are the key consumer acceptance factors and marketing strategies for {product_description}?"
                if domain:
                    research_query += f" in the {domain} sector"
                if segment:
                    research_query += f" targeting {segment} consumers"

                research_result = self.research_agent.execute({
                    'query': research_query,
                    'domain': domain,
                    'segment': segment,
                    'product_context': product_description
                })
                workflow['steps'].append({
                    'agent': 'research',
                    'status': research_result['status'],
                    'data': research_result
                })
            else:
                research_result = {'status': 'skipped', 'message': 'Research agent not initialized'}
                workflow['steps'].append({
                    'agent': 'research',
                    'status': 'skipped',
                    'data': research_result
                })

            # Step 3: Marketing Strategy
            print("🎯 Step 3: Generating marketing strategy...")
            if segment:
                marketing_task = {
                    'product_description': product_description,
                    'segment': segment,
                    'domain': domain,
                    'competitor_data': competitor_result.get('data', {}),
                    'research_insights': research_result.get('data', {}) if research_result['status'] == 'success' else {}
                }
                marketing_result = self.marketing_agent.execute(marketing_task)
                workflow['steps'].append({
                    'agent': 'marketing',
                    'status': marketing_result['status'],
                    'data': marketing_result
                })
            else:
                marketing_result = {'status': 'skipped', 'message': 'No target segment specified'}
                workflow['steps'].append({
                    'agent': 'marketing',
                    'status': 'skipped',
                    'data': marketing_result
                })

            # Compile results
            analysis = {
                'product': product_description,
                'domain': domain,
                'segment': segment,
                'competitor_intelligence': competitor_result.get('data', {}),
                'research_insights': research_result.get('data', {}) if research_result['status'] == 'success' else None,
                'marketing_strategy': marketing_result.get('data', {}) if marketing_result['status'] == 'success' else None,
                'workflow_id': workflow_id
            }

            self.workflow_history.append(workflow)
            return self._create_workflow_result(workflow, 'success', "Full analysis completed", analysis)

        except Exception as e:
            workflow['steps'].append({
                'agent': 'orchestrator',
                'status': 'error',
                'error': str(e)
            })
            self.workflow_history.append(workflow)
            return self._create_workflow_result(workflow, 'error', str(e))

    def execute_competitor_analysis(
        self,
        product_description: str,
        domain: Optional[str] = None,
        include_pricing: bool = True,
        include_sustainability: bool = True,
        include_gaps: bool = True
    ) -> Dict[str, Any]:
        """
        Execute comprehensive competitor analysis.

        Args:
            product_description: Product to analyze
            domain: Optional domain filter
            include_pricing: Include pricing analysis
            include_sustainability: Include sustainability analysis
            include_gaps: Include market gap analysis

        Returns:
            Comprehensive competitor analysis
        """
        results = {
            'product': product_description,
            'domain': domain
        }

        # Base competitor data
        base_result = self.competitor_agent.execute({
            'product_description': product_description,
            'domain': domain
        })
        results['competitors'] = base_result

        # Optional analyses
        if include_pricing and base_result['status'] == 'success':
            results['pricing_analysis'] = self.competitor_agent.analyze_pricing(
                product_description, domain
            )

        if include_sustainability and base_result['status'] == 'success':
            results['sustainability_analysis'] = self.competitor_agent.analyze_sustainability(
                product_description, domain
            )

        if include_gaps and base_result['status'] == 'success':
            results['market_gaps'] = self.competitor_agent.find_market_gaps(
                product_description, domain
            )

        return results

    def execute_research_analysis(
        self,
        domain: str,
        segment: Optional[str] = None,
        include_acceptance: bool = True,
        include_barriers: bool = True,
        include_marketing: bool = True
    ) -> Dict[str, Any]:
        """
        Execute comprehensive research analysis.

        Args:
            domain: Food innovation domain
            segment: Optional consumer segment
            include_acceptance: Include acceptance factors
            include_barriers: Include barrier analysis
            include_marketing: Include marketing insights

        Returns:
            Comprehensive research analysis
        """
        if not self.research_agent.index_initialized:
            return {
                'status': 'error',
                'message': 'Research agent not initialized. Call initialize_research() first.'
            }

        results = {
            'domain': domain,
            'segment': segment
        }

        if include_acceptance:
            results['acceptance_factors'] = self.research_agent.analyze_consumer_acceptance(
                domain, segment
            )

        if include_barriers:
            results['barriers'] = self.research_agent.identify_barriers(domain)

        if include_marketing and segment:
            results['marketing_insights'] = self.research_agent.get_marketing_insights(
                domain, segment
            )

        return results

    def execute_segment_comparison(
        self,
        product_description: str,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare marketing strategies across all consumer segments.

        Args:
            product_description: Product to analyze
            domain: Optional domain filter

        Returns:
            Comparison across all segments
        """
        return self.marketing_agent.compare_segments(product_description, domain)

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get status of all agents.

        Returns:
            Status dictionary for all agents
        """
        return {
            'research': self.research_agent.get_status(),
            'competitor': self.competitor_agent.get_status(),
            'marketing': self.marketing_agent.get_status(),
            'research_initialized': self.research_agent.index_initialized
        }

    def get_workflow_history(self) -> List[Dict[str, Any]]:
        """Get history of all executed workflows."""
        return self.workflow_history

    def clear_history(self):
        """Clear all agent histories and workflow history."""
        for agent in self.agents.values():
            agent.clear_history()
        self.workflow_history = []

    def _create_workflow_result(
        self,
        workflow: Dict[str, Any],
        status: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a standardized workflow result."""
        return {
            'status': status,
            'message': message,
            'workflow': workflow,
            'data': data,
            'agents_used': [step['agent'] for step in workflow['steps']]
        }


# Convenience function for quick analysis
def quick_analysis(
    product_description: str,
    domain: Optional[str] = None,
    segment: Optional[str] = None,
    data_dir: str = "data",
    persist_dir: str = ".storage",
    initialize_research: bool = True
) -> Dict[str, Any]:
    """
    Quick convenience function for full market analysis.

    Args:
        product_description: Product to analyze
        domain: Optional domain filter
        segment: Optional target segment
        data_dir: Directory for research PDFs
        persist_dir: Directory for RAG index
        initialize_research: Whether to initialize research agent

    Returns:
        Complete analysis results
    """
    orchestrator = AgentOrchestrator(data_dir=data_dir, persist_dir=persist_dir)

    if initialize_research:
        print("🔄 Initializing research database...")
        orchestrator.initialize_research()

    print(f"🚀 Analyzing: {product_description}")
    return orchestrator.execute_full_analysis(product_description, domain, segment)
