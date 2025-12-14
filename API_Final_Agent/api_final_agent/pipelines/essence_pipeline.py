"""
EssenceAI Pipeline Runner
Runs EssenceAI pipeline internally (no HTTP calls).
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Essence imports will be handled dynamically due to optional dependencies
essence_module_path = Path(__file__).parent.parent / "essence"

# Global state for Essence orchestrator
_essence_orchestrator = None


def _initialize_essence_pipeline():
    """Initialize EssenceAI orchestrator if not already initialized."""
    global _essence_orchestrator
    
    if _essence_orchestrator is not None:
        return
    
    try:
        from ..essence.agents.orchestrator import AgentOrchestrator
        
        data_dir = essence_module_path / "data"
        _essence_orchestrator = AgentOrchestrator(data_dir=str(data_dir))
        
        # Initialize research agent
        print("Initializing EssenceAI research agent...")
        _essence_orchestrator.initialize_research(force_reload=False)
        print("✅ EssenceAI orchestrator initialized")
        
    except ImportError as e:
        print(f"⚠️  EssenceAI agents not available: {e}")
        print("   EssenceAI pipeline will return mock data")
        _essence_orchestrator = None
    except Exception as e:
        print(f"⚠️  Failed to initialize EssenceAI: {e}")
        _essence_orchestrator = None


async def run_essence_analysis(
    product_link: Optional[str] = None,
    product_description: Optional[str] = None,
    business_objective: str = "",
    domain: Optional[str] = None,
    segment: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run EssenceAI pipeline analysis internally.
    
    Args:
        product_link: Optional product URL
        product_description: Optional product description
        business_objective: Business objective
        domain: Optional domain filter
        segment: Optional segment filter
        
    Returns:
        Complete EssenceAI analysis result as dict
    """
    # Initialize if needed
    _initialize_essence_pipeline()
    
    # If orchestrator not available, return mock
    if _essence_orchestrator is None:
        return {
            "status": "mock",
            "message": "EssenceAI agents not available (missing dependencies). Mock response.",
            "input": {
                "product_link": product_link,
                "product_description": product_description,
                "business_objective": business_objective,
                "domain": domain,
                "segment": segment
            },
            "mock_data": {
                "competitor_analysis": {
                    "competitors": [
                        {
                            "name": "Mock Competitor 1",
                            "price": "€X.XX",
                            "positioning": "Mock positioning"
                        }
                    ]
                },
                "research_insights": {
                    "insights": [
                        "Mock research insight 1",
                        "Mock research insight 2"
                    ]
                },
                "marketing_strategy": {
                    "recommendations": [
                        "Mock marketing recommendation 1",
                        "Mock marketing recommendation 2"
                    ]
                }
            },
            "workflow": {
                "steps": [
                    {"agent": "competitor", "status": "mock"},
                    {"agent": "research", "status": "mock"},
                    {"agent": "marketing", "status": "mock"}
                ]
            }
        }
    
    # Prepare product description
    if product_link:
        # For now, use link as description
        # In production, you might want to fetch product info from the link
        product_desc = f"Product from link: {product_link}"
    else:
        product_desc = product_description
    
    # Execute full analysis
    result = _essence_orchestrator.execute_full_analysis(
        product_description=product_desc,
        domain=domain,
        segment=segment
    )
    
    # Add business objective and input echo
    if business_objective:
        result["business_objective"] = business_objective
    
    result["input"] = {
        "product_link": product_link,
        "product_description": product_description,
        "business_objective": business_objective,
        "domain": domain,
        "segment": segment
    }
    
    return result

