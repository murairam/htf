"""
EssenceAI Normalizer
Converts EssenceAI API responses to a normalized format.
This will be implemented based on Phase 1 inspection results.
"""

from typing import Dict, Any, Optional


def normalize_essence(raw_json: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Normalize EssenceAI API response.
    
    This function will be implemented after Phase 1 inspection
    reveals the actual structure of EssenceAI responses.
    
    Args:
        raw_json: Raw response from EssenceAI API
        
    Returns:
        Normalized dict with common fields extracted
    """
    if raw_json is None:
        return {}
    
    normalized = {
        "source": "essence",
        "raw": raw_json,  # Keep raw for reference
    }
    
    # Handle mock responses (when agents are not available)
    if isinstance(raw_json, dict) and raw_json.get("status") == "mock":
        normalized["is_mock"] = True
        normalized["message"] = raw_json.get("message", "Mock response")
        # Extract mock data if present
        if "mock_data" in raw_json:
            normalized.update(raw_json["mock_data"])
        return normalized
    
    # Try to extract common fields (will be refined after inspection)
    if isinstance(raw_json, dict):
        # Extract top-level fields that might be useful
        # These will be updated based on actual EssenceAI output structure
        for key in ["competitor_analysis", "research_insights", "marketing_strategy",
                   "workflow", "steps", "results", "mock_data"]:
            if key in raw_json:
                normalized[key] = raw_json[key]
        
        # Extract business objective if present
        if "business_objective" in raw_json:
            normalized["business_objective"] = raw_json["business_objective"]
        
        # Extract input echo
        if "input" in raw_json:
            normalized["input"] = raw_json["input"]
        
        # Extract workflow steps if present
        if "workflow" in raw_json and isinstance(raw_json["workflow"], dict):
            workflow = raw_json["workflow"]
            if "steps" in workflow:
                normalized["workflow_steps"] = workflow["steps"]
    
    return normalized

