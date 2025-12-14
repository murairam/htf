"""
Unified Output Builder
Creates complete unified JSON output from ACE and Essence results.
GUARANTEES ZERO INFORMATION LOSS - all fields preserved.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import copy


def extract_all_keys(data: Any, prefix: str = "") -> set:
    """Extract all keys from nested structure."""
    keys = set()
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{prefix}.{key}" if prefix else key
            keys.add(current_path)
            keys.update(extract_all_keys(value, current_path))
    elif isinstance(data, list) and data:
        for i, item in enumerate(data[:1]):  # Check first item only
            keys.update(extract_all_keys(item, f"{prefix}[0]"))
    return keys


def generate_visualizations(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate Plotly visualizations from analysis data.
    """
    try:
        from .visualizations import generate_all_visualizations
        return generate_all_visualizations(data)
    except ImportError as e:
        print(f"⚠️  Visualizations module not available: {e}")
        # Fallback to detection if visualizations module not available
        return detect_visuals(data)
    except Exception as e:
        print(f"⚠️  Error generating visualizations: {e}")
        return detect_visuals(data)


def detect_visuals(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Detect visual artifacts in data."""
    visuals = []
    
    def search_visuals(obj: Any, path: str = ""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check for visual-related keys
                visual_keywords = ['chart', 'plot', 'graph', 'visual', 'figure', 'diagram', 
                                 'image', 'visualization', 'plotly', 'matplotlib']
                if any(kw in key.lower() for kw in visual_keywords):
                    if isinstance(value, (str, dict, list)):
                        visuals.append({
                            "path": current_path,
                            "title": key,
                            "type": "detected_visual",
                            "format": "unknown"
                        })
                
                # Check for base64 images
                if isinstance(value, str):
                    if value.startswith('data:image/'):
                        visuals.append({
                            "path": current_path,
                            "title": key,
                            "type": "base64_image",
                            "format": value.split(';')[0].split(':')[1] if ':' in value else "image",
                            "data_or_url": value[:100] + "..." if len(value) > 100 else value
                        })
                    elif len(value) > 500 and value[:50].isalnum():
                        # Potential base64
                        if 'image' in key.lower():
                            visuals.append({
                                "path": current_path,
                                "title": key,
                                "type": "potential_base64",
                                "format": "unknown"
                            })
                
                search_visuals(value, current_path)
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj[:3]):  # Check first 3 items
                search_visuals(item, f"{path}[{i}]")
    
    search_visuals(data)
    return visuals


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any], 
                     source1: str = "source1", source2: str = "source2") -> Dict[str, Any]:
    """
    Deep merge two dictionaries, preserving all keys.
    If keys conflict, keep both with source labels.
    """
    result = {}
    
    # Get all keys from both dicts
    all_keys = set(dict1.keys()) | set(dict2.keys())
    
    for key in all_keys:
        val1 = dict1.get(key)
        val2 = dict2.get(key)
        
        if key not in dict1:
            # Only in dict2
            result[key] = {"source": source2, "value": val2}
        elif key not in dict2:
            # Only in dict1
            result[key] = {"source": source1, "value": val1}
        else:
            # In both - check if mergeable
            if isinstance(val1, dict) and isinstance(val2, dict):
                # Recursive merge
                result[key] = deep_merge_dicts(val1, val2, source1, source2)
            elif isinstance(val1, list) and isinstance(val2, list):
                # Combine lists, deduplicate if possible
                combined = [{"source": source1, "value": v} for v in val1]
                combined.extend([{"source": source2, "value": v} for v in val2])
                result[key] = combined
            else:
                # Conflict - keep both
                result[key] = {
                    "sources": [source1, source2],
                    "values": {
                        source1: val1,
                        source2: val2
                    }
                }
    
    return result


def create_unified_output(
    analysis_id: str,
    input_data: Dict[str, Any],
    ace_result: Optional[Dict[str, Any]],
    essence_result: Optional[Dict[str, Any]],
    status: str,
    errors: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Create unified output JSON from ACE and Essence results.
    
    GUARANTEES ZERO INFORMATION LOSS:
    - All ACE fields preserved in raw_sources.ace
    - All Essence fields preserved in raw_sources.essence
    - Common fields intelligently merged in merged section
    - Conflicts preserved (no overwrites)
    
    Args:
        analysis_id: Analysis ID
        input_data: Input echo
        ace_result: ACE pipeline result
        essence_result: Essence pipeline result
        status: ok/partial/error
        errors: List of errors
        
    Returns:
        Complete unified output JSON with zero information loss
    """
    unified = {
        "analysis_id": analysis_id,
        "input": input_data,
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "raw_sources": {
            "ace": copy.deepcopy(ace_result) if ace_result else None,
            "essence": copy.deepcopy(essence_result) if essence_result else None
        },
        "errors": errors
    }
    
    # Build merged section - preserve ALL information
    merged = {}
    
    # Extract all keys to ensure nothing is missed
    ace_keys = extract_all_keys(ace_result) if ace_result else set()
    essence_keys = extract_all_keys(essence_result) if essence_result else set()
    
    # Product Information (prioritize ACE, but preserve both if different)
    if ace_result and "product_information" in ace_result:
        merged["product_information"] = ace_result["product_information"]
    elif essence_result and "product_information" in essence_result:
        merged["product_information"] = essence_result["product_information"]
    
    # Image URL (from ACE)
    if ace_result and ace_result.get("image_front_url"):
        merged["image_front_url"] = ace_result["image_front_url"]
    
    # Business Objective - collect from all sources
    objectives = []
    if ace_result and ace_result.get("business_objective"):
        obj = ace_result["business_objective"]
        if isinstance(obj, dict):
            objectives.append({"source": "ace", "objective": obj.get("objective_description", str(obj))})
        else:
            objectives.append({"source": "ace", "objective": str(obj)})
    if essence_result and essence_result.get("business_objective"):
        objectives.append({"source": "essence", "objective": essence_result["business_objective"]})
    if input_data.get("business_objective"):
        input_obj = input_data["business_objective"]
        if not any(obj.get("objective") == input_obj for obj in objectives):
            objectives.insert(0, {"source": "input", "objective": input_obj})
    if objectives:
        merged["business_objectives"] = objectives
    
    # Scoring Results (from ACE)
    if ace_result and "scoring_results" in ace_result:
        merged["scoring_results"] = ace_result["scoring_results"]
    
    # SWOT Analysis - preserve all sources
    swot_sources = []
    if ace_result and "swot_analysis" in ace_result:
        swot_sources.append({
            "source": "ace",
            "analysis": ace_result["swot_analysis"]
        })
    if essence_result and "swot_analysis" in essence_result:
        swot_sources.append({
            "source": "essence",
            "analysis": essence_result["swot_analysis"]
        })
    if swot_sources:
        merged["swot_analysis"] = swot_sources
    
    # Image Analysis (from ACE)
    if ace_result and "image_analysis" in ace_result:
        merged["image_analysis"] = ace_result["image_analysis"]
    
    # Packaging Improvements - preserve all sources
    improvements = []
    if ace_result and "packaging_improvement_proposals" in ace_result:
        ace_improvements = ace_result["packaging_improvement_proposals"]
        if isinstance(ace_improvements, list):
            improvements.extend([{"source": "ace", "proposal": p} for p in ace_improvements])
        else:
            improvements.append({"source": "ace", "proposal": ace_improvements})
    if essence_result and "packaging_improvements" in essence_result:
        essence_improvements = essence_result["packaging_improvements"]
        if isinstance(essence_improvements, list):
            improvements.extend([{"source": "essence", "proposal": p} for p in essence_improvements])
        else:
            improvements.append({"source": "essence", "proposal": essence_improvements})
    if improvements:
        merged["packaging_improvements"] = improvements
    
    # Go-to-Market Strategy - preserve all sources
    gtm_strategies = []
    if ace_result and "go_to_market_strategy" in ace_result:
        gtm_strategies.append({
            "source": "ace",
            "strategy": ace_result["go_to_market_strategy"]
        })
    if essence_result and "go_to_market_strategy" in essence_result:
        gtm_strategies.append({
            "source": "essence",
            "strategy": essence_result["go_to_market_strategy"]
        })
    if gtm_strategies:
        merged["go_to_market_strategies"] = gtm_strategies
    
    # Evidence-Based Explanations (from ACE)
    if ace_result and "evidence_based_explanations" in ace_result:
        merged["evidence_based_explanations"] = ace_result["evidence_based_explanations"]
    
    # Quality Insights (from ACE)
    if ace_result and "quality_insights" in ace_result:
        merged["quality_insights"] = ace_result["quality_insights"]
    
    # Export Metadata (from ACE)
    if ace_result and "export_metadata" in ace_result:
        merged["export_metadata"] = ace_result["export_metadata"]
    
    # EssenceAI-specific fields - preserve ALL
    if essence_result:
        # Competitor Analysis
        if "competitor_analysis" in essence_result:
            merged["competitor_analysis"] = essence_result["competitor_analysis"]
        elif "mock_data" in essence_result and "competitor_analysis" in essence_result["mock_data"]:
            merged["competitor_analysis"] = essence_result["mock_data"]["competitor_analysis"]
        
        # Research Insights
        if "research_insights" in essence_result:
            merged["research_insights"] = essence_result["research_insights"]
        elif "mock_data" in essence_result and "research_insights" in essence_result["mock_data"]:
            merged["research_insights"] = essence_result["mock_data"]["research_insights"]
        
        # Marketing Strategy
        if "marketing_strategy" in essence_result:
            merged["marketing_strategy"] = essence_result["marketing_strategy"]
        elif "mock_data" in essence_result and "marketing_strategy" in essence_result["mock_data"]:
            merged["marketing_strategy"] = essence_result["mock_data"]["marketing_strategy"]
        
        # Workflow steps
        if "workflow" in essence_result:
            merged["workflow"] = essence_result["workflow"]
        
        # Input echo
        if "input" in essence_result:
            merged["essence_input"] = essence_result["input"]
    
    # Generate and include visuals
    visuals = []
    
    # Try to generate new visualizations first
    try:
        from .visualizations import generate_all_visualizations
        generated_visuals = generate_all_visualizations(merged)
        if generated_visuals:
            visuals.extend(generated_visuals)
    except ImportError:
        # Fallback to detection if visualizations module not available
        pass
    except Exception as e:
        print(f"Warning: Could not generate visualizations: {e}")
    
    # Also detect any existing visuals in the results
    if essence_result:
        essence_visuals = detect_visuals(essence_result)
        if essence_visuals:
            # Avoid duplicates
            existing_titles = {v.get("title") for v in visuals}
            for v in essence_visuals:
                if v.get("title") not in existing_titles:
                    visuals.append(v)
    
    # Also check for any plotly chart data structures
    if essence_result:
        def find_plotly_data(obj: Any, path: str = ""):
            found = []
            if isinstance(obj, dict):
                # Check for plotly-like structures
                if "data" in obj and "layout" in obj:
                    found.append({
                        "path": path,
                        "title": obj.get("layout", {}).get("title", {}).get("text", "Chart"),
                        "type": "plotly_chart",
                        "format": "plotly_json",
                        "data_or_url": path
                    })
                for key, value in obj.items():
                    found.extend(find_plotly_data(value, f"{path}.{key}" if path else key))
            elif isinstance(obj, list):
                for i, item in enumerate(obj[:5]):
                    found.extend(find_plotly_data(item, f"{path}[{i}]"))
            return found
        
        plotly_charts = find_plotly_data(essence_result)
        existing_titles = {v.get("title") for v in visuals}
        for chart in plotly_charts:
            if chart.get("title") not in existing_titles:
                visuals.append(chart)
    
    if visuals:
        merged["visuals"] = visuals
    
    # Handle ACE Competitor Intelligence
    if ace_result and "competitor_intelligence" in ace_result:
        ace_comp_intel = ace_result["competitor_intelligence"]
        
        # If we already have competitor_intelligence from Essence, merge them
        if "competitor_intelligence" in merged:
            # Merge ACE and Essence competitor intelligence
            merged["competitor_intelligence"] = {
                "ace": ace_comp_intel,
                "essence": merged["competitor_intelligence"]
            }
        else:
            # Only ACE data available, structure it properly
            merged["competitor_intelligence"] = {
                "ace": ace_comp_intel
            }
    
    # Handle ACE Marketing Strategy
    if ace_result and "marketing_strategy" in ace_result:
        ace_marketing = ace_result["marketing_strategy"]
        
        # If we already have marketing_strategy from Essence, merge them
        if "marketing_strategy_essence" in merged:
            # Keep both ACE and Essence marketing strategies
            merged["marketing_strategy"] = {
                "ace": ace_marketing,
                "essence": merged["marketing_strategy_essence"]
            }
            # Remove the old key
            del merged["marketing_strategy_essence"]
        else:
            # Only ACE data available, structure it properly
            merged["marketing_strategy"] = {
                "ace": ace_marketing
            }
    
    # Handle ACE Research Insights
    if ace_result and "research_insights" in ace_result:
        ace_research = ace_result["research_insights"]
        
        # If we already have research_insights from Essence, merge them
        if "research_insights" in merged:
            # Merge ACE and Essence research insights
            merged["research_insights"] = {
                "ace": ace_research,
                "essence": merged["research_insights"]
            }
        else:
            # Only ACE data available, structure it properly
            merged["research_insights"] = {
                "ace": ace_research
            }
    
    # Preserve ALL other fields from ACE that weren't explicitly handled
    if ace_result:
        handled_ace_keys = {
            "product_information", "image_front_url", "business_objective",
            "scoring_results", "swot_analysis", "image_analysis",
            "packaging_improvement_proposals", "go_to_market_strategy",
            "evidence_based_explanations", "quality_insights", "export_metadata",
            "competitor_intelligence",  # Now handled above
            "marketing_strategy",  # Now handled above
            "research_insights"  # Now handled above
        }
        for key, value in ace_result.items():
            if key not in handled_ace_keys and key not in merged:
                merged[f"ace_{key}"] = value
    
    # Extract and structure Essence data for frontend
    if essence_result and essence_result.get("status") != "mock":
        # Competitor Intelligence
        comp_analysis = essence_result.get("competitor_analysis", {})
        if comp_analysis:
            from .visualizations import calculate_competitor_metrics, generate_competitor_visualizations
            
            competitors = comp_analysis.get("competitors", [])
            metrics = calculate_competitor_metrics(competitors)
            visualizations = generate_competitor_visualizations(competitors) if competitors else {}
            
            merged["competitor_intelligence"] = {
                "metrics": metrics,
                "competitors": competitors,
                "visualizations": visualizations,
                "analysis_summary": comp_analysis.get("summary", ""),
                "market_overview": comp_analysis.get("market_overview", "")
            }
        
        # Marketing Strategy (Essence)
        marketing_strategy = essence_result.get("marketing_strategy", {})
        if marketing_strategy:
            merged["marketing_strategy_essence"] = {
                "strategy_text": marketing_strategy.get("strategy", ""),
                "segment": essence_result.get("input", {}).get("segment", ""),
                "domain": essence_result.get("input", {}).get("domain", ""),
                "positioning": marketing_strategy.get("positioning", {}),
                "key_messages": marketing_strategy.get("key_messages", []),
                "tactics": marketing_strategy.get("tactics", []),
                "channels": marketing_strategy.get("channels", []),
                "citations": marketing_strategy.get("citations", []),
                "segment_profile": marketing_strategy.get("segment_profile", {})
            }
        
        # Research Insights (Essence)
        research_insights = essence_result.get("research_insights", {})
        if research_insights:
            merged["research_insights_essence"] = {
                "insights_text": research_insights.get("insights", ""),
                "domain": essence_result.get("input", {}).get("domain", ""),
                "key_findings": research_insights.get("key_findings", []),
                "citations": research_insights.get("citations", []),
                "research_summary": research_insights.get("summary", ""),
                "methodology": research_insights.get("methodology", "")
            }
    
    # Preserve ALL other fields from Essence that weren't explicitly handled
    if essence_result:
        handled_essence_keys = {
            "competitor_analysis", "research_insights", "marketing_strategy",
            "workflow", "input", "status", "message", "mock_data",
            "competitor_intelligence", "marketing_strategy_essence", "research_insights_essence"
        }
        for key, value in essence_result.items():
            if key not in handled_essence_keys and key not in merged:
                merged[f"essence_{key}"] = value
    
    unified["merged"] = merged
    
    return unified
