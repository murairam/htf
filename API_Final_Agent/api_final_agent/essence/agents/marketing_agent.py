"""
Marketing Agent
Specializes in generating marketing strategies based on consumer psychology
"""

from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv

from .base_agent import BaseAgent

load_dotenv()


class MarketingAgent(BaseAgent):
    """
    Agent specialized in marketing strategy generation.
    Uses consumer psychology research and market data to create targeted strategies.
    """

    # Consumer segment profiles based on Food Essentialism research
    SEGMENT_PROFILES = {
        "High Essentialist": {
            "description": "Values sensory mimicry and authentic taste/texture",
            "key_factors": ["Taste similarity", "Texture match", "Sensory experience"],
            "messaging_focus": "Indistinguishable from traditional products",
            "concerns": ["Authenticity", "Sensory quality"],
            "opportunities": ["High acceptance if product mimics well"]
        },
        "Skeptic": {
            "description": "Values naturalness and transparency about origins",
            "key_factors": ["Natural ingredients", "Minimal processing", "Transparency"],
            "messaging_focus": "Natural, simple, transparent production",
            "concerns": ["Over-processing", "Artificial ingredients", "Lack of transparency"],
            "opportunities": ["Open labeling", "Natural positioning"]
        },
        "Non-Consumer": {
            "description": "Fears unfamiliar and heavily processed foods",
            "key_factors": ["Familiarity", "Simplicity", "Trust"],
            "messaging_focus": "Familiar formats, trusted brands, gradual introduction",
            "concerns": ["Novelty", "Complexity", "Unknown risks"],
            "opportunities": ["Habituation", "Familiar product formats", "Brand trust"]
        }
    }

    def __init__(self):
        """Initialize the Marketing Agent."""
        super().__init__(
            name="MarketingAgent",
            description="Generates marketing strategies based on consumer psychology"
        )

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a marketing strategy task.

        Args:
            task: Task dictionary with:
                - product_description: Product to market
                - segment: Target consumer segment
                - domain: Optional domain
                - competitor_data: Optional competitor insights
                - research_insights: Optional research findings

        Returns:
            Result dictionary with marketing strategy
        """
        product_description = task.get('product_description')
        segment = task.get('segment')

        if not product_description:
            return self._create_error_response("No product_description provided")

        if not segment:
            return self._create_error_response("No target segment provided")

        if segment not in self.SEGMENT_PROFILES:
            return self._create_error_response(
                f"Unknown segment: {segment}. Available: {list(self.SEGMENT_PROFILES.keys())}"
            )

        try:
            domain = task.get('domain')
            competitor_data = task.get('competitor_data', {})
            research_insights = task.get('research_insights', {})

            # Generate strategy
            strategy = self._generate_strategy(
                product_description,
                segment,
                domain,
                competitor_data,
                research_insights
            )

            self.log_action("strategy_generation", {
                "product": product_description,
                "segment": segment,
                "domain": domain
            })

            return self._create_success_response(strategy, "Marketing strategy generated")

        except Exception as e:
            self.log_action("strategy_generation", {
                "error": str(e),
                "product": product_description
            })
            return self._create_error_response(str(e))

    def _generate_strategy(
        self,
        product: str,
        segment: str,
        domain: Optional[str],
        competitor_data: Dict[str, Any],
        research_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a comprehensive marketing strategy."""
        profile = self.SEGMENT_PROFILES[segment]

        strategy = {
            'segment': segment,
            'segment_profile': profile,
            'positioning': self._create_positioning(product, segment, domain, competitor_data),
            'messaging': self._create_messaging(product, segment, profile),
            'channels': self._recommend_channels(segment, domain),
            'key_messages': self._generate_key_messages(product, segment, profile),
            'differentiation': self._create_differentiation(product, competitor_data, profile),
            'tactics': self._recommend_tactics(segment, profile),
            'metrics': self._define_metrics(segment)
        }

        # Add research-backed recommendations if available
        if research_insights:
            strategy['research_backed_recommendations'] = self._extract_research_recommendations(
                research_insights,
                segment
            )

        return strategy

    def _create_positioning(
        self,
        product: str,
        segment: str,
        domain: Optional[str],
        competitor_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create positioning strategy."""
        profile = self.SEGMENT_PROFILES[segment]

        positioning = {
            'target_audience': f"{segment} consumers",
            'category': domain or "Sustainable food innovation",
            'point_of_difference': profile['messaging_focus'],
            'reason_to_believe': profile['key_factors']
        }

        # Add competitive positioning if data available
        if competitor_data and 'statistics' in competitor_data:
            stats = competitor_data['statistics']
            if 'price_stats' in stats:
                avg_price = stats['price_stats']['avg']
                positioning['price_positioning'] = self._determine_price_position(avg_price)

        return positioning

    def _create_messaging(self, product: str, segment: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create messaging framework."""
        return {
            'primary_message': f"{product} - {profile['messaging_focus']}",
            'supporting_messages': profile['key_factors'],
            'tone': self._determine_tone(segment),
            'avoid': profile['concerns']
        }

    def _recommend_channels(self, segment: str, domain: Optional[str]) -> List[Dict[str, str]]:
        """Recommend marketing channels."""
        base_channels = [
            {'channel': 'Social Media', 'priority': 'High', 'rationale': 'Build community and trust'},
            {'channel': 'Content Marketing', 'priority': 'High', 'rationale': 'Educate and inform'},
            {'channel': 'Influencer Partnerships', 'priority': 'Medium', 'rationale': 'Leverage credibility'}
        ]

        if segment == "Skeptic":
            base_channels.append({
                'channel': 'Transparency Reports',
                'priority': 'High',
                'rationale': 'Address naturalness concerns'
            })

        if segment == "Non-Consumer":
            base_channels.append({
                'channel': 'Sampling Programs',
                'priority': 'High',
                'rationale': 'Build familiarity through trial'
            })

        return base_channels

    def _generate_key_messages(self, product: str, segment: str, profile: Dict[str, Any]) -> List[str]:
        """Generate key marketing messages."""
        messages = []

        if segment == "High Essentialist":
            messages = [
                f"Experience the authentic taste and texture you love",
                f"Indistinguishable from traditional products",
                f"No compromise on sensory quality"
            ]
        elif segment == "Skeptic":
            messages = [
                f"Made with simple, natural ingredients",
                f"Transparent about our process and origins",
                f"Minimal processing, maximum nutrition"
            ]
        elif segment == "Non-Consumer":
            messages = [
                f"Familiar format, innovative nutrition",
                f"Trusted by families like yours",
                f"Easy to incorporate into your daily routine"
            ]

        return messages

    def _create_differentiation(
        self,
        product: str,
        competitor_data: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create differentiation strategy."""
        differentiation = {
            'unique_value_proposition': f"Designed specifically for {profile['description']}",
            'competitive_advantages': profile['opportunities']
        }

        # Add data-driven differentiation if available
        if competitor_data and 'statistics' in competitor_data:
            stats = competitor_data['statistics']
            if 'co2_stats' in stats:
                differentiation['sustainability_advantage'] = "Lower environmental impact than average"

        return differentiation

    def _recommend_tactics(self, segment: str, profile: Dict[str, Any]) -> List[Dict[str, str]]:
        """Recommend specific marketing tactics."""
        tactics = []

        if segment == "High Essentialist":
            tactics = [
                {'tactic': 'Blind taste tests', 'goal': 'Prove sensory equivalence'},
                {'tactic': 'Chef endorsements', 'goal': 'Build credibility on quality'},
                {'tactic': 'Sensory comparison videos', 'goal': 'Demonstrate similarity'}
            ]
        elif segment == "Skeptic":
            tactics = [
                {'tactic': 'Factory tours (virtual/physical)', 'goal': 'Show transparency'},
                {'tactic': 'Ingredient storytelling', 'goal': 'Highlight naturalness'},
                {'tactic': 'Third-party certifications', 'goal': 'Build trust'}
            ]
        elif segment == "Non-Consumer":
            tactics = [
                {'tactic': 'Free sampling programs', 'goal': 'Build familiarity'},
                {'tactic': 'Gradual product introduction', 'goal': 'Reduce fear of novelty'},
                {'tactic': 'Family testimonials', 'goal': 'Create social proof'}
            ]

        return tactics

    def _define_metrics(self, segment: str) -> List[Dict[str, str]]:
        """Define success metrics."""
        base_metrics = [
            {'metric': 'Brand Awareness', 'target': 'Increase by 30% in 6 months'},
            {'metric': 'Purchase Intent', 'target': 'Achieve 40% among target segment'},
            {'metric': 'Trial Rate', 'target': '25% of aware consumers'}
        ]

        if segment == "Non-Consumer":
            base_metrics.append({
                'metric': 'Repeat Purchase Rate',
                'target': '50% after first trial (habituation)'
            })

        return base_metrics

    def _determine_tone(self, segment: str) -> str:
        """Determine appropriate communication tone."""
        tones = {
            "High Essentialist": "Confident, quality-focused, sensory-rich",
            "Skeptic": "Transparent, honest, educational",
            "Non-Consumer": "Friendly, reassuring, familiar"
        }
        return tones.get(segment, "Professional and informative")

    def _determine_price_position(self, avg_price: float) -> str:
        """Determine price positioning strategy."""
        # This is a simplified heuristic
        if avg_price < 10:
            return "Value positioning - competitive pricing"
        elif avg_price < 20:
            return "Mid-market positioning - quality at fair price"
        else:
            return "Premium positioning - quality justifies price"

    def _extract_research_recommendations(
        self,
        research_insights: Dict[str, Any],
        segment: str
    ) -> List[str]:
        """Extract actionable recommendations from research insights."""
        recommendations = []

        if 'answer' in research_insights:
            # This would ideally parse the research answer for specific recommendations
            recommendations.append("Based on research: " + research_insights['answer'][:200] + "...")

        if 'citations' in research_insights:
            recommendations.append(f"Backed by {len(research_insights['citations'])} scientific sources")

        return recommendations

    def get_segment_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get all available consumer segment profiles."""
        return self.SEGMENT_PROFILES

    def compare_segments(self, product: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare marketing strategies across all segments.

        Args:
            product: Product description
            domain: Optional domain

        Returns:
            Comparison of strategies for all segments
        """
        comparison = {}

        for segment in self.SEGMENT_PROFILES.keys():
            result = self.execute({
                'product_description': product,
                'segment': segment,
                'domain': domain
            })

            if result['status'] == 'success':
                comparison[segment] = result['data']

        return self._create_success_response(comparison, "Segment comparison completed")
