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
                - product_context: Optional product description for context
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
        product_context = task.get('product_context')
        max_results = task.get('max_results', 5)

        try:
            # Enhance query with domain and segment context
            enhanced_query = self._enhance_query(query, domain, segment)

            # Add product context if provided
            if product_context:
                enhanced_query += f" Specific product: {product_context}"

            # Use get_cited_answer with product context for dynamic results
            answer, citations = self.rag_engine.get_cited_answer(
                enhanced_query,
                use_cache=False,
                product_context=product_context
            )

            result = {
                'query': query,
                'enhanced_query': enhanced_query,
                'answer': answer,
                'citations': citations[:max_results],
                'product_context': product_context
            }

            self.log_action("research_query", {
                "query": query,
                "domain": domain,
                "segment": segment,
                "product_context": product_context,
                "citations_found": len(citations)
            })

            return self._create_success_response(result, "Research completed successfully")

        except Exception as e:
            self.log_action("research_query", {"error": str(e), "query": query})
            return self._create_error_response(str(e), {"query": query})

    def analyze_consumer_acceptance(self, domain: str, segment: Optional[str] = None, product_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze consumer acceptance factors for a specific domain.

        Args:
            domain: Food innovation domain
            segment: Optional consumer segment
            product_context: Optional product description for context

        Returns:
            Analysis results with citations
        """
        query = f"What are the key consumer acceptance factors for {domain} products?"
        if segment:
            query += f" Focus on {segment} consumers."

        return self.execute({
            'query': query,
            'domain': domain,
            'segment': segment,
            'product_context': product_context
        })

    def get_marketing_insights(self, domain: str, segment: str, product_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Get marketing insights for a specific domain and consumer segment.

        Args:
            domain: Food innovation domain
            segment: Consumer segment
            product_context: Optional product description for context

        Returns:
            Marketing insights with citations
        """
        query = f"What marketing strategies and messaging work best for {segment} consumers when promoting {domain} products?"

        return self.execute({
            'query': query,
            'domain': domain,
            'segment': segment,
            'product_context': product_context
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
