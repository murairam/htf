"""
Marketing Strategy Generator for ACE Pipeline
Generates marketing strategy recommendations based on product analysis
"""

from typing import Dict, Any, List


def generate_marketing_strategy(
    product_data: Dict[str, Any],
    scoring_results: Dict[str, Any],
    competitor_intelligence: Dict[str, Any],
    business_objective: str
) -> Dict[str, Any]:
    """
    Generate marketing strategy recommendations based on product analysis.
    
    Args:
        product_data: Product information from OpenFoodFacts
        scoring_results: ACE scoring results
        competitor_intelligence: Competitor analysis data
        business_objective: User's business objective
        
    Returns:
        Dictionary with marketing strategy recommendations
    """
    
    # Extract key information
    product_name = product_data.get("name", "Product")
    category = product_data.get("plant_based_category", "plant-based")
    scores = scoring_results.get("scores", {})
    global_score = scores.get("global_score", 0)
    
    # Competitor metrics
    comp_metrics = competitor_intelligence.get("metrics", {})
    avg_price = comp_metrics.get("avg_price_per_kg", 25.0)
    avg_co2 = comp_metrics.get("avg_co2_emission", 2.2)
    
    # Determine positioning based on scores
    positioning = _determine_positioning(scores, comp_metrics)
    
    # Generate target segments
    target_segments = _generate_target_segments(product_data, positioning)
    
    # Generate key messages
    key_messages = _generate_key_messages(product_data, scores, positioning)
    
    # Generate channel recommendations
    channels = _generate_channel_recommendations(positioning, target_segments)
    
    # Generate tactics
    tactics = _generate_tactics(positioning, scores, business_objective)
    
    # Generate pricing strategy
    pricing_strategy = _generate_pricing_strategy(positioning, comp_metrics)
    
    return {
        "positioning": positioning,
        "target_segments": target_segments,
        "key_messages": key_messages,
        "channels": channels,
        "tactics": tactics,
        "pricing_strategy": pricing_strategy,
        "summary": _generate_summary(positioning, target_segments, key_messages)
    }


