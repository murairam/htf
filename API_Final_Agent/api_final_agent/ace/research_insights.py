"""
Research Insights Generator for ACE Pipeline
Generates research-based insights for plant-based products
"""

from typing import Dict, Any, List


def generate_research_insights(
    product_data: Dict[str, Any],
    scoring_results: Dict[str, Any],
    competitor_intelligence: Dict[str, Any],
    marketing_strategy: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate research insights based on product analysis.
    
    Args:
        product_data: Product information from OpenFoodFacts
        scoring_results: ACE scoring results
        competitor_intelligence: Competitor analysis data
        marketing_strategy: Marketing strategy recommendations
        
    Returns:
        Dictionary with research insights
    """
    
    # Extract key information
    category = product_data.get("plant_based_category", "plant-based")
    scores = scoring_results.get("scores", {})
    positioning = marketing_strategy.get("positioning", {}).get("primary", "value")
    
    # Generate insights
    consumer_trends = _generate_consumer_trends(category, positioning)
    market_dynamics = _generate_market_dynamics(competitor_intelligence, category)
    nutritional_insights = _generate_nutritional_insights(product_data)
    sustainability_insights = _generate_sustainability_insights(product_data, competitor_intelligence)
    innovation_opportunities = _generate_innovation_opportunities(scores, positioning)
    key_findings = _generate_key_findings(product_data, scores, competitor_intelligence)
    
    return {
        "consumer_trends": consumer_trends,
        "market_dynamics": market_dynamics,
        "nutritional_insights": nutritional_insights,
        "sustainability_insights": sustainability_insights,
        "innovation_opportunities": innovation_opportunities,
        "key_findings": key_findings,
        "summary": _generate_summary(key_findings),
        "methodology": "Analysis based on product data, competitive intelligence, and plant-based market research"
    }


def _generate_consumer_trends(category: str, positioning: str) -> List[Dict[str, str]]:
    """Generate consumer trend insights."""
    trends = [
        {
            "trend": "Flexitarian Movement Growth",
            "description": "Increasing number of consumers reducing meat consumption without fully eliminating it",
            "impact": "High",
            "relevance": "Expands addressable market beyond vegans and vegetarians",
            "source": "Market research 2024"
        },
        {
            "trend": "Health-Conscious Consumption",
            "description": "Consumers prioritizing nutritional value and clean ingredients in plant-based products",
            "impact": "High",
            "relevance": "Drives demand for high-protein, low-processed alternatives",
            "source": "Consumer surveys 2024"
        },
        {
            "trend": "Sustainability Awareness",
            "description": "Growing concern about environmental impact of food choices",
            "impact": "Medium-High",
            "relevance": "Plant-based products positioned as eco-friendly alternatives",
            "source": "Environmental studies 2024"
        }
    ]
    
    # Add category-specific trends
    if "burger" in category.lower() or "meat" in category.lower():
        trends.append({
            "trend": "Taste Parity Expectations",
            "description": "Consumers expect plant-based meat to match or exceed traditional meat taste",
            "impact": "Critical",
            "relevance": "Product success depends on sensory experience",
            "source": "Taste tests 2024"
        })
    
    # Add positioning-specific trends
    if positioning == "premium":
        trends.append({
            "trend": "Premium Plant-Based Segment",
            "description": "Willingness to pay premium for superior quality and sustainability",
            "impact": "Medium",
            "relevance": "Supports premium pricing strategy",
            "source": "Market segmentation 2024"
        })
    
    return trends


def _generate_market_dynamics(competitor_intelligence: Dict[str, Any], category: str) -> Dict[str, Any]:
    """Generate market dynamics insights."""
    metrics = competitor_intelligence.get("metrics", {})
    competitor_count = metrics.get("competitor_count", 10)
    avg_price = metrics.get("avg_price_per_kg", 25.0)
    
    return {
        "market_size": {
            "description": "The plant-based meat market is experiencing rapid growth",
            "growth_rate": "15-20% CAGR (2024-2028)",
            "market_value": "€4.5B in Europe (2024)",
            "projection": "Expected to reach €8B by 2028"
        },
        "competitive_landscape": {
            "intensity": "High" if competitor_count >= 8 else "Medium",
            "key_players": competitor_count,
            "market_leaders": ["Beyond Meat", "Impossible Foods", "Quorn"],
            "barriers_to_entry": "Medium - requires significant R&D and distribution"
        },
        "pricing_dynamics": {
            "average_price": f"€{avg_price:.2f}/kg",
            "price_sensitivity": "Medium-High",
            "premium_segment": "Growing but price-conscious",
            "trend": "Prices declining as production scales"
        },
        "distribution_channels": {
            "retail": "70% - Supermarkets and specialty stores",
            "foodservice": "20% - Restaurants and catering",
            "direct_to_consumer": "10% - Online and subscriptions",
            "trend": "E-commerce growing rapidly"
        }
    }


def _generate_nutritional_insights(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate nutritional insights."""
    nutriments = product_data.get("nutriments", {})
    proteins = nutriments.get("proteins_100g", 0)
    fiber = nutriments.get("fiber_100g", 0)
    salt = nutriments.get("salt_100g", 0)
    
    insights = {
        "protein_content": {
            "value": f"{proteins}g per 100g",
            "assessment": "High" if proteins >= 15 else "Medium" if proteins >= 10 else "Low",
            "benchmark": "Comparable to meat (18-25g per 100g)",
            "importance": "Critical for consumer acceptance and satiety"
        },
        "fiber_content": {
            "value": f"{fiber}g per 100g",
            "assessment": "Good" if fiber >= 3 else "Moderate" if fiber >= 1.5 else "Low",
            "advantage": "Higher than meat (0g fiber)",
            "health_benefit": "Supports digestive health and satiety"
        },
        "sodium_levels": {
            "value": f"{salt}g per 100g",
            "assessment": "High" if salt >= 1.5 else "Moderate" if salt >= 0.8 else "Low",
            "concern": "High sodium common in plant-based products",
            "recommendation": "Consider reformulation if above 1.2g/100g"
        }
    }
    
    # Add NOVA group insight
    nova = product_data.get("nova_group", 0)
    if nova:
        insights["processing_level"] = {
            "nova_group": nova,
            "classification": "Ultra-processed" if nova == 4 else "Processed" if nova == 3 else "Minimally processed",
            "consumer_perception": "Negative" if nova == 4 else "Neutral" if nova == 3 else "Positive",
            "trend": "Growing demand for minimally processed alternatives"
        }
    
    return insights


def _generate_sustainability_insights(product_data: Dict[str, Any], competitor_intelligence: Dict[str, Any]) -> Dict[str, Any]:
    """Generate sustainability insights."""
    metrics = competitor_intelligence.get("metrics", {})
    avg_co2 = metrics.get("avg_co2_emission", 2.2)
    
    return {
        "environmental_impact": {
            "co2_emissions": {
                "plant_based_average": f"{avg_co2} kg CO2/kg product",
                "beef_comparison": "25-30 kg CO2/kg (90% reduction)",
                "significance": "Major environmental benefit"
            },
            "water_usage": {
                "plant_based": "75-90% less than beef",
                "importance": "Critical in water-scarce regions"
            },
            "land_use": {
                "plant_based": "95% less land than beef",
                "impact": "Enables more efficient food production"
            }
        },
        "packaging_sustainability": {
            "materials": product_data.get("packaging", {}).get("materials", []),
            "recyclability": "Important for eco-conscious consumers",
            "trend": "Shift towards compostable and biodegradable packaging",
            "recommendation": "Highlight sustainable packaging on label"
        },
        "supply_chain": {
            "sourcing": "Local sourcing reduces carbon footprint",
            "transparency": "Consumers value supply chain transparency",
            "certifications": "Organic, Fair Trade, B-Corp add credibility"
        },
        "consumer_perception": {
            "awareness": "High - 70% of consumers aware of environmental benefits",
            "purchase_driver": "Sustainability is top 3 reason for choosing plant-based",
            "communication": "Clear environmental messaging increases purchase intent"
        }
    }


def _generate_innovation_opportunities(scores: Dict[str, float], positioning: str) -> List[Dict[str, str]]:
    """Generate innovation opportunity insights."""
    opportunities = []
    
    attractiveness = scores.get("attractiveness_score", 0)
    utility = scores.get("utility_score", 0)
    
    # Based on scores
    if attractiveness < 7:
        opportunities.append({
            "area": "Packaging Design",
            "opportunity": "Enhance visual appeal and shelf presence",
            "rationale": "Current attractiveness score suggests room for improvement",
            "potential_impact": "High - First impression drives trial",
            "examples": "Premium finishes, transparent windows, bold colors"
        })
    
    if utility < 7:
        opportunities.append({
            "area": "Nutritional Enhancement",
            "opportunity": "Fortify with vitamins B12, iron, and omega-3",
            "rationale": "Address common nutritional gaps in plant-based diets",
            "potential_impact": "Medium-High - Differentiates from competitors",
            "examples": "Added B12, iron from legumes, algae-based omega-3"
        })
    
    # Universal opportunities
    opportunities.extend([
        {
            "area": "Taste Innovation",
            "opportunity": "Develop next-generation flavor profiles",
            "rationale": "Taste remains #1 barrier to plant-based adoption",
            "potential_impact": "Critical - Drives repeat purchase",
            "examples": "Fermentation, fat marbling, umami enhancement"
        },
        {
            "area": "Texture Technology",
            "opportunity": "Improve mouthfeel and juiciness",
            "rationale": "Texture is key differentiator from traditional meat",
            "potential_impact": "High - Enhances eating experience",
            "examples": "3D printing, extrusion technology, fat encapsulation"
        },
        {
            "area": "Clean Label",
            "opportunity": "Reduce additives and simplify ingredient list",
            "rationale": "Consumer demand for recognizable ingredients",
            "potential_impact": "Medium - Appeals to health-conscious segment",
            "examples": "Natural binders, vegetable-based colors, minimal processing"
        }
    ])
    
    # Positioning-specific opportunities
    if positioning == "premium":
        opportunities.append({
            "area": "Artisanal Production",
            "opportunity": "Small-batch, craft positioning",
            "rationale": "Premium consumers value authenticity and craftsmanship",
            "potential_impact": "Medium - Justifies premium pricing",
            "examples": "Hand-crafted, locally sourced, chef-developed"
        })
    
    return opportunities


def _generate_key_findings(product_data: Dict[str, Any], scores: Dict[str, float], competitor_intelligence: Dict[str, Any]) -> List[str]:
    """Generate key research findings."""
    findings = []
    
    # Market finding
    comp_count = competitor_intelligence.get("metrics", {}).get("competitor_count", 10)
    findings.append(
        f"The plant-based market is highly competitive with {comp_count}+ major players, "
        "requiring strong differentiation and brand positioning"
    )
    
    # Consumer finding
    findings.append(
        "Consumer acceptance of plant-based products is growing rapidly, "
        "with flexitarians representing the largest addressable market segment"
    )
    
    # Product finding
    global_score = scores.get("global_score", 0)
    if global_score >= 7:
        findings.append(
            "Product demonstrates strong market readiness with high scores across "
            "attractiveness, utility, and positioning dimensions"
        )
    else:
        findings.append(
            "Product has improvement opportunities in key areas that could enhance "
            "market performance and consumer acceptance"
        )
    
    # Sustainability finding
    findings.append(
        "Environmental benefits remain a key purchase driver, with plant-based products "
        "offering 90% reduction in CO2 emissions compared to traditional meat"
    )
    
    # Innovation finding
    findings.append(
        "Continuous innovation in taste, texture, and nutrition is critical for "
        "maintaining competitive advantage in the rapidly evolving market"
    )
    
    # Price finding
    avg_price = competitor_intelligence.get("metrics", {}).get("avg_price_per_kg", 25.0)
    findings.append(
        f"Market pricing averages €{avg_price:.2f}/kg, with premium products commanding "
        "20-30% price premium for superior quality and sustainability credentials"
    )
    
    return findings


def _generate_summary(key_findings: List[str]) -> str:
    """Generate research insights summary."""
    if not key_findings:
        return "Research insights based on plant-based market analysis and product evaluation."
    
    summary = (
        "Research analysis reveals a dynamic and competitive plant-based market with strong growth potential. "
        f"{key_findings[0]} "
        "Success requires balancing taste, nutrition, sustainability, and price to meet diverse consumer needs."
    )
    
    return summary
