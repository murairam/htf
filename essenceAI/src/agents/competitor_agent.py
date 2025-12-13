"""
Competitor Agent
Specializes in gathering and analyzing competitor intelligence
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent
from competitor_data import OptimizedCompetitorIntelligence


class CompetitorAgent(BaseAgent):
    """
    Agent specialized in competitor intelligence gathering.
    Uses Tavily API and OpenAI to fetch real-time market data.
    """

    def __init__(self):
        """Initialize the Competitor Agent."""
        super().__init__(
            name="CompetitorAgent",
            description="Gathers and analyzes real-time competitor intelligence"
        )
        self.intelligence = OptimizedCompetitorIntelligence()

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a competitor intelligence task.

        Args:
            task: Task dictionary with:
                - product_description: Product to analyze
                - domain: Optional domain filter
                - max_competitors: Maximum number of competitors to find

        Returns:
            Result dictionary with competitor data
        """
        product_description = task.get('product_description')
        if not product_description:
            return self._create_error_response("No product_description provided in task")

        domain = task.get('domain')
        max_competitors = task.get('max_competitors', 5)

        try:
            # Fetch competitor data
            competitors = self.intelligence.get_competitors(
                product_description=product_description,
                category=domain,
                max_results=max_competitors
            )

            # Calculate statistics
            stats = self._calculate_statistics(competitors)

            result = {
                'product_description': product_description,
                'domain': domain,
                'competitors': competitors,
                'statistics': stats,
                'count': len(competitors)
            }

            self.log_action("competitor_analysis", {
                "product": product_description,
                "domain": domain,
                "competitors_found": len(competitors)
            })

            return self._create_success_response(result, "Competitor analysis completed")

        except Exception as e:
            self.log_action("competitor_analysis", {
                "error": str(e),
                "product": product_description
            })
            return self._create_error_response(str(e), {"product": product_description})

    def analyze_pricing(self, product_description: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze pricing landscape for a product category.

        Args:
            product_description: Product to analyze
            domain: Optional domain filter

        Returns:
            Pricing analysis results
        """
        result = self.execute({
            'product_description': product_description,
            'domain': domain,
            'max_competitors': 10
        })

        if result['status'] != 'success':
            return result

        competitors = result['data']['competitors']
        prices = [c['price_usd'] for c in competitors if c.get('price_usd')]

        if not prices:
            return self._create_error_response("No pricing data available")

        pricing_analysis = {
            'min_price': min(prices),
            'max_price': max(prices),
            'avg_price': sum(prices) / len(prices),
            'median_price': sorted(prices)[len(prices) // 2],
            'price_range': max(prices) - min(prices),
            'sample_size': len(prices)
        }

        return self._create_success_response(pricing_analysis, "Pricing analysis completed")

    def analyze_sustainability(self, product_description: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze sustainability metrics (CO2 emissions) for a product category.

        Args:
            product_description: Product to analyze
            domain: Optional domain filter

        Returns:
            Sustainability analysis results
        """
        result = self.execute({
            'product_description': product_description,
            'domain': domain,
            'max_competitors': 10
        })

        if result['status'] != 'success':
            return result

        competitors = result['data']['competitors']
        co2_values = [c['co2_kg_per_kg'] for c in competitors if c.get('co2_kg_per_kg')]

        if not co2_values:
            return self._create_error_response("No CO2 data available")

        sustainability_analysis = {
            'min_co2': min(co2_values),
            'max_co2': max(co2_values),
            'avg_co2': sum(co2_values) / len(co2_values),
            'median_co2': sorted(co2_values)[len(co2_values) // 2],
            'sample_size': len(co2_values),
            'leaders': [c for c in competitors if c.get('co2_kg_per_kg', float('inf')) <= min(co2_values) * 1.1]
        }

        return self._create_success_response(sustainability_analysis, "Sustainability analysis completed")

    def find_market_gaps(self, product_description: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Identify market gaps and opportunities.

        Args:
            product_description: Product to analyze
            domain: Optional domain filter

        Returns:
            Market gap analysis
        """
        result = self.execute({
            'product_description': product_description,
            'domain': domain,
            'max_competitors': 10
        })

        if result['status'] != 'success':
            return result

        competitors = result['data']['competitors']

        # Analyze market positioning
        gaps = {
            'premium_segment': self._check_premium_gap(competitors),
            'budget_segment': self._check_budget_gap(competitors),
            'sustainability_leaders': self._check_sustainability_gap(competitors),
            'underserved_regions': self._identify_regional_gaps(competitors)
        }

        return self._create_success_response(gaps, "Market gap analysis completed")

    def _calculate_statistics(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics from competitor data."""
        if not competitors:
            return {}

        prices = [c['price_usd'] for c in competitors if c.get('price_usd')]
        co2_values = [c['co2_kg_per_kg'] for c in competitors if c.get('co2_kg_per_kg')]

        stats = {
            'total_competitors': len(competitors),
            'with_pricing': len(prices),
            'with_co2': len(co2_values)
        }

        if prices:
            stats['price_stats'] = {
                'min': min(prices),
                'max': max(prices),
                'avg': sum(prices) / len(prices)
            }

        if co2_values:
            stats['co2_stats'] = {
                'min': min(co2_values),
                'max': max(co2_values),
                'avg': sum(co2_values) / len(co2_values)
            }

        return stats

    def _check_premium_gap(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if there's a gap in the premium segment."""
        prices = [c['price_usd'] for c in competitors if c.get('price_usd')]
        if not prices:
            return {'exists': False}

        avg_price = sum(prices) / len(prices)
        premium_count = len([p for p in prices if p > avg_price * 1.5])

        return {
            'exists': premium_count < len(prices) * 0.2,
            'premium_count': premium_count,
            'total_count': len(prices),
            'threshold': avg_price * 1.5
        }

    def _check_budget_gap(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if there's a gap in the budget segment."""
        prices = [c['price_usd'] for c in competitors if c.get('price_usd')]
        if not prices:
            return {'exists': False}

        avg_price = sum(prices) / len(prices)
        budget_count = len([p for p in prices if p < avg_price * 0.7])

        return {
            'exists': budget_count < len(prices) * 0.2,
            'budget_count': budget_count,
            'total_count': len(prices),
            'threshold': avg_price * 0.7
        }

    def _check_sustainability_gap(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if there's a gap in sustainability leadership."""
        co2_values = [c['co2_kg_per_kg'] for c in competitors if c.get('co2_kg_per_kg')]
        if not co2_values:
            return {'exists': False}

        min_co2 = min(co2_values)
        leaders = [c for c in competitors if c.get('co2_kg_per_kg', float('inf')) <= min_co2 * 1.2]

        return {
            'exists': len(leaders) < 3,
            'current_leaders': len(leaders),
            'best_co2': min_co2
        }

    def _identify_regional_gaps(self, competitors: List[Dict[str, Any]]) -> List[str]:
        """Identify underserved regions (placeholder for future enhancement)."""
        # This would require geographic data from competitors
        return ["Analysis requires geographic data"]