def _determine_positioning(scores: Dict[str, float], comp_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Determine product positioning based on scores."""
    attractiveness = scores.get("attractiveness_score", 0)
    utility = scores.get("utility_score", 0)
    positioning_score = scores.get("positioning_score", 0)
    
    # Determine primary positioning
    if attractiveness >= 7 and utility >= 7:
        primary = "premium"
        description = "Premium plant-based product with strong appeal and functionality"
    elif utility >= 7:
        primary = "functional"
        description = "Functional plant-based product focused on health benefits"
    elif attractiveness >= 7:
        primary = "lifestyle"
        description = "Lifestyle-oriented plant-based product with strong visual appeal"
    elif positioning_score >= 7:
        primary = "value"
        description = "Value-oriented plant-based product with good positioning"
    else:
        primary = "challenger"
        description = "Challenger brand with room for improvement"
    
    return {
        "primary": primary,
        "description": description,
        "strengths": _identify_strengths(scores),
        "differentiation": _identify_differentiation(primary, scores)
    }


def _identify_strengths(scores: Dict[str, float]) -> List[str]:
    """Identify product strengths based on scores."""
    strengths = []
    
    if scores.get("attractiveness_score", 0) >= 7:
        strengths.append("Strong visual appeal and packaging design")
    if scores.get("utility_score", 0) >= 7:
        strengths.append("High nutritional value and functionality")
    if scores.get("positioning_score", 0) >= 7:
        strengths.append("Clear market positioning")
    
    if not strengths:
        strengths.append("Opportunity for improvement across all dimensions")
    
    return strengths


def _identify_differentiation(primary: str, scores: Dict[str, float]) -> List[str]:
    """Identify differentiation opportunities."""
    diff = []
    
    if primary == "premium":
        diff.extend([
            "Emphasize superior quality and taste",
            "Highlight sustainable sourcing and production",
            "Position as indulgence without compromise"
        ])
    elif primary == "functional":
        diff.extend([
            "Focus on health benefits and nutrition",
            "Emphasize protein content and clean ingredients",
            "Target health-conscious consumers"
        ])
    elif primary == "lifestyle":
        diff.extend([
            "Align with consumer values and identity",
            "Create aspirational brand image",
            "Leverage social media and influencers"
        ])
    elif primary == "value":
        diff.extend([
            "Offer competitive pricing",
            "Emphasize accessibility and convenience",
            "Build trust through transparency"
        ])
    else:  # challenger
        diff.extend([
            "Identify unique selling proposition",
            "Focus on niche market segment",
            "Build brand awareness through innovation"
        ])
    
    return diff


def _generate_target_segments(product_data: Dict[str, Any], positioning: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate target segment recommendations."""
    primary_pos = positioning["primary"]
    
    segments = []
    
    if primary_pos == "premium":
        segments.extend([
            {
                "name": "Conscious Foodies",
                "description": "Food enthusiasts seeking premium plant-based alternatives",
                "size": "Medium",
                "priority": "Primary"
            },
            {
                "name": "Affluent Flexitarians",
                "description": "High-income consumers reducing meat consumption",
                "size": "Large",
                "priority": "Primary"
            }
        ])
    elif primary_pos == "functional":
        segments.extend([
            {
                "name": "Health Optimizers",
                "description": "Fitness-focused consumers prioritizing nutrition",
                "size": "Large",
                "priority": "Primary"
            },
            {
                "name": "Wellness Seekers",
                "description": "Health-conscious consumers with dietary restrictions",
                "size": "Medium",
                "priority": "Secondary"
            }
        ])
    elif primary_pos == "lifestyle":
        segments.extend([
            {
                "name": "Ethical Millennials",
                "description": "Young consumers driven by environmental values",
                "size": "Large",
                "priority": "Primary"
            },
            {
                "name": "Social Influencers",
                "description": "Trend-setters sharing lifestyle choices",
                "size": "Small",
                "priority": "Secondary"
            }
        ])
    else:  # value or challenger
        segments.extend([
            {
                "name": "Budget-Conscious Families",
                "description": "Families seeking affordable plant-based options",
                "size": "Large",
                "priority": "Primary"
            },
            {
                "name": "Curious Newcomers",
                "description": "First-time plant-based product buyers",
                "size": "Large",
                "priority": "Primary"
            }
        ])
    
    return segments


def _generate_key_messages(product_data: Dict[str, Any], scores: Dict[str, float], positioning: Dict[str, Any]) -> List[str]:
    """Generate key marketing messages."""
    messages = []
    primary_pos = positioning["primary"]
    
    # Core message based on positioning
    if primary_pos == "premium":
        messages.append("Experience plant-based excellence without compromise")
    elif primary_pos == "functional":
        messages.append("Fuel your body with powerful plant-based nutrition")
    elif primary_pos == "lifestyle":
        messages.append("Choose the future of food, choose plant-based")
    else:
        messages.append("Delicious plant-based food for everyone")
    
    # Add specific messages based on product attributes
    if scores.get("attractiveness_score", 0) >= 7:
        messages.append("Beautifully crafted, sustainably packaged")
    
    if scores.get("utility_score", 0) >= 7:
        messages.append("Packed with protein and essential nutrients")
    
    # Add sustainability message
    messages.append("Better for you, better for the planet")
    
    return messages


def _generate_channel_recommendations(positioning: Dict[str, Any], segments: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Generate marketing channel recommendations."""
    primary_pos = positioning["primary"]
    
    channels = []
    
    # Digital channels (always relevant)
    channels.append({
        "channel": "Social Media",
        "platforms": ["Instagram", "TikTok", "Facebook"],
        "priority": "High",
        "tactics": [
            "User-generated content campaigns",
            "Influencer partnerships",
            "Recipe videos and tutorials"
        ]
    })
    
    # E-commerce
    channels.append({
        "channel": "E-commerce",
        "platforms": ["Brand website", "Amazon", "Specialty retailers"],
        "priority": "High",
        "tactics": [
            "Direct-to-consumer sales",
            "Subscription models",
            "Online promotions"
        ]
    })
    
    # Retail
    if primary_pos in ["premium", "lifestyle"]:
        channels.append({
            "channel": "Specialty Retail",
            "platforms": ["Whole Foods", "Organic stores", "Gourmet shops"],
            "priority": "High",
            "tactics": [
                "In-store tastings",
                "Premium shelf placement",
                "Point-of-sale materials"
            ]
        })
    else:
        channels.append({
            "channel": "Mass Retail",
            "platforms": ["Supermarkets", "Hypermarkets", "Discount stores"],
            "priority": "High",
            "tactics": [
                "Volume promotions",
                "End-cap displays",
                "Price competitiveness"
            ]
        })
    
    # Content marketing
    channels.append({
        "channel": "Content Marketing",
        "platforms": ["Blog", "YouTube", "Email"],
        "priority": "Medium",
        "tactics": [
            "Educational content",
            "Recipe development",
            "Sustainability stories"
        ]
    })
    
    return channels


def _generate_tactics(positioning: Dict[str, Any], scores: Dict[str, float], business_objective: str) -> List[Dict[str, Any]]:
    """Generate specific marketing tactics."""
    tactics = []
    
    # Launch tactics
    tactics.append({
        "phase": "Launch",
        "timeframe": "Months 1-3",
        "activities": [
            "Product sampling campaigns",
            "Influencer seeding program",
            "PR and media outreach",
            "Social media launch campaign"
        ]
    })
    
    # Growth tactics
    tactics.append({
        "phase": "Growth",
        "timeframe": "Months 4-12",
        "activities": [
            "Expand distribution channels",
            "Customer loyalty program",
            "Seasonal promotions",
            "Partnership with complementary brands"
        ]
    })
    
    # Retention tactics
    tactics.append({
        "phase": "Retention",
        "timeframe": "Ongoing",
        "activities": [
            "Community building initiatives",
            "Subscription and repeat purchase incentives",
            "Customer feedback integration",
            "Continuous product innovation"
        ]
    })
    
    return tactics


def _generate_pricing_strategy(positioning: Dict[str, Any], comp_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Generate pricing strategy recommendations."""
    primary_pos = positioning["primary"]
    avg_price = comp_metrics.get("avg_price_per_kg", 25.0)
    price_range = comp_metrics.get("price_range", {"min": 20.0, "max": 30.0})
    
    if primary_pos == "premium":
        recommended_price = price_range["max"] * 1.05
        strategy = "Premium pricing"
        rationale = "Position above market average to signal quality and exclusivity"
    elif primary_pos == "functional":
        recommended_price = avg_price * 1.1
        strategy = "Value-based pricing"
        rationale = "Price reflects superior nutritional benefits"
    elif primary_pos == "lifestyle":
        recommended_price = avg_price * 1.05
        strategy = "Competitive premium"
        rationale = "Slight premium for brand value and lifestyle alignment"
    else:  # value or challenger
        recommended_price = avg_price * 0.95
        strategy = "Penetration pricing"
        rationale = "Competitive pricing to gain market share"
    
    return {
        "strategy": strategy,
        "recommended_price_per_kg": round(recommended_price, 2),
        "market_average": round(avg_price, 2),
        "rationale": rationale,
        "promotional_tactics": [
            "Introductory discounts for first-time buyers",
            "Bundle offers with complementary products",
            "Loyalty rewards for repeat purchases"
        ]
    }


def _generate_summary(positioning: Dict[str, Any], segments: List[Dict[str, str]], messages: List[str]) -> str:
    """Generate marketing strategy summary."""
    primary_pos = positioning["primary"]
    primary_segment = segments[0]["name"] if segments else "target consumers"
    core_message = messages[0] if messages else "plant-based excellence"
    
    summary = (
        f"This {primary_pos} positioning strategy targets {primary_segment} "
        f"with the core message: '{core_message}'. "
        f"The strategy leverages {positioning['description'].lower()} "
        f"to differentiate in the competitive plant-based market."
    )
    
    return summary
