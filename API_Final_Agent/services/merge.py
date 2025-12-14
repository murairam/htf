"""
Merge Service
Merges normalized results from ACE and EssenceAI into a unified output.
"""

from typing import Dict, Any, List, Optional


def merge_results(
    ace_normalized: Dict[str, Any],
    essence_normalized: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge normalized results from ACE and EssenceAI.
    
    Strategy:
    - Preserve all raw outputs in raw_sources
    - Extract common useful fields into merged section
    - Handle conflicts by keeping both (as arrays)
    - Only include fields that exist in sources
    
    Args:
        ace_normalized: Normalized ACE result
        essence_normalized: Normalized EssenceAI result
        
    Returns:
        Merged result dict
    """
    merged = {
        "merged": {},
        "raw_sources": {
            "ace": ace_normalized.get("raw", {}),
            "essence": essence_normalized.get("raw", {})
        }
    }
    
    # Extract business objectives
    objectives = []
    if ace_normalized.get("business_objective"):
        objectives.append({
            "source": "ace",
            "objective": ace_normalized["business_objective"]
        })
    if essence_normalized.get("business_objective"):
        objectives.append({
            "source": "essence",
            "objective": essence_normalized["business_objective"]
        })
    if objectives:
        merged["merged"]["business_objectives"] = objectives
    
    # Merge scoring results (if both have scores)
    scores = {}
    if "scoring_results" in ace_normalized:
        scores["ace"] = ace_normalized["scoring_results"]
    if "scoring_results" in essence_normalized:
        scores["essence"] = essence_normalized["scoring_results"]
    if scores:
        merged["merged"]["scoring_results"] = scores
    
    # Merge SWOT analysis
    swot_sources = []
    if "swot_analysis" in ace_normalized:
        swot_sources.append({
            "source": "ace",
            "analysis": ace_normalized["swot_analysis"]
        })
    if "swot_analysis" in essence_normalized:
        swot_sources.append({
            "source": "essence",
            "analysis": essence_normalized["swot_analysis"]
        })
    if swot_sources:
        merged["merged"]["swot_analysis"] = swot_sources
    
    # Merge product information
    product_info = {}
    if "product_information" in ace_normalized:
        product_info["ace"] = ace_normalized["product_information"]
    if "product_information" in essence_normalized:
        product_info["essence"] = essence_normalized["product_information"]
    if product_info:
        merged["merged"]["product_information"] = product_info
    
    # Merge image analysis
    if "image_analysis" in ace_normalized:
        merged["merged"]["image_analysis"] = ace_normalized["image_analysis"]
    elif "image_analysis" in essence_normalized:
        merged["merged"]["image_analysis"] = essence_normalized["image_analysis"]
    
    # Merge packaging improvements
    improvements = []
    if "packaging_improvement_proposals" in ace_normalized:
        ace_improvements = ace_normalized["packaging_improvement_proposals"]
        if isinstance(ace_improvements, list):
            improvements.extend([{"source": "ace", "proposal": p} for p in ace_improvements])
        else:
            improvements.append({"source": "ace", "proposal": ace_improvements})
    if "packaging_improvements" in essence_normalized:
        essence_improvements = essence_normalized["packaging_improvements"]
        if isinstance(essence_improvements, list):
            improvements.extend([{"source": "essence", "proposal": p} for p in essence_improvements])
        else:
            improvements.append({"source": "essence", "proposal": essence_improvements})
    if improvements:
        merged["merged"]["packaging_improvements"] = improvements
    
    # Merge go-to-market strategy
    gtm_strategies = []
    if "go_to_market_strategy" in ace_normalized:
        gtm_strategies.append({
            "source": "ace",
            "strategy": ace_normalized["go_to_market_strategy"]
        })
    if "go_to_market_strategy" in essence_normalized:
        gtm_strategies.append({
            "source": "essence",
            "strategy": essence_normalized["go_to_market_strategy"]
        })
    if gtm_strategies:
        merged["merged"]["go_to_market_strategies"] = gtm_strategies
    
    # Merge research insights (EssenceAI specific)
    if "research_insights" in essence_normalized:
        merged["merged"]["research_insights_essence"] = essence_normalized["research_insights"]
    
    # Merge competitor intelligence (from both ACE and EssenceAI)
    competitor_data = {}
    if "competitor_intelligence" in ace_normalized:
        competitor_data["ace"] = ace_normalized["competitor_intelligence"]
    if "competitor_intelligence" in essence_normalized:
        competitor_data["essence"] = essence_normalized["competitor_intelligence"]
    elif "competitor_analysis" in essence_normalized:
        # Fallback for old format
        competitor_data["essence"] = essence_normalized["competitor_analysis"]
    
    if competitor_data:
        merged["merged"]["competitor_intelligence"] = competitor_data
    
    # Merge marketing strategy (EssenceAI specific)
    if "marketing_strategy" in essence_normalized:
        merged["merged"]["marketing_strategy_essence"] = essence_normalized["marketing_strategy"]
    
    # Merge quality insights (ACE specific)
    if "quality_insights" in ace_normalized:
        merged["merged"]["quality_insights"] = ace_normalized["quality_insights"]
    
    return merged


def determine_status(
    ace_result: Optional[Dict[str, Any]],
    essence_result: Optional[Dict[str, Any]]
) -> str:
    """
    Determine overall status based on API results.
    
    Returns:
        "ok" if both succeeded
        "partial" if one succeeded (or mock response)
        "error" if both failed
    """
    ace_ok = ace_result is not None and ace_result.get("status") == "success"
    essence_ok = essence_result is not None and essence_result.get("status") == "success"
    
    # Check for mock responses (treated as partial success)
    essence_mock = False
    if essence_result is not None:
        essence_data = essence_result.get("data", {})
        if isinstance(essence_data, dict) and essence_data.get("status") == "mock":
            essence_mock = True
            essence_ok = True  # Treat mock as success for status calculation
    
    if ace_ok and (essence_ok or essence_mock):
        return "ok" if not essence_mock else "partial"
    elif ace_ok or essence_ok or essence_mock:
        return "partial"
    else:
        return "error"


def collect_errors(
    ace_result: Optional[Dict[str, Any]],
    essence_result: Optional[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Collect errors from API results.
    
    Returns:
        List of error dicts
    """
    errors = []
    
    if ace_result and ace_result.get("status") == "error":
        errors.append({
            "source": "ace",
            "error": ace_result.get("error", "Unknown error"),
            "error_detail": ace_result.get("error_detail")
        })
    
    if essence_result and essence_result.get("status") == "error":
        errors.append({
            "source": "essence",
            "error": essence_result.get("error", "Unknown error"),
            "error_detail": essence_result.get("error_detail")
        })
    
    return errors

