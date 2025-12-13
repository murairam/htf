"""
Research Agent
Specializes in analyzing scientific papers and extracting research insights
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent
from rag_engine import OptimizedRAGEngine


class ResearchAgent(BaseAgent):
    """
    Agent specialized in scientific research analysis.
    Uses RAG engine to query research papers and extract cited insights.
    """

    def __init__(self, data_dir: str = "data", persist_dir: str = ".storage"):
        """
        Initialize the Research Agent.

        Args:
            data_dir: Directory containing research PDFs
            persist_dir: Directory to store the RAG index
        """
        super().__init__(
            name="ResearchAgent",
            description="Analyzes scientific papers and extracts research-backed insights"
        )
        self.rag_engine = OptimizedRAGEngine(data_dir=data_dir, persist_dir=persist_dir)
        self.index_initialized = False

    def initialize(self, force_reload: bool = False) -> bool:
        """
        Initialize the RAG engine and load research papers.

        Args:
            force_reload: Force rebuild of the index

        Returns:
            True if successful
        """
        try:
            self.rag_engine.initialize_index(force_reload=force_reload)
            self.index_initialized = True
            self.log_action("initialize", {"force_reload": force_reload, "status": "success"})
            return True
        except Exception as e:
            self.log_action("initialize", {"error": str(e), "status": "failed"})
            return False

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a research task.

        Args:
            task: Task dictionary with:
                - query: Research question to answer
                - domain: Optional domain filter (Precision Fermentation, Plant-Based, Algae)
                - segment: Optional consumer segment
                - max_results: Maximum number of citations to return

        Returns:
            Result dictionary with research insights and citations
        """
        if not self.index_initialized:
            return self._create_error_response(
                "RAG engine not initialized. Call initialize() first."
            )

        query = task.get('query')
        if not query:
            return self._create_error_response("No query provided in task")

        domain = task.get('domain')
        segment = task.get('segment')
        max_results = task.get('max_results', 5)

        try:
            # Enhance query with domain and segment context
            enhanced_query = self._enhance_query(query, domain, segment)

            # Query the RAG engine
            response = self.rag_engine.query(enhanced_query)

            # Extract citations
            citations = self.rag_engine.get_citations(response)

            result = {
                'query': query,
                'enhanced_query': enhanced_query,
                'answer': response.response,
                'citations': citations[:max_results],
                'source_nodes': len(response.source_nodes)
            }

            self.log_action("research_query", {
                "query": query,
                "domain": domain,
                "segment": segment,
                "citations_found": len(citations)
            })

            return self._create_success_response(result, "Research completed successfully")

        except Exception as e:
            self.log_action("research_query", {"error": str(e), "query": query})
            return self._create_error_response(str(e), {"query": query})

    def analyze_consumer_acceptance(self, domain: str, segment: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze consumer acceptance factors for a specific domain.

        Args:
            domain: Food innovation domain
            segment: Optional consumer segment

        Returns:
            Analysis results with citations
        """
        query = f"What are the key consumer acceptance factors for {domain} products?"
        if segment:
            query += f" Focus on {segment} consumers."

        return self.execute({
            'query': query,
            'domain': domain,
            'segment': segment
        })

    def get_marketing_insights(self, domain: str, segment: str) -> Dict[str, Any]:
        """
        Get marketing insights for a specific domain and consumer segment.

        Args:
            domain: Food innovation domain
            segment: Consumer segment

        Returns:
            Marketing insights with citations
        """
        query = f"What marketing strategies and messaging work best for {segment} consumers when promoting {domain} products?"

        return self.execute({
            'query': query,
            'domain': domain,
            'segment': segment
        })

    def identify_barriers(self, domain: str) -> Dict[str, Any]:
        """
        Identify barriers to adoption for a specific domain.

        Args:
            domain: Food innovation domain

        Returns:
            Barriers analysis with citations
        """
        query = f"What are the main barriers preventing consumer adoption of {domain} products?"

        return self.execute({
            'query': query,
            'domain': domain
        })

    def _enhance_query(self, query: str, domain: Optional[str], segment: Optional[str]) -> str:
        """
        Enhance the query with domain and segment context.

        Args:
            query: Original query
            domain: Optional domain
            segment: Optional segment

        Returns:
            Enhanced query string
        """
        enhanced = query

        if domain:
            enhanced += f" Context: {domain} products."

        if segment:
            enhanced += f" Target audience: {segment} consumers."

        return enhanced

    def get_available_papers(self) -> List[str]:
        """
        Get list of available research papers.

        Returns:
            List of paper filenames
        """
        if not self.index_initialized:
            return []

        data_dir = Path(self.rag_engine.data_dir)
        if not data_dir.exists():
            return []

        return [f.name for f in data_dir.glob("*.pdf")]
